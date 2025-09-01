import sqlite3 as sq

conn = sq.connect("database.db")
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        task TEXT NOT NULL,
        FOREIGN KEY (username) REFERENCES users (username)
    )
''')

#Example User
username = 'skyy4y'
password = '123'

try:
    c.execute('''
        INSERT INTO users (username, password)
        VALUES (?, ?)
    ''', (username, password))

    conn.commit()
except sq.IntegrityError:
    print("User already exists"), 400

#Example task
task = 'Task 2'

try:
    c.execute('''
        INSERT INTO tasks (username, task)
        VALUES (?, ?)
    ''', (username, task))

    conn.commit()
except:
    print("System Error!"), 400