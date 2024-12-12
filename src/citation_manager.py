"""
Citation Manager Module

This module manages citations and references for research articles, providing functionality
to add citations and generate formatted reference sections. It supports various citation
formats and handles different types of source materials.

Example:
   manager = CitationManager()
   citation_id = manager.add_citation(
       title="Example Paper",
       authors="Smith, J.",
       year="2023",
       url="https://example.com"
   )
   references = manager.get_references()
"""

from typing import Dict, Optional, List
from datetime import datetime
from utils.logger import logger

class CitationManager:
   """
   Manages citations and generates formatted references for research articles.
   
   This class handles the storage, formatting, and organization of citations,
   providing methods to add new citations and generate a properly formatted
   references section.

   Attributes:
       citations (Dict[int, Dict]): Storage for citation data
       citation_counter (int): Counter for generating unique citation IDs
   """
   
   def __init__(self):
       """Initialize the citation manager with empty citations dictionary."""
       self.citations: Dict[int, Dict] = {}
       self.citation_counter: int = 1

   def add_citation(
       self,
       title: Optional[str] = None,
       url: Optional[str] = None,
       authors: Optional[str] = None,
       year: Optional[str] = None,
       journal: Optional[str] = None,
       **kwargs
   ) -> int:
       """
       Add a new citation and return its reference number.
       
       Processes citation details, validates them, and stores them with a unique
       identifier. Handles missing fields gracefully and supports additional
       metadata through kwargs.
       
       Args:
           title (Optional[str]): Title of the source
           url (Optional[str]): URL of the source
           authors (Optional[str]): Authors of the source
           year (Optional[str]): Publication year
           journal (Optional[str]): Journal or publication name
           **kwargs: Additional citation details for future extensibility
           
       Returns:
           int: Unique citation ID for referencing
           
       Raises:
           ValueError: If all main citation fields are None
       """
       # Validate and clean citation data
       citation_data = {
           "title": str(title).strip() if title else None,
           "url": str(url).strip() if url else None,
           "authors": str(authors).strip() if authors else None,
           "year": str(year).strip() if year else str(datetime.now().year),
           "journal": str(journal).strip() if journal else None
       }
       
       # Check if citation has at least some valid data
       if not any(citation_data.values()):
           logger.warning("Attempting to add empty citation")
           raise ValueError("Citation must contain at least one valid field")
       
       # Store citation and increment counter
       citation_id = self.citation_counter
       self.citations[citation_id] = citation_data
       self.citation_counter += 1
       
       logger.info(f"Added citation {citation_id}: {citation_data['title']}")
       return citation_id

   def get_references(self) -> str:
       """
       Generate a formatted references section in markdown.
       
       Creates a properly formatted references section with all stored citations,
       organized by citation ID. Handles missing fields gracefully and creates
       consistent formatting.
       
       Returns:
           str: Markdown formatted references section
           
       Example:
           [1] Smith, J. (2023). *Example Paper*. [Available online](https://example.com)
       """
       if not self.citations:
           logger.info("No citations to format")
           return ""
           
       references = "## References\n\n"
       
       # Sort citations by ID for consistent ordering
       for citation_id, details in sorted(self.citations.items()):
           reference_parts = []
           
           # Build reference components
           if details["authors"]:
               reference_parts.append(f"{details['authors']}")
           if details["year"]:
               reference_parts.append(f"({details['year']})")
           if details["title"]:
               reference_parts.append(f"*{details['title']}*")
           if details["journal"]:
               reference_parts.append(f"{details['journal']}")
           if details["url"]:
               reference_parts.append(f"[Available online]({details['url']})")
           
           # Format reference line
           if reference_parts:
               reference_line = f"[{citation_id}] " + ". ".join(reference_parts) + "\n\n"
               references += reference_line
           
       logger.info(f"Generated references section with {len(self.citations)} citations")
       return references

   def get_citation_by_id(self, citation_id: int) -> Optional[Dict]:
       """
       Retrieve citation data by ID.
       
       Args:
           citation_id (int): The ID of the citation to retrieve
           
       Returns:
           Optional[Dict]: Citation data if found, None otherwise
       """
       return self.citations.get(citation_id)