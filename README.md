# Engineering Drawing Data Agent

A local AI-powered assistant for querying structured engineering drawing data using natural language.

## Features

- **ChromaDB**: Vectorizes and stores drawing metadata for semantic search.
- **Streamlit UI**: Simple interface for uploading JSON files and chatting with the agent.
- **Ollama**: Handles both embedding and conversational AI locally.
- **Local-first**: All data processing and interaction happens on your machine.

## Workflow

1. Upload a JSON file containing engineering drawing metadata (e.g., part numbers, titles, revisions, weld callouts).
2. The agent vectorizes the data using ChromaDB and stores it locally.
3. A chatbot interface opens via Streamlit.
4. Ask questions in natural language; Ollama retrieves and responds using the embedded data.

## Tech Stack

- `ChromaDB` for vector storage
- `Streamlit` for UI
- `Ollama` for embedding and chat
- `Python` for backend logic

## Use Case

Designed for engineers and technical teams needing fast, local access to drawing records without cloud dependencies. Supports conversational queries over thousands of entries.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/RylanBosquez/engineeringDrawingDataAgent.git
    cd engineeringDrawingDataAgent
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Pull required Ollama models:
    ```bash
    ollama pull nomic-embed-text
    ollama pull llama3.2
    ```

## Running the App

Start the Streamlit interface:
```bash
streamlit run app.py
```


## Example Usage

### Searching database using a specified part number:
![Example Usage](assets/searchByPartNumber.png)

### Searching database using a specified title:
![Example Usage](assets/searchByTitle.png)