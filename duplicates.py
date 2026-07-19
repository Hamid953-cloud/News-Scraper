"""
Duplicate/Related Story Detection.
Finds articles from DIFFERENT sources that are likely covering the SAME
news event, by comparing headline word overlap (no external NLP library needed).
"""

import re

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "is", "are", "was", "were", "be", "been", "as", "by",
    "it", "this", "that", "from", "after", "over", "new", "says", "say",
}


def normalize_title(title: str) -> set:
    """Turn a headline into a set of meaningful lowercase words."""
    words = re.findall(r"[a-z']+", title.lower())
    return {w for w in words if w not in STOPWORDS and len(w) > 2}


def similarity(words_a: set, words_b: set) -> float:
    """Jaccard similarity: overlap size / union size, between 0 and 1."""
    if not words_a or not words_b:
        return 0.0
    intersection = len(words_a & words_b)
    union = len(words_a | words_b)
    return intersection / union


def find_related_stories(articles: list[dict], threshold: float = 0.35, limit: int = 150) -> list[list[dict]]:
    """
    Group articles from DIFFERENT sources that likely cover the same event.
    Returns a list of clusters (each cluster is a list of 2+ related articles).

    `limit` caps how many recent articles we compare (comparing every
    article against every other is O(n^2), fine for ~100-200 articles).
    """
    recent = articles[:limit]
    word_sets = [normalize_title(a["title"]) for a in recent]

    used = set()
    clusters = []

    for i in range(len(recent)):
        if i in used:
            continue
        cluster = [recent[i]]
        cluster_sources = {recent[i]["source"]}

        for j in range(i + 1, len(recent)):
            if j in used:
                continue
            # Only match articles from a DIFFERENT source (that's the point:
            # same story, different outlet) with a title similar enough.
            if recent[j]["source"] in cluster_sources:
                continue
            score = similarity(word_sets[i], word_sets[j])
            if score >= threshold:
                cluster.append(recent[j])
                cluster_sources.add(recent[j]["source"])
                used.add(j)

        if len(cluster) > 1:
            used.add(i)
            clusters.append(cluster)

    return clusters
