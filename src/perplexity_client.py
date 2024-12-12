"""
Perplexity API Client Module

This module provides functionality to interact with the Perplexity AI API for retrieving
relevant research URLs. It handles API communication, URL extraction, and error handling
for research-related queries.

References used from existing streamlit repositories and projects available online

Classes:
   PerplexityClient: Handles communication with Perplexity AI API
"""

from typing import List, Dict, Optional
import requests
from utils.logger import logger
from src.config import PPLX_API_KEY, PPLX_MODEL, MAX_RETRIES, RETRY_DELAY
import time

class PerplexityClient:
   """
   Client for interacting with Perplexity AI API.
   
   This class handles authentication and communication with the Perplexity API,
   specifically for retrieving research-related URLs.

   Attributes:
       headers (Dict[str, str]): HTTP headers for API requests including authentication
   """

   def __init__(self):
       """Initialize the Perplexity client with necessary headers."""
       self.headers = {
           "Authorization": f"Bearer {PPLX_API_KEY}",
           "Content-Type": "application/json"
       }

   def _create_research_prompt(self, topic: str) -> str:
       """
       Create a detailed research prompt for the given topic.
       
       Args:
           topic (str): The research topic to create a prompt for
           
       Returns:
           str: Formatted prompt for the Perplexity API
       """
       return f"""Find the most relevant and reliable online resources about {topic}.
       
       Focus on:
       1. Academic papers (especially ones with PDF links)
       2. Research articles
       3. Technical documentation
       4. Educational resources
       
       For each source, provide:
       RESOURCE:
       **URL:** [direct link]
       Type: [paper/article/documentation/etc]
       Relevance: [brief explanation]
       
       Requirements:
       - Return at least 5 high-quality sources
       - Prioritize peer-reviewed content
       - Include recent publications
       - Ensure URLs are accessible
       """

   def _make_api_request(self, topic: str) -> Optional[Dict]:
       """
       Make the API request to Perplexity with retry logic.
       
       Args:
           topic (str): Research topic
           
       Returns:
           Optional[Dict]: API response if successful, None otherwise
       """
       for attempt in range(MAX_RETRIES):
           try:
               response = requests.post(
                   "https://api.perplexity.ai/chat/completions",
                   headers=self.headers,
                   json={
                       "model": PPLX_MODEL,
                       "messages": [
                           {
                               "role": "system",
                               "content": "You are a research assistant focused on finding reliable academic sources."
                           },
                           {
                               "role": "user",
                               "content": self._create_research_prompt(topic)
                           }
                       ]
                   },
                   timeout=30  # 30 second timeout
               )
               response.raise_for_status()
               return response.json()
               
           except requests.exceptions.RequestException as e:
               logger.error(f"API request attempt {attempt + 1} failed: {str(e)}")
               if attempt < MAX_RETRIES - 1:
                   time.sleep(RETRY_DELAY)
               continue
               
       return None

   def extract_urls(self, topic: str) -> List[str]:
       """
       Extract relevant URLs from Perplexity API response.
       
       This method queries the Perplexity API for relevant research sources
       and extracts valid URLs from the response.
       
       Args:
           topic (str): Research topic to find sources for
           
       Returns:
           List[str]: List of extracted URLs. Empty list if no URLs found or on error.
       """
       try:
           response_data = self._make_api_request(topic)
           if not response_data:
               return []

           content = response_data['choices'][0]['message']['content']
           logger.info(f"Perplexity response received for topic: {topic}")
           
           # Extract URLs from response
           urls = []
           for line in content.split('\n'):
               if "**URL:**" in line:
                   url_part = line.split('**URL:**')[1].strip()
                   url = url_part.strip('* ').strip()
                   if url.startswith('http'):
                       urls.append(url)
           
           # Log results
           logger.info(f"Found {len(urls)} URLs for topic: {topic}")
           logger.debug(f"Extracted URLs: {urls}")
           
           return urls
           
       except Exception as e:
           logger.error(f"URL extraction failed for topic '{topic}': {str(e)}")
           return []