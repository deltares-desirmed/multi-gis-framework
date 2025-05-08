# ecosystem_search.py
"""
Ecosystem Services Knowledge Retrieval Module (Chroma Version for Windows)
--------------------------------------------------------------------------
This script enables retrieval-augmented generation (RAG) from an Excel-based
multi-sheet database of ecosystem services. It transforms structured data into
vector-searchable knowledge using Chroma for intelligent LLM responses.

Logical Steps:
1. Load Excel sheets into DataFrames
2. Convert rows into meaningful text chunks
3. Embed chunks using SentenceTransformers
4. Store chunks and embeddings in Chroma vector DB
5. Query top matches using semantic similarity
6. Return context to be injected into LLM prompts
"""

import os
import pandas as pd
import pickle
from sentence_transformers import SentenceTransformer
from chromadb import Client
from chromadb.config import Settings
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# --- Configuration ---
DATA_PATH = "database/ecosystem_data.xlsx"
VECTOR_FOLDER = "vector_store"
VECTOR_DB_NAME = "ess_knowledge"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# ----------- Step 1: Load Excel sheets -----------
def load_excel_data(path):
    """Reads all sheets in the Excel workbook into a dictionary of DataFrames."""
    try:
        excel_file = pd.ExcelFile(path)
        return {sheet: excel_file.parse(sheet) for sheet in excel_file.sheet_names}
    except Exception as e:
        raise RuntimeError(f"Failed to read Excel file: {e}")

# ----------- Step 2: Convert rows to text chunks -----------
def dataframe_to_chunks(df_dict):
    """Converts all rows from all sheets into natural-language formatted text chunks."""
    chunks = []
    metadata = []
    for sheet_name, df in df_dict.items():
        for idx, row in df.iterrows():
            text = f"Sheet: {sheet_name}\n" + "\n".join(
                [f"{col}: {row[col]}" for col in df.columns if pd.notna(row[col])]
            )
            chunks.append(text)
            metadata.append({"sheet": sheet_name, "row": idx})
    return chunks, metadata

# ----------- Step 3–4: Embedding & Storing in Chroma DB -----------
def build_vector_store(chunks, metadata, persist_dir=VECTOR_FOLDER):
    if not os.path.exists(persist_dir):
        os.makedirs(persist_dir)

    embedding_fn = SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)
    client = Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory=persist_dir))
    collection = client.create_collection(name=VECTOR_DB_NAME, embedding_function=embedding_fn)

    ids = [f"chunk_{i}" for i in range(len(chunks))]
    collection.add(documents=chunks, metadatas=metadata, ids=ids)
    client.persist()
    return collection

# ----------- Step 5: Semantic Query -----------
def search_ess_knowledge(query, top_k=5):
    embedding_fn = SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)
    client = Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory=VECTOR_FOLDER))
    collection = client.get_collection(name=VECTOR_DB_NAME, embedding_function=embedding_fn)
    results = collection.query(query_texts=[query], n_results=top_k)
    chunks = results["documents"][0]
    metadatas = results["metadatas"][0]
    df = pd.DataFrame(metadatas)
    return df, chunks

# ----------- Step 6: Optional Initial Index Creation -----------
if __name__ == "__main__":
    print("[INFO] Creating knowledge index from Excel...")
    excel_data = load_excel_data(DATA_PATH)
    chunks, metadata = dataframe_to_chunks(excel_data)
    build_vector_store(chunks, metadata)
    print("[INFO] Chroma vector store created and saved.")
