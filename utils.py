import os
import random
import json
from datetime import datetime
from urllib.parse import urlparse
import re
from typing import Dict, Any

def generate_unique_folder_name(url: str) -> str:
    """Generate a unique folder name based on URL and timestamp."""
    timestamp = datetime.now().strftime('%Y_%m_%d__%H_%M_%S')
    parsed_url = urlparse(url)
    domain = parsed_url.netloc or parsed_url.path.split('/')[0]
    domain = re.sub(r'^www\.', '', domain)
    clean_domain = re.sub(r'\W+', '_', domain)
    return f"{clean_domain}_{timestamp}"

def is_running_in_docker() -> bool:
    """Check if the application is running in a Docker container."""
    try:
        with open("/proc/1/cgroup", "rt") as file:
            return "docker" in file.read()
    except Exception:
        return False

def calculate_price(token_counts: Dict[str, int], model: str) -> tuple[int, int, float]:
    """Calculate price based on token usage and model."""
    from assets import PRICING
    
    input_token_count = token_counts.get("input_tokens", 0)
    output_token_count = token_counts.get("output_tokens", 0)
    
    input_cost = input_token_count * PRICING[model]["input"]
    output_cost = output_token_count * PRICING[model]["output"]
    total_cost = input_cost + output_cost
    
    return input_token_count, output_token_count, total_cost

def save_data(data: Any, output_folder: str, filename: str, format: str = 'json') -> str:
    """Save data to file in specified format."""
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, filename)
    
    if format == 'json':
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    else:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(str(data))
            
    return output_path