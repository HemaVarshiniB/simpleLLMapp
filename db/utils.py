from db.databaseFile import get_connection

def get_db_connection():
    return get_connection()

def create_newChat():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO SESSIONS(CREATED_AT, UPDATED_AT) VALUES (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) RETURNING session_id;")
    chat_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return chat_id


def insert_messages(session_id: int, role:str, content: str):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO MESSAGES (session_id, role, content, created_at) VALUES (%s, %s, %s, CURRENT_TIMESTAMP);", (session_id, role, content))
    connection.commit()
    cursor.close()
    connection.close()