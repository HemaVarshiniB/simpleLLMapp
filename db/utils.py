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
    
def get_messages(session_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM MESSAGES WHERE session_id=%s;", (session_id,),)
    rows = cursor.fetchall()
    messages = [{"role": row[2], "content": row[3]} for row in rows]
    cursor.close()
    connection.close()
    return messages
    
def get_all_sessions():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM SESSIONS;")
    sessions = cursor.fetchall()
    cursor.close()
    connection.close()
    return sessions