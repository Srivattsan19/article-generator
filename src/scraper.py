"""
Web Scraping Module

This module provides web scraping functionality for extracting content from web pages.
It handles various webpage structures, content extraction, and error recovery.

References used from existing streamlit repositories and projects available online

Classes:
   WebScraper: Manages web scraping operations with retry logic and content cleaning
"""

from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup
from utils.logger import logger
from src.config import MAX_RETRIES, RETRY_DELAY
import time

class WebScraper:
   """
   Web scraping class with robust error handling and content extraction.
   
   This class provides methods to scrape and clean content from web pages,
   handling various page structures and potential errors.

   Attributes:
       headers (Dict[str, str]): HTTP headers for making requests
       content_selectors (List[str]): CSS selectors for finding main content
       unwanted_elements (List[str]): HTML elements to remove
   """

   def __init__(self):
       """Initialize the WebScraper with default configurations."""
       # Headers to mimic a regular browser request
       self.headers = {
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                        '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Language': 'en-US,en;q=0.5',
           'DNT': '1',  # Do Not Track request header
       }
       
       # Common selectors for finding main content
       self.content_selectors = [
           'article',
           'main',
           '.content',
           '#content',
           '.post',
           '.article-content',
           '.entry-content'
       ]
       
       # Elements to remove from content
       self.unwanted_elements = [
           'script',
           'style',
           'nav',
           'header',
           'footer',
           'aside',
           'advertisement',
           '.ads',
           '#comments'
       ]

   def _clean_text(self, text: str) -> str:
       """
       Clean and normalize extracted text.
       
       Args:
           text (str): Raw text to clean
           
       Returns:
           str: Cleaned and normalized text
       """
       # Remove extra whitespace and normalize spacing
       cleaned = ' '.join(text.split())
       return cleaned.strip()

   def _extract_content(self, soup: BeautifulSoup) -> str:
       """
       Extract main content from parsed HTML.
       
       Args:
           soup (BeautifulSoup): Parsed HTML content
           
       Returns:
           str: Extracted main content
       """
       # Try content selectors first
       for selector in self.content_selectors:
           content = soup.select_one(selector)
           if content and len(content.get_text().strip()) > 100:  # Minimum content length
               return content.get_text()
       
       # Fallback to paragraph collection
       paragraphs = soup.find_all('p')
       if paragraphs:
           return ' '.join(p.get_text() for p in paragraphs)
           
       return ""

   def scrape_webpage(self, url: str) -> Dict:
       """
       Scrape content from a webpage with retry logic.
       
       Attempts to extract the main content and title from a webpage,
       with automatic retries on failure and content cleaning.
       
       Args:
           url (str): URL to scrape
           
       Returns:
           Dict: Contains keys:
               - success (bool): Whether scraping was successful
               - title (str): Page title if found
               - content (str): Main content if found
               - url (str): Original URL
               - error (str, optional): Error message if failed
       """
       logger.info(f"Starting scrape of URL: {url}")
       
       for attempt in range(MAX_RETRIES):
           try:
               # Make request with timeout
               response = requests.get(
                   url,
                   headers=self.headers,
                   timeout=10,
                   verify=True  # Verify SSL certificates
               )
               response.raise_for_status()  # Raise exception for bad status codes
               
               # Parse HTML
               soup = BeautifulSoup(response.text, 'lxml')
               
               # Remove unwanted elements
               for element in self.unwanted_elements:
                   for tag in soup.select(element):
                       tag.decompose()
               
               # Extract title
               title = soup.title.string if soup.title else ""
               title = self._clean_text(title)
               
               # Extract main content
               main_content = self._extract_content(soup)
               main_content = self._clean_text(main_content)
               
               if not main_content:
                   raise ValueError("No content found")
               
               logger.info(f"Successfully scraped URL: {url}")
               return {
                   "success": True,
                   "title": title,
                   "content": main_content,
                   "url": url
               }
               
           except Exception as e:
               logger.error(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
               if attempt < MAX_RETRIES - 1:
                   time.sleep(RETRY_DELAY)
                   continue
               
               return {
                   "success": False,
                   "error": str(e),
                   "url": url
               }