# memory.py

import faiss
import numpy as np
import datetime

class MemoryBank:
    def __init__(self, dimension=768):
        self.index = faiss.IndexFlatL2(dimension)
        self.vectors = []
        self.metadata = []

    def store(self, embedding, content):
        self.index.add(np.array([embedding]).astype('float32'))
        self.vectors.append(embedding)
        self.metadata.append({
            'timestamp': str(datetime.datetime.now()),
            'content': content
        })

    def query(self, embedding, top_k=5):
        D, I = self.index.search(np.array([embedding]).astype('float32'), top_k)
        return [self.metadata[i] for i in I[0]]