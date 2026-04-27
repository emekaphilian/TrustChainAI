"""RAG agent for retrieval-augmented generation."""

from typing import Any, Dict, List

from rag.index import INDEX, retrieve


class RAGAgent:
    """
    Retrieval-augmented generation agent.
    Uses FAISS vector index for semantic search.
    """
    
    def __init__(self):
        self.index = INDEX
    
    def query(self, text: str) -> List[Dict[str, Any]]:
        """
        Query the RAG index for relevant documents.
        
        Args:
            text: Query text
            
        Returns:
            List of retrieved documents
        """
        return self.index.search(text)
    
    def query_by_swc(self, swc_id: str) -> List[Dict[str, Any]]:
        """
        Query by SWC ID.
        
        Args:
            swc_id: SWC identifier
            
        Returns:
            List of matching documents
        """
        return self.index.search(f"SWC {swc_id}")
    
    def get_all_swc(self) -> List[Dict[str, Any]]:
        """
        Get all SWC entries.
        
        Returns:
            List of all SWC documents
        """
        return self.index.search("", k=10)