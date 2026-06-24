# HR Policy Assistant - RAG Chatbot

An intelligent **Retrieval-Augmented Generation (RAG)** chatbot that allows employees to ask natural language questions about company HR policies and receive accurate, context-aware answers from uploaded policy documents.

## Overview

HR policies are often lengthy and difficult to navigate. This project uses a **RAG (Retrieval-Augmented Generation)** architecture to retrieve the most relevant policy sections and generate reliable answers using an LLM.

Instead of searching through hundreds of pages, employees can simply ask questions like:

- "How many annual leave days do I get?"
- "What is the work from home policy?"
- "How is overtime calculated?"
- "What is the notice period?"


The system retrieves the relevant policy chunks and generates answers grounded in the uploaded documents.

##  Features

- Upload HR policy PDF documents
- Automatic document processing and chunking
- Vector embeddings for semantic search
- LLM-powered answer generation
- Source citation for transparency
- Modern chatbot interface
- Fast retrieval using vector similarity search
- Answers based only on uploaded company policies

---

##  Architecture

```
                HR Policy PDF
                      │
                      ▼
             Document Processing
                      │
                      ▼
          Text Chunking & Cleaning
                      │
                      ▼
              Embedding Model
                      │
                      ▼
                Vector Database
                      │
                      ▼
User Question ──► Similarity Search
                      │
                      ▼
          Retrieved Relevant Chunks
                      │
                      ▼
                  Large Language Model
                      │
                      ▼
             Context-Aware Response
```

##  Workflow

### 1. Upload Documents

Users upload HR policy PDF files through the application.

### 2. Process Documents

The system:

- Extracts text
- Splits content into chunks
- Generates embeddings
- Stores embeddings in the vector database

### 3. Ask Questions

Users can ask natural language questions about:

- Leave policies
- Working hours
- Benefits
- Overtime
- Remote work
- Attendance
- Company rules
- Employee guidelines

### 4. Retrieve Relevant Context

Instead of sending the entire document to the LLM, the system retrieves only the most relevant sections.

### 5. Generate Answer

The LLM generates a response using only the retrieved policy information, reducing hallucinations and improving accuracy.

---

## Tech Stack

| Component | Technology |
|------------|----------------------------|
| Frontend | Streamlit |
| Language | Python |
| Document Processing | PDF Parser |
| Embeddings | Sentence Transformers / OpenAI Embeddings |
| Vector Store | ChromaDB / FAISS |
| LLM | OpenAI / Local LLM |
| Retrieval | Semantic Similarity Search |

---




# ⭐ If you found this project useful, consider giving it a star!
