import json
from pathlib import Path
import psycopg2

# -------------------------------
# PostgreSQL Connection
# -------------------------------

conn = psycopg2.connect(
    host="127.0.0.1",
    port=5433,
    database="ragdb",
    user="postgres",
    password="postgres"
)

cursor = conn.cursor()

DATA_FOLDER = Path("data")

# ---------------------------------
# Process every tender
# ---------------------------------

for tender in sorted(DATA_FOLDER.iterdir()):

    if not tender.is_dir():
        continue

    json_file = tender / "parent_child.json"

    if not json_file.exists():
        continue

    print(f"\nProcessing {tender.name}")

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # --------------------------
    # Find document_id
    # --------------------------

    document_name = tender.name

    cursor.execute(
        """
        SELECT id
        FROM document
        WHERE title = %s;
        """,
        (document_name,)
    )

    result = cursor.fetchone()

    if result is None:
        print(f"Document '{document_name}' not found.")
        continue

    document_id = result[0]

    # --------------------------
    # Insert Parents
    # --------------------------

    for parent in data["parents"]:

        cursor.execute(
            """
            INSERT INTO parent
            (
                document_id,
                heading,
                content,
                page_start,
                page_end
            )
            VALUES (%s,%s,%s,%s,%s)
            RETURNING id;
            """,
            (
                document_id,
                parent["title"],
                parent["text"],
                parent["page_start"],
                parent["page_end"]
            )
        )

        parent_db_id = cursor.fetchone()[0]

        # --------------------------
        # Insert Children
        # --------------------------

        for child in parent["children"]:

            cursor.execute(
                """
                INSERT INTO child
                (
                    parent_id,
                    chunk_index,
                    page_start,
                    page_end,
                    word_count,
                    chunk_text
                )
                VALUES (%s,%s,%s,%s,%s,%s);
                """,
                (
                    parent_db_id,
                    child["chunk_index"],
                    child["page_start"],
                    child["page_end"],
                    child["word_count"],
                    child["text"]
                )
            )

conn.commit()

cursor.close()
conn.close()

print("\nAll parent-child data inserted successfully.")