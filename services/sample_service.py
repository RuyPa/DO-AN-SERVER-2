from db import get_db_connection
from models.sample import Sample
from services.label_service import create_label, get_labels_by_sample_id

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

    try:
        cursor.execute('INSERT INTO tbl_sample (code, path, name) VALUES (%s, %s, %s)',
                       (sample.code, sample.path, sample.name))
        sample_id = cursor.lastrowid
        print(f"Sample created with ID: {sample_id}") 
        
        if sample.labels:
            for label in sample.labels:
                label.sample_id = sample_id
                cursor.execute('''
                    INSERT INTO tbl_label (centerX, centerY, height, width, sample_id, traffic_sign_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (label.centerX, label.centerY, label.height, label.width, label.sample_id, label.traffic_sign.id))        
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
