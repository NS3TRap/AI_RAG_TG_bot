import os
import logging
from pathlib import Path
from chromadb import PersistentClient
import uuid
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChromaService:
    def __init__(self):
        db_path = os.getenv("CHROMA_DB_DIR")
        if not db_path:
            raise ValueError("CHROMA_DB_DIR не задан")

        db_path = os.path.abspath(db_path)
        Path(db_path).mkdir(parents=True, exist_ok=True)

        self.client = PersistentClient(path=db_path)
        self.collection_name = os.getenv("CHROMA_COLLECTION_NAME")
        self.collection = self._get_or_create_collection()
        self.embedding_model = SentenceTransformer(
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )

        logger.info("Инициализация ChromaService завершена: %s", self.collection_name)
        logger.info("CHROMA_DB_DIR=%s", db_path)

    def _get_or_create_collection(self):
        try:
            return self.client.get_collection(name=self.collection_name)
        except Exception as e:
            logger.warning("Коллекция не найдена, создаю новую. Ошибка: %s", e)
            return self.client.create_collection(name=self.collection_name)

    def insert_query(self, text: str, metadata: dict = None):
        doc_id = str(uuid.uuid4())
        embedding = self.embedding_model.encode(text).tolist()
        self.collection.add(
            documents=[text],
            metadatas=[metadata] if metadata else [{}],
            embeddings=[embedding],
            ids=[doc_id]
        )

        logger.info("Документ добавлен с ID: %s", doc_id)

    def select_query(self, query_text, top_k=1):
        embedding = self.embedding_model.encode(query_text).tolist()
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k
        )
        logger.info("Запрос выполнен: '%s', найдено %d результатов", query_text, len(results['documents'][0]) if results['documents'] else 0)
        return results['documents'][0] if results['documents'] else []
    
    def delete_query(self, doc_id):
        self.collection.delete(ids=[doc_id])
        logger.info("Документ с ID %s удалён", doc_id)

    def list_query(self):
        all_docs = self.collection.get()
        logger.info("Всего документов в коллекции '%s': %d", self.collection_name, len(all_docs['documents']))
        return list(zip(all_docs["ids"], all_docs["documents"]))
    