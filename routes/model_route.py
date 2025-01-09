import random
from flask import Blueprint, Response, jsonify, request, stream_with_context
from services.auth_service import role_required
from services.model_service import add_model, add_model_with_logging, download_model_file, get_model_by_id, get_all_models, delete_model, get_model_path_by_id, set_active_model
from extension import cache
from const import CACHE_TTL

model_bp = Blueprint('model_bp', __name__)

# API lấy tất cả models
@model_bp.route('/api/models', methods=['GET'])
@role_required('admin','user')
def get_models():
    models = get_all_models()
    return jsonify([model.to_dict() for model in models]), 200

# API lấy model theo id
@model_bp.route('/api/models/<int:id>', methods=['GET'])
@cache.cached(timeout= CACHE_TTL)  # Cache API trong 60 giây
@role_required('admin')
def get_model(id):
    model = get_model_by_id(id)
    if model:
        return jsonify(model.to_dict()), 200
    else:
        return jsonify({'message': 'Model not found'}), 404
    
def generate_logs(sample_ids):
    # Yield logs one by one, converting them to bytes
    for log in add_model_with_logging(sample_ids):
        yield log.encode('utf-8')

@model_bp.route('/api/models', methods=['POST'])
@role_required('admin')
def create_model():
    data = request.get_json()

    if 'samples' not in data or not isinstance(data['samples'], list):
        return jsonify({'error': 'Missing or invalid sample list'}), 400

    sample_ids = [sample['id'] for sample in data['samples']]

    # Return a streaming response
    return Response(stream_with_context(generate_logs(sample_ids)), mimetype='text/plain')


@model_bp.route('/api/models/<int:id>', methods=['DELETE'])
@role_required('admin')
def delete_model_api(id):
    result = delete_model(id)
    if result['status'] == 'success':
        return jsonify({'message': result['message']}), 200
    else:
        return jsonify({'message': result['message'], 'error': result.get('error')}), 500
    
@model_bp.route('/api/models/<int:id>/set-active', methods=['PUT'])
@role_required('admin')
def set_model_active(id):
    result = set_active_model(id)
    
    if result['status'] == 'success':
        cache_key = f"view//api/models"  
        cache.delete(cache_key) 
        return jsonify({'message': result['message']}), 200  # Trả về phản hồi thành công

    else:
        return jsonify({'message': result['message'], 'error': result.get('error')}), 500


@model_bp.route('/api/models/<int:id>/download', methods=['GET'])
def download_model(id):
    # model_path = "C:\\Users\\ruy_pa_\\Dropbox\\do_an_2024\\YOLO\\" + get_model_path_by_id(id) +"\weights\\best.pt"
    # model_path = "C:\\Users\\ruy_pa_\\OneDrive - ptit.edu.vn\\do_an_2024\\YOLO\\appclone\\" + get_model_path_by_id(id) +"\weights\\best.pt"
    model_path = "C:\\Users\\ruy_pa_\\OneDrive - ptit.edu.vn\\do_an_2024\\YOLO\\appclone\\model\\model.tflite"
    print(model_path)
    return download_model_file(model_path)