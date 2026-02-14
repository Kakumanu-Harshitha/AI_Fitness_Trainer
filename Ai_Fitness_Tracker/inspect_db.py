import sqlite3
import os

db_path = os.path.join(os.getcwd(), 'fitness_v3.db')
print(f"Checking database at: {db_path}")

if not os.path.exists(db_path):
    print("Database file not found!")
else:
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables: {tables}")
        
        if ('users',) in tables:
            cursor.execute("SELECT id, username, email FROM users;")
            users = cursor.fetchall()
            print(f"Users found: {len(users)}")
            for user in users:
                print(f"  - ID: {user[0]}, Username: {user[1]}, Email: {user[2]}")
        else:
            print("Table 'users' does not exist.")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
