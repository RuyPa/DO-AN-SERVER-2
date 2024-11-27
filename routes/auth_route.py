from flask import Blueprint, request, jsonify, render_template, session
from flask_login import login_user, logout_user, login_required, current_user
from services.auth_service import User

auth_bp = Blueprint('auth', __name__)

# @auth_bp.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']
        
#         # Fetch user by email
#         user = User.get_user_by_email(email)
        
#         if user and user.check_password(password):
#             print("Session: ", session)
#             login_user(user)
#             print("Session: ", session)
#             session_dict = dict(session)

#             return jsonify({
#                 'session': session_dict,
#                 'message': 'Login successful!',
#                 'role': user.role,  # Return the user's role
#                 'name': user.name
#             }), 200
#         else:
#             return jsonify({'error': 'Invalid email or password'}), 401
    
#     # Render a login form for GET request
#     return render_template('login.html')

from flask import request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import timedelta

@auth_bp.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Lấy user theo email
        user = User.get_user_by_email(email)
        
        if user and user.check_password(password):
            # Tạo access và refresh tokens
            access_token = create_access_token(identity={'id': user.id, 'role': user.role, 'email': user.email}, expires_delta=timedelta(hours=12))
            refresh_token = create_refresh_token(identity={'id': user.id, 'role': user.role, 'email': user.email})
            
            return jsonify({
                'access_token': access_token,
                'refresh_token': refresh_token,
                'message': 'Login successful!',
                'role': user.role,
                'name': user.name
            }), 200
        else:
            return jsonify({'error': 'Invalid email or password'}), 401


@auth_bp.route('/logout', methods=['POST'])
def logout():
    # logout_user()
    return jsonify({'message': 'Logged out successfully!'}), 200


# Protected route example
@auth_bp.route('/protected', methods=['GET'])
@login_required
def protected():
    return jsonify({'message': f'Hello, {current_user.name}! You have access to this route.'})


# Role-based protected route example
@auth_bp.route('/admin-only', methods=['GET'])
@login_required
def admin_only():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized access'}), 403
    return jsonify({'message': 'Welcome, admin!'})


