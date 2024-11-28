import os
import unicodedata
from flask import Blueprint, jsonify, request, abort
from models.search import SearchParams
from models.traffic_sign import TrafficSign
from cloudinary.uploader import upload
from extension import cache
from const import CACHE_TTL
import cloudinary
cloudinary.config( 
        cloud_name = "dkf74ju3o", 
        api_key = "639453249624293", 
        api_secret = "2GY34a7PT11RkkaTwEsKP9eYkwI",
        secure = True
    )
from services.auth_service import role_required
from services.traffic_sign_service import (
    get_all_categories,
    get_all_signs,
    get_sign_by_id,
    add_sign,
    search_signs,
    update_sign,
    delete_sign
)

api_routes = Blueprint('api_routes', __name__)


@api_routes.route('/api/traffic_signs', methods=['GET'])
@cache.cached(timeout= CACHE_TTL)  # Cache API trong 60 giây
@role_required('admin', 'user')
def get_signs():
    signs = get_all_signs()
    return jsonify([sign.to_dict() for sign in signs])

@api_routes.route('/api/traffic_signs/<int:id>', methods=['GET'])
@cache.cached(timeout= CACHE_TTL)  # Cache API trong 60 giây
@role_required('admin', 'user')
def get_sign(id):
    sign = get_sign_by_id(id)
    if sign is None:
        abort(404, description="Sign not found")
    return jsonify(sign.to_dict())

# @api_routes.route('/api/traffic_signs', methods=['POST'])
# def create_sign():
#     data = request.get_json()
    
#     if not data:
#         abort(400, description="Request body is missing or not valid JSON")
    
#     name = data.get('name')
#     code = data.get('code')  
#     description = data.get('description', '')  
#     path = data.get('path', '') 
    
#     if not name or not code:
#         abort(400, description="Name and Code are required")
    
#     sign = TrafficSign(name=name, code=code, description=description, path=path)
    
#     add_sign(sign)
    
#     return jsonify({'message': 'Traffic sign created successfully'}), 201
@api_routes.route('/api/traffic_signs', methods=['POST'])
@role_required('admin')
def create_sign():
    data = request.form  # Dữ liệu không phải JSON, mà là form-data
    
    # Lấy thông tin từ form-data
    name = data.get('name')
    code = data.get('code')  
    description = data.get('description', '')  
    
    # Kiểm tra thông tin bắt buộc
    if not name or not code:
        abort(400, description="Name and Code are required")
    
    # Xử lý file ảnh
    file = request.files.get('image')  # Nhận file từ multipart/form-data
    if not file:
        abort(400, description="Image file is required")
    
    try:
        # Upload file lên Cloudinary
        upload_result = cloudinary.uploader.upload(file)
        path = upload_result.get('secure_url')  # Nhận URL an toàn của ảnh đã upload
        
    except Exception as e:
        abort(500, description=f"Image upload failed: {str(e)}")
    
    # Tạo object TrafficSign và thêm vào database
    sign = TrafficSign(name=name, code=code, description=description, path=path)
    add_sign(sign)
    
    return jsonify({'message': 'Traffic sign created successfully'}), 201

@api_routes.route('/api/traffic_signs/<int:id>', methods=['PUT'])
@role_required('admin')
def update_sign_route(id):
    data = request.form  # Lấy dữ liệu từ form-data
    
    # Tìm TrafficSign hiện tại từ database
    sign = get_sign_by_id(id)  # Giả sử có hàm này để lấy đối tượng TrafficSign hiện tại
    
    if not sign:
        abort(404, description="Traffic sign not found")
    
    # Lấy thông tin mới từ form-data
    name = data.get('name', sign.name)  # Nếu không có, giữ nguyên giá trị cũ
    code = data.get('code', sign.code)  # Nếu không có, giữ nguyên giá trị cũ
    description = data.get('description', sign.description)  # Nếu không có, giữ nguyên giá trị cũ
    path = sign.path  # Giữ nguyên đường dẫn cũ

    # Kiểm tra thông tin bắt buộc
    if not name or not code:
        abort(400, description="Name and Code are required")
    
    file = request.files.get('image')  # Nhận file từ multipart/form-data
    
    # Nếu có file ảnh mới, upload và lấy URL mới
    if file:
        try:
            upload_result = cloudinary.uploader.upload(file)
            path = upload_result.get('secure_url')  # Nhận URL an toàn của ảnh mới đã upload
            
        except Exception as e:
            abort(500, description=f"Image upload failed: {str(e)}")

    # Cập nhật TrafficSign trong database
    update_sign(id, name, code, description, path)  # Cập nhật các thông tin cần thiết
    
    return jsonify({'message': 'Traffic sign updated successfully'})


@api_routes.route('/api/traffic_signs/<int:id>', methods=['DELETE'])
@role_required('admin')
def delete_sign_route(id):
    delete_sign(id)
    return jsonify({'message': 'Traffic sign deleted successfully'})


# @api_routes.route('/api/traffic_signs/search', methods=['GET'])
# @role_required('admin', 'user')
# def search_traffic_signs():
#     keyword = request.args.get('keyword', default=None, type=str)
#     page = request.args.get('page', default=1, type=int)
#     page_size = request.args.get('page_size', default=10, type=int)

#     search_params = SearchParams(keyword=keyword, page=page, page_size=page_size)
#     signs, total = search_signs(search_params)

#     response = {
#         'data': [sign.to_dict() for sign in signs],
#         'pagination': {
#             'current_page': search_params.page,
#             'page_size': search_params.page_size,
#             'total_items': total,
#             'total_pages': (total + search_params.page_size - 1) // search_params.page_size
#         }
#     }

#     return jsonify(response)

@api_routes.route('/api/traffic_signs/search', methods=['GET'])
@role_required('admin', 'user')
def search_traffic_signs():
    keyword = request.args.get('keyword', default=None, type=str)
    category_id = request.args.get('category_id', default=None, type=int)
    page = request.args.get('page', default=1, type=int)
    page_size = request.args.get('page_size', default=10, type=int)

    search_params = SearchParams(keyword=keyword, page=page, page_size=page_size, category_id=category_id)
    signs, total = search_signs(search_params)

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




def generate_code(name):
    """Sinh mã code từ tên."""
    name = unicodedata.normalize('NFKD', name)
    name = ''.join(c for c in name if not unicodedata.combining(c))  # Loại bỏ dấu
    name = name.lower().replace(' ', '_')  # Đổi khoảng trắng thành _
    name = ''.join(c for c in name if c.isalnum() or c == '_')  # Chỉ giữ lại ký tự latin và _
    return name

@api_routes.route('/api/traffic_signs/add_batch', methods=['GET'])
def add_batch():
    images_dir = "C:/Users/ruy_pa_/Downloads/data"
    descriptions_dir = "C:/Users/ruy_pa_/Downloads/data_des"

    if not images_dir or not descriptions_dir:
        abort(400, description="Both images_dir and descriptions_dir are required.")

    if not os.path.isdir(images_dir) or not os.path.isdir(descriptions_dir):
        abort(400, description="Invalid directory path(s).")

    added_signs = []
    for image_name in os.listdir(images_dir):
        if image_name.lower().endswith(('png', 'jpg', 'jpeg')):
            # Đường dẫn file ảnh
            image_path = os.path.join(images_dir, image_name)

            # Tên file mô tả tương ứng
            txt_file_name = os.path.splitext(image_name)[0] + ".txt"
            txt_file_path = os.path.join(descriptions_dir, txt_file_name)

            if not os.path.exists(txt_file_path):
                continue  # Bỏ qua nếu không tìm thấy file mô tả

            # Đọc nội dung từ file mô tả
            with open(txt_file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            if len(lines) < 2:
                continue  # Bỏ qua nếu file không đủ nội dung

            name = lines[0].strip()  # Dòng đầu tiên là tên
            description = lines[1].strip()  # Dòng thứ hai là mô tả
            code = generate_code(name)

            try:
                # Upload file ảnh lên Cloudinary
                upload_result = cloudinary.uploader.upload(image_path)
                path = upload_result.get('secure_url')  # Nhận URL an toàn của ảnh đã upload
            except Exception as e:
                # Bỏ qua ảnh nếu upload thất bại
                print(f"Failed to upload image {image_path}: {e}")
                continue

            # Tạo object TrafficSign và thêm vào database
            sign = TrafficSign(name=name, code=code, description=description, path=path)
            add_sign(sign)

            added_signs.append({
                'name': name,
                'code': code,
                'description': description,
                'path': path
            })

    return jsonify({'message': 'Batch processing completed', 'added_signs': added_signs}), 201

@api_routes.route('/api/categories', methods=['GET'])
@role_required('admin', 'user')
def get_all_cate():
    categories = get_all_categories()
    return jsonify([category.to_dict() for category in categories])
