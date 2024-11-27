import re
import bcrypt
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from flask_login import login_required, current_user
from db import add_user, save_update_user
from models.search import SearchParams
from services.auth_service import User, role_required
from extension import cache
from const import CACHE_TTL
from services.user_service import search_users

from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

user_bp = Blueprint('user', __name__)

@user_bp.route('/api/users', methods=['POST'])
@role_required('admin')
def add_user_route():
    # Lấy thông tin người dùng từ token
    current_user = get_jwt_identity()  
    current_user_email = current_user.get('email') 

    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    address = data.get('address')
    role = data.get('role', 'user') 
    created_by = current_user_email
    password = data.get('password')

    # Kiểm tra các trường bắt buộc
    if not all([name, email, address, password]):
        return jsonify({'mé': 'Missing required fields'}), 400

    # Kiểm tra định dạng email
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        return jsonify({'error': 'Invalid email format'}), 400

    if User.get_user_by_email(email): 
        return jsonify({'error': 'Email already exists'}), 400

    try:
        add_user(name, email, address, role, created_by, password)
        return jsonify({'message': 'User added successfully!'}), 201
    except Exception as e:
        print(e)
        return jsonify({'error': 'An error occurred while adding the user'}), 500
    
@user_bp.route('/api/users/search', methods=['GET'])
# @cache.cached(timeout= CACHE_TTL)  # Cache API trong 60 giây
@role_required('admin')
def search_users_route():
    keyword = request.args.get('keyword', default=None, type=str)
    page = request.args.get('page', default=1, type=int)
    page_size = request.args.get('page_size', default=10, type=int)

    search_params = SearchParams(keyword=keyword, page=page, page_size=page_size)
    signs, total = search_users(search_params)

    response = {
        'data': [sign.to_dict() for sign in signs],
        'pagination': {
            'current_page': search_params.page,
            'page_size': search_params.page_size,
            'total_items': total,
            'total_pages': (total + search_params.page_size - 1) // search_params.page_size
        }
    }

    return jsonify(response)


@user_bp.route('/api/users/<int:user_id>', methods=['GET'])
@role_required('admin') 
def get_user_by_id(user_id):

    try:
        user = User.get_user_by_id(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify(user.to_dict()), 200
    except Exception as e:
        # Xử lý lỗi không mong muốn
        return jsonify({'error': 'An error occurred', 'details': str(e)}), 500
    
@user_bp.route('/api/users/<int:user_id>', methods=['PUT'])
@role_required('admin')  # Chỉ admin mới có thể cập nhật thông tin người dùng
def update_user_route(user_id):

    current_user = get_jwt_identity()

    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    address = data.get('address')
    role = data.get('role')
    password = data.get('password')

    # Kiểm tra nếu người dùng tồn tại
    user = User.get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Kiểm tra và xử lý email nếu có thay đổi
    if email:
        # Kiểm tra định dạng email
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            return jsonify({'error': 'Invalid email format'}), 400

        # Kiểm tra email đã tồn tại chưa (trừ khi là email của người dùng hiện tại)
        if User.get_user_by_email(email) and email != user.email:
            return jsonify({'error': 'Email already exists'}), 400

    try:
        # Cập nhật thông tin người dùng
        if name:
            user.name = name
        if email:
            user.email = email
        if address:
            user.address = address
        if role:
            user.role = role
        if password:
            user.password = password
        save_update_user(user_id, user)

        return jsonify({'message': 'User updated successfully!'}), 200

    except Exception as e:
        print(e)
        return jsonify({'error': 'An error occurred while updating the user'}), 500