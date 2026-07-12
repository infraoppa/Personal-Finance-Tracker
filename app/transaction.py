from app.database import get_connection
from datetime import date

def add_transaction(amount,category,description,transaction_date):
    conn = get_connection()
    cursor = conn.cursor()
    transaction_date = date.isoformat()
    cursor.execute("""
    INSERT INTO transactions(
    amount, category, description, transaction_date) VALUES (?,?,?,?)"""
    ,(amount,category,description,transaction_date))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id

def get_transaction(transaction_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM transactions WHERE id =?""",(transaction_id,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    return dict(row)

def get_transactions():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM transactions ORDER BY transaction_date DESC, id DESC""")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

