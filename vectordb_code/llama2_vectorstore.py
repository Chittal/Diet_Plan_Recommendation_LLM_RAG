import chromadb

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore


def create_index(name, chroma_collection):
    documents = SimpleDirectoryReader("data/" + name).load_data()
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_documents(documents, storage_context=storage_context, show_progress=True)
    return index

def retrieve_index(chroma_collection):
    # fetch documents and index from storage
    chroma_vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    index = VectorStoreIndex.from_vector_store(vector_store=chroma_vector_store)
    return index

def create_or_retrieve_index(name):
    db = chromadb.PersistentClient(path="./storage/chroma")
    try:
        chroma_collection = db.get_collection(name=name)
        index = retrieve_index(chroma_collection)
    except:
        chroma_collection = db.get_or_create_collection(name)
        index = create_index(name, chroma_collection)
    return index



def list_all_collections():
    db = chromadb.PersistentClient(path="./storage/chroma")
    print(f"Available collections: {db.list_collections()}")
