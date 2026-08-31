import os
import pickle
import numpy as np

from sklearn.neighbors import NearestNeighbors


# File where facial embeddings will be stored
EMBEDDINGS_FILE = "database/embeddings.pkl"


def load_embeddings():
    """
    Load all registered facial embeddings.
    """

    if not os.path.exists(EMBEDDINGS_FILE):
        return {}

    try:
        with open(EMBEDDINGS_FILE, "rb") as file:
            return pickle.load(file)

    except Exception:
        return {}


def save_embeddings(embeddings):
    """
    Save facial embeddings to disk.
    """

    os.makedirs(
        "database",
        exist_ok=True
    )

    with open(
        EMBEDDINGS_FILE,
        "wb"
    ) as file:

        pickle.dump(
            embeddings,
            file
        )


def add_embedding(child_id, embedding):
    """
    Add a new child's facial embedding
    to the embedding database.
    """

    database = load_embeddings()

    database[child_id] = np.asarray(
        embedding,
        dtype=np.float32
    )

    save_embeddings(database)


def find_matches(query_embedding, top_k=5):
    """
    Find the closest registered faces using
    KNN with cosine distance.
    """

    database = load_embeddings()

    if not database:
        return []

    child_ids = list(database.keys())

    embeddings = np.array(
        [
            database[child_id]
            for child_id in child_ids
        ],
        dtype=np.float32
    )

    query_embedding = np.asarray(
        query_embedding,
        dtype=np.float32
    )

    # Normalize database embeddings
    embedding_norms = np.linalg.norm(
        embeddings,
        axis=1,
        keepdims=True
    )

    embedding_norms[
        embedding_norms == 0
    ] = 1

    normalized_embeddings = (
        embeddings / embedding_norms
    )

    # Normalize query embedding
    query_norm = np.linalg.norm(
        query_embedding
    )

    if query_norm == 0:
        return []

    normalized_query = (
        query_embedding / query_norm
    )

    # KNN using cosine distance
    number_of_neighbors = min(
        top_k,
        len(normalized_embeddings)
    )

    knn = NearestNeighbors(
        n_neighbors=number_of_neighbors,
        metric="cosine"
    )

    knn.fit(
        normalized_embeddings
    )

    distances, indices = knn.kneighbors(
        normalized_query.reshape(1, -1)
    )

    results = []

    for distance, index in zip(
        distances[0],
        indices[0]
    ):

        similarity = 1 - float(distance)

        results.append(
            {
                "id": child_ids[index],
                "similarity": similarity
            }
        )

    return results