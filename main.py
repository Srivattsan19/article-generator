"""
Main Application Module for Research Article Generator

This module serves as the main entry point for the Research Article Generator application.
It integrates various components including web scraping, content processing, and article
generation using a Streamlit interface.

The application follows these main steps:
1. Gather research content from web sources
2. Process and embed content using RAG system
3. Generate structured research article
4. Present results with interactive interface

Author: Your Name
Version: 1.0.0
"""

import streamlit as st
from openai import OpenAI
import time
from typing import Dict, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.scraper import WebScraper
from src.citation_manager import CitationManager
from src.rag_system import RAGSystem
from src.perplexity_client import PerplexityClient
from src.config import OPENAI_API_KEY, PPLX_API_KEY
from utils.logger import logger
import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"

def initialize_clients() -> Tuple[OpenAI, PerplexityClient]:
   """
   Initialize API clients for OpenAI and Perplexity.
   
   Returns:
       Tuple[OpenAI, PerplexityClient]: Initialized API clients
       
   Raises:
       ValueError: If API keys are missing or invalid
   """
   try:
       if not OPENAI_API_KEY or not PPLX_API_KEY:
           raise ValueError("Missing API keys")
           
       openai_client = OpenAI(api_key=OPENAI_API_KEY)
       perplexity_client = PerplexityClient()
       
       logger.info("Successfully initialized API clients")
       return openai_client, perplexity_client
   except Exception as e:
       logger.error(f"Failed to initialize clients: {e}")
       raise

def gather_research_content(
   topic: str,
   perplexity_client: PerplexityClient,
   scraper: WebScraper
) -> Dict:
   """
   Gather research content by scraping URLs provided by Perplexity.
   
   Args:
       topic (str): Research topic
       perplexity_client (PerplexityClient): Client for URL retrieval
       scraper (WebScraper): Web scraping utility
       
   Returns:
       Dict: Mapping of URLs to their content and citations
       
   Raises:
       ValueError: If no URLs are found for the topic
   """
   logger.info(f"Starting research gathering for topic: {topic}")
   urls = perplexity_client.extract_urls(topic)
   
   if not urls:
       logger.error("No URLs found for topic")
       raise ValueError("No URLs found for the topic")
   
   research_content = {}
   
   for url in urls:
       try:
           time.sleep(1)  # Rate limiting
           scraped_data = scraper.scrape_webpage(url)
           
           if scraped_data["success"]:
               citation_details = {
                   "title": scraped_data["title"],
                   "url": url
               }
               
               research_content[url] = {
                   "content": scraped_data["content"],
                   "citations": citation_details
               }
               logger.info(f"Successfully processed URL: {url}")
               
       except Exception as e:
           logger.error(f"Failed to process {url}: {str(e)}")
           continue
   
   logger.info(f"Gathered content from {len(research_content)} sources")
   return research_content

def setup_page():
   """Configure Streamlit page settings."""
   st.set_page_config(
       page_title="Research Article Generator",
       page_icon="📚",
       layout="wide",
       initial_sidebar_state="expanded"
   )
   
   st.title("📚 Research Article Generator")
   st.write("Generate research articles using web content and RAG technology")

def generate_article_sections(
   rag_system: RAGSystem,
   topic: str,
   progress_callback: Optional[callable] = None
) -> Dict[str, str]:
   """
   Generate all sections of the research article.
   
   Args:
       rag_system (RAGSystem): RAG system for content generation
       topic (str): Research topic
       progress_callback (Optional[callable]): Callback for progress updates
       
   Returns:
       Dict[str, str]: Mapping of section names to content
   """
   sections = ["Abstract", "Introduction", "Methods", "Results", "Discussion", "Conclusion"]
   article_sections = {}
   
   for i, section in enumerate(sections):
       article_sections[section] = rag_system.generate_section(section, topic)
       if progress_callback:
           progress = max(0.0, min(1.0, (66 + (34 * (i + 1) / len(sections))) / 100))  # Clamp values
           progress_callback(progress)
   
   return article_sections

def main():
   """Main application entry point."""
   setup_page()
   
   try:
       # Initialize components
       openai_client, perplexity_client = initialize_clients()
       citation_manager = CitationManager()
       rag_system = RAGSystem(openai_client, citation_manager)
       scraper = WebScraper()
       
       # Input section
       topic = st.text_input(
           "Enter research topic:",
           placeholder="e.g., Quantum Computing Applications"
       )
       
       if st.button("Generate Article") and topic:
           try:
               with st.spinner("Researching..."):
                   # Progress tracking
                   progress_bar = st.progress(0)
                   status_text = st.empty()
                   
                   # Research phase
                   status_text.text("Gathering URLs from Perplexity...")
                   research_content = gather_research_content(
                       topic,
                       perplexity_client,
                       scraper
                   )
                   progress_bar.progress(33)
                   
                   # Processing phase
                   status_text.text("Processing content...")
                   for url, data in research_content.items():
                       rag_system.add_content(
                           content=data["content"],
                           source=url,
                           citation_details=data["citations"]
                       )
                   progress_bar.progress(66)
                   
                   # Generation phase
                   status_text.text("Writing article...")
                   article_sections = generate_article_sections(
                       rag_system,
                       topic,
                       progress_bar.progress
                   )
                   progress_bar.progress(100)
                   status_text.empty()
               
               # Display results
               st.header(f"Research Article: {topic}")
               
               # Article sections
               for section, content in article_sections.items():
                   st.subheader(section)
                   st.markdown(content)
                   st.markdown("---")
               
               # References
               st.markdown(citation_manager.get_references())
               
               # Sources
               with st.expander("View Sources"):
                   st.markdown("### Research Sources")
                   for source in set(rag_system.sources):
                       st.markdown(f"- {source}")
               
               # Download options
               full_article = "\n\n".join([
                   f"# {topic}",
                   *[f"## {section}\n{content}"
                     for section, content in article_sections.items()],
                   citation_manager.get_references()
               ])
               
               st.download_button(
                   "Download Article",
                   full_article,
                   file_name=f"{topic.replace(' ', '_')}_article.md",
                   mime="text/markdown"
               )
               
           except Exception as e:
               st.error(f"An error occurred: {str(e)}")
               logger.error(f"Process failed with error: {str(e)}")
               
   except Exception as e:
       st.error("Application initialization failed. Please check your configuration.")
       logger.error(f"Application initialization failed: {str(e)}")

if __name__ == "__main__":
   main()