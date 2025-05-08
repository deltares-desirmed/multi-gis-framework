# ecosystem_search.py
"""
Ecosystem Services Knowledge Retrieval Module
----------------------------------------------
This script enables retrieval-augmented generation (RAG) from an Excel-based
multi-sheet database of ecosystem services. It transforms structured data into
vector-searchable knowledge for intelligent LLM responses.

Logical Steps:
1. Load Excel sheets into DataFrames
2. Convert rows into meaningful text chunks
3. Embed chunks using SentenceTransformers
4. Store chunks and vectors in FAISS index
5. Allow semantic query to retrieve relevant chunks
6. (Optional) Reuse chunks to inject context into LLM prompts
"""

import pandas as pd
import os
from sentence_transformers import SentenceTransformer
import faiss
import pickle

# --- Configuration ---
DATA_PATH = "database/ecosystem_data.xlsx"
FAISS_PATH = "vector_store/ess_index.faiss"
META_PATH = "vector_store/ess_meta.pkl"
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
def embed_chunks(chunks, model_name=MODEL_NAME):
    model = SentenceTransformer(model_name)
    embeddings = model.encode(chunks, show_progress_bar=True)
    return model, embeddings

# ----------- Step 4: Store vectors in FAISS -----------
def save_faiss_index(embeddings, chunks, metadata, faiss_path=FAISS_PATH, meta_path=META_PATH):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    faiss.write_index(index, faiss_path)
    with open(meta_path, "wb") as f:
        pickle.dump({"chunks": chunks, "metadata": metadata}, f)

# ----------- Step 5: Query function -----------
def search_index(query, model, faiss_path=FAISS_PATH, meta_path=META_PATH, top_k=5):
    index = faiss.read_index(faiss_path)
    with open(meta_path, "rb") as f:
        meta = pickle.load(f)
    q_vec = model.encode([query])
    D, I = index.search(q_vec, top_k)
    results = [meta["chunks"][i] for i in I[0]]
    return results

# ----------- Step 6: Context injector for chatbot -----------
def get_context_chunks(query):
    """Loads model and searches relevant chunks for a query."""
    model = SentenceTransformer(MODEL_NAME)
    return search_index(query, model)

# Optional: Initial run to generate index if not present
if __name__ == "__main__":
    if not os.path.exists(FAISS_PATH):
        print("[INFO] Generating vector index from Excel data...")
        excel_data = load_excel_data(DATA_PATH)
        chunks, metadata = dataframe_to_chunks(excel_data)
        model, embeddings = embed_chunks(chunks)
        save_faiss_index(embeddings, chunks, metadata)
        print("[INFO] Vector index saved.")
    else:
        print("[INFO] FAISS index already exists. Ready for query.")