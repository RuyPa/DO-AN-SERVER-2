from db import get_db_connection

from models.search import SearchParams
from services.auth_service import User
from extension import bcrypt


def add_user(username, password, role='user'):
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)', (username, password_hash, role))
    connection.commit()
    cursor.close()
    connection.close()


def search_users(search_params: SearchParams):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Base SQL query
    query = "SELECT SQL_CALC_FOUND_ROWS * FROM tbl_user"
    params = []

    # Add filtering condition if keyword is provided
    if search_params.keyword:
        query += " WHERE name LIKE %s OR email LIKE %s OR address LIKE %s "
        keyword = f"%{search_params.keyword}%"
        params.extend([keyword, keyword])

    # Add pagination
    query += " LIMIT %s OFFSET %s"
    params.extend([search_params.page_size, search_params.offset])

    cursor.execute(query, params)
    rows = cursor.fetchall()

    # Get total count of items
    cursor.execute("SELECT FOUND_ROWS()")
    total = cursor.fetchone()['FOUND_ROWS()']

    cursor.close()
    connection.close()

    # Return the paginated data and total count
    return [User.from_row(row) for row in rows], total
