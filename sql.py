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


def clear_rows_of(table: str, database_path: str) -> None:
    try:
        # this will clear all the stuff from whatever table you specify
        statement = """DELETE from """ + str(table) + ";"
        conn = sqlite3.connect(database_path)
        cur = conn.cursor()
        cur.execute(statement)
        conn.commit()
    except Exception as err:
        print("Error processing SQL in clear_rows_of function")
        print(err)