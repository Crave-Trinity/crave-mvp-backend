# File: app/infrastructure/external/langchain_integration.py (Potentially Corrected)

from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import json

from langchain.vectorstores import Pinecone as LangchainPinecone
from langchain.embeddings import OpenAIEmbeddings # THIS MIGHT NEED UPDATING.
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.llms.base import BaseLLM

from app.config.settings import Settings
from app.infrastructure.vector_db.pinecone_client import get_pinecone_index

# Setup logging
logger = logging.getLogger(__name__)

# Get settings
settings = Settings()

class LangChainService:
    """
    Service for LangChain integrations with enhanced RAG capabilities.
    """

    def __init__(self, llm: Optional[BaseLLM] = None):
        """
        Initialize the LangChain service.

        Args:
            llm: Optional LangChain LLM object to use with chains
        """
        self.llm = llm
        # Use OpenAIEmbeddings, but ensure it's configured correctly
        self.embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
        self._vector_store = None

    @property
    def vector_store(self):
        """
        Lazy-loaded LangChain vector store connected to Pinecone.

        Returns:
            LangChain Pinecone vector store instance
        """
        if self._vector_store is None:
            # Connect to existing Pinecone index
            pinecone_index = get_pinecone_index(settings.PINECONE_INDEX_NAME)

            # Create LangChain vector store
            self._vector_store = LangchainPinecone(
                index=pinecone_index,
                embedding=self.embeddings,
                text_key="description"  # Field in metadata containing the text
            )

        return self._vector_store

    def create_craving_documents(self, cravings_data: List[Dict[str, Any]]) -> List[Document]:
        """
        Convert raw craving data to LangChain Document objects.

        Args:
            cravings_data: List of craving data dictionaries

        Returns:
            List of LangChain Document objects
        """
        documents = []

        for craving in cravings_data:
            # Extract raw text for the document
            raw_text = craving.get("description", "")
            if not raw_text:
                continue

            # Format a more comprehensive text
            formatted_text = (
                f"Craving: {raw_text}\n"
                f"Intensity: {craving.get('intensity', 0)}/10\n"
                f"Created: {craving.get('created_at', '')}\n"
                f"Additional notes: {craving.get('notes', '')}"
            )

            # Create metadata for the document
            metadata = {
                "user_id": craving.get("user_id"),
                "craving_id": craving.get("id"),
                "intensity": craving.get("intensity", 0),
                "created_at": craving.get("created_at", ""),
                "description": raw_text,  # Store original description
            }

            # Create document
            doc = Document(page_content=formatted_text, metadata=metadata)
            documents.append(doc)

        return documents

    def chunk_documents(
        self,
        documents: List[Document],
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> List[Document]:
        """
        Split documents into smaller chunks.
        """
        # Skip chunking if documents are small
        if all(len(doc.page_content) < chunk_size for doc in documents):
            return documents

        # Configure text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        # Chunk documents and maintain metadata
        chunked_docs = text_splitter.split_documents(documents)

        logger.info(f"Chunked {len(documents)} documents into {len(chunked_docs)} chunks")
        return chunked_docs

    def create_conversational_rag_chain(
        self,
        system_prompt: str = None,
        memory_key: str = "chat_history"
    ):
        """
        Create a conversational retrieval chain.
        """
        if self.llm is None:
            raise ValueError("LLM must be provided to create conversational chain")

        # Conversation memory
        memory = ConversationBufferMemory(
            memory_key=memory_key,
            return_messages=True
        )

        # Default system prompt
        if system_prompt is None:
            system_prompt = """You are CRAVE AI..."""

        # QA prompt template
        qa_prompt = PromptTemplate(
            input_variables=["system", "context", "question"],
            template="""
{system}

RELEVANT CONTEXT:
{context}

USER QUESTION:
{question}

YOUR RESPONSE:
"""
        )

        # Retrieval chain
        retriever = self.vector_store.as_retriever(
            search_kwargs={"k": 5, "fetch_k": 10}
        )

        # Build chain
        chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            memory=memory,
            verbose=True,
            return_source_documents=True,
            combine_docs_chain_kwargs={"prompt": qa_prompt}
        )

        return chain

    def add_documents_to_vector_store(self, documents: List[Document]) -> None:
        """
        Add documents to the vector store.
        """
        self.vector_store.add_documents(documents)
        logger.info(f"Added {len(documents)} documents to vector store")