import faiss
import numpy as np
from .embedded import embed

class CVEDatabase:
    def __init__(self):
        self.index = faiss.IndexFlatL2(384)
        self.cves = []

    def add_cve(self, description):
        vec = embed(description)
        self.index.add(np.array([vec]).astype('float32'))
        self.cves.append(description)

    def search(self, query):
        q_vec = embed(query)
        D, I = self.index.search(np.array([q_vec]).astype('float32'), 3)
        return [self.cves[i] for i in I[0]]