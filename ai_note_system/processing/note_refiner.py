"""
Note refinement module for AI Note System.
Refines notes by improving clarity, adding missing context, and generating analogies.
"""

import os
import logging
import json
from typing import Dict, Any, List, Optional, Union
import requests
from datetime import datetime

# Setup logging
logger = logging.getLogger("ai_note_system.processing.note_refiner")

def refine_note(
    content: Dict[str, Any],
    improve_clarity: bool = True,
    add_context: bool = True,
    generate_analogies: bool = True,
    internet_retrieval: bool = True,
    flag_unclear_explanations: bool = True,
    identify_missing_diagrams: bool = True
) -> Dict[str, Any]:
    """
    Refine a note by improving clarity, adding missing context, generating analogies,
    flagging unclear explanations, and identifying missing diagrams/examples.
    
    Args:
        content (Dict[str, Any]): The content to refine
        improve_clarity (bool): Whether to improve clarity
        add_context (bool): Whether to add missing context
        generate_analogies (bool): Whether to generate analogies
        internet_retrieval (bool): Whether to use internet retrieval for adding context
        flag_unclear_explanations (bool): Whether to flag unclear explanations
        identify_missing_diagrams (bool): Whether to identify missing diagrams/examples
        
    Returns:
        Dict[str, Any]: Refined content
    """
    logger.info("Refining note")
    
    # Create a copy of the content to avoid modifying the original
    refined_content = content.copy()
    
    # Get the text to refine
    text = content.get("text", "")
    summary = content.get("summary", "")
    
    # Skip if no text or summary
    if not text and not summary:
        logger.warning("No text or summary to refine")
        return refined_content
    
    # Use the summary if available, otherwise use the text
    content_to_refine = summary if summary else text
    
    # Refine the content
    refinements = {}
    
    # Improve clarity if requested
    if improve_clarity:
        logger.info("Improving clarity")
        refinements["improved_clarity"] = improve_content_clarity(content_to_refine)
    
    # Add missing context if requested
    if add_context:
        logger.info("Adding missing context")
        refinements["added_context"] = add_missing_context(content_to_refine, internet_retrieval)
    
    # Generate analogies if requested
    if generate_analogies:
        logger.info("Generating analogies")
        refinements["analogies"] = generate_content_analogies(content_to_refine)
    
    # Flag unclear explanations if requested
    if flag_unclear_explanations:
        logger.info("Flagging unclear explanations")
        refinements["unclear_explanations"] = flag_unclear_content_explanations(content_to_refine)
    
    # Identify missing diagrams/examples if requested
    if identify_missing_diagrams:
        logger.info("Identifying missing diagrams/examples")
        refinements["missing_diagrams"] = identify_missing_content_diagrams(content_to_refine)
    
    # Add refinements to the content
    refined_content["refinements"] = refinements
    
    # Add quality score based on refinements
    quality_score = calculate_content_quality_score(refinements)
    refined_content["quality_score"] = quality_score
    
    # Add timestamp
    refined_content["refinement_timestamp"] = datetime.now().isoformat()
    
    return refined_content

def improve_content_clarity(content: str) -> str:
    """
    Improve the clarity of content.
    
    Args:
        content (str): The content to improve
        
    Returns:
        str: Improved content
    """
    from ai_note_system.api.llm_interface import get_llm_interface
    
    # Create prompt for improving clarity
    prompt = f"""
    Please improve the clarity of the following text while preserving all the information:
    
    {content}
    
    Improved version:
    """
    
    # Get improved content from LLM
    try:
        # Get LLM interface
        llm = get_llm_interface("openai")  # Use default provider, can be configured
        
        # Generate text
        improved_content = llm.generate_text(prompt)
        return improved_content
    except Exception as e:
        logger.error(f"Error improving clarity: {str(e)}")
        return content

def add_missing_context(content: str, use_internet: bool = True) -> str:
    """
    Add missing context to content.
    
    Args:
        content (str): The content to add context to
        use_internet (bool): Whether to use internet retrieval
        
    Returns:
        str: Content with added context
    """
    from ai_note_system.api.llm_interface import get_llm_interface
    
    # Identify topics that need more context
    topics_prompt = f"""
    Please identify up to 3 topics or concepts in the following text that would benefit from additional context or explanation:
    
    {content}
    
    List the topics in JSON format like this:
    [
        "topic1",
        "topic2",
        "topic3"
    ]
    """
    
    try:
        # Get LLM interface
        llm = get_llm_interface("openai")  # Use default provider, can be configured
        
        # Generate text
        topics_json = llm.generate_text(topics_prompt)
        topics = json.loads(topics_json)
    except Exception as e:
        logger.error(f"Error identifying topics: {str(e)}")
        return content
    
    # Get additional context for each topic
    additional_context = ""
    
    for topic in topics:
        if use_internet:
            # Get information from the internet
            internet_info = retrieve_information_from_internet(topic)
            
            if internet_info:
                # Create prompt for adding context with internet information
                context_prompt = f"""
                Please add context to the topic "{topic}" based on the following information:
                
                Original content:
                {content}
                
                Additional information:
                {internet_info}
                
                Provide a concise paragraph with the additional context:
                """
                
                try:
                    # Use the same LLM interface
                    topic_context = llm.generate_text(context_prompt)
                    additional_context += f"\n\n**Additional Context for {topic}**:\n{topic_context}"
                except Exception as e:
                    logger.error(f"Error adding context for {topic}: {str(e)}")
        else:
            # Create prompt for adding context without internet information
            context_prompt = f"""
            Please add context to the topic "{topic}" based on your knowledge:
            
            Original content:
            {content}
            
            Provide a concise paragraph with additional context:
            """
            
            try:
                # Use the same LLM interface
                topic_context = llm.generate_text(context_prompt)
                additional_context += f"\n\n**Additional Context for {topic}**:\n{topic_context}"
            except Exception as e:
                logger.error(f"Error adding context for {topic}: {str(e)}")
    
    # Return content with additional context
    if additional_context:
        return f"{content}\n\n**Additional Context**:{additional_context}"
    else:
        return content

def generate_content_analogies(content: str) -> List[Dict[str, str]]:
    """
    Generate analogies for difficult concepts in the content.
    
    Args:
        content (str): The content to generate analogies for
        
    Returns:
        List[Dict[str, str]]: List of analogies with concept and analogy
    """
    from ai_note_system.api.llm_interface import get_llm_interface
    
    # Create prompt for identifying difficult concepts
    concepts_prompt = f"""
    Please identify up to 3 difficult or abstract concepts in the following text that would benefit from analogies:
    
    {content}
    
    List the concepts in JSON format like this:
    [
        "concept1",
        "concept2",
        "concept3"
    ]
    """
    
    try:
        # Get LLM interface
        llm = get_llm_interface("openai")  # Use default provider, can be configured
        
        # Generate text
        concepts_json = llm.generate_text(concepts_prompt)
        concepts = json.loads(concepts_json)
    except Exception as e:
        logger.error(f"Error identifying concepts: {str(e)}")
        return []
    
    # Generate analogies for each concept
    analogies = []
    
    for concept in concepts:
        # Create prompt for generating an analogy
        analogy_prompt = f"""
        Please generate a clear, intuitive analogy for the concept "{concept}" based on the following content:
        
        {content}
        
        The analogy should make the concept easier to understand for someone unfamiliar with it.
        """
        
        try:
            analogy = llm.generate_text(analogy_prompt)
            analogies.append({
                "concept": concept,
                "analogy": analogy
            })
        except Exception as e:
            logger.error(f"Error generating analogy for {concept}: {str(e)}")
    
    return analogies

def retrieve_information_from_internet(query: str) -> str:
    """
    Retrieve information from the internet using SerpAPI.
    
    Args:
        query (str): The query to search for
        
    Returns:
        str: Retrieved information
    """
    logger.info(f"Retrieving information for: {query}")
    
    try:
        # Use SerpAPI for internet search
        api_key = os.environ.get("SERPAPI_API_KEY", "")
        if not api_key:
            logger.warning("No SerpAPI key found in environment variables")
            return ""
        
        # Make API request to SerpAPI
        response = requests.get(
            "https://serpapi.com/search",
            params={
                "q": query,
                "api_key": api_key,
                "engine": "google",
                "num": 5  # Get top 5 results
            }
        )
        
        # Check response
        if response.status_code != 200:
            logger.error(f"SerpAPI error: {response.text}")
            return ""
        
        # Parse response
        result = response.json()
        
        # Extract information from search results
        information = ""
        
        # Add organic results
        if "organic_results" in result:
            for i, res in enumerate(result["organic_results"][:3], 1):
                title = res.get("title", "")
                snippet = res.get("snippet", "")
                link = res.get("link", "")
                
                information += f"{i}. {title}\n{snippet}\n{link}\n\n"
        
        # Add knowledge graph if available
        if "knowledge_graph" in result:
            kg = result["knowledge_graph"]
            title = kg.get("title", "")
            description = kg.get("description", "")
            
            information += f"Knowledge Graph: {title}\n{description}\n\n"
        
        # Add answer box if available
        if "answer_box" in result:
            answer = result["answer_box"]
            if "answer" in answer:
                information += f"Direct Answer: {answer['answer']}\n\n"
            elif "snippet" in answer:
                information += f"Featured Snippet: {answer['snippet']}\n\n"
        
        if not information:
            logger.warning(f"No information found for query: {query}")
            return ""
        
        return information
    except Exception as e:
        logger.error(f"Error retrieving information: {str(e)}")
        return ""
def flag_unclear_content_explanations(content: str) -> List[Dict[str, Any]]:
    """
    Flag unclear explanations in content.
    
    Args:
        content (str): The content to analyze
        
    Returns:
        List[Dict[str, Any]]: List of unclear explanations with suggestions
    """
    from ai_note_system.api.llm_interface import get_llm_interface
    
    # Create prompt for identifying unclear explanations
    prompt = f"""
    Please analyze the following text and identify any unclear explanations, complex concepts without sufficient explanation, or confusing passages.
    For each unclear explanation, provide:
    1. The unclear text or concept
    2. Why it's unclear or confusing
    3. A suggestion for improvement
    
    Text to analyze:
    {content}
    
    Format your response as a JSON array with objects containing "text", "reason", and "suggestion" fields.
    Only include genuinely unclear explanations, not minor stylistic issues.
    If there are no unclear explanations, return an empty array.
    """
    
    try:
        # Get LLM interface
        llm = get_llm_interface("openai", model="gpt-4")
        
        # Generate analysis
        response = llm.generate_text(prompt)
        
        # Parse response as JSON
        try:
            unclear_explanations = json.loads(response)
            if not isinstance(unclear_explanations, list):
                unclear_explanations = []
        except json.JSONDecodeError:
            logger.error(f"Error parsing unclear explanations response: {response}")
            unclear_explanations = []
        
        return unclear_explanations
    except Exception as e:
        logger.error(f"Error flagging unclear explanations: {str(e)}")
        return []

def identify_missing_content_diagrams(content: str) -> List[Dict[str, Any]]:
    """
    Identify concepts that would benefit from diagrams or examples.
    
    Args:
        content (str): The content to analyze
        
    Returns:
        List[Dict[str, Any]]: List of concepts that need diagrams or examples
    """
    from ai_note_system.api.llm_interface import get_llm_interface
    
    # Create prompt for identifying missing diagrams/examples
    prompt = f"""
    Please analyze the following text and identify concepts or explanations that would benefit from diagrams, visualizations, or concrete examples.
    For each identified concept:
    1. The concept or explanation that needs a diagram/example
    2. Why a diagram or example would be helpful
    3. A description of what the diagram/example should illustrate
    
    Text to analyze:
    {content}
    
    Format your response as a JSON array with objects containing "concept", "reason", and "diagram_description" fields.
    Focus on concepts where a visual aid or example would significantly improve understanding.
    If there are no concepts that need diagrams/examples, return an empty array.
    """
    
    try:
        # Get LLM interface
        llm = get_llm_interface("openai", model="gpt-4")
        
        # Generate analysis
        response = llm.generate_text(prompt)
        
        # Parse response as JSON
        try:
            missing_diagrams = json.loads(response)
            if not isinstance(missing_diagrams, list):
                missing_diagrams = []
        except json.JSONDecodeError:
            logger.error(f"Error parsing missing diagrams response: {response}")
            missing_diagrams = []
        
        return missing_diagrams
    except Exception as e:
        logger.error(f"Error identifying missing diagrams: {str(e)}")
        return []

def calculate_content_quality_score(refinements: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate a quality score based on refinements.
    
    Args:
        refinements (Dict[str, Any]): The refinements dictionary
        
    Returns:
        Dict[str, Any]: Quality score and breakdown
    """
    # Initialize scores
    clarity_score = 10.0  # Start with perfect score
    completeness_score = 10.0
    overall_score = 10.0
    
    # Deduct points for unclear explanations
    unclear_explanations = refinements.get("unclear_explanations", [])
    if unclear_explanations:
        # Deduct 1 point for each unclear explanation, up to 5 points
        clarity_deduction = min(5.0, len(unclear_explanations))
        clarity_score -= clarity_deduction
    
    # Deduct points for missing diagrams/examples
    missing_diagrams = refinements.get("missing_diagrams", [])
    if missing_diagrams:
        # Deduct 0.5 points for each missing diagram, up to 3 points
        completeness_deduction = min(3.0, len(missing_diagrams) * 0.5)
        completeness_score -= completeness_deduction
    
    # Calculate overall score (weighted average)
    overall_score = (clarity_score * 0.6) + (completeness_score * 0.4)
    
    # Round scores to one decimal place
    clarity_score = round(clarity_score, 1)
    completeness_score = round(completeness_score, 1)
    overall_score = round(overall_score, 1)
    
    # Create quality score dictionary
    quality_score = {
        "overall": overall_score,
        "clarity": clarity_score,
        "completeness": completeness_score,
        "issues_count": {
            "unclear_explanations": len(unclear_explanations),
            "missing_diagrams": len(missing_diagrams)
        },
        "rating": _get_quality_rating(overall_score),
        "improvement_needed": overall_score < 8.0
    }
    
    return quality_score

def _get_quality_rating(score: float) -> str:
    """
    Get a quality rating based on score.
    
    Args:
        score (float): The quality score
        
    Returns:
        str: Quality rating
    """
    if score >= 9.0:
        return "Excellent"
    elif score >= 8.0:
        return "Good"
    elif score >= 6.0:
        return "Needs Improvement"
    else:
        return "Poor"

def run_periodic_quality_check(db_manager, days: int = 30) -> Dict[str, Any]:
    """
    Run a periodic quality check on notes.
    
    Args:
        db_manager: Database manager instance
        days (int): Number of days to look back
        
    Returns:
        Dict[str, Any]: Quality check results
    """
    logger.info(f"Running periodic quality check for notes from the last {days} days")
    
    try:
        # Get recent notes
        recent_notes = db_manager.get_recent_notes(days)
        
        if not recent_notes:
            logger.info("No recent notes found for quality check")
            return {
                "status": "success",
                "message": "No recent notes found for quality check",
                "notes_checked": 0,
                "notes_needing_improvement": 0
            }
        
        # Check each note
        notes_checked = 0
        notes_needing_improvement = []
        
        for note in recent_notes:
            # Skip notes that have already been refined recently
            if "refinement_timestamp" in note:
                continue
            
            # Refine the note
            refined_note = refine_note(
                note,
                flag_unclear_explanations=True,
                identify_missing_diagrams=True
            )
            
            notes_checked += 1
            
            # Check if note needs improvement
            quality_score = refined_note.get("quality_score", {})
            if quality_score.get("improvement_needed", False):
                notes_needing_improvement.append({
                    "id": note.get("id"),
                    "title": note.get("title"),
                    "quality_score": quality_score,
                    "unclear_explanations": len(refined_note.get("refinements", {}).get("unclear_explanations", [])),
                    "missing_diagrams": len(refined_note.get("refinements", {}).get("missing_diagrams", []))
                })
                
                # Update note with quality score
                db_manager.update_note(note.get("id"), {"quality_score": quality_score})
        
        # Create result
        result = {
            "status": "success",
            "message": f"Quality check completed for {notes_checked} notes",
            "notes_checked": notes_checked,
            "notes_needing_improvement": len(notes_needing_improvement),
            "improvement_details": notes_needing_improvement
        }
        
        logger.info(f"Quality check completed: {notes_checked} notes checked, {len(notes_needing_improvement)} need improvement")
        return result
        
    except Exception as e:
        logger.error(f"Error running periodic quality check: {str(e)}")
        return {
            "status": "error",
            "message": f"Error running periodic quality check: {str(e)}",
            "notes_checked": 0,
            "notes_needing_improvement": 0
        }