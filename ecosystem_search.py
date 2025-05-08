# ecosystem_search.py
"""
Ecosystem Services Knowledge Retrieval Module (Safe Portable Version)
--------------------------------------------------------------------------
This script enables retrieval-augmented generation (RAG) from an Excel-based
multi-sheet database of ecosystem services. It transforms structured data into
vector-searchable knowledge using SentenceTransformers and local cosine similarity
instead of Chroma or FAISS, making it lighter and more compatible across systems.

Logical Steps:
1. Load Excel sheets into DataFrames
2. Convert rows into meaningful text chunks
3. Embed chunks using SentenceTransformers
4. Save embeddings and metadata locally
5. Query top matches using cosine similarity
6. Return context to be injected into LLM prompts
"""

import os
import pandas as pd
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# --- Configuration ---
DATA_PATH = "database/ecosystem_data.xlsx"
EMBEDDING_PATH = "vector_store/ess_embeddings.npz"
CHUNKS_META_PATH = "vector_store/ess_chunks_metadata.pkl"
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

# ----------- Step 3: Create embeddings -----------
def embed_chunks(chunks):
    model = SentenceTransformer(MODEL_NAME)
    embeddings = model.encode(chunks, show_progress_bar=True)
    return model, embeddings

# ----------- Step 4: Save locally -----------
def save_local_store(embeddings, chunks, metadata):
    if not os.path.exists("vector_store"):
        os.makedirs("vector_store")
    np.savez(EMBEDDING_PATH, embeddings=embeddings)
    with open(CHUNKS_META_PATH, "wb") as f:
        pickle.dump({"chunks": chunks, "metadata": metadata}, f)

# ----------- Step 5: Semantic Search -----------
def search_ess_knowledge(query, top_k=5):
    model = SentenceTransformer(MODEL_NAME)
    query_vec = model.encode([query])

    # Load stored data
    with np.load(EMBEDDING_PATH) as data:
        embeddings = data["embeddings"]
    with open(CHUNKS_META_PATH, "rb") as f:
        meta = pickle.load(f)

    # Cosine similarity
    scores = cosine_similarity(query_vec, embeddings)[0]
    top_idx = np.argsort(scores)[::-1][:top_k]
    top_chunks = [meta["chunks"][i] for i in top_idx]
    top_meta = [meta["metadata"][i] for i in top_idx]
    df = pd.DataFrame(top_meta)
    return df, top_chunks

# ----------- Step 6: Optional Initial Index Creation -----------
if __name__ == "__main__":
    print("[INFO] Creating local vector index from Excel...")
    excel_data = load_excel_data(DATA_PATH)
    chunks, metadata = dataframe_to_chunks(excel_data)
    model, embeddings = embed_chunks(chunks)
    save_local_store(embeddings, chunks, metadata)
    print("[INFO] Local vector index saved. Ready for querying.")
