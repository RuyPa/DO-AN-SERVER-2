from db import get_db_connection
from models.category import Category
from models.search import SearchParams
from models.traffic_sign import TrafficSign

def create_tables():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tbl_traffic_sign (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            code VARCHAR(50) NOT NULL,
            description TEXT,
            path VARCHAR(255)
        )
    ''')
    connection.commit()
    cursor.close()
    connection.close()

def get_all_signs():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM tbl_traffic_sign')
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return [TrafficSign.from_row(row) for row in rows]

def get_sign_by_id(sign_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM tbl_traffic_sign WHERE id = %s', (sign_id,))
    row = cursor.fetchone()
    category = get_category_by_id(row['category_id'])

    cursor.close()
    connection.close()
    return TrafficSign.from_row(row, category=category) if row else None

def add_sign(sign: TrafficSign):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('INSERT INTO tbl_traffic_sign (name, code, description, path, created_by, created_date, category_id) VALUES (%s, %s, %s, %s, %s, NOW(), %s)',
                   (sign.name, sign.code, sign.description, sign.path, sign.create_by, sign.category.id))
    connection.commit()
    cursor.close()
    connection.close()

def update_sign(sign: TrafficSign):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('UPDATE tbl_traffic_sign SET name = %s, code = %s, description = %s, path = %s, category_id = %s WHERE id = %s',
                   (sign.name, sign.code, sign.description, sign.path, sign.category.id, sign.id))
    connection.commit()
    cursor.close()
    connection.close()

def delete_sign(sign_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('DELETE FROM tbl_traffic_sign WHERE id = %s', (sign_id,))
    connection.commit()
    cursor.close()
    connection.close()


# def search_signs(search_params: SearchParams):
#     connection = get_db_connection()
#     cursor = connection.cursor(dictionary=True)

#     # Base SQL query
#     query = "SELECT SQL_CALC_FOUND_ROWS * FROM tbl_traffic_sign"
#     params = []

#     # Add filtering condition if keyword is provided
#     if search_params.keyword:
#         query += " WHERE name LIKE %s OR description LIKE %s"
#         keyword = f"%{search_params.keyword}%"
#         params.extend([keyword, keyword])

#     # Add pagination
#     query += " LIMIT %s OFFSET %s"
#     params.extend([search_params.page_size, search_params.offset])

#     cursor.execute(query, params)
#     rows = cursor.fetchall()

#     # Get total count of items
#     cursor.execute("SELECT FOUND_ROWS()")
#     total = cursor.fetchone()['FOUND_ROWS()']

#     cursor.close()
#     connection.close()

#     # Return the paginated data and total count
#     return [TrafficSign.from_row(row) for row in rows], total

def search_signs(search_params: SearchParams):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Base SQL query
    query = "SELECT SQL_CALC_FOUND_ROWS * FROM tbl_traffic_sign"
    params = []

    # Add filtering condition if keyword is provided
    if search_params.keyword:
        query += " WHERE (name LIKE %s OR description LIKE %s)"
        keyword = f"%{search_params.keyword}%"
        params.extend([keyword, keyword])

    # Add filtering condition if category_id is provided
    if search_params.category_id:
        if search_params.keyword:  # If there is already a keyword filter, add AND
            query += " AND category_id = %s"
        else:
            query += " WHERE category_id = %s"
        params.append(search_params.category_id)

    # Add pagination
    query += " LIMIT %s OFFSET %s"
    params.extend([search_params.page_size, search_params.offset])

    cursor.execute(query, params)
    rows = cursor.fetchall()

    # Get total count of items
    cursor.execute("SELECT FOUND_ROWS()")
    total = cursor.fetchone()['FOUND_ROWS()']

    cursor.close()

    # Thêm thông tin category vào từng traffic sign
    result = []
    for row in rows:
        # Lấy category tương ứng với category_id của mỗi traffic sign
        category = get_category_by_id(row['category_id'])
        
        # Tạo đối tượng TrafficSign với category
        traffic_sign = TrafficSign.from_row(row, category=category)
        
        # Thêm vào danh sách kết quả
        result.append(traffic_sign)

    # Đóng kết nối sau khi hoàn thành
    connection.close()

    # Trả về danh sách traffic signs đã có category và tổng số lượng
    return result, total

def get_all_categories():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM tbl_category')
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return [Category.from_row(row) for row in rows]


def get_category_by_id(category_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM tbl_category WHERE id = %s', (category_id,))
    row = cursor.fetchone()
    cursor.close()
    connection.close()
    if row:
        return Category.from_row(row)
    else:
        return None


def get_owner_by_id(sign_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT tf.created_by FROM tbl_traffic_sign tf WHERE tf.id = %s', (sign_id,))
    row = cursor.fetchone()
    cursor.close()
    connection.close()
    
    if row:
        return row['created_by']
    else:
        return None  

def get_path_by_id(sign_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT tf.path FROM tbl_traffic_sign tf WHERE tf.id = %s', (sign_id,))
    row = cursor.fetchone()
    cursor.close()
    connection.close()
    
    if row:
        return row['path']
    else:
        return None  