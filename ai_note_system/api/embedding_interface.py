"""
Embedding Interface module for AI Note System.
Provides a unified interface for different embedding models (OpenAI, Hugging Face, SentenceTransformers).
"""

import os
import logging
from typing import Dict, Any, List, Optional, Union, Callable
from abc import ABC, abstractmethod

# Setup logging
logger = logging.getLogger("ai_note_system.api.embedding_interface")

class EmbeddingInterface(ABC):
    """
    Abstract base class for embedding interfaces.
    Defines the common interface that all embedding providers must implement.
    """
    
    @abstractmethod
    def get_embeddings(
        self,
        texts: Union[str, List[str]],
        **kwargs
    ) -> Union[List[float], List[List[float]]]:
        """
        Get embeddings for one or more texts.
        
        Args:
            texts (Union[str, List[str]]): Text or list of texts to embed
            **kwargs: Additional model-specific parameters
            
        Returns:
            Union[List[float], List[List[float]]]: Embeddings for the input texts
        """
        pass
    
    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embeddings.
        
        Returns:
            int: Dimension of the embeddings
        """
        pass
    
    @abstractmethod
    def compute_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """
        Compute the similarity between two embeddings.
        
        Args:
            embedding1 (List[float]): First embedding
            embedding2 (List[float]): Second embedding
            
        Returns:
            float: Similarity score (0.0 to 1.0)
        """
        pass
    
    def batch_compute_similarity(
        self,
        query_embedding: List[float],
        embeddings: List[List[float]]
    ) -> List[float]:
        """
        Compute similarities between a query embedding and multiple embeddings.
        
        Args:
            query_embedding (List[float]): Query embedding
            embeddings (List[List[float]]): List of embeddings to compare against
            
        Returns:
            List[float]: List of similarity scores
        """
        return [self.compute_similarity(query_embedding, emb) for emb in embeddings]


class OpenAIEmbeddingInterface(EmbeddingInterface):
    """
    Interface for OpenAI embeddings.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "text-embedding-3-small",
        organization: Optional[str] = None,
        dimensions: Optional[int] = None
    ):
        """
        Initialize the OpenAI embedding interface.
        
        Args:
            api_key (str, optional): OpenAI API key (defaults to OPENAI_API_KEY env var)
            model (str): Model to use (e.g., "text-embedding-3-small", "text-embedding-3-large")
            organization (str, optional): OpenAI organization ID
            dimensions (int, optional): Number of dimensions for the embeddings
        """
        try:
            import openai
            self.openai = openai
            
            # Set API key
            self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError("OpenAI API key not provided and not found in environment variables")
            
            # Initialize client
            self.client = openai.OpenAI(
                api_key=self.api_key,
                organization=organization
            )
            
            # Set model and dimensions
            self.model = model
            self.dimensions = dimensions
            
            # Set embedding dimension based on model
            if model == "text-embedding-3-small":
                self._embedding_dimension = 1536
            elif model == "text-embedding-3-large":
                self._embedding_dimension = 3072
            elif model == "text-embedding-ada-002":
                self._embedding_dimension = 1536
            else:
                self._embedding_dimension = 1536  # Default
            
            # Override with specified dimensions if provided
            if dimensions is not None:
                self._embedding_dimension = dimensions
            
            logger.info(f"Initialized OpenAI embedding interface with model: {model}")
            
        except ImportError:
            logger.error("OpenAI package not installed. Install with: pip install openai")
            raise
    
    def get_embeddings(
        self,
        texts: Union[str, List[str]],
        **kwargs
    ) -> Union[List[float], List[List[float]]]:
        """
        Get embeddings for one or more texts using OpenAI.
        
        Args:
            texts (Union[str, List[str]]): Text or list of texts to embed
            **kwargs: Additional model-specific parameters
            
        Returns:
            Union[List[float], List[List[float]]]: Embeddings for the input texts
        """
        try:
            # Convert single text to list
            if isinstance(texts, str):
                texts = [texts]
                single_input = True
            else:
                single_input = False
            
            # Get embeddings
            response = self.client.embeddings.create(
                model=self.model,
                input=texts,
                dimensions=self.dimensions,
                **kwargs
            )
            
            # Extract embeddings
            embeddings = [item.embedding for item in response.data]
            
            # Return single embedding for single input
            if single_input:
                return embeddings[0]
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error getting embeddings with OpenAI: {e}")
            # Return empty embeddings
            if isinstance(texts, str):
                return [0.0] * self._embedding_dimension
            else:
                return [[0.0] * self._embedding_dimension for _ in range(len(texts))]
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embeddings.
        
        Returns:
            int: Dimension of the embeddings
        """
        return self._embedding_dimension
    
    def compute_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """
        Compute the cosine similarity between two embeddings.
        
        Args:
            embedding1 (List[float]): First embedding
            embedding2 (List[float]): Second embedding
            
        Returns:
            float: Cosine similarity (0.0 to 1.0)
        """
        try:
            import numpy as np
            
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Compute cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
                
            cosine_similarity = dot_product / (norm1 * norm2)
            
            # Ensure result is in [0, 1] range
            return max(0.0, min(1.0, (1 + cosine_similarity) / 2))
            
        except Exception as e:
            logger.error(f"Error computing similarity: {e}")
            return 0.0


class SentenceTransformersInterface(EmbeddingInterface):
    """
    Interface for SentenceTransformers embeddings.
    """
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        device: str = "cpu",
        **model_kwargs
    ):
        """
        Initialize the SentenceTransformers interface.
        
        Args:
            model_name (str): Name of the model to use
            device (str): Device to run the model on ("cpu", "cuda")
            **model_kwargs: Additional model initialization parameters
        """
        try:
            from sentence_transformers import SentenceTransformer
            
            # Initialize model
            self.model = SentenceTransformer(model_name, device=device, **model_kwargs)
            
            # Store model name and embedding dimension
            self.model_name = model_name
            self._embedding_dimension = self.model.get_sentence_embedding_dimension()
            
            logger.info(f"Initialized SentenceTransformers interface with model: {model_name}")
            
        except ImportError:
            logger.error("SentenceTransformers package not installed. Install with: pip install sentence-transformers")
            raise
    
    def get_embeddings(
        self,
        texts: Union[str, List[str]],
        **kwargs
    ) -> Union[List[float], List[List[float]]]:
        """
        Get embeddings for one or more texts using SentenceTransformers.
        
        Args:
            texts (Union[str, List[str]]): Text or list of texts to embed
            **kwargs: Additional model-specific parameters
            
        Returns:
            Union[List[float], List[List[float]]]: Embeddings for the input texts
        """
        try:
            # Convert single text to list
            if isinstance(texts, str):
                texts = [texts]
                single_input = True
            else:
                single_input = False
            
            # Get embeddings
            embeddings = self.model.encode(texts, **kwargs)
            
            # Convert numpy arrays to lists
            embeddings = embeddings.tolist()
            
            # Return single embedding for single input
            if single_input:
                return embeddings[0]
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error getting embeddings with SentenceTransformers: {e}")
            # Return empty embeddings
            if isinstance(texts, str):
                return [0.0] * self._embedding_dimension
            else:
                return [[0.0] * self._embedding_dimension for _ in range(len(texts))]
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embeddings.
        
        Returns:
            int: Dimension of the embeddings
        """
        return self._embedding_dimension
    
    def compute_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """
        Compute the cosine similarity between two embeddings.
        
        Args:
            embedding1 (List[float]): First embedding
            embedding2 (List[float]): Second embedding
            
        Returns:
            float: Cosine similarity (0.0 to 1.0)
        """
        try:
            import numpy as np
            from sklearn.metrics.pairwise import cosine_similarity
            
            # Convert to numpy arrays
            vec1 = np.array(embedding1).reshape(1, -1)
            vec2 = np.array(embedding2).reshape(1, -1)
            
            # Compute cosine similarity
            similarity = cosine_similarity(vec1, vec2)[0][0]
            
            # Ensure result is in [0, 1] range
            return max(0.0, min(1.0, (1 + similarity) / 2))
            
        except ImportError:
            logger.warning("scikit-learn not installed. Using numpy for similarity calculation.")
            # Fallback to numpy implementation
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
                
            cosine_similarity = dot_product / (norm1 * norm2)
            
            # Ensure result is in [0, 1] range
            return max(0.0, min(1.0, (1 + cosine_similarity) / 2))
            
        except Exception as e:
            logger.error(f"Error computing similarity: {e}")
            return 0.0
    
    def batch_compute_similarity(
        self,
        query_embedding: List[float],
        embeddings: List[List[float]]
    ) -> List[float]:
        """
        Compute similarities between a query embedding and multiple embeddings.
        
        Args:
            query_embedding (List[float]): Query embedding
            embeddings (List[List[float]]): List of embeddings to compare against
            
        Returns:
            List[float]: List of similarity scores
        """
        try:
            import numpy as np
            from sklearn.metrics.pairwise import cosine_similarity
            
            # Convert to numpy arrays
            query_vec = np.array(query_embedding).reshape(1, -1)
            corpus_vecs = np.array(embeddings)
            
            # Compute cosine similarities
            similarities = cosine_similarity(query_vec, corpus_vecs)[0]
            
            # Ensure results are in [0, 1] range
            similarities = [(1 + sim) / 2 for sim in similarities]
            similarities = [max(0.0, min(1.0, sim)) for sim in similarities]
            
            return similarities
            
        except ImportError:
            logger.warning("scikit-learn not installed. Using base implementation.")
            # Fallback to base implementation
            return super().batch_compute_similarity(query_embedding, embeddings)
            
        except Exception as e:
            logger.error(f"Error computing batch similarities: {e}")
            return [0.0] * len(embeddings)


class HuggingFaceEmbeddingInterface(EmbeddingInterface):
    """
    Interface for Hugging Face embeddings.
    """
    
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        device: str = "cpu",
        token: Optional[str] = None,
        **model_kwargs
    ):
        """
        Initialize the Hugging Face embedding interface.
        
        Args:
            model_name (str): Name of the model to use
            device (str): Device to run the model on ("cpu", "cuda")
            token (str, optional): Hugging Face API token for gated models
            **model_kwargs: Additional model initialization parameters
        """
        try:
            from transformers import AutoTokenizer, AutoModel
            import torch
            
            self.torch = torch
            
            # Set API token if provided
            if token:
                os.environ["HUGGINGFACE_TOKEN"] = token
            
            # Initialize tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name, **model_kwargs)
            
            # Set device
            self.device = device
            if device == "cuda" and torch.cuda.is_available():
                self.model = self.model.to("cuda")
            else:
                self.device = "cpu"
                self.model = self.model.to("cpu")
            
            # Store model name
            self.model_name = model_name
            
            # Get embedding dimension
            with torch.no_grad():
                dummy_input = self.tokenizer("dummy text", return_tensors="pt", padding=True, truncation=True)
                if self.device == "cuda":
                    dummy_input = {k: v.to("cuda") for k, v in dummy_input.items()}
                outputs = self.model(**dummy_input)
                self._embedding_dimension = outputs.last_hidden_state.shape[-1]
            
            logger.info(f"Initialized Hugging Face embedding interface with model: {model_name}")
            
        except ImportError:
            logger.error("Transformers package not installed. Install with: pip install transformers torch")
            raise
    
    def get_embeddings(
        self,
        texts: Union[str, List[str]],
        **kwargs
    ) -> Union[List[float], List[List[float]]]:
        """
        Get embeddings for one or more texts using Hugging Face.
        
        Args:
            texts (Union[str, List[str]]): Text or list of texts to embed
            **kwargs: Additional model-specific parameters
            
        Returns:
            Union[List[float], List[List[float]]]: Embeddings for the input texts
        """
        try:
            # Convert single text to list
            if isinstance(texts, str):
                texts = [texts]
                single_input = True
            else:
                single_input = False
            
            # Tokenize texts
            inputs = self.tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
            
            # Move inputs to device
            if self.device == "cuda":
                inputs = {k: v.to("cuda") for k, v in inputs.items()}
            
            # Get embeddings
            with self.torch.no_grad():
                outputs = self.model(**inputs)
                
                # Use mean pooling to get sentence embeddings
                attention_mask = inputs["attention_mask"]
                token_embeddings = outputs.last_hidden_state
                
                # Mask padded tokens
                input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
                
                # Sum the masked token embeddings
                sum_embeddings = self.torch.sum(token_embeddings * input_mask_expanded, 1)
                
                # Sum the number of tokens
                sum_mask = self.torch.clamp(input_mask_expanded.sum(1), min=1e-9)
                
                # Divide to get mean
                embeddings = sum_embeddings / sum_mask
                
                # Convert to numpy and then to list
                embeddings = embeddings.cpu().numpy().tolist()
            
            # Return single embedding for single input
            if single_input:
                return embeddings[0]
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error getting embeddings with Hugging Face: {e}")
            # Return empty embeddings
            if isinstance(texts, str):
                return [0.0] * self._embedding_dimension
            else:
                return [[0.0] * self._embedding_dimension for _ in range(len(texts))]
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embeddings.
        
        Returns:
            int: Dimension of the embeddings
        """
        return self._embedding_dimension
    
    def compute_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """
        Compute the cosine similarity between two embeddings.
        
        Args:
            embedding1 (List[float]): First embedding
            embedding2 (List[float]): Second embedding
            
        Returns:
            float: Cosine similarity (0.0 to 1.0)
        """
        try:
            # Convert to torch tensors
            vec1 = self.torch.tensor(embedding1)
            vec2 = self.torch.tensor(embedding2)
            
            # Compute cosine similarity
            cos_sim = self.torch.nn.functional.cosine_similarity(vec1.unsqueeze(0), vec2.unsqueeze(0))
            similarity = cos_sim.item()
            
            # Ensure result is in [0, 1] range
            return max(0.0, min(1.0, (1 + similarity) / 2))
            
        except Exception as e:
            logger.error(f"Error computing similarity: {e}")
            # Fallback to numpy implementation
            import numpy as np
            
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
                
            cosine_similarity = dot_product / (norm1 * norm2)
            
            # Ensure result is in [0, 1] range
            return max(0.0, min(1.0, (1 + cosine_similarity) / 2))


def get_embedding_interface(provider: str, **kwargs) -> EmbeddingInterface:
    """
    Factory function to get an embedding interface based on the provider.
    
    Args:
        provider (str): Embedding provider ("openai", "sentence-transformers", "huggingface")
        **kwargs: Additional parameters for the interface
        
    Returns:
        EmbeddingInterface: The embedding interface
    """
    provider = provider.lower()
    
    if provider == "openai":
        return OpenAIEmbeddingInterface(**kwargs)
    elif provider in ["sentence-transformers", "st"]:
        return SentenceTransformersInterface(**kwargs)
    elif provider in ["huggingface", "hf"]:
        return HuggingFaceEmbeddingInterface(**kwargs)
    else:
        raise ValueError(f"Unsupported embedding provider: {provider}")


def create_embedding_interface_from_config(config: Dict[str, Any]) -> EmbeddingInterface:
    """
    Create an embedding interface from a configuration dictionary.
    
    Args:
        config (Dict[str, Any]): Configuration dictionary
        
    Returns:
        EmbeddingInterface: The embedding interface
    """
    provider = config.get("EMBEDDING_PROVIDER", "sentence-transformers")
    
    if provider == "openai":
        return OpenAIEmbeddingInterface(
            api_key=config.get("OPENAI_API_KEY"),
            model=config.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
            organization=config.get("OPENAI_ORGANIZATION"),
            dimensions=config.get("EMBEDDING_DIMENSIONS")
        )
    elif provider in ["sentence-transformers", "st"]:
        return SentenceTransformersInterface(
            model_name=config.get("SENTENCE_TRANSFORMERS_MODEL", "all-MiniLM-L6-v2"),
            device=config.get("EMBEDDING_DEVICE", "cpu")
        )
    elif provider in ["huggingface", "hf"]:
        return HuggingFaceEmbeddingInterface(
            model_name=config.get("HUGGINGFACE_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
            device=config.get("EMBEDDING_DEVICE", "cpu"),
            token=config.get("HUGGINGFACE_TOKEN")
        )
    else:
        raise ValueError(f"Unsupported embedding provider: {provider}")