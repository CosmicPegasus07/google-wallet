def execute_query(sql_query: str):
    """
    Function to execute the sqlite query and provide realtime data.
    Args:
        sql_query(str): Sqlite3 compatible sql query to execute against database and retrieve results

    Returns:
        Results fetched from database
    """
    import sqlite3
    import os

    # Get the database path relative to the project root
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'database', 'mock_finance.db')
    conn = sqlite3.connect(db_path)
    print(f"SQL QUERY RECEIVED ----------------- {sql_query} -----------------------")
    cursor = conn.cursor()

    cursor.execute(sql_query)

    results = cursor.fetchall()
    conn.close()

    return results


# 