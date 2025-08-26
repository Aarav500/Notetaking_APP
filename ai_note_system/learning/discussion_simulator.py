"""
AI-Driven Discussion Simulator module for AI Note System.
Generates debate simulations between agent personas with different viewpoints.
"""

import os
import logging
import json
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime
import time
import random

# Setup logging
logger = logging.getLogger("ai_note_system.learning.discussion_simulator")

# Import required modules
from ..api.llm_interface import get_llm_interface

class DiscussionSimulator:
    """
    Generates debate simulations between agent personas with different viewpoints.
    Allows users to observe reasoning paths, intervene with questions, and add arguments.
    """
    
    def __init__(
        self,
        llm_provider: str = "openai",
        llm_model: str = "gpt-4",
        output_dir: Optional[str] = None
    ):
        """
        Initialize the Discussion Simulator.
        
        Args:
            llm_provider (str): LLM provider to use for generating discussions
            llm_model (str): LLM model to use for generating discussions
            output_dir (str, optional): Directory to save discussion transcripts
        """
        # Initialize LLM interface
        self.llm = get_llm_interface(llm_provider, model=llm_model)
        
        # Set output directory
        self.output_dir = output_dir
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"Initialized Discussion Simulator with {llm_provider} {llm_model}")
    
    def create_discussion(
        self,
        topic: str,
        concept: str,
        num_agents: int = 2,
        agent_personas: Optional[List[Dict[str, str]]] = None,
        context: Optional[str] = None,
        max_turns: int = 10
    ) -> Dict[str, Any]:
        """
        Create a new discussion simulation.
        
        Args:
            topic (str): The general topic area
            concept (str): The specific concept to discuss
            num_agents (int): Number of agent personas to include
            agent_personas (List[Dict[str, str]], optional): Custom agent personas
            context (str, optional): Additional context about the concept
            max_turns (int): Maximum number of turns in the discussion
            
        Returns:
            Dict[str, Any]: The created discussion
        """
        logger.info(f"Creating discussion on {concept} in {topic}")
        
        # Generate agent personas if not provided
        if not agent_personas:
            agent_personas = self._generate_agent_personas(topic, concept, num_agents)
        
        # Create discussion object
        discussion = {
            "id": f"discussion_{int(time.time())}",
            "topic": topic,
            "concept": concept,
            "context": context,
            "created_at": datetime.now().isoformat(),
            "agent_personas": agent_personas,
            "max_turns": max_turns,
            "turns": [],
            "user_interventions": [],
            "status": "created"
        }
        
        # Generate initial prompt for the discussion
        discussion["initial_prompt"] = self._generate_initial_prompt(
            topic, concept, context, agent_personas
        )
        
        return discussion
    
    def _generate_agent_personas(
        self,
        topic: str,
        concept: str,
        num_agents: int
    ) -> List[Dict[str, str]]:
        """
        Generate agent personas with different viewpoints.
        
        Args:
            topic (str): The general topic area
            concept (str): The specific concept to discuss
            num_agents (int): Number of agent personas to generate
            
        Returns:
            List[Dict[str, str]]: List of agent personas
        """
        logger.info(f"Generating {num_agents} agent personas for {concept}")
        
        # Define the schema for structured output
        personas_schema = {
            "type": "object",
            "properties": {
                "personas": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "background": {"type": "string"},
                            "viewpoint": {"type": "string"},
                            "argumentation_style": {"type": "string"},
                            "key_arguments": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        }
                    }
                }
            }
        }
        
        # Create the prompt for generating personas
        prompt = f"""
        Generate {num_agents} distinct agent personas for a simulated discussion about '{concept}' in the field of {topic}.
        
        Each persona should have:
        1. A name and brief background (academic/professional)
        2. A distinct viewpoint on {concept} (they should have different perspectives)
        3. A unique argumentation style
        4. 3-5 key arguments they might make
        
        The personas should represent different valid perspectives on the concept, not just "pro" and "con".
        They should have nuanced views based on different theoretical frameworks, methodologies, or applications.
        """
        
        try:
            # Generate structured personas
            response = self.llm.generate_structured_output(
                prompt=prompt,
                output_schema=personas_schema,
                temperature=0.7
            )
            
            return response.get("personas", [])
            
        except Exception as e:
            logger.error(f"Error generating agent personas: {e}")
            
            # Create default personas as fallback
            default_personas = []
            for i in range(num_agents):
                default_personas.append({
                    "name": f"Agent {i+1}",
                    "background": f"Expert in {topic}",
                    "viewpoint": f"Perspective {i+1} on {concept}",
                    "argumentation_style": "Logical and evidence-based" if i % 2 == 0 else "Practical and example-oriented",
                    "key_arguments": [f"Argument {j+1} for perspective {i+1}" for j in range(3)]
                })
            
            return default_personas
    
    def _generate_initial_prompt(
        self,
        topic: str,
        concept: str,
        context: Optional[str],
        agent_personas: List[Dict[str, str]]
    ) -> str:
        """
        Generate the initial prompt for the discussion.
        
        Args:
            topic (str): The general topic area
            concept (str): The specific concept to discuss
            context (str, optional): Additional context about the concept
            agent_personas (List[Dict[str, str]]): Agent personas
            
        Returns:
            str: Initial prompt for the discussion
        """
        # Create the initial prompt
        prompt = f"Discussion on '{concept}' in the field of {topic}.\n\n"
        
        if context:
            prompt += f"Context: {context}\n\n"
        
        prompt += "Participants:\n"
        for persona in agent_personas:
            prompt += f"- {persona['name']} ({persona['background']}): {persona['viewpoint']}\n"
        
        prompt += "\nThe discussion will explore different perspectives on this concept, with each participant presenting their viewpoint and responding to others."
        
        return prompt
    
    def run_discussion(
        self,
        discussion: Dict[str, Any],
        interactive: bool = True,
        save_transcript: bool = True
    ) -> Dict[str, Any]:
        """
        Run a discussion simulation.
        
        Args:
            discussion (Dict[str, Any]): The discussion to run
            interactive (bool): Whether to allow user interaction
            save_transcript (bool): Whether to save the discussion transcript
            
        Returns:
            Dict[str, Any]: The updated discussion with turns
        """
        logger.info(f"Running discussion {discussion['id']} on {discussion['concept']}")
        
        # Print initial prompt
        if interactive:
            print("\n" + "="*50)
            print("AI-DRIVEN DISCUSSION SIMULATOR")
            print("="*50)
            print(discussion["initial_prompt"])
            print("\nStarting discussion...\n")
        
        # Initialize discussion state
        current_turn = 0
        discussion["status"] = "in_progress"
        
        # Run discussion turns
        while current_turn < discussion["max_turns"] and discussion["status"] == "in_progress":
            # Generate next turn
            turn = self._generate_turn(discussion, current_turn)
            discussion["turns"].append(turn)
            
            # Print turn
            if interactive:
                self._print_turn(turn)
            
            # Allow user intervention
            if interactive and current_turn < discussion["max_turns"] - 1:
                intervention = self._get_user_intervention()
                if intervention:
                    discussion["user_interventions"].append({
                        "turn": current_turn,
                        "intervention": intervention,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # Generate response to intervention
                    response = self._generate_intervention_response(discussion, intervention)
                    discussion["turns"].append(response)
                    
                    # Print response
                    self._print_turn(response)
            
            # Increment turn counter
            current_turn += 1
        
        # Mark discussion as completed
        discussion["status"] = "completed"
        
        # Save transcript if requested
        if save_transcript and self.output_dir:
            self._save_transcript(discussion)
        
        return discussion
    
    def _generate_turn(
        self,
        discussion: Dict[str, Any],
        turn_number: int
    ) -> Dict[str, Any]:
        """
        Generate the next turn in the discussion.
        
        Args:
            discussion (Dict[str, Any]): The discussion
            turn_number (int): The current turn number
            
        Returns:
            Dict[str, Any]: The generated turn
        """
        # Get discussion context
        topic = discussion["topic"]
        concept = discussion["concept"]
        personas = discussion["agent_personas"]
        previous_turns = discussion["turns"]
        user_interventions = discussion["user_interventions"]
        
        # Determine which agent speaks in this turn
        agent_idx = turn_number % len(personas)
        agent = personas[agent_idx]
        
        # Create the prompt for generating the turn
        prompt = self._create_turn_prompt(
            topic, concept, agent, personas, previous_turns, user_interventions
        )
        
        try:
            # Generate the turn content
            response = self.llm.generate_text(prompt=prompt, temperature=0.7)
            
            # Create turn object
            turn = {
                "turn_number": turn_number,
                "agent_idx": agent_idx,
                "agent_name": agent["name"],
                "content": response.strip(),
                "timestamp": datetime.now().isoformat(),
                "type": "agent_turn"
            }
            
            return turn
            
        except Exception as e:
            logger.error(f"Error generating turn: {e}")
            
            # Create a fallback turn
            return {
                "turn_number": turn_number,
                "agent_idx": agent_idx,
                "agent_name": agent["name"],
                "content": f"I'd like to share my perspective on {concept} based on my background in {agent['background']}. {agent['key_arguments'][0] if agent['key_arguments'] else ''}",
                "timestamp": datetime.now().isoformat(),
                "type": "agent_turn"
            }
    
    def _create_turn_prompt(
        self,
        topic: str,
        concept: str,
        current_agent: Dict[str, str],
        all_agents: List[Dict[str, str]],
        previous_turns: List[Dict[str, Any]],
        user_interventions: List[Dict[str, Any]]
    ) -> str:
        """
        Create a prompt for generating a turn.
        
        Args:
            topic (str): The general topic area
            concept (str): The specific concept to discuss
            current_agent (Dict[str, str]): The agent speaking in this turn
            all_agents (List[Dict[str, str]]): All agent personas
            previous_turns (List[Dict[str, Any]]): Previous turns in the discussion
            user_interventions (List[Dict[str, Any]]): User interventions
            
        Returns:
            str: Prompt for generating the turn
        """
        # Create the base prompt
        prompt = f"""
        You are simulating {current_agent['name']}, a {current_agent['background']}.
        
        Your viewpoint on '{concept}' in {topic} is: {current_agent['viewpoint']}
        
        Your argumentation style is: {current_agent['argumentation_style']}
        
        Key arguments you might make:
        {' '.join(['- ' + arg for arg in current_agent['key_arguments']])}
        
        The discussion so far:
        """
        
        # Add previous turns
        for turn in previous_turns:
            prompt += f"\n{turn['agent_name']}: {turn['content']}\n"
        
        # Add recent user interventions
        recent_interventions = [i for i in user_interventions if i["turn"] == len(previous_turns) - 1]
        if recent_interventions:
            prompt += "\nUser interventions/questions:\n"
            for intervention in recent_interventions:
                prompt += f"- {intervention['intervention']}\n"
        
        # Add instructions for this turn
        prompt += f"\nNow, as {current_agent['name']}, provide your next contribution to the discussion. "
        
        if not previous_turns:
            prompt += "This is the start of the discussion, so introduce your perspective on the concept."
        else:
            prompt += "Respond to previous points, defend your viewpoint, and advance the discussion with new insights."
        
        if recent_interventions:
            prompt += " Also address the user's questions or points."
        
        prompt += "\n\nYour response should be 2-3 paragraphs, showing your reasoning process and maintaining your unique perspective and argumentation style."
        
        return prompt
    
    def _print_turn(self, turn: Dict[str, Any]) -> None:
        """
        Print a turn to the console.
        
        Args:
            turn (Dict[str, Any]): The turn to print
        """
        if turn["type"] == "agent_turn":
            print(f"\n{turn['agent_name']}:")
            print(f"{turn['content']}")
        elif turn["type"] == "intervention_response":
            print(f"\nResponse to your question/point:")
            print(f"{turn['content']}")
        
        print("\n" + "-"*50)
    
    def _get_user_intervention(self) -> Optional[str]:
        """
        Get an intervention from the user.
        
        Returns:
            Optional[str]: The user's intervention, or None if no intervention
        """
        print("\nOptions:")
        print("1. Continue the discussion")
        print("2. Ask a question or make a point")
        print("3. End the discussion")
        
        choice = input("\nYour choice (1-3): ").strip()
        
        if choice == "2":
            intervention = input("\nEnter your question or point: ").strip()
            return intervention
        elif choice == "3":
            return "END_DISCUSSION"
        else:
            return None
    
    def _generate_intervention_response(
        self,
        discussion: Dict[str, Any],
        intervention: str
    ) -> Dict[str, Any]:
        """
        Generate a response to a user intervention.
        
        Args:
            discussion (Dict[str, Any]): The discussion
            intervention (str): The user's intervention
            
        Returns:
            Dict[str, Any]: The generated response
        """
        # Check if the user wants to end the discussion
        if intervention == "END_DISCUSSION":
            discussion["status"] = "completed"
            return {
                "turn_number": len(discussion["turns"]),
                "agent_name": "System",
                "content": "Discussion ended by user.",
                "timestamp": datetime.now().isoformat(),
                "type": "system_message"
            }
        
        # Create the prompt for generating the response
        prompt = f"""
        In a discussion about '{discussion['concept']}' in {discussion['topic']}, a user has asked the following question or made the following point:
        
        "{intervention}"
        
        Provide a thoughtful response that:
        1. Addresses the question or point directly
        2. Incorporates perspectives from the different viewpoints in the discussion
        3. Provides additional insights or clarifications
        4. Encourages further thinking on the topic
        
        Your response should be balanced and educational, helping the user understand the different perspectives on this concept.
        """
        
        try:
            # Generate the response
            response = self.llm.generate_text(prompt=prompt, temperature=0.7)
            
            # Create response object
            return {
                "turn_number": len(discussion["turns"]),
                "content": response.strip(),
                "intervention": intervention,
                "timestamp": datetime.now().isoformat(),
                "type": "intervention_response"
            }
            
        except Exception as e:
            logger.error(f"Error generating intervention response: {e}")
            
            # Create a fallback response
            return {
                "turn_number": len(discussion["turns"]),
                "content": f"That's an interesting point about {discussion['concept']}. The different perspectives we've discussed would approach this in various ways, considering factors like [relevant factors]. Would you like the discussion to explore this aspect further?",
                "intervention": intervention,
                "timestamp": datetime.now().isoformat(),
                "type": "intervention_response"
            }
    
    def _save_transcript(self, discussion: Dict[str, Any]) -> str:
        """
        Save the discussion transcript to a file.
        
        Args:
            discussion (Dict[str, Any]): The discussion to save
            
        Returns:
            str: Path to the saved transcript
        """
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        concept_slug = discussion["concept"].lower().replace(" ", "_")
        filename = f"discussion_{concept_slug}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        # Save as JSON
        with open(filepath, "w") as f:
            json.dump(discussion, f, indent=2)
        
        logger.info(f"Saved discussion transcript to {filepath}")
        return filepath
    
    def generate_summary(self, discussion: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a summary of the discussion.
        
        Args:
            discussion (Dict[str, Any]): The discussion to summarize
            
        Returns:
            Dict[str, Any]: Summary of the discussion
        """
        logger.info(f"Generating summary for discussion {discussion['id']}")
        
        # Define the schema for structured output
        summary_schema = {
            "type": "object",
            "properties": {
                "key_points": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Key points made during the discussion"
                },
                "perspectives": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "agent_name": {"type": "string"},
                            "main_arguments": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "reasoning_approach": {"type": "string"}
                        }
                    },
                    "description": "Summary of each agent's perspective and arguments"
                },
                "areas_of_agreement": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Points where agents found common ground"
                },
                "areas_of_disagreement": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Points where agents disagreed"
                },
                "learning_insights": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Key insights for learning about this concept"
                }
            }
        }
        
        # Create the prompt for generating the summary
        prompt = f"""
        Summarize the following discussion about '{discussion['concept']}' in the field of {discussion['topic']}.
        
        Discussion transcript:
        """
        
        # Add turns to the prompt
        for turn in discussion["turns"]:
            if turn["type"] == "agent_turn":
                prompt += f"\n{turn['agent_name']}: {turn['content']}\n"
            elif turn["type"] == "intervention_response":
                prompt += f"\nResponse to user: {turn['content']}\n"
        
        # Add instructions for the summary
        prompt += """
        Provide a structured summary that includes:
        1. Key points made during the discussion
        2. Summary of each agent's perspective and main arguments
        3. Areas where the agents found common ground
        4. Areas where the agents disagreed
        5. Key insights for learning about this concept
        """
        
        try:
            # Generate structured summary
            summary = self.llm.generate_structured_output(
                prompt=prompt,
                output_schema=summary_schema,
                temperature=0.3
            )
            
            # Add metadata
            summary["discussion_id"] = discussion["id"]
            summary["topic"] = discussion["topic"]
            summary["concept"] = discussion["concept"]
            summary["generated_at"] = datetime.now().isoformat()
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating discussion summary: {e}")
            
            # Create a simple summary as fallback
            return {
                "discussion_id": discussion["id"],
                "topic": discussion["topic"],
                "concept": discussion["concept"],
                "generated_at": datetime.now().isoformat(),
                "key_points": ["The discussion covered various aspects of the concept."],
                "perspectives": [
                    {
                        "agent_name": agent["name"],
                        "main_arguments": agent["key_arguments"][:2],
                        "reasoning_approach": agent["argumentation_style"]
                    }
                    for agent in discussion["agent_personas"]
                ],
                "areas_of_agreement": ["There were some areas of agreement."],
                "areas_of_disagreement": ["There were some areas of disagreement."],
                "learning_insights": ["The concept has multiple valid perspectives."]
            }


def main():
    """
    Command-line interface for the Discussion Simulator.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="AI-Driven Discussion Simulator")
    parser.add_argument("--topic", required=True, help="General topic area")
    parser.add_argument("--concept", required=True, help="Specific concept to discuss")
    parser.add_argument("--agents", type=int, default=2, help="Number of agent personas")
    parser.add_argument("--turns", type=int, default=10, help="Maximum number of turns")
    parser.add_argument("--context", help="Additional context about the concept")
    parser.add_argument("--output", help="Directory to save discussion transcript")
    parser.add_argument("--non-interactive", action="store_true", help="Run in non-interactive mode")
    parser.add_argument("--llm", default="openai", help="LLM provider")
    parser.add_argument("--model", default="gpt-4", help="LLM model")
    
    args = parser.parse_args()
    
    # Initialize simulator
    simulator = DiscussionSimulator(
        llm_provider=args.llm,
        llm_model=args.model,
        output_dir=args.output
    )
    
    # Create discussion
    discussion = simulator.create_discussion(
        topic=args.topic,
        concept=args.concept,
        num_agents=args.agents,
        context=args.context,
        max_turns=args.turns
    )
    
    # Run discussion
    discussion = simulator.run_discussion(
        discussion=discussion,
        interactive=not args.non_interactive,
        save_transcript=bool(args.output)
    )
    
    # Generate summary
    summary = simulator.generate_summary(discussion)
    
    # Print summary
    print("\n" + "="*50)
    print("DISCUSSION SUMMARY")
    print("="*50)
    
    print(f"\nTopic: {summary['topic']}")
    print(f"Concept: {summary['concept']}")
    
    print("\nKey Points:")
    for point in summary["key_points"]:
        print(f"- {point}")
    
    print("\nPerspectives:")
    for perspective in summary["perspectives"]:
        print(f"\n{perspective['agent_name']}:")
        print(f"Reasoning approach: {perspective['reasoning_approach']}")
        print("Main arguments:")
        for arg in perspective["main_arguments"]:
            print(f"- {arg}")
    
    print("\nAreas of Agreement:")
    for area in summary["areas_of_agreement"]:
        print(f"- {area}")
    
    print("\nAreas of Disagreement:")
    for area in summary["areas_of_disagreement"]:
        print(f"- {area}")
    
    print("\nLearning Insights:")
    for insight in summary["learning_insights"]:
        print(f"- {insight}")
    
    print("\n" + "="*50)


if __name__ == "__main__":
    main()