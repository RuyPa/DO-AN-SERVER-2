import csv
from flask import Flask, abort, request, jsonify, send_file, render_template
from flask_caching import Cache
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flask_socketio import SocketIO, emit
from sklearn.model_selection import train_test_split

from db import get_db_connection


app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading', cors_allowed_origins="*")  # Sử dụng threading cho SocketIO

# CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})
CORS(app, supports_credentials=True)  # Allow credentials for all domains


# Database configuration
app.config['DB_HOST'] = 'localhost'
app.config['DB_USER'] = 'root'
app.config['DB_PASSWORD'] = '123456'
app.config['DB_DATABASE'] = 'traffic_sign'

# app.config['DB_HOST'] = '45.252.248.164'
# app.config['DB_USER'] = 'duydoba00'
# app.config['DB_PASSWORD'] = 'Duydoba@02'
# app.config['DB_DATABASE'] = 'traffic_sign'


#----------redis-------------------
from extension import cache
app.config['CACHE_TYPE'] = 'RedisCache'
app.config['CACHE_REDIS_HOST'] = 'localhost'  # Địa chỉ Redis
app.config['CACHE_REDIS_PORT'] = 6379         # Cổng Redis (mặc định)
app.config['CACHE_DEFAULT_TIMEOUT'] = 300     # Cache mặc định 5 phút
cache.init_app(app)
#----------redis-------------------

from extension import bcrypt
bcrypt.init_app(app)

# Import routes and services after app config
from services.traffic_sign_service import create_tables
from routes.routes import api_routes
from routes.sample_route import sample_bp
from routes.label_route import label_bp
from routes.model_sample_route import model_sample_bp
from routes.model_route import model_bp
from routes.auth_route import auth_bp
from routes.user_route import user_bp


# Register blueprints
app.register_blueprint(api_routes)
app.register_blueprint(sample_bp)
app.register_blueprint(label_bp)
app.register_blueprint(model_sample_bp)
app.register_blueprint(model_bp)

# Register the auth blueprint
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)

from flask_bcrypt import Bcrypt

# app.secret_key = 'jkasKAHS7QFjhagd662QHFCASHFGAW56QAWFHIHAWIEFHCBvVAS'  # Needed for session management

app.config['JWT_SECRET_KEY'] = 'jkasKAHS7QFjhagd662QHFCASHFGAW56QAWFHIHAWIEFHCBvVAS'  # Thay bằng khóa bí mật của bạn
jwt = JWTManager(app)

# login_manager = LoginManager()
# login_manager.init_app(app)  # Attach the LoginManager to the app
# login_manager.login_view = 'login'  # Set the login view (route name)

# Optionally, you can also set a custom message for unauthorized access
# login_manager.login_message = "Please log in to access this page."


from services.auth_service import User, role_required

@jwt.unauthorized_loader
def custom_unauthorized_response(callback):
    return jsonify({
        'error': 'You must be logged in to access this resource',
        'message': 'Missing or invalid token'
    }), 401

# Callback khi token hết hạn
@jwt.expired_token_loader
def custom_expired_token_response(jwt_header, jwt_payload):
    return jsonify({
        'error': 'Token has expired',
        'message': 'Please log in again to get a new token'
    }), 401

# Callback khi token không hợp lệ
@jwt.invalid_token_loader
def custom_invalid_token_response(callback):
    return jsonify({
        'error': 'Invalid token',
        'message': 'The provided token is not valid'
    }), 422



if __name__ == '__main__':
    # socketio.run(app, host='127.0.0.1', port=5000, debug=False)
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)

