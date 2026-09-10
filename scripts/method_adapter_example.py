"""Minimal word-overlap integration example, not a paper baseline."""
import re


class Retriever:
    def __init__(self, candidates):
        self.documents = [(r['candidate_id'], set(re.findall(r'\w+', r['text'].lower())))
                          for r in candidates]

    def rank(self, query, k):
        words = set(re.findall(r'\w+', query.lower()))
        scores = [(cid, float(len(words & tokens))) for cid, tokens in self.documents]
        return sorted(scores, key=lambda item: (-item[1], item[0]))[:k]
