"""
Configuration variables and constants for the web scraping application.
"""

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
]

PRICING = {
    "gpt-4o-mini": {
        "input": 0.150 / 1_000_000,
        "output": 0.600 / 1_000_000,
    },
    "gpt-4o-2024-08-06": {
        "input": 2.5 / 1_000_000,
        "output": 10 / 1_000_000,
    },
    "gemini-1.5-flash": {
        "input": 0.075 / 1_000_000,
        "output": 0.30 / 1_000_000,
    },
    "Llama3.1 8B": {
        "input": 0,
        "output": 0,
    },
    "Groq Llama3.1 70b": {
        "input": 0,
        "output": 0,
    }
}

HEADLESS_OPTIONS = [
    "--disable-gpu",
    "--disable-dev-shm-usage",
    "--window-size=1920,1080",
    "--disable-search-engine-choice-screen",
    "--disable-blink-features=AutomationControlled"
]

HEADLESS_OPTIONS_DOCKER = [
    "--headless=new",
    "--no-sandbox",
    "--disable-gpu",
    "--disable-dev-shm-usage",
    "--disable-software-rasterizer",
    "--disable-setuid-sandbox",
    "--remote-debugging-port=9222",
    "--disable-search-engine-choice-screen"
]

LLAMA_MODEL_FULLNAME = "lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF"
GROQ_LLAMA_MODEL_FULLNAME = "llama-3.1-70b-versatile"

SYSTEM_MESSAGE = """You are an intelligent text extraction and conversion assistant. Extract structured information 
from the given text and convert it into pure JSON format. Include only structured data, no additional commentary."""

USER_MESSAGE = "Extract the following information from the provided text:\nPage content:\n\n"

PROMPT_PAGINATION = """
Extract pagination elements from markdown content. Your goal is to find:
1. Next/More/See more button URLs
2. Numbered page URL patterns
Provide output as JSON: {"page_urls": ["url1", "url2", "url3"]}
"""