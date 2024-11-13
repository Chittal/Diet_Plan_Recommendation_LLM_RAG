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


def create_collection_fast_embedding(name):
    embeddings = get_embedding()
    base_dir = 'data/' + name
    collection = Chroma(persist_directory='./storage/chroma', embedding_function=embeddings, collection_name=name)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1024, chunk_overlap=80, length_function=len, is_separator_regex=False
    )
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".pdf"):
                file_name = os.path.join(root, file)
                loader = PDFPlumberLoader(file_name)
                docs = loader.load_and_split()
                print(f"docs len={len(docs)}")

                chunks = text_splitter.split_documents(docs)
                print(f"chunks len={len(chunks)}")
                # ids = []
                # embedding = []
                # for chunk_index, chunk in enumerate(chunks):
                #     text_content = chunk.page_content
                #     embed_chunk = embeddings(text_content)  # Ensure this calls the embedding function correctly
                #     embedding.append(embed_chunk)
                #     ids.append(f"{file_name}_{chunk_index}")

                collection.add_documents(documents=chunks) # , embeddings=embedding, ids=ids
    # db.persist()


def get_vector_store_retriever(name):
    embeddings = get_embedding()
    # chroma_collection = db.get_or_create_collection(
    #     name=name,
    #     embedding_function=embeddings
    # )
    # vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    vector_store = Chroma(persist_directory='./storage/chroma', embedding_function=embeddings, collection_name=name)

    print("Creating chain with collection")

    # Set up retriever with the Chroma collection
    retriever = vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={
            "k": 20,
            "score_threshold": 0.1,
        },
    )

    return retriever


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

# delete_collection("diet_plan")


def create_index(name):
    db = get_db()
    chroma_collection = db.get_or_create_collection(name)
    documents = SimpleDirectoryReader("data/" + name, recursive=True).load_data()
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    Settings.embed_model = get_embedding()
    index = VectorStoreIndex.from_documents(documents, storage_context=storage_context, show_progress=True)
    retriever = index.as_retriever()
    return retriever


def retrieve_index(name):
    # fetch documents and index from storage
    # db = get_db()
    # chroma_collection = db.get_collection(name=name)
    # chroma_vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    # Settings.embed_model = get_embedding()
    # index = VectorStoreIndex.from_vector_store(vector_store=chroma_vector_store)
    # retriever = index.as_retriever(search_type="similarity_score_threshold",
    #     search_kwargs={
    #         "k": 20,
    #         "score_threshold": 0.1,
    #     },)
    # return retriever
    vector_store = Chroma(persist_directory='storage/chroma', embedding_function=get_embedding(), collection_name=name)

    print("Creating chain with collection")

    # Set up retriever with the Chroma collection
    retriever = vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={
            "k": 20,
            "score_threshold": 0.1,
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
            create_collection_sentence_transormer(name)
            print("disease done")
        else:
            print('creating diet')
            create_index(name)


if __name__ == '__main__':
    create_collection('disease')
    create_collection('diet_plan')
    list_all_collections()