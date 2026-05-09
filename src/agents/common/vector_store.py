"""
Vector Store Client for AI-Powered Observability Platform

Provides interface to Chroma vector database for:
- Conversation memory storage
- Context retrieval
- Semantic search
- Agent memory persistence
"""

import os
from typing import List, Dict, Any, Optional

import structlog
import chromadb
from chromadb.config import Settings

logger = structlog.get_logger(__name__)


class VectorStoreClient:
    """
    Chroma vector store client for agent memory.
    
    Each agent has its own collection for isolated memory:
    - supervisor-memory
    - observability-memory
    - pod-recovery-memory
    - backup-restore-memory
    """
    
    def __init__(
        self,
        collection_name: str,
        host: Optional[str] = None,
        port: Optional[int] = None,
    ):
        """
        Initialize vector store client.
        
        Args:
            collection_name: Name of the collection (e.g., "supervisor-memory")
            host: Chroma server host (default: from CHROMA_HOST env)
            port: Chroma server port (default: from CHROMA_PORT env)
        """
        self.collection_name = collection_name
        self.host = host or os.getenv("CHROMA_HOST", "localhost")
        self.port = int(port or os.getenv("CHROMA_PORT", "8000"))
        
        # Initialize Chroma client
        self.client = chromadb.HttpClient(
            host=self.host,
            port=self.port,
            settings=Settings(
                anonymized_telemetry=False,
            ),
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": f"Memory for {collection_name}"},
        )
        
        logger.info(
            "vector_store_initialized",
            collection=self.collection_name,
            host=self.host,
            port=self.port,
        )
    
    def add_memory(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        id: Optional[str] = None,
    ) -> str:
        """
        Add memory to vector store.
        
        Args:
            text: Text content to store
            metadata: Optional metadata (e.g., timestamp, user_id, intent)
            id: Optional custom ID (auto-generated if None)
        
        Returns:
            Memory ID
        """
        import uuid
        
        memory_id = id or str(uuid.uuid4())
        
        self.collection.add(
            documents=[text],
            metadatas=[metadata or {}],
            ids=[memory_id],
        )
        
        logger.info(
            "memory_added",
            collection=self.collection_name,
            memory_id=memory_id,
            text_length=len(text),
        )
        
        return memory_id
    
    def search_memory(
        self,
        query: str,
        n_results: int = 5,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar memories.
        
        Args:
            query: Search query
            n_results: Number of results to return
            filter: Optional metadata filter
        
        Returns:
            List of matching memories with scores
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=filter,
        )
        
        memories = []
        for i in range(len(results["ids"][0])):
            memories.append({
                "id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
            })
        
        logger.info(
            "memory_search",
            collection=self.collection_name,
            query_length=len(query),
            results_count=len(memories),
        )
        
        return memories
    
    def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Get specific memory by ID.
        
        Args:
            memory_id: Memory ID
        
        Returns:
            Memory dict or None if not found
        """
        try:
            result = self.collection.get(ids=[memory_id])
            
            if result["ids"]:
                return {
                    "id": result["ids"][0],
                    "text": result["documents"][0],
                    "metadata": result["metadatas"][0],
                }
            return None
        
        except Exception as e:
            logger.error(
                "memory_get_error",
                collection=self.collection_name,
                memory_id=memory_id,
                error=str(e),
            )
            return None
    
    def delete_memory(self, memory_id: str) -> bool:
        """
        Delete memory by ID.
        
        Args:
            memory_id: Memory ID
        
        Returns:
            True if deleted, False otherwise
        """
        try:
            self.collection.delete(ids=[memory_id])
            
            logger.info(
                "memory_deleted",
                collection=self.collection_name,
                memory_id=memory_id,
            )
            
            return True
        
        except Exception as e:
            logger.error(
                "memory_delete_error",
                collection=self.collection_name,
                memory_id=memory_id,
                error=str(e),
            )
            return False
    
    def get_recent_memories(
        self,
        n_results: int = 10,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get most recent memories.
        
        Args:
            n_results: Number of results to return
            filter: Optional metadata filter
        
        Returns:
            List of recent memories
        """
        # Get all memories (Chroma doesn't have built-in sorting by timestamp)
        result = self.collection.get(
            where=filter,
            limit=n_results * 2,  # Get more to sort
        )
        
        memories = []
        for i in range(len(result["ids"])):
            memories.append({
                "id": result["ids"][i],
                "text": result["documents"][i],
                "metadata": result["metadatas"][i],
            })
        
        # Sort by timestamp if available
        if memories and "timestamp" in memories[0]["metadata"]:
            memories.sort(
                key=lambda x: x["metadata"].get("timestamp", 0),
                reverse=True,
            )
        
        return memories[:n_results]
    
    def clear_collection(self) -> bool:
        """
        Clear all memories from collection.
        
        WARNING: This deletes all data in the collection!
        
        Returns:
            True if successful
        """
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": f"Memory for {self.collection_name}"},
            )
            
            logger.warning(
                "collection_cleared",
                collection=self.collection_name,
            )
            
            return True
        
        except Exception as e:
            logger.error(
                "collection_clear_error",
                collection=self.collection_name,
                error=str(e),
            )
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get collection statistics.
        
        Returns:
            Dict with collection stats
        """
        count = self.collection.count()
        
        return {
            "collection_name": self.collection_name,
            "total_memories": count,
            "host": self.host,
            "port": self.port,
        }


# Made with Bob