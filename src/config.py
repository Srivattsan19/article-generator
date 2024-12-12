"""
Configuration Module for Research Article Generator

This module contains all configuration settings and constants used throughout the application.
It handles environment variable loading, API key management, and defines various operational
parameters for the application's functionality.

Environment Variables Required:
   - OPENAI_API_KEY: API key for OpenAI services
   - PPLX_API_KEY: API key for Perplexity AI services

Note:
   Make sure to create a .env file in the root directory with the required API keys
   before running the application.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys for external services
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PPLX_API_KEY = os.getenv('PPLX_API_KEY')

# Application Constants
CHUNK_SIZE = 500  # Number of characters per text chunk for processing
MAX_RETRIES = 3   # Maximum number of retry attempts for API calls
RETRY_DELAY = 1   # Delay between retry attempts in seconds

# Model Configurations
EMBEDDING_MODEL = "text-embedding-3-small"  # OpenAI's embedding model
GPT_MODEL = "gpt-4"                        # OpenAI's GPT model for text generation
PPLX_MODEL = "llama-3.1-sonar-huge-128k-online"  # Perplexity's model for research

# Validate required environment variables
if not OPENAI_API_KEY:
   raise ValueError("OpenAI API key not found in environment variables")
if not PPLX_API_KEY:
   raise ValueError("Perplexity API key not found in environment variables")