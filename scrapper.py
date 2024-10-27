from typing import List, Dict, Any, Optional, Tuple
import os

from web_driver import fetch_page_content, setup_selenium
from content_processor import (
    html_to_markdown,
    create_dynamic_model,
    trim_tokens
)
from model_handler import ModelHandler
from pagination_detector import detect_pagination
from utils import (
    generate_unique_folder_name,
    save_data,
    calculate_price
)

class WebScraper:
    def __init__(
        self,
        model_name: str,
        fields: List[str],
        output_folder: str,
        use_pagination: bool = False,
        pagination_details: str = "",
        attended_mode: bool = False
    ):
        self.model_name = model_name
        self.fields = fields
        self.output_folder = output_folder
        self.use_pagination = use_pagination
        self.pagination_details = pagination_details
        self.attended_mode = attended_mode
        self.model_handler = ModelHandler(model_name)
        self.driver = None if not attended_mode else setup_selenium(True)

    def scrape_url(self, url: str, file_number: int = 1) -> Tuple[Dict[str, Any], Dict[str, int]]:
        """Scrape data from a single URL."""
        try:
            # Fetch and process content
            html_content = fetch_page_content(url, self.driver, self.attended_mode)
            markdown_content = html_to_markdown(html_content)
            
            # Save raw content
            save_data(markdown_content, self.output_folder, f'raw_data_{file_number}.md', 'text')
            
            # Create dynamic models
            ListingModel, ContainerModel = create_dynamic_model(self.fields)
            
            # Process content with AI model
            formatted_data, token_counts = self.model_handler.process_content(
                content=markdown_content,
                response_format=ContainerModel
            )
            
            # Save formatted data
            save_data(formatted_data, self.output_folder, f'formatted_data_{file_number}.json')
            
            return formatted_data, token_counts
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return {}, {"input_tokens": 0, "output_tokens": 0}

    def detect_pagination(self, url: str, content: str) -> Optional[Dict[str, Any]]:
        """Detect pagination if enabled."""
        if not self.use_pagination:
            return None
            
        pagination_data, token_counts, price = detect_pagination(
            url,
            content,
            self.model_name,
            self.pagination_details
        )
        
        return {
            "pagination_data": pagination_data,
            "token_counts": token_counts,
            "price": price
        }

    def cleanup(self):
        """Clean up resources."""
        if self.driver:
            self.driver.quit()
            self.driver = None