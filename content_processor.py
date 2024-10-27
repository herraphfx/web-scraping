from bs4 import BeautifulSoup
import html2text
import tiktoken
from typing import Dict, Any, Type
from pydantic import BaseModel, create_model
from typing import List

def clean_html(html_content: str) -> str:
    """Clean HTML content by removing unnecessary elements."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove common non-content elements
    for element in soup.find_all(['header', 'footer', 'nav', 'script', 'style']):
        element.decompose()
    
    return str(soup)

def html_to_markdown(html_content: str) -> str:
    """Convert HTML to markdown format."""
    cleaned_html = clean_html(html_content)
    
    converter = html2text.HTML2Text()
    converter.ignore_links = False
    converter.ignore_images = False
    converter.ignore_tables = False
    
    return converter.handle(cleaned_html)

def trim_tokens(text: str, model: str, max_tokens: int = 120000) -> str:
    """Trim text to stay within token limit."""
    try:
        encoder = tiktoken.encoding_for_model(model)
        tokens = encoder.encode(text)
        
        if len(tokens) > max_tokens:
            return encoder.decode(tokens[:max_tokens])
        return text
    except Exception:
        # Fallback to approximate token counting if model not found
        words = text.split()
        avg_tokens_per_word = 1.3
        if len(words) * avg_tokens_per_word > max_tokens:
            return ' '.join(words[:int(max_tokens/avg_tokens_per_word)])
        return text

def create_dynamic_model(field_names: List[str]) -> tuple[Type[BaseModel], Type[BaseModel]]:
    """Create dynamic Pydantic models for data extraction."""
    # Create field definitions
    field_definitions = {field: (str, ...) for field in field_names}
    
    # Create individual listing model
    ListingModel = create_model('DynamicListingModel', **field_definitions)
    
    # Create container model for multiple listings
    ContainerModel = create_model('DynamicListingsContainer', 
                                listings=(List[ListingModel], ...))
    
    return ListingModel, ContainerModel