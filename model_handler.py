from typing import Dict, Any, Tuple, Union
import json
import tiktoken
from openai import OpenAI
import google.generativeai as genai
from groq import Groq

from assets import (
    SYSTEM_MESSAGE, USER_MESSAGE, LLAMA_MODEL_FULLNAME, 
    GROQ_LLAMA_MODEL_FULLNAME
)
from api_management import get_api_key

class ModelHandler:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self._setup_client()

    def _setup_client(self):
        """Set up the appropriate client based on model name."""
        if self.model_name.startswith("gpt"):
            self.client = OpenAI(api_key=get_api_key('OPENAI_API_KEY'))
        elif self.model_name.startswith("gemini"):
            genai.configure(api_key=get_api_key('GOOGLE_API_KEY'))
        elif self.model_name.startswith("Groq"):
            self.client = Groq(api_key=get_api_key('GROQ_API_KEY'))
        elif self.model_name.startswith("Llama"):
            self.client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

    def process_content(self, content: str, response_format: Any = None) -> Tuple[Union[Dict, Any], Dict[str, int]]:
        """Process content using the selected model."""
        if self.model_name.startswith("gpt"):
            return self._process_with_openai(content, response_format)
        elif self.model_name.startswith("gemini"):
            return self._process_with_gemini(content, response_format)
        elif self.model_name.startswith("Groq"):
            return self._process_with_groq(content, response_format)
        elif self.model_name.startswith("Llama"):
            return self._process_with_llama(content, response_format)
        else:
            raise ValueError(f"Unsupported model: {self.model_name}")

    def _process_with_openai(self, content: str, response_format: Any) -> Tuple[Dict, Dict[str, int]]:
        """Process content using OpenAI models."""
        completion = self.client.beta.chat.completions.parse(
            model=self.model_name,
            messages=[
                {"role": "system", "content": SYSTEM_MESSAGE},
                {"role": "user", "content": USER_MESSAGE + content}
            ],
            response_format=response_format
        )
        
        # Calculate token usage
        encoder = tiktoken.encoding_for_model(self.model_name)
        token_counts = {
            "input_tokens": len(encoder.encode(USER_MESSAGE + content)),
            "output_tokens": len(encoder.encode(str(completion.choices[0].message.parsed)))
        }
        
        return completion.choices[0].message.parsed, token_counts

    def _process_with_gemini(self, content: str, response_format: Any) -> Tuple[Dict, Dict[str, int]]:
        """Process content using Google's Gemini model."""
        model = genai.GenerativeModel(
            'gemini-1.5-flash',
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": response_format
            }
        )
        
        prompt = SYSTEM_MESSAGE + "\n" + USER_MESSAGE + content
        completion = model.generate_content(prompt)
        
        token_counts = {
            "input_tokens": completion.usage_metadata.prompt_token_count,
            "output_tokens": completion.usage_metadata.candidates_token_count
        }
        
        return json.loads(completion.text), token_counts

    def _process_with_groq(self, content: str, response_format: Any) -> Tuple[Dict, Dict[str, int]]:
        """Process content using Groq's model."""
        completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_MESSAGE},
                {"role": "user", "content": USER_MESSAGE + content}
            ],
            model=GROQ_LLAMA_MODEL_FULLNAME
        )
        
        token_counts = {
            "input_tokens": completion.usage.prompt_tokens,
            "output_tokens": completion.usage.completion_tokens
        }
        
        return json.loads(completion.choices[0].message.content), token_counts

    def _process_with_llama(self, content: str, response_format: Any) -> Tuple[Dict, Dict[str, int]]:
        """Process content using local Llama model."""
        completion = self.client.chat.completions.create(
            model=LLAMA_MODEL_FULLNAME,
            messages=[
                {"role": "system", "content": SYSTEM_MESSAGE},
                {"role": "user", "content": USER_MESSAGE + content}
            ],
            temperature=0.7
        )
        
        token_counts = {
            "input_tokens": completion.usage.prompt_tokens,
            "output_tokens": completion.usage.completion_tokens
        }
        
        return json.loads(completion.choices[0].message.content), token_counts