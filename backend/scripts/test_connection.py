import psycopg2

print("psycopg2 version:", psycopg2.__version__)

try:
    conn = psycopg2.connect(
        host="127.0.0.1",
        port=5433,
        database="ragdb",
        user="postgres",
        password="postgres"
    )

    print("✅ Connected successfully!")

    conn.close()

except Exception as e:
    print("❌ Connection failed")
    print(type(e))
    print(e)