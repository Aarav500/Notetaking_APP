"""
LLM Interface module for AI Note System.
Provides a unified interface for different LLM providers (OpenAI, Ollama, LM Studio, Hugging Face).
"""

import os
import logging
import json
from typing import Dict, Any, List, Optional, Union, Callable
from abc import ABC, abstractmethod

# Setup logging
logger = logging.getLogger("ai_note_system.api.llm_interface")

class LLMInterface(ABC):
    """
    Abstract base class for LLM interfaces.
    Defines the common interface that all LLM providers must implement.
    """
    
    @abstractmethod
    def generate_text(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        top_p: float = 1.0,
        stop_sequences: Optional[List[str]] = None,
        **kwargs
    ) -> str:
        """
        Generate text from a prompt.
        
        Args:
            prompt (str): The prompt to generate text from
            max_tokens (int): Maximum number of tokens to generate
            temperature (float): Sampling temperature (0.0 to 1.0)
            top_p (float): Nucleus sampling parameter (0.0 to 1.0)
            stop_sequences (List[str], optional): Sequences that stop generation
            **kwargs: Additional model-specific parameters
            
        Returns:
            str: The generated text
        """
        pass
    
    @abstractmethod
    def generate_chat_response(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 500,
        temperature: float = 0.7,
        top_p: float = 1.0,
        stop_sequences: Optional[List[str]] = None,
        **kwargs
    ) -> str:
        """
        Generate a response in a chat conversation.
        
        Args:
            messages (List[Dict[str, str]]): List of message dictionaries with 'role' and 'content'
            max_tokens (int): Maximum number of tokens to generate
            temperature (float): Sampling temperature (0.0 to 1.0)
            top_p (float): Nucleus sampling parameter (0.0 to 1.0)
            stop_sequences (List[str], optional): Sequences that stop generation
            **kwargs: Additional model-specific parameters
            
        Returns:
            str: The generated response
        """
        pass
    
    @abstractmethod
    def generate_structured_output(
        self,
        prompt: str,
        output_schema: Dict[str, Any],
        temperature: float = 0.2,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate structured output (JSON) from a prompt.
        
        Args:
            prompt (str): The prompt to generate structured output from
            output_schema (Dict[str, Any]): JSON schema defining the expected output structure
            temperature (float): Sampling temperature (0.0 to 1.0)
            **kwargs: Additional model-specific parameters
            
        Returns:
            Dict[str, Any]: The generated structured output
        """
        pass
    
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a text.
        
        Args:
            text (str): The text to count tokens for
            
        Returns:
            int: The number of tokens
        """
        pass


class OpenAIInterface(LLMInterface):
    """
    Interface for OpenAI models (GPT-3.5, GPT-4, etc.).
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4",
        organization: Optional[str] = None
    ):
        """
        Initialize the OpenAI interface.
        
        Args:
            api_key (str, optional): OpenAI API key (defaults to OPENAI_API_KEY env var)
            model (str): Model to use (e.g., "gpt-4", "gpt-3.5-turbo")
            organization (str, optional): OpenAI organization ID
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
            
            # Set model
            self.model = model
            
            logger.info(f"Initialized OpenAI interface with model: {model}")
            
        except ImportError:
            logger.error("OpenAI package not installed. Install with: pip install openai")
            raise
    
    def generate_text(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        top_p: float = 1.0,
        stop_sequences: Optional[List[str]] = None,
        **kwargs
    ) -> str:
        """
        Generate text from a prompt using OpenAI.
        
        Args:
            prompt (str): The prompt to generate text from
            max_tokens (int): Maximum number of tokens to generate
            temperature (float): Sampling temperature (0.0 to 1.0)
            top_p (float): Nucleus sampling parameter (0.0 to 1.0)
            stop_sequences (List[str], optional): Sequences that stop generation
            **kwargs: Additional model-specific parameters
            
        Returns:
            str: The generated text
        """
        try:
            # For text completion, we use chat completion with a user message
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stop=stop_sequences,
                **kwargs
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating text with OpenAI: {e}")
            return ""
    
    def generate_chat_response(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 500,
        temperature: float = 0.7,
        top_p: float = 1.0,
        stop_sequences: Optional[List[str]] = None,
        **kwargs
    ) -> str:
        """
        Generate a response in a chat conversation using OpenAI.
        
        Args:
            messages (List[Dict[str, str]]): List of message dictionaries with 'role' and 'content'
            max_tokens (int): Maximum number of tokens to generate
            temperature (float): Sampling temperature (0.0 to 1.0)
            top_p (float): Nucleus sampling parameter (0.0 to 1.0)
            stop_sequences (List[str], optional): Sequences that stop generation
            **kwargs: Additional model-specific parameters
            
        Returns:
            str: The generated response
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stop=stop_sequences,
                **kwargs
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating chat response with OpenAI: {e}")
            return ""
    
    def generate_structured_output(
        self,
        prompt: str,
        output_schema: Dict[str, Any],
        temperature: float = 0.2,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate structured output (JSON) from a prompt using OpenAI.
        
        Args:
            prompt (str): The prompt to generate structured output from
            output_schema (Dict[str, Any]): JSON schema defining the expected output structure
            temperature (float): Sampling temperature (0.0 to 1.0)
            **kwargs: Additional model-specific parameters
            
        Returns:
            Dict[str, Any]: The generated structured output
        """
        try:
            # Create a system message with the schema
            schema_str = json.dumps(output_schema, indent=2)
            system_message = f"You are a structured data extraction assistant. Extract information from the user's input and respond with a JSON object that follows this schema:\n{schema_str}"
            
            # Generate response with JSON mode
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                response_format={"type": "json_object"},
                **kwargs
            )
            
            # Parse the JSON response
            content = response.choices[0].message.content.strip()
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"Error generating structured output with OpenAI: {e}")
            return {}
    
    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a text using OpenAI's tokenizer.
        
        Args:
            text (str): The text to count tokens for
            
        Returns:
            int: The number of tokens
        """
        try:
            import tiktoken
            
            # Get the encoding for the model
            encoding = tiktoken.encoding_for_model(self.model)
            
            # Count tokens
            tokens = encoding.encode(text)
            return len(tokens)
            
        except ImportError:
            logger.warning("tiktoken package not installed. Install with: pip install tiktoken")
            # Fallback to approximate token count (1 token ≈ 4 characters)
            return len(text) // 4
        except Exception as e:
            logger.error(f"Error counting tokens: {e}")
            # Fallback to approximate token count
            return len(text) // 4


class HuggingFaceInterface(LLMInterface):
    """
    Interface for Hugging Face models (Mistral, Llama, Phi, etc.).
    """
    
    def __init__(
        self,
        model_name: str = "mistral-7b-instruct",
        device: str = "auto",
        token: Optional[str] = None,
        **model_kwargs
    ):
        """
        Initialize the Hugging Face interface.
        
        Args:
            model_name (str): Name of the model to use
            device (str): Device to run the model on ("cpu", "cuda", "auto")
            token (str, optional): Hugging Face API token for gated models
            **model_kwargs: Additional model initialization parameters
        """
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
            
            self.model_name = model_name
            self.device = device
            
            # Set API token if provided
            if token:
                os.environ["HUGGINGFACE_TOKEN"] = token
            
            # Initialize tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            # Initialize pipeline
            self.pipe = pipeline(
                "text-generation",
                model=model_name,
                tokenizer=self.tokenizer,
                device_map=device,
                **model_kwargs
            )
            
            logger.info(f"Initialized Hugging Face interface with model: {model_name}")
            
        except ImportError:
            logger.error("Transformers package not installed. Install with: pip install transformers")
            raise
    
    def generate_text(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        top_p: float = 1.0,
        stop_sequences: Optional[List[str]] = None,
        **kwargs
    ) -> str:
        """
        Generate text from a prompt using Hugging Face.
        
        Args:
            prompt (str): The prompt to generate text from
            max_tokens (int): Maximum number of tokens to generate
            temperature (float): Sampling temperature (0.0 to 1.0)
            top_p (float): Nucleus sampling parameter (0.0 to 1.0)
            stop_sequences (List[str], optional): Sequences that stop generation
            **kwargs: Additional model-specific parameters
            
        Returns:
            str: The generated text
        """
        try:
            # Generate text
            response = self.pipe(
                prompt,
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=temperature > 0,
                **kwargs
            )
            
            # Extract generated text
            generated_text = response[0]["generated_text"]
            
            # Remove the prompt from the generated text
            if generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt):].strip()
            
            # Apply stop sequences if provided
            if stop_sequences:
                for stop_seq in stop_sequences:
                    if stop_seq in generated_text:
                        generated_text = generated_text[:generated_text.find(stop_seq)]
            
            return generated_text.strip()
            
        except Exception as e:
            logger.error(f"Error generating text with Hugging Face: {e}")
            return ""
    
    def generate_chat_response(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 500,
        temperature: float = 0.7,
        top_p: float = 1.0,
        stop_sequences: Optional[List[str]] = None,
        **kwargs
    ) -> str:
        """
        Generate a response in a chat conversation using Hugging Face.
        
        Args:
            messages (List[Dict[str, str]]): List of message dictionaries with 'role' and 'content'
            max_tokens (int): Maximum number of tokens to generate
            temperature (float): Sampling temperature (0.0 to 1.0)
            top_p (float): Nucleus sampling parameter (0.0 to 1.0)
            stop_sequences (List[str], optional): Sequences that stop generation
            **kwargs: Additional model-specific parameters
            
        Returns:
            str: The generated response
        """
        try:
            # Convert chat messages to a prompt format suitable for the model
            prompt = self._format_chat_messages(messages)
            
            # Generate response
            return self.generate_text(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stop_sequences=stop_sequences,
                **kwargs
            )
            
        except Exception as e:
            logger.error(f"Error generating chat response with Hugging Face: {e}")
            return ""
    
    def generate_structured_output(
        self,
        prompt: str,
        output_schema: Dict[str, Any],
        temperature: float = 0.2,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate structured output (JSON) from a prompt using Hugging Face.
        
        Args:
            prompt (str): The prompt to generate structured output from
            output_schema (Dict[str, Any]): JSON schema defining the expected output structure
            temperature (float): Sampling temperature (0.0 to 1.0)
            **kwargs: Additional model-specific parameters
            
        Returns:
            Dict[str, Any]: The generated structured output
        """
        try:
            # Create a prompt with the schema
            schema_str = json.dumps(output_schema, indent=2)
            structured_prompt = f"""
            Extract information from the following text and respond with a JSON object that follows this schema:
            {schema_str}
            
            Text: {prompt}
            
            JSON response:
            """
            
            # Generate response
            response = self.generate_text(
                structured_prompt,
                temperature=temperature,
                **kwargs
            )
            
            # Extract JSON from the response
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON object directly
                json_match = re.search(r'(\{.*\})', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = response
            
            # Parse the JSON
            return json.loads(json_str)
            
        except Exception as e:
            logger.error(f"Error generating structured output with Hugging Face: {e}")
            return {}
    
    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a text using the model's tokenizer.
        
        Args:
            text (str): The text to count tokens for
            
        Returns:
            int: The number of tokens
        """
        try:
            tokens = self.tokenizer.encode(text)
            return len(tokens)
            
        except Exception as e:
            logger.error(f"Error counting tokens: {e}")
            # Fallback to approximate token count
            return len(text) // 4
    
    def _format_chat_messages(self, messages: List[Dict[str, str]]) -> str:
        """
        Format chat messages into a prompt suitable for the model.
        
        Args:
            messages (List[Dict[str, str]]): List of message dictionaries with 'role' and 'content'
            
        Returns:
            str: Formatted prompt
        """
        # Different models have different chat formats
        # This is a generic format that works with many instruction-tuned models
        formatted_messages = []
        
        for message in messages:
            role = message.get("role", "user").lower()
            content = message.get("content", "")
            
            if role == "system":
                formatted_messages.append(f"<|system|>\n{content}")
            elif role == "user":
                formatted_messages.append(f"<|user|>\n{content}")
            elif role == "assistant":
                formatted_messages.append(f"<|assistant|>\n{content}")
            else:
                formatted_messages.append(f"<|{role}|>\n{content}")
        
        # Add final assistant prompt
        formatted_messages.append("<|assistant|>")
        
        return "\n".join(formatted_messages)


class OllamaInterface(LLMInterface):
    """
    Interface for Ollama models (local LLMs).
    """
    
    def __init__(
        self,
        model: str = "llama3",
        base_url: str = "http://localhost:11434",
        **model_kwargs
    ):
        """
        Initialize the Ollama interface.
        
        Args:
            model (str): Name of the model to use
            base_url (str): Base URL for the Ollama API
            **model_kwargs: Additional model parameters
        """
        self.model = model
        self.base_url = base_url
        self.model_kwargs = model_kwargs
        
        logger.info(f"Initialized Ollama interface with model: {model}")
    
    def generate_text(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        top_p: float = 1.0,
        stop_sequences: Optional[List[str]] = None,
        **kwargs
    ) -> str:
        """
        Generate text from a prompt using Ollama.
        
        Args:
            prompt (str): The prompt to generate text from
            max_tokens (int): Maximum number of tokens to generate
            temperature (float): Sampling temperature (0.0 to 1.0)
            top_p (float): Nucleus sampling parameter (0.0 to 1.0)
            stop_sequences (List[str], optional): Sequences that stop generation
            **kwargs: Additional model-specific parameters
            
        Returns:
            str: The generated text
        """
        try:
            import requests
            
            # Prepare request data
            data = {
                "model": self.model,
                "prompt": prompt,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": temperature,
                    "top_p": top_p,
                    "stop": stop_sequences or []
                },
                **self.model_kwargs,
                **kwargs
            }
            
            # Make API request
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=data
            )
            
            # Check for errors
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            
            return result.get("response", "").strip()
            
        except ImportError:
            logger.error("Requests package not installed. Install with: pip install requests")
            return ""
        except Exception as e:
            logger.error(f"Error generating text with Ollama: {e}")
            return ""
    
    def generate_chat_response(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 500,
        temperature: float = 0.7,
        top_p: float = 1.0,
        stop_sequences: Optional[List[str]] = None,
        **kwargs
    ) -> str:
        """
        Generate a response in a chat conversation using Ollama.
        
        Args:
            messages (List[Dict[str, str]]): List of message dictionaries with 'role' and 'content'
            max_tokens (int): Maximum number of tokens to generate
            temperature (float): Sampling temperature (0.0 to 1.0)
            top_p (float): Nucleus sampling parameter (0.0 to 1.0)
            stop_sequences (List[str], optional): Sequences that stop generation
            **kwargs: Additional model-specific parameters
            
        Returns:
            str: The generated response
        """
        try:
            import requests
            
            # Prepare request data
            data = {
                "model": self.model,
                "messages": messages,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": temperature,
                    "top_p": top_p,
                    "stop": stop_sequences or []
                },
                **self.model_kwargs,
                **kwargs
            }
            
            # Make API request
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=data
            )
            
            # Check for errors
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            
            return result.get("message", {}).get("content", "").strip()
            
        except ImportError:
            logger.error("Requests package not installed. Install with: pip install requests")
            return ""
        except Exception as e:
            logger.error(f"Error generating chat response with Ollama: {e}")
            return ""
    
    def generate_structured_output(
        self,
        prompt: str,
        output_schema: Dict[str, Any],
        temperature: float = 0.2,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate structured output (JSON) from a prompt using Ollama.
        
        Args:
            prompt (str): The prompt to generate structured output from
            output_schema (Dict[str, Any]): JSON schema defining the expected output structure
            temperature (float): Sampling temperature (0.0 to 1.0)
            **kwargs: Additional model-specific parameters
            
        Returns:
            Dict[str, Any]: The generated structured output
        """
        try:
            # Create a prompt with the schema
            schema_str = json.dumps(output_schema, indent=2)
            structured_prompt = f"""
            Extract information from the following text and respond with a JSON object that follows this schema:
            {schema_str}
            
            Text: {prompt}
            
            JSON response:
            """
            
            # Generate response
            response = self.generate_text(
                structured_prompt,
                temperature=temperature,
                **kwargs
            )
            
            # Extract JSON from the response
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON object directly
                json_match = re.search(r'(\{.*\})', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = response
            
            # Parse the JSON
            return json.loads(json_str)
            
        except Exception as e:
            logger.error(f"Error generating structured output with Ollama: {e}")
            return {}
    
    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a text.
        
        Args:
            text (str): The text to count tokens for
            
        Returns:
            int: The number of tokens
        """
        try:
            import requests
            
            # Make API request to tokenize
            response = requests.post(
                f"{self.base_url}/api/tokenize",
                json={
                    "model": self.model,
                    "prompt": text
                }
            )
            
            # Check for errors
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            
            return len(result.get("tokens", []))
            
        except ImportError:
            logger.error("Requests package not installed. Install with: pip install requests")
            # Fallback to approximate token count
            return len(text) // 4
        except Exception as e:
            logger.error(f"Error counting tokens: {e}")
            # Fallback to approximate token count
            return len(text) // 4


class LMStudioInterface(LLMInterface):
    """
    Interface for LM Studio models (local LLMs with OpenAI-compatible API).
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:1234/v1",
        model: str = "local-model",
        **model_kwargs
    ):
        """
        Initialize the LM Studio interface.
        
        Args:
            base_url (str): Base URL for the LM Studio API
            model (str): Name of the model to use
            **model_kwargs: Additional model parameters
        """
        try:
            import openai
            self.openai = openai
            
            # Initialize client with custom base URL
            self.client = openai.OpenAI(
                base_url=base_url,
                api_key="lm-studio"  # LM Studio doesn't require a real API key
            )
            
            self.model = model
            self.model_kwargs = model_kwargs
            
            logger.info(f"Initialized LM Studio interface with model: {model}")
            
        except ImportError:
            logger.error("OpenAI package not installed. Install with: pip install openai")
            raise
    
    def generate_text(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        top_p: float = 1.0,
        stop_sequences: Optional[List[str]] = None,
        **kwargs
    ) -> str:
        """
        Generate text from a prompt using LM Studio.
        
        Args:
            prompt (str): The prompt to generate text from
            max_tokens (int): Maximum number of tokens to generate
            temperature (float): Sampling temperature (0.0 to 1.0)
            top_p (float): Nucleus sampling parameter (0.0 to 1.0)
            stop_sequences (List[str], optional): Sequences that stop generation
            **kwargs: Additional model-specific parameters
            
        Returns:
            str: The generated text
        """
        try:
            # For text completion, we use chat completion with a user message
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stop=stop_sequences,
                **self.model_kwargs,
                **kwargs
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating text with LM Studio: {e}")
            return ""
    
    def generate_chat_response(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 500,
        temperature: float = 0.7,
        top_p: float = 1.0,
        stop_sequences: Optional[List[str]] = None,
        **kwargs
    ) -> str:
        """
        Generate a response in a chat conversation using LM Studio.
        
        Args:
            messages (List[Dict[str, str]]): List of message dictionaries with 'role' and 'content'
            max_tokens (int): Maximum number of tokens to generate
            temperature (float): Sampling temperature (0.0 to 1.0)
            top_p (float): Nucleus sampling parameter (0.0 to 1.0)
            stop_sequences (List[str], optional): Sequences that stop generation
            **kwargs: Additional model-specific parameters
            
        Returns:
            str: The generated response
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stop=stop_sequences,
                **self.model_kwargs,
                **kwargs
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating chat response with LM Studio: {e}")
            return ""
    
    def generate_structured_output(
        self,
        prompt: str,
        output_schema: Dict[str, Any],
        temperature: float = 0.2,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate structured output (JSON) from a prompt using LM Studio.
        
        Args:
            prompt (str): The prompt to generate structured output from
            output_schema (Dict[str, Any]): JSON schema defining the expected output structure
            temperature (float): Sampling temperature (0.0 to 1.0)
            **kwargs: Additional model-specific parameters
            
        Returns:
            Dict[str, Any]: The generated structured output
        """
        try:
            # Create a system message with the schema
            schema_str = json.dumps(output_schema, indent=2)
            system_message = f"You are a structured data extraction assistant. Extract information from the user's input and respond with a JSON object that follows this schema:\n{schema_str}\nRespond ONLY with the JSON object, no other text."
            
            # Generate response
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                **self.model_kwargs,
                **kwargs
            )
            
            # Extract JSON from the response
            content = response.choices[0].message.content.strip()
            
            # Try to parse the JSON
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON object directly
                json_match = re.search(r'(\{.*\})', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = content
            
            return json.loads(json_str)
            
        except Exception as e:
            logger.error(f"Error generating structured output with LM Studio: {e}")
            return {}
    
    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a text.
        
        Args:
            text (str): The text to count tokens for
            
        Returns:
            int: The number of tokens
        """
        # LM Studio doesn't provide a token counting API
        # Fallback to approximate token count (1 token ≈ 4 characters)
        return len(text) // 4


def get_llm_interface(provider: str, **kwargs) -> LLMInterface:
    """
    Factory function to get an LLM interface based on the provider.
    
    Args:
        provider (str): LLM provider ("openai", "huggingface", "ollama", "lmstudio")
        **kwargs: Additional parameters for the interface
        
    Returns:
        LLMInterface: The LLM interface
    """
    provider = provider.lower()
    
    if provider == "openai":
        return OpenAIInterface(**kwargs)
    elif provider in ["huggingface", "hf"]:
        return HuggingFaceInterface(**kwargs)
    elif provider == "ollama":
        return OllamaInterface(**kwargs)
    elif provider == "lmstudio":
        return LMStudioInterface(**kwargs)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")