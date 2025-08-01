
import os
import sqlite3

# Get the base path for the database from environment variable


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

    db_path = os.path.join(os.path.dirname(__file__), '..', 'mock_finance.db')
    db_path = os.path.abspath(db_path)  # Convert to absolute path
    conn = sqlite3.connect(db_path)
    print(f"SQL QUERY RECEIVED ----------------- {sql_query} -----------------------")
    cursor = conn.cursor()

    cursor.execute(sql_query)

    # Commit for INSERT, UPDATE, DELETE operations
    if sql_query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
        conn.commit()

    results = cursor.fetchall()
    conn.close()

    return results


# def execute_query(sql_query:str):
#     """
#     Function to execute the sqlite query and provide realtime data.
#     Args:
#         sql_query(str): Sqlite3 compatible sql query to execute against database and retreive results

#     Returns:
#         Results fetched from database
#     """
#     import sqlite3
#     conn = sqlite3.connect(f'{base_path}/mock_finance.db')
#     print(f"SQL QUERY RECEIVED ----------------- {sql_query} -----------------------")
#     cursor = conn.cursor()
#     cursor.execute(sql_query)
#     results = cursor.fetchall()
#     conn.close()
#     print(results)
#     return results

def execute_query_fetch(sql_query: str):
    """
    Function to execute the sqlite query and provide realtime data.
    Args:
        sql_query(str): Sqlite3 compatible sql query to execute against database and retreive results

    Returns:
        Results fetched from database
    """
    db_path = os.path.join(os.path.dirname(__file__), '..', 'mock_finance.db')
    db_path = os.path.abspath(db_path)  # Convert to absolute path
    conn = sqlite3.connect(db_path)
    
    # Ensure the query always filters for USER_ID=10 for security
    sql_query_upper = sql_query.upper()
    
    # Check if query already has USER_ID=10 filter
    if 'USER_ID=10' in sql_query_upper:
        # Query already has USER_ID=10 filter, proceed as is
        pass
    elif 'WHERE' not in sql_query_upper:
        # No WHERE clause exists, need to add user_id filter
        # First, check if the main table has user_id column
        if any(table in sql_query_upper for table in ['USERS', 'TASKS', 'USER_GROUPS', 'USER_SUBSCRIPTIONS', 'EXPENSE_SHARES']):
            # These tables have direct user_id column
            if sql_query.strip().endswith(';'):
                sql_query = sql_query[:-1] + ' WHERE USER_ID=10;'
            else:
                sql_query = sql_query + ' WHERE USER_ID=10'
        elif 'EXPENSES' in sql_query_upper:
            # Expenses table uses payer_id instead of user_id
            if sql_query.strip().endswith(';'):
                sql_query = sql_query[:-1] + ' WHERE payer_id=1;'
            else:
                sql_query = sql_query + ' WHERE payer_id=1'
        elif 'GROUPS' in sql_query_upper:
            # Groups table uses created_by instead of user_id
            if sql_query.strip().endswith(';'):
                sql_query = sql_query[:-1] + ' WHERE created_by=1;'
            else:
                sql_query = sql_query + ' WHERE created_by=1'
        elif any(table in sql_query_upper for table in ['FREQUENT_ITEMS', 'EXPENSE_RECEIPTS', 'EXPENSE_ITEMS']):
            # These tables don't have user_id, need to JOIN with related tables
            if 'FREQUENT_ITEMS' in sql_query_upper:
                # Join with user_subscriptions to filter by user_id
                if 'FROM FREQUENT_ITEMS' in sql_query_upper:
                    sql_query = sql_query.replace('FROM frequent_items', 'FROM frequent_items fi JOIN user_subscriptions us ON fi.item_id = us.item_id')
                    if sql_query.strip().endswith(';'):
                        sql_query = sql_query[:-1] + ' WHERE us.USER_ID=10;'
                    else:
                        sql_query = sql_query + ' WHERE us.USER_ID=10'
            elif 'EXPENSE_RECEIPTS' in sql_query_upper:
                # Join with expenses to filter by payer_id
                if 'FROM EXPENSE_RECEIPTS' in sql_query_upper:
                    sql_query = sql_query.replace('FROM expense_receipts', 'FROM expense_receipts er JOIN expenses e ON er.expense_id = e.expense_id')
                    if sql_query.strip().endswith(';'):
                        sql_query = sql_query[:-1] + ' WHERE e.payer_id=1;'
                    else:
                        sql_query = sql_query + ' WHERE e.payer_id=1'
            elif 'EXPENSE_ITEMS' in sql_query_upper:
                # Join with expenses to filter by payer_id
                if 'FROM EXPENSE_ITEMS' in sql_query_upper:
                    sql_query = sql_query.replace('FROM expense_items', 'FROM expense_items ei JOIN expenses e ON ei.expense_id = e.expense_id')
                    if sql_query.strip().endswith(';'):
                        sql_query = sql_query[:-1] + ' WHERE e.payer_id=1;'
                    else:
                        sql_query = sql_query + ' WHERE e.payer_id=1'
        else:
            # Unknown table, add generic USER_ID=10 filter (may not work for all cases)
            if sql_query.strip().endswith(';'):
                sql_query = sql_query[:-1] + ' WHERE USER_ID=10;'
            else:
                sql_query = sql_query + ' WHERE USER_ID=10'
    else:
        # WHERE clause exists, add user_id filter to it
        if any(table in sql_query_upper for table in ['USERS', 'TASKS', 'USER_GROUPS', 'USER_SUBSCRIPTIONS', 'EXPENSE_SHARES']):
            # These tables have direct user_id column
            if 'USER_ID=10' not in sql_query_upper:
                where_pos = sql_query_upper.find('WHERE')
                sql_query = sql_query[:where_pos+5] + ' USER_ID=10 AND ' + sql_query[where_pos+5:]
        elif 'EXPENSES' in sql_query_upper:
            # Expenses table uses payer_id instead of user_id
            if 'PAYER_ID=1' not in sql_query_upper:
                where_pos = sql_query_upper.find('WHERE')
                sql_query = sql_query[:where_pos+5] + ' payer_id=1 AND ' + sql_query[where_pos+5:]
        elif 'GROUPS' in sql_query_upper:
            # Groups table uses created_by instead of user_id
            if 'CREATED_BY=1' not in sql_query_upper:
                where_pos = sql_query_upper.find('WHERE')
                sql_query = sql_query[:where_pos+5] + ' created_by=1 AND ' + sql_query[where_pos+5:]
        elif any(table in sql_query_upper for table in ['FREQUENT_ITEMS', 'EXPENSE_RECEIPTS', 'EXPENSE_ITEMS']):
            # These tables need JOINs to filter by user_id
            if 'FREQUENT_ITEMS' in sql_query_upper and 'USER_SUBSCRIPTIONS' not in sql_query_upper:
                # Add JOIN for frequent_items
                sql_query = sql_query.replace('FROM frequent_items', 'FROM frequent_items fi JOIN user_subscriptions us ON fi.item_id = us.item_id')
                if 'US.USER_ID=10' not in sql_query_upper:
                    where_pos = sql_query_upper.find('WHERE')
                    sql_query = sql_query[:where_pos+5] + ' us.USER_ID=10 AND ' + sql_query[where_pos+5:]
            elif 'EXPENSE_RECEIPTS' in sql_query_upper and 'EXPENSES' not in sql_query_upper:
                # Add JOIN for expense_receipts
                sql_query = sql_query.replace('FROM expense_receipts', 'FROM expense_receipts er JOIN expenses e ON er.expense_id = e.expense_id')
                if 'E.PAYER_ID=1' not in sql_query_upper:
                    where_pos = sql_query_upper.find('WHERE')
                    sql_query = sql_query[:where_pos+5] + ' e.payer_id=1 AND ' + sql_query[where_pos+5:]
            elif 'EXPENSE_ITEMS' in sql_query_upper and 'EXPENSES' not in sql_query_upper:
                # Add JOIN for expense_items
                sql_query = sql_query.replace('FROM expense_items', 'FROM expense_items ei JOIN expenses e ON ei.expense_id = e.expense_id')
                if 'E.PAYER_ID=1' not in sql_query_upper:
                    where_pos = sql_query_upper.find('WHERE')
                    sql_query = sql_query[:where_pos+5] + ' e.payer_id=1 AND ' + sql_query[where_pos+5:]
        else:
            # Unknown table, add generic USER_ID=10 filter
            if 'USER_ID=10' not in sql_query_upper:
                where_pos = sql_query_upper.find('WHERE')
                sql_query = sql_query[:where_pos+5] + ' USER_ID=10 AND ' + sql_query[where_pos+5:]
    
    print(f"SQL QUERY RECEIVED ----------------- {sql_query} -----------------------")
    cursor = conn.cursor()
    cursor.execute(sql_query)
    results = cursor.fetchall()
    conn.close()
    print(results)
    return results

# def create_expense_record(it)