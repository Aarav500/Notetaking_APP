"""
Topic Linker module for AI Note System.
Handles finding and linking related topics across the note hierarchy.
"""

import os
import logging
import json
from typing import Dict, Any, List, Optional, Tuple, Union
import numpy as np

# Setup logging
logger = logging.getLogger("ai_note_system.processing.topic_linker")

def find_related_topics(
    text: str,
    topic_db: Union[str, Dict[str, Any]],
    max_results: int = 5,
    threshold: float = 0.75,
    embedding_model: str = "all-MiniLM-L6-v2",
    hierarchical: bool = True
) -> Dict[str, Any]:
    """
    Find related topics for a given text.
    
    Args:
        text (str): The text to find related topics for
        topic_db (Union[str, Dict[str, Any]]): Path to topic database JSON file or the database dict
        max_results (int): Maximum number of related topics to return
        threshold (float): Similarity threshold (0-1)
        embedding_model (str): Model to use for embeddings
        hierarchical (bool): Whether to organize results hierarchically
        
    Returns:
        Dict[str, Any]: Dictionary containing the related topics and metadata
    """
    logger.info(f"Finding related topics using {embedding_model} model")
    
    if not text:
        logger.warning("Empty text provided for topic linking")
        return {"error": "Empty text provided"}
    
    # Load topic database if path is provided
    if isinstance(topic_db, str):
        try:
            with open(topic_db, 'r', encoding='utf-8') as f:
                topic_db = json.load(f)
        except Exception as e:
            logger.error(f"Error loading topic database: {e}")
            return {"error": f"Error loading topic database: {e}"}
    
    # Get embeddings for the text
    text_embedding = get_text_embedding(text, embedding_model)
    if text_embedding is None:
        return {"error": "Failed to generate text embedding"}
    
    # Find related topics
    related_topics = find_similar_topics(text_embedding, topic_db, max_results, threshold, hierarchical)
    
    # Create result dictionary
    result = {
        "related_topics": related_topics,
        "count": len(related_topics),
        "model": embedding_model,
        "threshold": threshold,
        "hierarchical": hierarchical
    }
    
    logger.debug(f"Related topics found: {result['count']} topics")
    return result

def get_text_embedding(
    text: str,
    model: str = "all-MiniLM-L6-v2"
) -> Optional[List[float]]:
    """
    Get embedding vector for text.
    
    Args:
        text (str): The text to get embedding for
        model (str): The embedding model to use
        
    Returns:
        Optional[List[float]]: The embedding vector or None if failed
    """
    try:
        # Try to use sentence-transformers
        from sentence_transformers import SentenceTransformer
        
        logger.debug(f"Generating embedding with {model}")
        
        # Load model
        embedding_model = SentenceTransformer(model)
        
        # Generate embedding
        embedding = embedding_model.encode(text)
        
        # Convert to list if numpy array
        if isinstance(embedding, np.ndarray):
            embedding = embedding.tolist()
        
        logger.debug(f"Embedding generated: {len(embedding)} dimensions")
        return embedding
        
    except ImportError:
        # Fall back to OpenAI if sentence-transformers not available
        try:
            import openai
            
            logger.debug("Falling back to OpenAI embeddings")
            
            # Call OpenAI API
            client = openai.OpenAI()
            response = client.embeddings.create(
                input=text,
                model="text-embedding-ada-002"
            )
            
            # Extract embedding
            embedding = response.data[0].embedding
            
            logger.debug(f"OpenAI embedding generated: {len(embedding)} dimensions")
            return embedding
            
        except ImportError:
            logger.error("Neither sentence-transformers nor OpenAI package is installed")
            return None
            
        except Exception as e:
            logger.error(f"Error generating OpenAI embedding: {e}")
            return None
            
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        return None

def find_similar_topics(
    embedding: List[float],
    topic_db: Dict[str, Any],
    max_results: int = 5,
    threshold: float = 0.75,
    hierarchical: bool = True
) -> List[Dict[str, Any]]:
    """
    Find similar topics based on embedding similarity.
    
    Args:
        embedding (List[float]): The embedding vector to compare against
        topic_db (Dict[str, Any]): The topic database
        max_results (int): Maximum number of results to return
        threshold (float): Similarity threshold (0-1)
        hierarchical (bool): Whether to organize results hierarchically
        
    Returns:
        List[Dict[str, Any]]: List of related topics
    """
    # Extract topics from database
    topics = topic_db.get("topics", [])
    if not topics:
        logger.warning("Empty topic database")
        return []
    
    # Calculate similarity for each topic
    similarities = []
    for topic in topics:
        # Skip topics without embeddings
        if "embedding" not in topic:
            continue
        
        # Calculate cosine similarity
        similarity = cosine_similarity(embedding, topic["embedding"])
        
        # Add to list if above threshold
        if similarity >= threshold:
            similarities.append((topic, similarity))
    
    # Sort by similarity (descending)
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    # Limit to max_results
    similarities = similarities[:max_results]
    
    # Format results
    if hierarchical:
        return format_hierarchical_results(similarities)
    else:
        return format_flat_results(similarities)

def cosine_similarity(
    vec1: List[float],
    vec2: List[float]
) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Args:
        vec1 (List[float]): First vector
        vec2 (List[float]): Second vector
        
    Returns:
        float: Cosine similarity (0-1)
    """
    # Convert to numpy arrays
    a = np.array(vec1)
    b = np.array(vec2)
    
    # Calculate cosine similarity
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    
    # Avoid division by zero
    if norm_a == 0 or norm_b == 0:
        return 0
    
    similarity = dot_product / (norm_a * norm_b)
    
    # Ensure result is between 0 and 1
    return max(0, min(1, similarity))

def format_flat_results(
    similarities: List[Tuple[Dict[str, Any], float]]
) -> List[Dict[str, Any]]:
    """
    Format similarity results as a flat list.
    
    Args:
        similarities (List[Tuple[Dict[str, Any], float]]): List of (topic, similarity) tuples
        
    Returns:
        List[Dict[str, Any]]: Formatted results
    """
    results = []
    
    for topic, similarity in similarities:
        # Create result dictionary
        result = {
            "title": topic.get("title", ""),
            "path": topic.get("path", ""),
            "similarity": round(similarity, 4)
        }
        
        # Add summary if available
        if "summary" in topic:
            result["summary"] = topic["summary"]
        
        results.append(result)
    
    return results

def format_hierarchical_results(
    similarities: List[Tuple[Dict[str, Any], float]]
) -> List[Dict[str, Any]]:
    """
    Format similarity results hierarchically by path.
    
    Args:
        similarities (List[Tuple[Dict[str, Any], float]]): List of (topic, similarity) tuples
        
    Returns:
        List[Dict[str, Any]]: Hierarchically formatted results
    """
    # Group by top-level category
    categories = {}
    
    for topic, similarity in similarities:
        # Get path components
        path = topic.get("path", "")
        path_components = path.split("/") if path else []
        
        # Use first component as category
        category = path_components[0] if path_components else "Uncategorized"
        
        # Create category if not exists
        if category not in categories:
            categories[category] = []
        
        # Create result dictionary
        result = {
            "title": topic.get("title", ""),
            "path": path,
            "similarity": round(similarity, 4)
        }
        
        # Add summary if available
        if "summary" in topic:
            result["summary"] = topic["summary"]
        
        # Add to category
        categories[category].append(result)
    
    # Format as hierarchical results
    results = []
    
    for category, topics in categories.items():
        # Sort topics by similarity
        topics.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Create category dictionary
        category_dict = {
            "category": category,
            "topics": topics
        }
        
        results.append(category_dict)
    
    # Sort categories by highest similarity in each
    results.sort(key=lambda x: max([t["similarity"] for t in x["topics"]]), reverse=True)
    
    return results

def create_topic_entry(
    title: str,
    text: str,
    path: str = "",
    summary: Optional[str] = None,
    embedding_model: str = "all-MiniLM-L6-v2"
) -> Dict[str, Any]:
    """
    Create a topic entry for the topic database.
    
    Args:
        title (str): Topic title
        text (str): Topic text content
        path (str): Hierarchical path (e.g., "CS/Basics/Variables")
        summary (str, optional): Topic summary
        embedding_model (str): Model to use for embeddings
        
    Returns:
        Dict[str, Any]: Topic entry
    """
    # Generate embedding
    embedding = get_text_embedding(text, embedding_model)
    
    # Create topic entry
    topic = {
        "title": title,
        "path": path,
        "embedding": embedding
    }
    
    # Add summary if provided
    if summary:
        topic["summary"] = summary
    
    return topic

def update_topic_database(
    topic_db_path: str,
    new_topic: Dict[str, Any]
) -> bool:
    """
    Update the topic database with a new topic.
    
    Args:
        topic_db_path (str): Path to topic database JSON file
        new_topic (Dict[str, Any]): New topic entry
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Load existing database
        if os.path.exists(topic_db_path):
            with open(topic_db_path, 'r', encoding='utf-8') as f:
                topic_db = json.load(f)
        else:
            # Create new database
            topic_db = {"topics": []}
        
        # Add new topic
        topic_db["topics"].append(new_topic)
        
        # Save database
        with open(topic_db_path, 'w', encoding='utf-8') as f:
            json.dump(topic_db, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Topic database updated: {topic_db_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error updating topic database: {e}")
        return False