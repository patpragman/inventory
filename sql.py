import sqlite3


def query_database(sql_query: str, database_path: str) -> list:
    # this function connects to the specified database
    # then it executes the query, then in returns the rows as a list

    conn = sqlite3.connect(database_path)  # connect
    cur = conn.cursor()
    cur.execute(sql_query)  # execute the query
    rows = cur.fetchall()  # get all the rows
    conn.close()

    return rows  # send them back to the user