from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_classic.chains import ConversationalRetrievalChain
from langchain_classic.memory import ConversationBufferWindowMemory
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

import os
load_dotenv()

def load_document(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    
    # Initialize loader as None
    loader = None 

    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext == ".docx":
        loader = Docx2txtLoader(file_path)
    elif ext == ".txt":
        loader = TextLoader(file_path)

    # Check if loader was actually created before trying to use it
    if loader:
        return loader.load()
    else:
        print(f"Unsupported file extension: {ext}")
        return [] # Return an empty list so the app doesn't crash

def build_vectorestore(file_paths):
    """
    Loads all documents, splits into chunks,
    converts to vectors and stores in FAISS
    """
    all_docs = []

    for path in file_paths:
        docs= load_document(path)
        all_docs.extend(docs)
        print(f"Loaded: {os.path.basename(path)} → {len(docs)} pages")


        splitter= RecursiveCharacterTextSplitter(
            chunk_size = 500,
            chunk_overlap=50
        )
        chunks= splitter.split_documents(all_docs)
        print(f"total Chunks Created: {len(chunks)}")

        embeddings= OpenAIEmbeddings()
        vectorstore=FAISS.from_documents(chunks, embeddings)

        return vectorstore
    
def build_hr_chain(vectorstore):

    
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0  # 0 = consistent factual answers
    )

    memory = ConversationBufferWindowMemory(
        k=5,
        memory_key="chat_history",
        return_messages = True,
        output_key="answer"
    )
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k":4}
    )

    hr_prompt = """
You are a professional HR assistant for our company.
Your job is to answer employee questions based ONLY
on the official HR policy documents provided.

Rules you must follow:
1. Only answer from the policy documents
2. Always mention which policy/section you found it in
3. Be professional and friendly
4. If not found say exactly:
   "I couldn't find this in our policy documents.
    Please contact HR at hr@company.com for clarification."
5. Never make up policies or guess

Policy Documents Context:
{context}

Conversation History:
{chat_history}

Employee Question: {question}

HR Assistant Answer:"""

    prompt = PromptTemplate(
        input_variables=["context", "chat_history", "question"],
        template=hr_prompt
    )

    hr_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever= retriever,
        memory=memory,
        return_source_documents=True,
        combine_docs_chain_kwargs= {"prompt":prompt}
    )

    return hr_chain

def ask_hr(chain, question):
     """
    Sends question to chain
    Returns answer + source documents + confidence
    """
     
     response = chain.invoke({"question":question})

     answer = response["answer"]

     sources = []

     for doc in response["source_documents"]:
         filename= doc.metadata.get("filename","unknown")
         page= doc.metadata.get("page","N/A")
         source_str = f"[filename] (Page {page})"
         if source_str not in sources:
             sources.append(source_str)
    
     if "couldn't find" in answer.lower():
        confidence = "low"
     elif len(response["source_documents"]) >= 3:
        confidence = "high"
     else:
        confidence = "medium"

     return answer, sources, confidence