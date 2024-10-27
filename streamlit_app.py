import streamlit as st
from streamlit_tags import st_tags_sidebar
import pandas as pd
from typing import List, Dict, Any

from scrapper import WebScraper
from utils import generate_unique_folder_name
from assets import PRICING

def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'scraping_state' not in st.session_state:
        st.session_state['scraping_state'] = 'idle'
    if 'results' not in st.session_state:
        st.session_state['results'] = None
    if 'scraper' not in st.session_state:
        st.session_state['scraper'] = None

def setup_sidebar() -> tuple[str, str, List[str], bool, str, bool]:
    """Setup sidebar components and return user inputs."""
    st.sidebar.title("Settings")

    # API Keys
    with st.sidebar.expander("Paid API Keys", expanded=False):
        st.session_state['openai_api_key'] = st.text_input("OpenAI API Key", type="password")
        st.session_state['gemini_api_key'] = st.text_input("Gemini API Key", type="password")
        st.session_state['groq_api_key'] = st.text_input("Groq API Key", type="password")

    # Model selection
    model_selection = st.sidebar.selectbox("Select Model", options=list(PRICING.keys()))

    # URL input
    url_input = st.sidebar.text_input("Enter URL(s) separated by whitespace")
    urls = url_input.strip().split()
    num_urls = len(urls)

    # Fields to extract
    show_tags = st.sidebar.toggle("Enable Scraping")
    fields = []
    if show_tags:
        fields = st_tags_sidebar(
            label='Enter Fields to Extract:',
            text='Press enter to add a field',
            value=[],
            suggestions=[],
            maxtags=-1,
            key='fields_input'
        )

    # Pagination and attended mode options
    use_pagination = False
    pagination_details = ""
    attended_mode = False
    
    if num_urls <= 1:
        use_pagination = st.sidebar.toggle("Enable Pagination")
        if use_pagination:
            pagination_details = st.sidebar.text_input(
                "Enter Pagination Details (optional)",
                help="Describe how to navigate through pages"
            )
        attended_mode = st.sidebar.toggle("Enable Attended Mode")
    else:
        st.sidebar.info("Pagination and Attended Mode are disabled for multiple URLs.")

    return url_input, model_selection, fields, use_pagination, pagination_details, attended_mode

def display_results(results: Dict[str, Any]):
    """Display scraping results and statistics."""
    if not results:
        return

    all_data = results['data']
    total_input_tokens = results['input_tokens']
    total_output_tokens = results['output_tokens']
    total_cost = results['total_cost']
    pagination_info = results.get('pagination_info')

    # Display scraped data
    st.subheader("Scraped Data")
    for i, data in enumerate(all_data, 1):
        st.write(f"Data from URL {i}:")
        if isinstance(data, dict) and 'listings' in data:
            df = pd.DataFrame(data['listings'])
            st.dataframe(df, use_container_width=True)

    # Display statistics in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Scraping Statistics")
    st.sidebar.markdown(f"Input Tokens: {total_input_tokens:,}")
    st.sidebar.markdown(f"Output Tokens: {total_output_tokens:,}")
    st.sidebar.markdown(f"Total Cost: ${total_cost:.4f}")

    # Display pagination information
    if pagination_info:
        st.markdown("---")
        st.subheader("Pagination Results")
        urls_df = pd.DataFrame(pagination_info["pagination_data"].page_urls, columns=["URLs"])
        st.dataframe(urls_df, use_container_width=True)
        
        st.sidebar.markdown("### Pagination Statistics")
        st.sidebar.markdown(f"Pages Found: {len(pagination_info['pagination_data'].page_urls)}")
        st.sidebar.markdown(f"Pagination Cost: ${pagination_info['price']:.4f}")

def main():
    """Main application function."""
    st.set_page_config(page_title="Henry Web Scraper", page_icon="🕵️‍♂️")
    st.title("Henry's Web Scraper 🕵️‍♂️🕵️‍♂️🕵️‍♂️ ")

    initialize_session_state()
    
    # Setup sidebar and get user inputs
    url_input, model_selection, fields, use_pagination, pagination_details, attended_mode = setup_sidebar()

    # Main action button
    if st.sidebar.button("Start Scraping", type="primary"):
        if not url_input.strip():
            st.error("Please enter at least one URL.")
            return
        if not fields:
            st.error("Please enter at least one field to extract.")
            return

        urls = url_input.strip().split()
        output_folder = generate_unique_folder_name(urls[0])

        with st.spinner("Scraping in progress..."):
            scraper = WebScraper(
                model_name=model_selection,
                fields=fields,
                output_folder=output_folder,
                use_pagination=use_pagination,
                pagination_details=pagination_details,
                attended_mode=attended_mode
            )

            results = {
                'data': [],
                'input_tokens': 0,
                'output_tokens': 0,
                'total_cost': 0,
                'pagination_info': None
            }

            for i, url in enumerate(urls, 1):
                data, token_counts = scraper.scrape_url(url, i)
                results['data'].append(data)
                results['input_tokens'] += token_counts['input_tokens']
                results['output_tokens'] += token_counts['output_tokens']
                
                if use_pagination and i == 1:
                    results['pagination_info'] = scraper.detect_pagination(url, data)

            scraper.cleanup()
            st.session_state['results'] = results
            st.session_state['scraping_state'] = 'completed'

    # Display results if available
    if st.session_state['scraping_state'] == 'completed':
        display_results(st.session_state['results'])

if __name__ == "__main__":
    main()