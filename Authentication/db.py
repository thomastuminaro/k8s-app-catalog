import sqlite3
from pathlib import Path

DB_FILE = Path(__file__).parent / "users.db"

conn = sqlite3.connect(DB_FILE)
c = conn.cursor()

c.execute("""
          CREATE TABLE IF NOT EXISTS users(
            username text,
            password text,
            role text
          )
          """)

test_users = (
    {"username": "admin", "password": "admin", "role": "admin"},
    {"username": "dev", "password": "dev", "role": "dev"}
)

c.executemany("INSERT INTO users VALUES(:username, :password, :role)", test_users)

c.execute("SELECT * FROM users")
print(c.fetchall())

c.close()