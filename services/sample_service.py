from flask_jwt_extended import get_jwt_identity
from db import get_db_connection
from models.sample import Sample
from models.search import SearchParams
from services.label_service import create_label, get_labels_by_sample_id

def update_sample_path(sample: Sample):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Chỉ cập nhật trường path cho sample
        cursor.execute('''
            UPDATE tbl_sample
            SET path = %s
            WHERE name = %s
        ''', (sample.path, sample.name))

        connection.commit()

    except Exception as e:
        connection.rollback()
        print(f"Error while updating sample path: {str(e)}")
    
    finally:
        cursor.close()
        connection.close()

def get_sample_by_name(name: str):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)  # Dùng dictionary=True để lấy kết quả dưới dạng từ điển

    try:
        # Thực thi câu lệnh SQL để tìm Sample theo tên ảnh
        cursor.execute('''
            SELECT * FROM tbl_sample
            WHERE name = %s
        ''', (name,))

        # Lấy kết quả trả về
        row = cursor.fetchone()  # Dùng fetchone để lấy một kết quả duy nhất

        if row:
            # Chuyển đổi kết quả thành đối tượng Sample
            sample = Sample.from_row(row)
            return sample
        else:
            return None

    except Exception as e:
        print(f"Error while fetching sample: {str(e)}")
        return None
    
    finally:
        cursor.close()
        connection.close()


def create_sample_table():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tbl_sample (
            id INT AUTO_INCREMENT PRIMARY KEY,
            code VARCHAR(100) NOT NULL,
            path VARCHAR(200),
            name VARCHAR(100)
        )
    ''')
    connection.commit()
    cursor.close()
    connection.close()

def get_all_samples():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM tbl_sample')
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return [Sample.from_row(row) for row in rows]

# def get_sample_by_id(sample_id):
#     connection = get_db_connection()
#     cursor = connection.cursor(dictionary=True)
#     cursor.execute('SELECT * FROM tbl_sample WHERE id = %s', (sample_id,))
#     row = cursor.fetchone()
#     cursor.close()
#     connection.close()
#     return Sample.from_row(row) if row else None

def get_sample_by_id(sample_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM tbl_sample WHERE id = %s', (sample_id,))
    row = cursor.fetchone()
    cursor.close()
    connection.close()

    if row:
        labels = get_labels_by_sample_id(sample_id)
        return Sample.from_row(row, labels=labels)
    return None

def add_sample(sample: Sample):
    connection = get_db_connection()
    cursor = connection.cursor()
    current_user = get_jwt_identity()  
    current_user_email = current_user.get('email') 
    try:
        cursor.execute('INSERT INTO tbl_sample (code, path, name, created_by, created_date) VALUES (%s, %s, %s, %s, NOW())',
                    (sample.code, sample.path, sample.name, sample.created_by))

        sample_id = cursor.lastrowid
        if sample.labels:
            for label in sample.labels:
                label.sample_id = sample_id
                cursor.execute('''
                    INSERT INTO tbl_label (centerX, centerY, height, width, sample_id, traffic_sign_id, created_by, created_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                ''', (label.centerX, label.centerY, label.height, label.width, label.sample_id, label.traffic_sign.id, current_user_email))        
                # create_label(label)
        connection.commit()
    
    except Exception as e:
        connection.rollback()
    
    finally:
        cursor.close()
        connection.close()

def update_sample(sample_id, code=None, path=None, name=None):
    connection = get_db_connection()
    cursor = connection.cursor()

    # Xây dựng query động dựa trên các trường có giá trị
    query_parts = []
    params = []

    if code is not None:
        query_parts.append("code = %s")
        params.append(code)
    
    if path is not None:
        query_parts.append("path = %s")
        params.append(path)
    
    if name is not None:
        query_parts.append("name = %s")
        params.append(name)

    # Nếu không có gì để cập nhật thì không thực hiện truy vấn
    if not query_parts:
        return

    # Xây dựng câu lệnh SQL
    query = "UPDATE tbl_sample SET " + ", ".join(query_parts) + " WHERE id = %s"
    params.append(sample_id)

    # Thực hiện truy vấn
    cursor.execute(query, tuple(params))
    connection.commit()

    cursor.close()
    connection.close()


def delete_sample(sample_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('DELETE FROM tbl_sample WHERE id = %s', (sample_id,))
    connection.commit()
    cursor.close()
    connection.close()


def delete_sample(sample_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('DELETE FROM tbl_sample WHERE id = %s', (sample_id,))
    connection.commit()
    cursor.close()
    connection.close()


# def search_samples_in_db(search_params: SearchParams):
#     connection = get_db_connection()
#     cursor = connection.cursor(dictionary=True)

#     # Base SQL query
#     query = """
#     SELECT SQL_CALC_FOUND_ROWS s.*
#     FROM tbl_sample s
#     JOIN tbl_label l ON l.sample_id = s.id
#     JOIN tbl_traffic_sign ts ON ts.id = l.traffic_sign_id
#     """
#     params = []

#     # Add filtering condition if keyword is provided
#     if search_params.keyword:
#         query += " WHERE (s.code LIKE %s OR s.name LIKE %s)"
#         keyword = f"%{search_params.keyword}%"
#         params.extend([keyword, keyword])

#     # Add filtering condition if category_id is provided
#     if search_params.category_id:
#         if search_params.keyword:  # If there is already a keyword filter, add AND
#             query += " AND ts.category_id = %s"
#         else:
#             query += " WHERE ts.category_id = %s"
#         params.append(search_params.category_id)

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
#     return [Sample.from_row(row) for row in rows], total

def search_samples_in_db(search_params: SearchParams):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Base SQL query
    query = """
    SELECT SQL_CALC_FOUND_ROWS DISTINCT s.*
    FROM tbl_sample s
    JOIN tbl_label l ON l.sample_id = s.id
    JOIN tbl_traffic_sign ts ON ts.id = l.traffic_sign_id
    """
    params = []

    # Add filtering condition if keyword is provided
    if search_params.keyword:
        query += " WHERE (s.code LIKE %s OR s.name LIKE %s)"
        keyword = f"%{search_params.keyword}%"
        params.extend([keyword, keyword])

    # Add filtering condition if category_id is provided
    if search_params.category_id:
        if search_params.keyword:  # If there is already a keyword filter, add AND
            query += " AND ts.category_id = %s"
        else:
            query += " WHERE ts.category_id = %s"
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
    connection.close()

    # Return the paginated data and total count
    return [Sample.from_row(row) for row in rows], total