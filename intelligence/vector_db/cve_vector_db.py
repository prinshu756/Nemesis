import faiss
import numpy as np
from .embedded import embed

class CVEDatabase:
    def __init__(self):
        try:
            self.index = faiss.IndexFlatL2(384)
            self.cves = []
            self.available = True
        except Exception as e:
            print(f"Warning: Faiss initialization failed: {e}. Using fallback search.")
            self.index = None
            self.cves = []
            self.available = False

    def add_cve(self, description):
        if not self.available:
            self.cves.append(description)
            return

        try:
            vec = embed(description)
            self.index.add(np.array([vec]).astype('float32'))
            self.cves.append(description)
        except Exception as e:
            print(f"Warning: Failed to add CVE to vector index: {e}")
            self.cves.append(description)

    def search(self, query):
        if not self.available or len(self.cves) == 0:
            # Fallback to simple text matching
            return self._simple_search(query)

        try:
            q_vec = embed(query)
            D, I = self.index.search(np.array([q_vec]).astype('float32'), min(3, len(self.cves)))
            return [self.cves[i] for i in I[0] if i < len(self.cves)]
        except Exception as e:
            print(f"Warning: Vector search failed: {e}. Using fallback search.")
            return self._simple_search(query)

    def _simple_search(self, query):
        """Simple text-based search fallback"""
        query_lower = query.lower()
        matches = []
        for cve in self.cves:
            if any(word in cve.lower() for word in query_lower.split()):
                matches.append(cve)
                if len(matches) >= 3:
                    break
        return matches