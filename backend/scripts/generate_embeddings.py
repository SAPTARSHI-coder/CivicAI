from sentence_transformers import SentenceTransformer
import psycopg2
from pgvector.psycopg2 import register_vector

# -------------------------------
# Load embedding model
# -------------------------------

print("Loading embedding model...")
model = SentenceTransformer("BAAI/bge-small-en-v1.5")

# -------------------------------
# PostgreSQL Connection
# -------------------------------

conn = psycopg2.connect(
    host="localhost",
    port=5433,
    database="ragdb",
    user="postgres",
    password="postgres"
)

register_vector(conn)

cursor = conn.cursor()

# -------------------------------
# Read all child chunks
# -------------------------------

cursor.execute("""
SELECT id, chunk_text
FROM child;
""")

rows = cursor.fetchall()

print(f"Found {len(rows)} chunks")

# -------------------------------
# Generate embeddings
# -------------------------------

for chunk_id, chunk_text in rows:

    embedding = model.encode(
        chunk_text,
        normalize_embeddings=True
    ).tolist()

    cursor.execute(
        """
        UPDATE child
        SET embedding = %s
        WHERE id = %s;
        """,
        (embedding, chunk_id)
    )

    print(f"Embedded chunk {chunk_id}")

conn.commit()

cursor.close()
conn.close()

print("\nAll embeddings generated successfully!")