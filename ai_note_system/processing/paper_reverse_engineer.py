"""
Research Paper Reverse Engineering module for AI Note System.
Extracts structured information from research papers and generates research recipes and quiz questions.
"""

import os
import logging
import json
import re
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime
import tempfile

# Setup logging
logger = logging.getLogger("ai_note_system.processing.paper_reverse_engineer")

# Import required modules
from ..api.llm_interface import get_llm_interface
from ..inputs.pdf_input import extract_text_from_pdf

class PaperReverseEngineer:
    """
    Extracts structured information from research papers and generates research recipes and quiz questions.
    """
    
    def __init__(
        self,
        llm_provider: str = "openai",
        llm_model: str = "gpt-4",
        output_dir: Optional[str] = None
    ):
        """
        Initialize the Paper Reverse Engineer.
        
        Args:
            llm_provider (str): LLM provider to use for analysis
            llm_model (str): LLM model to use for analysis
            output_dir (str, optional): Directory to save output files
        """
        # Initialize LLM interface
        self.llm = get_llm_interface(llm_provider, model=llm_model)
        
        # Set output directory
        self.output_dir = output_dir
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"Initialized Paper Reverse Engineer with {llm_provider} {llm_model}")
    
    def process_paper(
        self,
        paper_path: str,
        paper_title: Optional[str] = None,
        paper_authors: Optional[str] = None,
        paper_abstract: Optional[str] = None,
        generate_recipe: bool = True,
        generate_quiz: bool = True,
        save_output: bool = True
    ) -> Dict[str, Any]:
        """
        Process a research paper to extract structured information.
        
        Args:
            paper_path (str): Path to the research paper (PDF)
            paper_title (str, optional): Title of the paper (if not provided, will attempt to extract)
            paper_authors (str, optional): Authors of the paper (if not provided, will attempt to extract)
            paper_abstract (str, optional): Abstract of the paper (if not provided, will attempt to extract)
            generate_recipe (bool): Whether to generate a research recipe
            generate_quiz (bool): Whether to generate quiz questions
            save_output (bool): Whether to save the output to files
            
        Returns:
            Dict[str, Any]: Extracted information and generated materials
        """
        logger.info(f"Processing research paper: {paper_path}")
        
        # Extract text from PDF
        try:
            paper_text = extract_text_from_pdf(paper_path)
            if not paper_text:
                raise ValueError("Failed to extract text from PDF")
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return {"error": f"Error extracting text from PDF: {e}"}
        
        # Extract basic information if not provided
        if not paper_title or not paper_authors or not paper_abstract:
            basic_info = self._extract_basic_info(paper_text)
            
            if not paper_title:
                paper_title = basic_info.get("title", "Unknown Title")
            
            if not paper_authors:
                paper_authors = basic_info.get("authors", "Unknown Authors")
            
            if not paper_abstract:
                paper_abstract = basic_info.get("abstract", "")
        
        # Create result object
        result = {
            "paper_path": paper_path,
            "title": paper_title,
            "authors": paper_authors,
            "abstract": paper_abstract,
            "processed_at": datetime.now().isoformat()
        }
        
        # Extract structured information
        structured_info = self._extract_structured_info(paper_text, paper_title, paper_abstract)
        result.update(structured_info)
        
        # Generate research recipe if requested
        if generate_recipe:
            recipe = self._generate_research_recipe(structured_info)
            result["research_recipe"] = recipe
        
        # Generate quiz questions if requested
        if generate_quiz:
            quiz = self._generate_quiz_questions(structured_info)
            result["quiz_questions"] = quiz
        
        # Save output if requested
        if save_output and self.output_dir:
            self._save_output(result)
        
        return result
    
    def _extract_basic_info(self, paper_text: str) -> Dict[str, str]:
        """
        Extract basic information from paper text.
        
        Args:
            paper_text (str): Text of the paper
            
        Returns:
            Dict[str, str]: Basic information (title, authors, abstract)
        """
        logger.info("Extracting basic information from paper")
        
        # Define the schema for structured output
        basic_info_schema = {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "The title of the research paper"
                },
                "authors": {
                    "type": "string",
                    "description": "The authors of the research paper"
                },
                "abstract": {
                    "type": "string",
                    "description": "The abstract of the research paper"
                }
            }
        }
        
        # Use first 2000 characters for basic info extraction
        text_sample = paper_text[:2000]
        
        # Create the prompt for extraction
        prompt = f"""
        Extract the title, authors, and abstract from the following research paper text:
        
        {text_sample}
        
        Provide only these three pieces of information.
        """
        
        try:
            # Generate structured output
            basic_info = self.llm.generate_structured_output(
                prompt=prompt,
                output_schema=basic_info_schema,
                temperature=0.3
            )
            
            return basic_info
            
        except Exception as e:
            logger.error(f"Error extracting basic information: {e}")
            
            # Try simple regex extraction as fallback
            title_match = re.search(r'^(.+?)\n', paper_text)
            title = title_match.group(1) if title_match else "Unknown Title"
            
            authors_match = re.search(r'\n(.+?)\n.+?@', paper_text)
            authors = authors_match.group(1) if authors_match else "Unknown Authors"
            
            abstract_match = re.search(r'Abstract\s*\n(.+?)(?:\n\n|\n[A-Z][a-z]+\s*\n)', paper_text, re.DOTALL)
            abstract = abstract_match.group(1) if abstract_match else ""
            
            return {
                "title": title,
                "authors": authors,
                "abstract": abstract
            }
    
    def _extract_structured_info(
        self,
        paper_text: str,
        paper_title: str,
        paper_abstract: str
    ) -> Dict[str, Any]:
        """
        Extract structured information from paper text.
        
        Args:
            paper_text (str): Text of the paper
            paper_title (str): Title of the paper
            paper_abstract (str): Abstract of the paper
            
        Returns:
            Dict[str, Any]: Structured information
        """
        logger.info("Extracting structured information from paper")
        
        # Define the schema for structured output
        structured_info_schema = {
            "type": "object",
            "properties": {
                "research_questions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The main research questions addressed in the paper"
                },
                "hypotheses": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The hypotheses proposed in the paper"
                },
                "methods": {
                    "type": "object",
                    "properties": {
                        "approach": {"type": "string"},
                        "data_collection": {"type": "string"},
                        "analysis_techniques": {"type": "string"}
                    },
                    "description": "The methods used in the research"
                },
                "key_experiments": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "results": {"type": "string"}
                        }
                    },
                    "description": "The key experiments conducted in the research"
                },
                "conclusions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The main conclusions of the research"
                },
                "limitations": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The limitations acknowledged in the research"
                },
                "future_work": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Suggestions for future work mentioned in the paper"
                },
                "key_contributions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The key contributions of the research"
                }
            }
        }
        
        # Create the prompt for extraction
        prompt = f"""
        Extract structured information from the following research paper:
        
        Title: {paper_title}
        
        Abstract: {paper_abstract}
        
        Paper Text (excerpt):
        {paper_text[:5000]}...
        
        Extract the following information:
        1. Research questions
        2. Hypotheses
        3. Methods (approach, data collection, analysis techniques)
        4. Key experiments with results
        5. Conclusions
        6. Limitations
        7. Future work
        8. Key contributions
        
        If any section is not explicitly stated in the paper, make a reasonable inference based on the content.
        """
        
        try:
            # Generate structured output
            structured_info = self.llm.generate_structured_output(
                prompt=prompt,
                output_schema=structured_info_schema,
                temperature=0.3
            )
            
            return structured_info
            
        except Exception as e:
            logger.error(f"Error extracting structured information: {e}")
            
            # Return empty structured info as fallback
            return {
                "research_questions": ["Could not extract research questions"],
                "hypotheses": ["Could not extract hypotheses"],
                "methods": {
                    "approach": "Could not extract approach",
                    "data_collection": "Could not extract data collection methods",
                    "analysis_techniques": "Could not extract analysis techniques"
                },
                "key_experiments": [
                    {
                        "name": "Unknown experiment",
                        "description": "Could not extract experiment details",
                        "results": "Could not extract results"
                    }
                ],
                "conclusions": ["Could not extract conclusions"],
                "limitations": ["Could not extract limitations"],
                "future_work": ["Could not extract future work"],
                "key_contributions": ["Could not extract key contributions"]
            }
    
    def _generate_research_recipe(self, structured_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a research recipe based on structured information.
        
        Args:
            structured_info (Dict[str, Any]): Structured information extracted from the paper
            
        Returns:
            Dict[str, Any]: Research recipe
        """
        logger.info("Generating research recipe")
        
        # Define the schema for structured output
        recipe_schema = {
            "type": "object",
            "properties": {
                "overview": {
                    "type": "string",
                    "description": "A brief overview of the research approach"
                },
                "prerequisites": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "knowledge": {"type": "string"},
                            "importance": {"type": "string"}
                        }
                    },
                    "description": "Knowledge prerequisites for understanding and replicating the research"
                },
                "steps": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "step_number": {"type": "integer"},
                            "description": {"type": "string"},
                            "details": {"type": "string"},
                            "tips": {"type": "string"}
                        }
                    },
                    "description": "Step-by-step guide to replicate or extend the research"
                },
                "potential_extensions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Potential ways to extend or build upon the research"
                },
                "common_pitfalls": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Common pitfalls to avoid when replicating or extending the research"
                },
                "resources": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "type": {"type": "string"}
                        }
                    },
                    "description": "Useful resources for replicating or extending the research"
                }
            }
        }
        
        # Create the prompt for recipe generation
        prompt = f"""
        Generate a detailed "research recipe" based on the following structured information extracted from a research paper:
        
        Research Questions: {structured_info.get('research_questions', [])}
        
        Hypotheses: {structured_info.get('hypotheses', [])}
        
        Methods:
        - Approach: {structured_info.get('methods', {}).get('approach', '')}
        - Data Collection: {structured_info.get('methods', {}).get('data_collection', '')}
        - Analysis Techniques: {structured_info.get('methods', {}).get('analysis_techniques', '')}
        
        Key Experiments:
        {json.dumps(structured_info.get('key_experiments', []), indent=2)}
        
        Conclusions: {structured_info.get('conclusions', [])}
        
        Limitations: {structured_info.get('limitations', [])}
        
        Future Work: {structured_info.get('future_work', [])}
        
        Key Contributions: {structured_info.get('key_contributions', [])}
        
        The research recipe should provide a step-by-step guide for someone who wants to replicate or extend this research.
        Include prerequisites, detailed steps, potential extensions, common pitfalls, and useful resources.
        """
        
        try:
            # Generate structured output
            recipe = self.llm.generate_structured_output(
                prompt=prompt,
                output_schema=recipe_schema,
                temperature=0.5
            )
            
            # Add metadata
            recipe["generated_at"] = datetime.now().isoformat()
            
            return recipe
            
        except Exception as e:
            logger.error(f"Error generating research recipe: {e}")
            
            # Return simple recipe as fallback
            return {
                "overview": "This research recipe provides a simplified approach to replicating the study.",
                "prerequisites": [
                    {
                        "knowledge": "Understanding of the research domain",
                        "importance": "Essential for comprehending the methodology"
                    }
                ],
                "steps": [
                    {
                        "step_number": 1,
                        "description": "Review the methodology",
                        "details": "Carefully read the methods section of the paper",
                        "tips": "Pay attention to the specific techniques used"
                    },
                    {
                        "step_number": 2,
                        "description": "Replicate the experiments",
                        "details": "Follow the experimental procedures described in the paper",
                        "tips": "Start with a simplified version if the full experiment is complex"
                    }
                ],
                "potential_extensions": ["Consider applying the methodology to different datasets"],
                "common_pitfalls": ["Overlooking important details in the methodology"],
                "resources": [
                    {
                        "name": "Original paper",
                        "description": "The primary source for understanding the research",
                        "type": "reference"
                    }
                ],
                "generated_at": datetime.now().isoformat()
            }
    
    def _generate_quiz_questions(self, structured_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate quiz questions based on structured information.
        
        Args:
            structured_info (Dict[str, Any]): Structured information extracted from the paper
            
        Returns:
            List[Dict[str, Any]]: Quiz questions
        """
        logger.info("Generating quiz questions")
        
        # Define the schema for structured output
        quiz_schema = {
            "type": "object",
            "properties": {
                "questions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "question_type": {
                                "type": "string",
                                "enum": ["multiple_choice", "true_false", "short_answer", "fill_in_blank"]
                            },
                            "question_text": {"type": "string"},
                            "options": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "correct_answer": {"type": "string"},
                            "explanation": {"type": "string"},
                            "difficulty": {
                                "type": "string",
                                "enum": ["easy", "medium", "hard"]
                            },
                            "topic": {"type": "string"}
                        },
                        "required": ["question_type", "question_text", "correct_answer", "explanation", "difficulty", "topic"]
                    }
                }
            }
        }
        
        # Create the prompt for quiz generation
        prompt = f"""
        Generate a set of 10 quiz questions based on the following structured information extracted from a research paper:
        
        Research Questions: {structured_info.get('research_questions', [])}
        
        Hypotheses: {structured_info.get('hypotheses', [])}
        
        Methods:
        - Approach: {structured_info.get('methods', {}).get('approach', '')}
        - Data Collection: {structured_info.get('methods', {}).get('data_collection', '')}
        - Analysis Techniques: {structured_info.get('methods', {}).get('analysis_techniques', '')}
        
        Key Experiments:
        {json.dumps(structured_info.get('key_experiments', []), indent=2)}
        
        Conclusions: {structured_info.get('conclusions', [])}
        
        Key Contributions: {structured_info.get('key_contributions', [])}
        
        Create a mix of question types (multiple choice, true/false, short answer, fill in the blank).
        For multiple choice questions, provide 4 options.
        Include questions of varying difficulty (easy, medium, hard).
        Each question should test understanding of the paper's methodology, results, or implications.
        """
        
        try:
            # Generate structured output
            quiz_data = self.llm.generate_structured_output(
                prompt=prompt,
                output_schema=quiz_schema,
                temperature=0.7
            )
            
            # Process questions
            questions = quiz_data.get("questions", [])
            
            # Add metadata
            for question in questions:
                question["generated_at"] = datetime.now().isoformat()
                
                # Ensure options exist for multiple choice questions
                if question["question_type"] == "multiple_choice" and "options" not in question:
                    question["options"] = [
                        question["correct_answer"],
                        f"Incorrect option 1",
                        f"Incorrect option 2",
                        f"Incorrect option 3"
                    ]
                    # Shuffle options (simple approach)
                    import random
                    random.shuffle(question["options"])
            
            return questions
            
        except Exception as e:
            logger.error(f"Error generating quiz questions: {e}")
            
            # Return simple questions as fallback
            return [
                {
                    "question_type": "multiple_choice",
                    "question_text": "What is the main research question addressed in the paper?",
                    "options": [
                        structured_info.get("research_questions", ["Unknown"])[0],
                        "A different research question",
                        "Another different research question",
                        "Yet another different research question"
                    ],
                    "correct_answer": structured_info.get("research_questions", ["Unknown"])[0],
                    "explanation": "This is the primary research question stated in the paper.",
                    "difficulty": "easy",
                    "topic": "Research Questions",
                    "generated_at": datetime.now().isoformat()
                },
                {
                    "question_type": "true_false",
                    "question_text": "The paper acknowledges limitations in the research methodology.",
                    "correct_answer": "True" if structured_info.get("limitations") else "False",
                    "explanation": "The paper does discuss limitations of the research approach.",
                    "difficulty": "easy",
                    "topic": "Research Limitations",
                    "generated_at": datetime.now().isoformat()
                }
            ]
    
    def _save_output(self, result: Dict[str, Any]) -> Dict[str, str]:
        """
        Save output to files.
        
        Args:
            result (Dict[str, Any]): Processing result
            
        Returns:
            Dict[str, str]: Paths to saved files
        """
        # Create a sanitized filename base from the paper title
        title = result.get("title", "unknown_paper")
        base_filename = re.sub(r'[^\w\s-]', '', title).strip().lower().replace(' ', '_')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create output paths
        structured_info_path = os.path.join(self.output_dir, f"{base_filename}_structured_info_{timestamp}.json")
        recipe_path = os.path.join(self.output_dir, f"{base_filename}_research_recipe_{timestamp}.json")
        quiz_path = os.path.join(self.output_dir, f"{base_filename}_quiz_questions_{timestamp}.json")
        
        # Save structured information
        structured_info = {k: v for k, v in result.items() if k not in ["research_recipe", "quiz_questions"]}
        with open(structured_info_path, "w") as f:
            json.dump(structured_info, f, indent=2)
        
        # Save research recipe if available
        saved_paths = {"structured_info": structured_info_path}
        
        if "research_recipe" in result:
            with open(recipe_path, "w") as f:
                json.dump(result["research_recipe"], f, indent=2)
            saved_paths["research_recipe"] = recipe_path
        
        # Save quiz questions if available
        if "quiz_questions" in result:
            with open(quiz_path, "w") as f:
                json.dump(result["quiz_questions"], f, indent=2)
            saved_paths["quiz_questions"] = quiz_path
        
        logger.info(f"Saved output files: {saved_paths}")
        return saved_paths


def main():
    """
    Command-line interface for the Paper Reverse Engineer.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Research Paper Reverse Engineering")
    parser.add_argument("--paper", required=True, help="Path to the research paper (PDF)")
    parser.add_argument("--title", help="Title of the paper")
    parser.add_argument("--authors", help="Authors of the paper")
    parser.add_argument("--abstract", help="Abstract of the paper")
    parser.add_argument("--no-recipe", action="store_true", help="Skip generating research recipe")
    parser.add_argument("--no-quiz", action="store_true", help="Skip generating quiz questions")
    parser.add_argument("--output", help="Output directory")
    parser.add_argument("--llm", default="openai", help="LLM provider")
    parser.add_argument("--model", default="gpt-4", help="LLM model")
    
    args = parser.parse_args()
    
    # Initialize reverse engineer
    engineer = PaperReverseEngineer(
        llm_provider=args.llm,
        llm_model=args.model,
        output_dir=args.output
    )
    
    # Process paper
    result = engineer.process_paper(
        paper_path=args.paper,
        paper_title=args.title,
        paper_authors=args.authors,
        paper_abstract=args.abstract,
        generate_recipe=not args.no_recipe,
        generate_quiz=not args.no_quiz,
        save_output=bool(args.output)
    )
    
    # Check for errors
    if "error" in result:
        print(f"Error: {result['error']}")
        return
    
    # Print summary
    print("\nRESEARCH PAPER REVERSE ENGINEERING")
    print("=" * 50)
    
    print(f"\nTitle: {result['title']}")
    print(f"Authors: {result['authors']}")
    print(f"\nAbstract: {result['abstract'][:200]}...")
    
    print("\nResearch Questions:")
    for question in result.get("research_questions", []):
        print(f"- {question}")
    
    print("\nHypotheses:")
    for hypothesis in result.get("hypotheses", []):
        print(f"- {hypothesis}")
    
    print("\nMethods:")
    methods = result.get("methods", {})
    print(f"- Approach: {methods.get('approach', '')}")
    print(f"- Data Collection: {methods.get('data_collection', '')}")
    print(f"- Analysis Techniques: {methods.get('analysis_techniques', '')}")
    
    print("\nKey Experiments:")
    for i, experiment in enumerate(result.get("key_experiments", []), 1):
        print(f"\n{i}. {experiment.get('name', 'Experiment')}")
        print(f"   Description: {experiment.get('description', '')}")
        print(f"   Results: {experiment.get('results', '')}")
    
    print("\nConclusions:")
    for conclusion in result.get("conclusions", []):
        print(f"- {conclusion}")
    
    if "research_recipe" in result:
        recipe = result["research_recipe"]
        print("\nRESEARCH RECIPE")
        print("=" * 50)
        print(f"\nOverview: {recipe.get('overview', '')}")
        
        print("\nPrerequisites:")
        for prereq in recipe.get("prerequisites", []):
            print(f"- {prereq.get('knowledge', '')}: {prereq.get('importance', '')}")
        
        print("\nSteps:")
        for step in recipe.get("steps", []):
            print(f"\n{step.get('step_number', 0)}. {step.get('description', '')}")
            print(f"   Details: {step.get('details', '')}")
            print(f"   Tips: {step.get('tips', '')}")
    
    if "quiz_questions" in result:
        print("\nQUIZ QUESTIONS")
        print("=" * 50)
        
        for i, question in enumerate(result["quiz_questions"], 1):
            print(f"\n{i}. [{question.get('difficulty', 'medium')}] {question.get('question_text', '')}")
            
            if question.get("question_type") == "multiple_choice":
                for j, option in enumerate(question.get("options", []), 1):
                    print(f"   {j}. {option}")
            
            print(f"\n   Answer: {question.get('correct_answer', '')}")
            print(f"   Explanation: {question.get('explanation', '')}")
    
    if args.output:
        print(f"\nOutput saved to {args.output}")


if __name__ == "__main__":
    main()