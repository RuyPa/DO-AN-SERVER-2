from flask import Blueprint, jsonify

from services.auth_service import role_required
from db import get_db_connection


stat_routes = Blueprint('stat_routes', __name__)

@stat_routes.route('/api/stats/category_stats', methods=['GET'])
@role_required('admin', 'user')  
def category_stats():
    query = """
    SELECT 
        c.name AS traffic_sign_type, 
        COUNT(ts.id) AS num_traffic_signs
    FROM 
        tbl_category c
    JOIN 
        tbl_traffic_sign ts ON c.id = ts.category_id
    GROUP BY 
        c.name
    ORDER BY 
        num_traffic_signs DESC;
    """

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()

    return jsonify(result)

@stat_routes.route('/api/stats/category_sample_label_stats', methods=['GET'])
@role_required('admin', 'user')  
def category_sample_label_stats():
    query = """
    SELECT 
        c.name AS traffic_sign_type, 
        COUNT(DISTINCT s.id) AS num_samples, 
        COUNT(DISTINCT l.id) AS num_labels
    FROM 
        tbl_category c
    JOIN 
        tbl_traffic_sign ts ON c.id = ts.category_id
    JOIN 
        tbl_label l ON ts.id = l.traffic_sign_id
    JOIN 
        tbl_sample s ON l.sample_id = s.id
    GROUP BY 
        c.name
    ORDER BY 
        c.name;
    """

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()

    return jsonify(result)

@stat_routes.route('/api/stats/sign_sample_label_stats', methods=['GET'])
@role_required('admin', 'user')  
def sign_sample_label_stats():
    query = """
    SELECT 
        ts.name AS traffic_sign, 
        COUNT(DISTINCT s.id) AS num_samples, 
        COUNT(DISTINCT l.id) AS num_labels
    FROM 
        tbl_traffic_sign ts
    JOIN 
        tbl_label l ON ts.id = l.traffic_sign_id
    JOIN 
        tbl_sample s ON l.sample_id = s.id
    GROUP BY 
        ts.name
    ORDER BY 
        ts.name;
    """

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()

    return jsonify(result)