from pathlib import Path
import psycopg2

# Connect to PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    port=5433,
    database="ragdb",
    user="postgres",
    password="postgres"
)

cursor = conn.cursor()

# Find all sample.md files
md_files = list(Path("data").rglob("sample.md"))

print(f"Found {len(md_files)} markdown files.\n")

for md_file in md_files:

    title = md_file.parent.name

    cursor.execute(
        """
        INSERT INTO document (title, source, organization)
        VALUES (%s, %s, %s)
        RETURNING id;
        """,
        (
            title,
            "eProcurement",
            "NHIDCL"
        )
    )

    document_id = cursor.fetchone()[0]

    print(f"Inserted Document ID {document_id}: {title}")

conn.commit()

cursor.close()
conn.close()

print("\nDone!")