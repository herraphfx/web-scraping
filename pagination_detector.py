from typing import Dict, List, Tuple
from pydantic import BaseModel, Field
import json

from model_handler import ModelHandler
from assets import PROMPT_PAGINATION

class PaginationData(BaseModel):
    page_urls: List[str] = Field(default_factory=list)

def detect_pagination(url: str, content: str, model_name: str, indications: str = "") -> Tuple[PaginationData, Dict[str, int], float]:
    """Detect pagination elements in the content."""
    try:
        # Prepare prompt
        prompt = PROMPT_PAGINATION + f"\nURL: {url}\n"
        if indications:
            prompt += f"\nPagination instructions: {indications}\n"
        prompt += f"\nContent:\n{content}"
        
        # Initialize model handler
        model_handler = ModelHandler(model_name)
        
        # Process content
        result, token_counts = model_handler.process_content(
            content=prompt,
            response_format=PaginationData
        )
        
        # Parse result into PaginationData
        if isinstance(result, dict):
            pagination_data = PaginationData(**result)
        else:
            pagination_data = result
            
        # Calculate price
        from utils import calculate_price
        _, _, price = calculate_price(token_counts, model_name)
        
        return pagination_data, token_counts, price
        
    except Exception as e:
        print(f"Error detecting pagination: {e}")
        return PaginationData(), {"input_tokens": 0, "output_tokens": 0}, 0.0