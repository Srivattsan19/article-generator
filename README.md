# Article Generator

A Retrieval-Augmented Generation (RAG) system that generates well-researched articles by combining web content retrieval, semantic search, and GPT-based text generation. The system automatically retrieves relevant sources, processes web content, and generates structured academic articles with proper citations.

## Table of Contents
- [Quick Start](#quick-start)
- [Project Overview](#project-overview)
- [Technical Architecture](#technical-architecture)
- [Implementation Details](#implementation-details)
- [Usage Guide](#usage-guide)
- [Troubleshooting](#troubleshooting)

## Quick Start

### Prerequisites
- Python 3.8 or higher
- OpenAI API key
- Perplexity API key
- Internet connection for web content retrieval

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/article-generator.git
cd article-generator
```

2. Create and activate a virtual environment:
```bash
# Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory:
```plaintext
OPENAI_API_KEY=your_openai_api_key_here
PPLX_API_KEY=your_perplexity_api_key_here
```

5. Create required directories:
```bash
mkdir logs
```

### Running the Application

1. Start the Streamlit app:
```bash
streamlit run main.py
```

2. Open your web browser and navigate to:
```
http://localhost:8501
```

## Project Overview

The RAG system generates research articles through the following steps:

1. **Content Retrieval**: Uses Perplexity API to find relevant sources
2. **Web Scraping**: Extracts content from retrieved URLs
3. **Embedding Generation**: Creates semantic embeddings using Sentence Transformers
4. **Content Selection**: Ranks content relevance using cosine similarity
5. **Article Generation**: Produces structured content using GPT-4
6. **Citation Management**: Maintains source attribution and references

## Technical Architecture

### Project Structure
```
article-generator/
├── main.py                 # Application entry point
├── requirements.txt        # Project dependencies
├── .env                    # API keys and config
├── src/
│   ├── __init__.py
│   ├── citation_manager.py # Citation handling
│   ├── config.py          # Configuration settings
│   ├── perplexity_client.py # Perplexity API interface
│   ├── rag_system.py      # RAG implementation
│   └── scraper.py         # Web content extraction
├── utils/
│   ├── __init__.py
│   └── logger.py          # Logging configuration
└── logs/                  # Log files
```

### Key Components

- **Web Scraping**: BeautifulSoup4 for content extraction
- **Embeddings**: Sentence Transformers for semantic understanding
- **Text Generation**: OpenAI's GPT-4
- **Interface**: Streamlit web application

## Implementation Details

### Core Technologies

- **RAG Pipeline**:
  - Combines retrieval and generation for improved accuracy
  - Uses semantic search for content relevance
  - Maintains source attribution

- **Embedding System**:
  - Local embedding generation using Sentence Transformers
  - Efficient similarity matching
  - Chunked text processing

- **Content Generation**:
  - Structured article sections
  - Citation integration
  - Academic formatting

## Usage Guide

1. **Enter Research Topic**:
   - Type your topic in the input field
   - Click "Generate Article"

2. **Generation Process**:
   - URL collection (Progress: 0-33%)
   - Content processing (Progress: 33-66%)
   - Article generation (Progress: 66-100%)

3. **Output**:
   - View generated article sections
   - Check references and sources
   - Download article in Markdown format

## Troubleshooting

### Common Issues

1. **API Key Errors**:
   - Verify keys in `.env` file
   - Check API subscription status
   - Ensure proper key format

2. **Connection Issues**:
   - Check internet connectivity
   - Verify proxy settings if applicable
   - Ensure API endpoints are accessible

3. **Generation Failures**:
   - Check log files in `logs` directory
   - Verify sufficient API credits
   - Ensure topic is well-defined

### Error Messages

- "Missing API keys": Check `.env` file configuration
- "No URLs found": Try reformulating your topic
- "Failed to process URL": Check website accessibility

## Performance Optimization

- Uses batch processing for embeddings
- Implements caching where appropriate
- Optimizes chunk sizes for processing

## Limitations

- Requires active internet connection
- Subject to API rate limits
- Processing time varies with content volume

## Support

For issues and questions:
1. Check the logs directory
2. Open an issue on GitHub
3. Contact project maintainers

## License

MIT License - see LICENSE file for details

## Contributing

1. Fork the repository
2. Create your feature branch
3. Submit a pull request

## Acknowledgments

- OpenAI for GPT-4 API
- Perplexity AI for research capabilities
- Hugging Face for Sentence Transformers