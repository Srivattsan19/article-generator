"""
RAG (Retrieval-Augmented Generation) System Module

This module implements a RAG system for generating research articles by combining
local embeddings using Sentence Transformers and text generation using OpenAI's GPT.
It handles content chunking, embedding generation, similarity search, and section generation.

References used from existing streamlit repositories and projects available online

Example:
   rag = RAGSystem(openai_client, citation_manager)
   rag.add_content("Research content", "Source1", {"title": "Paper1"})
   section = rag.generate_section("Introduction", "AI Ethics")
"""

from typing import List, Dict, Optional, Union, Tuple
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from .citation_manager import CitationManager
from utils.logger import logger
from src.config import CHUNK_SIZE, EMBEDDING_MODEL, GPT_MODEL

class RAGSystem:
   """
   Retrieval-Augmented Generation system for research article generation.
   
   Combines embedding-based retrieval using Sentence Transformers with
   GPT-based text generation to create coherent research article sections.

   Attributes:
       client (OpenAI): OpenAI client for text generation
       citation_manager (CitationManager): Manager for citations
       chunks (List[str]): Stored text chunks
       embeddings (List[List[float]]): Embeddings for chunks
       sources (List[str]): Source identifiers for chunks
       citations (List[int]): Citation IDs for chunks
       embedding_model (SentenceTransformer): Local embedding model
   """
   
   def __init__(self, openai_client: OpenAI, citation_manager: CitationManager):
       """
       Initialize RAG system with required clients and models.
       
       Args:
           openai_client (OpenAI): OpenAI API client
           citation_manager (CitationManager): Citation management system
       """
       self.client = openai_client
       self.citation_manager = citation_manager
       self.chunks: List[str] = []
       self.embeddings: List[List[float]] = []
       self.sources: List[str] = []
       self.citations: List[Optional[int]] = []
       
       # Initialize local embedding model
       try:
           self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
           logger.info("Successfully initialized Sentence Transformer model")
       except Exception as e:
           logger.error(f"Failed to initialize embedding model: {e}")
           raise

   def chunk_text(self, text: str, chunk_size: int = CHUNK_SIZE) -> List[str]:
       """
       Split text into chunks of approximately equal size.
       
       Args:
           text (str): Input text to chunk
           chunk_size (int): Target size for each chunk
           
       Returns:
           List[str]: List of text chunks
           
       Note:
           Chunks are created at word boundaries to preserve meaning
       """
       if not text or not text.strip():
           logger.warning("Empty text provided for chunking")
           return []
       
       words = text.split()
       chunks = []
       current_chunk = []
       current_size = 0
       
       for word in words:
           current_chunk.append(word)
           current_size += len(word) + 1
           
           if current_size >= chunk_size:
               chunks.append(" ".join(current_chunk))
               current_chunk = []
               current_size = 0
               
       if current_chunk:
           chunks.append(" ".join(current_chunk))
       
       logger.debug(f"Created {len(chunks)} chunks from text of length {len(text)}")
       return chunks

   def get_embedding(self, text: str) -> Optional[List[float]]:
       """
       Generate embeddings using Sentence Transformers model.
       
       Args:
           text (str): Text to embed
           
       Returns:
           Optional[List[float]]: Embedding vector or None if failed
       """
       try:
           embedding = self.embedding_model.encode(text).tolist()
           return embedding
       except Exception as e:
           logger.error(f"Embedding generation failed: {e}")
           return None

   def add_content(self, content: str, source: str, citation_details: Optional[Dict] = None):
       """
       Process and store new content with embeddings and citations.
       
       Args:
           content (str): Content to process and store
           source (str): Source identifier
           citation_details (Optional[Dict]): Citation information
       """
       if not content:
           logger.warning("Empty content provided")
           return
           
       chunks = self.chunk_text(content)
       if not chunks:
           logger.warning("No chunks created from content")
           return
       
       citation_id = None
       if citation_details and isinstance(citation_details, dict):
           try:
               citation_id = self.citation_manager.add_citation(**citation_details)
           except Exception as e:
               logger.error(f"Failed to add citation: {e}")
       
       # Process chunks in batches
       for chunk in chunks:
           embedding = self.get_embedding(chunk)
           if embedding:
               self.chunks.append(chunk)
               self.embeddings.append(embedding)
               self.sources.append(source)
               self.citations.append(citation_id)
       
       logger.info(f"Added {len(chunks)} chunks from source: {source}")

   def get_relevant_chunks(
       self,
       query: str,
       n_chunks: int = 5,
       similarity_threshold: float = 0.3
   ) -> List[Dict]:
       """
       Retrieve most relevant chunks based on similarity.
       
       Args:
           query (str): Search query
           n_chunks (int): Number of chunks to retrieve
           similarity_threshold (float): Minimum similarity score
           
       Returns:
           List[Dict]: Relevant chunks with metadata
       """
       query_embedding = self.get_embedding(query)
       if not query_embedding or not self.embeddings:
           logger.warning("No query embedding or stored embeddings available")
           return []
       
       # Calculate similarities
       similarities = cosine_similarity([query_embedding], self.embeddings)[0]
       
       # Filter by threshold and get top chunks
       relevant_indices = [i for i, sim in enumerate(similarities) 
                         if sim > similarity_threshold]
       top_indices = sorted(relevant_indices,
                          key=lambda i: similarities[i],
                          reverse=True)[:n_chunks]
       
       return [
           {
               "text": self.chunks[i],
               "source": self.sources[i],
               "citation": self.citations[i],
               "similarity": float(similarities[i])
           }
           for i in top_indices
       ]

   def generate_section(self, section: str, topic: str) -> str:
       """
       Generate an article section using retrieved content.
       
       Args:
           section (str): Section name to generate
           topic (str): Research topic
           
       Returns:
           str: Generated section content
           
       Note:
           Uses GPT to generate content based on retrieved chunks
       """
       try:
           # Get relevant content
           relevant_chunks = self.get_relevant_chunks(
               query=f"{section} {topic}",
               n_chunks=5
           )
           
           if not relevant_chunks:
               logger.warning("No relevant chunks found for section generation")
               return f"No content available for {section} section"
           
           # Prepare context with citations
           context_parts = []
           for chunk in relevant_chunks:
               text = chunk["text"]
               if chunk["citation"]:
                   text += f" [{chunk['citation']}]"
               context_parts.append(text)
               
           context = "\n\n".join(context_parts)
           
           # Generate section
           prompt = self._create_section_prompt(section, topic, context)
           
           response = self.client.chat.completions.create(
               model=GPT_MODEL,
               messages=[
                   {"role": "system", "content": "You are an expert academic writer."},
                   {"role": "user", "content": prompt}
               ],
               temperature=0.7
           )
           
           generated_content = response.choices[0].message.content
           logger.info(f"Successfully generated {section} section")
           return generated_content
           
       except Exception as e:
           logger.error(f"Section generation failed: {e}")
           return f"Error generating {section} section"

   def _create_section_prompt(self, section: str, topic: str, context: str) -> str:
       """Create a detailed prompt for section generation."""
       return f"""Using the following research context, generate the {section} section 
       of a research article about {topic}.

       Research Context:
       {context}

       Requirements:
       - Follow academic writing standards
       - Use the provided citations [n] where appropriate
       - Use formal language
       - Be precise and objective
       - Connect ideas logically
       - Maintain consistent citation format

       Generate the {section} section:"""