import sqlite3

connection = sqlite3.connect("users.db")

cursor = connection.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        is_free INTEGER DEFAULT 0,
        free_compressions INTEGER DEFAULT 5,
        paid_compressions INTEGER DEFAULT 0,
        total_compressions INTEGER DEFAULT 0
    )
''')
connection.commit()
connection.close()

def add_user(user_id):
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id) VALUES (?)
    ''', (user_id,))
    connection.commit()
    connection.close()

def get_user(user_id):
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    
    cursor.execute('''
        SELECT * FROM users 
        WHERE user_id = ?
    ''', (user_id,)
    )
    user = cursor.fetchone()
    connection.close()
    return user

def can_compress(user_id):
    user = get_user(user_id)

    if user is None:
        add_user(user_id)
        user = get_user(user_id)
        
    if user[1] == 1:
        return True
    elif user[2] > 0:
        return True
    elif user[3] > 0:
        return True
    else:
        return False
