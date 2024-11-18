import os
import fitz
import chromadb

from flask import session, g

from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_community.vectorstores import Chroma

from llama_index.core import SimpleDirectoryReader

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from sentence_transformers import SentenceTransformer
from langchain.embeddings.huggingface import HuggingFaceEmbeddings

from llama_index.core import Settings


model = SentenceTransformer('all-MiniLM-L6-v2')


def get_db():
    db = chromadb.PersistentClient(path="storage/chroma")
    # try:
    #     db = g.db
    # except:
    #     db = chromadb.PersistentClient(path="storage/chroma")
    return db


def get_embedding():
    huggingface_ef = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    return huggingface_ef

def extract_text_from_pdf(file_path):
  with fitz.open(file_path) as pdf_document:
      text = ""
      for page in pdf_document:
          text += page.get_text()
      return text
  

def get_category_from_path(file_path):
    # Extract the folder name from the path to use it as the category
    folder_name = os.path.basename(os.path.dirname(file_path))
    return folder_name


def create_collection_sentence_transormer(name):
    # Load the Sentence Transformer model for disease
    # Initialize ChromaDB
    base_dir = 'data/' + name
    db = get_db()
    collection = db.get_or_create_collection(name=name)

    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".pdf"):
              file_path = os.path.join(root, file)

              # Extract text from the PDF
              text = extract_text_from_pdf(file_path)

              # Assign category based on folder structure
              category = get_category_from_path(file_path)

              # Generate embeddings for the document
              document_embedding = model.encode(text).tolist()

              # Store document with metadata in ChromaDB
            #   print(text, "text")
              print(file_path, "file_path")
              print(category, "category")
              collection.add(
                  documents=[text],
                  embeddings=[document_embedding],
                  ids=[file_path],  # Use file path as a unique ID
                  metadatas=[{'category': category, "file_name": file}]
              )
    return collection


def query_sentence_transormer_collection(name, query_text, n_results=5):
    """Query the ChromaDB collection with a semantic search."""
    # print(query_text)
    db = get_db()
    query_embedding = model.encode(query_text).tolist()
    # print("query embedding", query_embedding)
    collection = db.get_collection(name=name)
    # print(collection, name)
    # print(len(collection.get()), "collection length")
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    # print(results, "result")
    # for document, metadata in zip(results['documents'][0], results['metadatas'][0]):
    #     print(f"Filename: {metadata['filename']}\nContent: {document}\n")
    return results['metadatas']


def list_all_collections():
    db = get_db()
    print(f"Available collections: {db.list_collections()}")


def delete_collection(collection_name):
    db = get_db()
    try:
        db.delete_collection(collection_name)
        print(f"Collection '{collection_name}' has been deleted successfully.")
    except Exception as e:
        print(f"An error occurred while deleting the collection: {e}")


# def create_index(name):
#     db = get_db()
#     chroma_collection = db.get_or_create_collection(name)
#     documents = SimpleDirectoryReader("data/" + name, recursive=True).load_data()
#     vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
#     storage_context = StorageContext.from_defaults(vector_store=vector_store)
#     Settings.embed_model = get_embedding()
#     index = VectorStoreIndex.from_documents(documents, storage_context=storage_context, show_progress=True)
#     retriever = index.as_retriever()
#     return retriever


def create_index(name):
    db = get_db()
    collection = db.get_or_create_collection(name)
    embed_model = get_embedding()
    documents = SimpleDirectoryReader("data/" + name, recursive=True).load_data()
    for doc in documents:
        # Embed the document content
        embedding = embed_model.embed_documents([doc.text])  # Assuming `embed()` returns an embedding for the content
         # Add the folder name to the metadata
        doc_metadata = doc.metadata.copy() if doc.metadata else {}
        folder_name = os.path.basename(os.path.dirname(doc_metadata['file_path']))
        doc_metadata['folder'] = os.path.basename(folder_name) 
        # print("folder anme", folder_name)
        
        # Add document and its embedding to the collection
        collection.add(
            documents=[doc.text],               # Content of the document
            metadatas=doc_metadata,                # Metadata if available
            ids=[doc.id_],                          # Unique ID for each document
            embeddings=embedding                   # Embedded representation of the document
        )
    
    # Create retriever with embeddings included
    # retriever = collection.as_retriever()
    # return retriever
    # return retrieve_index(name)
    return collection


def retrieve_index(name):
    vector_store = Chroma(persist_directory='storage/chroma', embedding_function=get_embedding(), collection_name=name)
    print("Creating chain with collection")
    retriever = vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={
            "k": 10,
            "score_threshold": 0.1,
        },
    )
    return retriever


def retrieve_index_with_folder(name, folder):
    vector_store = Chroma(persist_directory='storage/chroma', embedding_function=get_embedding(), collection_name=name)
    print("Creating chain with collection")
    retriever = vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={
            "filter": {
                "folder": folder
            },
            "k": 10,
            "score_threshold": 0.3,
        },
    )
    return retriever


def create_collection(name):
    db = get_db()
    print('here db ')
    try:
        db.get_collection(name=name)
    except:
        if name == 'disease':
            print('creating disease')
            # create_collection_sentence_transormer(name)
            create_index(name)
            print("disease done")
        else:
            print('creating diet')
            create_index(name)


if __name__ == '__main__':
    create_collection('disease')
    create_collection('diet_plan')
    list_all_collections()

