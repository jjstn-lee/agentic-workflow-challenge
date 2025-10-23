import json
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity



class KBClient:
    # location of "kb_documents.jsonl"
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.file_path = Path(__file__).resolve().parents[2] / "data" / "kb_documents.jsonl"
        self.docs = self.load_docs_from_csv()
        # unwrap textfield because sklearn compares about being passed dicts
        self.doc_vectors = self.vectorizer.fit_transform([d['text'] for d in self.docs])
        
    def load_docs_from_csv(self):
        """
        Loads JSON-formatted rows from a .csv or .txt file in the same directory.
        Each line should be a JSON object with keys: doc_id, title, text.
        Returns a list of dicts.
        """
        
        docs = []

        with open(self.file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    docs.append(obj)
                except json.JSONDecodeError as e:
                    print(f"Skipping line due to JSON error: {e}")
                    
        return docs    

    def find_nearest(self, query):
        query_vec = self.vectorizer.transform([query])
        
        sims = cosine_similarity(query_vec, self.doc_vectors).flatten()
        best_idx = sims.argmax()
        best_score = sims[best_idx]
        
        print(f"Most relevant with score of {best_score}: {self.docs[best_idx]}")
        
        return best_score, self.docs[best_idx]