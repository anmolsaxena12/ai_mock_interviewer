import os
import shutil
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Global vector store and embeddings instance
_db = None
_embeddings = None

def get_embeddings_model():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return _embeddings

def get_vector_store():
    global _db
    return _db

def set_vector_store(db_instance):
    global _db
    _db = db_instance

def load_and_split_file_document(filepath):
    """Loads a document (PDF/DOCX) from a file and splits it into chunks."""
    if filepath.endswith('.pdf'):
        loader = PyPDFLoader(filepath)
    elif filepath.endswith('.docx'):
        loader = Docx2txtLoader(filepath)
    else:
        raise ValueError("Unsupported file type")

    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_documents(documents)
    return chunks

def process_text_to_chunks(text_content, source="Job Description"):
    """Converts raw text content into LangChain Documents and splits them."""
    if not text_content or not text_content.strip():
        return []

    doc = Document(page_content=text_content, metadata={'source': source})
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_documents([doc])
    return chunks

def initialize_vector_db(all_chunks, chroma_db_dir):
    """Initializes and persists the ChromaDB from chunks."""
    if os.path.exists(chroma_db_dir) and os.listdir(chroma_db_dir):
         shutil.rmtree(chroma_db_dir)
    os.makedirs(chroma_db_dir, exist_ok=True)

    print(f"Creating ChromaDB from {len(all_chunks)} chunks...")
    db = Chroma.from_documents(
        documents=all_chunks,
        embedding=get_embeddings_model(),
        persist_directory=chroma_db_dir
    )
    db.persist()
    set_vector_store(db)
    print("ChromaDB created and persisted successfully!")

def get_retriever():
    db_instance = get_vector_store()
    if db_instance:
        return db_instance.as_retriever(search_kwargs={"k": 3})
    return None

def clear_vector_db(chroma_db_dir):
    global _db, _embeddings
    _db = None
    _embeddings = None
    if os.path.exists(chroma_db_dir):
        shutil.rmtree(chroma_db_dir)
    os.makedirs(chroma_db_dir, exist_ok=True)