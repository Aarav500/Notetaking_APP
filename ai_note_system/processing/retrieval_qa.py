"""
Retrieval-Augmented Question Answering module for AI Note System.
Handles retrieving relevant notes and generating answers using an LLM.
"""

import os
import logging
import json
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime

# Import embedding interface
from ..api.llm_interface import LLMInterface, OpenAIInterface, HuggingFaceInterface

# Setup logging
logger = logging.getLogger("ai_note_system.processing.retrieval_qa")

def retrieve_relevant_notes(
    query: str,
    db_manager,
    embedder,
    max_results: int = 5,
    threshold: float = 0.7,
    filter_tags: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve notes relevant to a query using semantic search.
    
    Args:
        query (str): The query to search for
        db_manager: Database manager instance
        embedder: Embedder instance
        max_results (int): Maximum number of results to return
        threshold (float): Minimum similarity threshold (0-1)
        filter_tags (List[str], optional): Filter notes by tags
        
    Returns:
        List[Dict[str, Any]]: List of relevant notes with similarity scores
    """
    logger.info(f"Retrieving notes relevant to query: {query}")
    
    try:
        # Perform semantic search
        results = embedder.search_notes_by_embedding(
            query_text=query,
            limit=max_results,
            threshold=threshold,
            filter_tags=filter_tags
        )
        
        # Fetch full note content for each result
        enriched_results = []
        for note in results:
            note_id = note["id"]
            full_note = db_manager.get_note(note_id)
            
            if full_note:
                # Add similarity score from search results
                full_note["similarity"] = note["similarity"]
                enriched_results.append(full_note)
        
        logger.info(f"Retrieved {len(enriched_results)} relevant notes")
        return enriched_results
        
    except Exception as e:
        logger.error(f"Error retrieving relevant notes: {e}")
        return []

def generate_answer(
    query: str,
    relevant_notes: List[Dict[str, Any]],
    model: str = "gpt-4",
    max_tokens: int = 500,
    temperature: float = 0.7,
    include_sources: bool = True
) -> Dict[str, Any]:
    """
    Generate an answer to a query based on relevant notes using an LLM.
    
    Args:
        query (str): The query to answer
        relevant_notes (List[Dict[str, Any]]): List of relevant notes
        model (str): LLM model to use
        max_tokens (int): Maximum number of tokens in the response
        temperature (float): Temperature for LLM generation
        include_sources (bool): Whether to include source information
        
    Returns:
        Dict[str, Any]: Dictionary containing the answer and metadata
    """
    logger.info(f"Generating answer for query: {query}")
    
    try:
        # Initialize LLM interface
        llm = _initialize_llm_interface(model)
        
        # Prepare context from relevant notes
        context = _prepare_context_from_notes(relevant_notes)
        
        # Prepare prompt
        prompt = _create_qa_prompt(query, context, include_sources)
        
        # Generate answer
        response = llm.generate_text(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        # Parse response
        answer, sources = _parse_llm_response(response, relevant_notes, include_sources)
        
        # Create result
        result = {
            "query": query,
            "answer": answer,
            "model": model,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add sources if included
        if include_sources and sources:
            result["sources"] = sources
        
        logger.info(f"Generated answer ({len(answer)} chars)")
        return result
        
    except Exception as e:
        logger.error(f"Error generating answer: {e}")
        return {
            "query": query,
            "answer": f"Error generating answer: {e}",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def ask_question(
    query: str,
    db_manager,
    embedder,
    model: str = "gpt-4",
    max_results: int = 5,
    threshold: float = 0.7,
    filter_tags: Optional[List[str]] = None,
    max_tokens: int = 500,
    temperature: float = 0.7,
    include_sources: bool = True,
    use_knowledge_graph: bool = True,
    reasoning_mode: str = "advanced"
) -> Dict[str, Any]:
    """
    End-to-end function to ask a question and get an answer based on notes.
    
    Args:
        query (str): The question to ask
        db_manager: Database manager instance
        embedder: Embedder instance
        model (str): LLM model to use
        max_results (int): Maximum number of relevant notes to retrieve
        threshold (float): Minimum similarity threshold (0-1)
        filter_tags (List[str], optional): Filter notes by tags
        max_tokens (int): Maximum number of tokens in the response
        temperature (float): Temperature for LLM generation
        include_sources (bool): Whether to include source information
        use_knowledge_graph (bool): Whether to use knowledge graph for reasoning
        reasoning_mode (str): Reasoning mode ("basic", "advanced", "teaching")
        
    Returns:
        Dict[str, Any]: Dictionary containing the answer and metadata
    """
    logger.info(f"Processing question: {query} (reasoning_mode={reasoning_mode}, use_knowledge_graph={use_knowledge_graph})")
    
    # Retrieve relevant notes
    relevant_notes = retrieve_relevant_notes(
        query=query,
        db_manager=db_manager,
        embedder=embedder,
        max_results=max_results,
        threshold=threshold,
        filter_tags=filter_tags
    )
    
    # If no relevant notes found, return early
    if not relevant_notes:
        return {
            "query": query,
            "answer": "I couldn't find any relevant information in your notes to answer this question.",
            "timestamp": datetime.now().isoformat()
        }
    
    # Get knowledge graph information if requested
    knowledge_graph_data = None
    if use_knowledge_graph:
        try:
            # Import knowledge graph module
            from ..visualization.knowledge_graph_gen import extract_graph_data_from_db, query_knowledge_graph
            
            # Query knowledge graph
            knowledge_graph_data = query_knowledge_graph(
                db_manager=db_manager,
                query=query,
                max_nodes=max_results * 3,  # Use more nodes for knowledge graph
                similarity_threshold=threshold,
                tags=filter_tags
            )
            
            logger.info(f"Retrieved knowledge graph data with {len(knowledge_graph_data.get('matches', []))} matches")
        except Exception as e:
            logger.error(f"Error retrieving knowledge graph data: {e}")
            knowledge_graph_data = None
    
    # Generate answer with reasoning
    result = generate_answer_with_reasoning(
        query=query,
        relevant_notes=relevant_notes,
        knowledge_graph_data=knowledge_graph_data,
        reasoning_mode=reasoning_mode,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        include_sources=include_sources
    )
    
    return result

def _initialize_llm_interface(model: str) -> LLMInterface:
    """
    Initialize the appropriate LLM interface based on the model.
    
    Args:
        model (str): LLM model to use
        
    Returns:
        LLMInterface: Initialized LLM interface
    """
    # Check if model is an OpenAI model
    if model.startswith(("gpt-", "text-davinci-")):
        return OpenAIInterface(model=model)
    else:
        # Try to use Hugging Face
        return HuggingFaceInterface(model=model)

def _prepare_context_from_notes(notes: List[Dict[str, Any]]) -> str:
    """
    Prepare context from relevant notes for the LLM.
    
    Args:
        notes (List[Dict[str, Any]]): List of relevant notes
        
    Returns:
        str: Formatted context
    """
    context_parts = []
    
    for i, note in enumerate(notes, 1):
        # Get note information
        title = note.get("title", "Untitled")
        text = note.get("text", "")
        summary = note.get("summary", "")
        
        # Use summary if available, otherwise use text (truncated if too long)
        content = summary if summary else (text[:1000] + "..." if len(text) > 1000 else text)
        
        # Format note as context
        note_context = f"[NOTE {i}: {title}]\n{content}\n"
        context_parts.append(note_context)
    
    return "\n".join(context_parts)

def _create_qa_prompt(query: str, context: str, include_sources: bool) -> str:
    """
    Create a prompt for the LLM to answer the query based on the context.
    
    Args:
        query (str): The query to answer
        context (str): Context from relevant notes
        include_sources (bool): Whether to include source information
        
    Returns:
        str: Formatted prompt
    """
    if include_sources:
        prompt = f"""You are an AI assistant that answers questions based on the user's personal notes. 
Answer the following question using ONLY the information provided in the notes below.
If the notes don't contain enough information to answer the question fully, say so clearly.
Include references to which notes you used in your answer using the format [NOTE X].

NOTES:
{context}

QUESTION: {query}

ANSWER (including references to the notes used):"""
    else:
        prompt = f"""You are an AI assistant that answers questions based on the user's personal notes. 
Answer the following question using ONLY the information provided in the notes below.
If the notes don't contain enough information to answer the question fully, say so clearly.

NOTES:
{context}

QUESTION: {query}

ANSWER:"""
    
    return prompt

def _parse_llm_response(
    response: str,
    relevant_notes: List[Dict[str, Any]],
    include_sources: bool
) -> Tuple[str, Optional[List[Dict[str, Any]]]]:
    """
    Parse the LLM response to extract the answer and sources.
    
    Args:
        response (str): Raw LLM response
        relevant_notes (List[Dict[str, Any]]): List of relevant notes
        include_sources (bool): Whether to include source information
        
    Returns:
        Tuple[str, Optional[List[Dict[str, Any]]]]: Tuple of (answer, sources)
    """
    # For now, just return the response as is
    answer = response.strip()
    
    # Extract sources if requested
    sources = None
    if include_sources:
        sources = []
        for i, note in enumerate(relevant_notes, 1):
            # Check if this note is referenced in the answer
            if f"[NOTE {i}]" in answer or f"[NOTE {i}:" in answer:
                sources.append({
                    "id": note["id"],
                    "title": note.get("title", "Untitled"),
                    "similarity": note.get("similarity", 0.0)
                })
    
    return answer, sources
def generate_answer_with_reasoning(
    query: str,
    relevant_notes: List[Dict[str, Any]],
    knowledge_graph_data: Optional[Dict[str, Any]] = None,
    reasoning_mode: str = "advanced",
    model: str = "gpt-4",
    max_tokens: int = 800,
    temperature: float = 0.7,
    include_sources: bool = True
) -> Dict[str, Any]:
    """
    Generate an answer to a query with advanced reasoning capabilities.
    
    Args:
        query (str): The query to answer
        relevant_notes (List[Dict[str, Any]]): List of relevant notes
        knowledge_graph_data (Dict[str, Any], optional): Knowledge graph data
        reasoning_mode (str): Reasoning mode ("basic", "advanced", "teaching")
        model (str): LLM model to use
        max_tokens (int): Maximum number of tokens in the response
        temperature (float): Temperature for LLM generation
        include_sources (bool): Whether to include source information
        
    Returns:
        Dict[str, Any]: Dictionary containing the answer and metadata
    """
    logger.info(f"Generating answer with reasoning mode: {reasoning_mode}")
    
    try:
        # Initialize LLM interface
        llm = _initialize_llm_interface(model)
        
        # Prepare context from relevant notes
        context = _prepare_context_from_notes(relevant_notes)
        
        # Prepare knowledge graph context if available
        knowledge_graph_context = ""
        if knowledge_graph_data and knowledge_graph_data.get("matches"):
            knowledge_graph_context = _prepare_knowledge_graph_context(knowledge_graph_data)
        
        # Prepare prompt based on reasoning mode
        if reasoning_mode == "teaching":
            prompt = _create_teaching_prompt(query, context, knowledge_graph_context, include_sources)
        elif reasoning_mode == "advanced":
            prompt = _create_advanced_reasoning_prompt(query, context, knowledge_graph_context, include_sources)
        else:  # basic
            prompt = _create_qa_prompt(query, context, include_sources)
        
        # Generate answer
        response = llm.generate_text(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        # Parse response
        answer, sources = _parse_llm_response(response, relevant_notes, include_sources)
        
        # Create result
        result = {
            "query": query,
            "answer": answer,
            "model": model,
            "reasoning_mode": reasoning_mode,
            "used_knowledge_graph": knowledge_graph_data is not None,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add sources if included
        if include_sources and sources:
            result["sources"] = sources
        
        # Add knowledge graph matches if available
        if knowledge_graph_data and knowledge_graph_data.get("matches"):
            result["knowledge_graph_matches"] = knowledge_graph_data.get("matches")
        
        logger.info(f"Generated answer with reasoning ({len(answer)} chars)")
        return result
        
    except Exception as e:
        logger.error(f"Error generating answer with reasoning: {e}")
        return {
            "query": query,
            "answer": f"Error generating answer: {e}",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def _prepare_knowledge_graph_context(knowledge_graph_data: Dict[str, Any]) -> str:
    """
    Prepare context from knowledge graph data.
    
    Args:
        knowledge_graph_data (Dict[str, Any]): Knowledge graph data
        
    Returns:
        str: Formatted knowledge graph context
    """
    context_parts = []
    
    # Add explanation
    if knowledge_graph_data.get("explanation"):
        context_parts.append(f"Knowledge Graph Analysis: {knowledge_graph_data['explanation']}")
    
    # Add matches
    matches = knowledge_graph_data.get("matches", [])
    if matches:
        context_parts.append("\nKnowledge Graph Relationships:")
        
        for i, match in enumerate(matches, 1):
            if "prerequisite" in match:
                context_parts.append(f"{i}. Prerequisite: {match['prerequisite']} is required for understanding {match['for_concept']}")
                if "explanation" in match:
                    context_parts.append(f"   Explanation: {match['explanation']}")
            elif "source" in match and "target" in match:
                context_parts.append(f"{i}. Relationship: {match['source']} → {match['target']}")
                if "path_type" in match:
                    context_parts.append(f"   Type: {match['path_type']}")
                if "explanation" in match:
                    context_parts.append(f"   Explanation: {match['explanation']}")
            elif "dependency" in match:
                context_parts.append(f"{i}. Dependency: {match['for_concept']} depends on {match['dependency']}")
                if "relationship_type" in match:
                    context_parts.append(f"   Type: {match['relationship_type']}")
    
    return "\n".join(context_parts)

def _create_advanced_reasoning_prompt(
    query: str, 
    context: str, 
    knowledge_graph_context: str, 
    include_sources: bool
) -> str:
    """
    Create a prompt for advanced reasoning.
    
    Args:
        query (str): The query to answer
        context (str): Context from relevant notes
        knowledge_graph_context (str): Context from knowledge graph
        include_sources (bool): Whether to include source information
        
    Returns:
        str: Formatted prompt
    """
    prompt = f"""You are an AI assistant that answers questions based on the user's personal notes and knowledge graph. 
You don't just retrieve information; you reason through it to provide insightful, coherent explanations.

Answer the following question using the information provided in the notes and knowledge graph below.
If the information doesn't contain enough details to answer the question fully, say so clearly.
Use logical reasoning to connect concepts and explain relationships between ideas.
"""

    if knowledge_graph_context:
        prompt += f"""
KNOWLEDGE GRAPH INFORMATION:
{knowledge_graph_context}
"""

    prompt += f"""
NOTES:
{context}

QUESTION: {query}

"""

    if include_sources:
        prompt += "ANSWER (including references to the notes used and logical reasoning steps):"
    else:
        prompt += "ANSWER (including logical reasoning steps):"
    
    return prompt

def _create_teaching_prompt(
    query: str, 
    context: str, 
    knowledge_graph_context: str, 
    include_sources: bool
) -> str:
    """
    Create a prompt for teaching mode.
    
    Args:
        query (str): The query to answer
        context (str): Context from relevant notes
        knowledge_graph_context (str): Context from knowledge graph
        include_sources (bool): Whether to include source information
        
    Returns:
        str: Formatted prompt
    """
    prompt = f"""You are an expert tutor that teaches concepts based on the user's personal notes and knowledge graph.
Your goal is to explain concepts clearly, building understanding from fundamentals to advanced topics.

The user wants to learn about the following topic. Teach them using the information provided in the notes and knowledge graph below.
If the information doesn't contain enough details, say so clearly.
Structure your explanation pedagogically, starting with prerequisites and building to more complex ideas.
Use analogies and examples where helpful.
"""

    if knowledge_graph_context:
        prompt += f"""
KNOWLEDGE GRAPH INFORMATION (use this to understand prerequisites and relationships):
{knowledge_graph_context}
"""

    prompt += f"""
NOTES:
{context}

TOPIC TO TEACH: {query}

"""

    if include_sources:
        prompt += "EXPLANATION (including references to the notes used and building concepts step by step):"
    else:
        prompt += "EXPLANATION (building concepts step by step):"
    
    return prompt