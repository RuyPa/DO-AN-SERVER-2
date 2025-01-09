import os
import uuid
from flask import Blueprint, json, jsonify, request, abort
from flask_jwt_extended import get_jwt_identity
from models.label import Label
from models.sample import Sample
from models.search import SearchParams
from models.traffic_sign import TrafficSign
from services.auth_service import role_required
from extension import cache
from const import CACHE_TTL
from services.label_service import create_label, delete_label, update_label, delete_labels_by_sample_id
from services.sample_service import (
    get_all_samples,
    get_sample_by_id,
    add_sample,
    get_sample_by_name,
    search_samples_in_db,
    update_sample,
    delete_sample,
    update_sample_path
)

sample_bp = Blueprint('sample_bp', __name__)

@sample_bp.route('/api/samples', methods=['GET'])
@role_required('admin', 'user')
def get_samples():
    samples = get_all_samples()
    return jsonify([sample.to_dict() for sample in samples])

@sample_bp.route('/api/samples/<int:id>', methods=['GET'])
@role_required('admin', 'user')
def get_sample(id):
    sample = get_sample_by_id(id)
    if sample is None:
        abort(404, description="Sample not found")
    return jsonify(sample.to_dict())

# @sample_bp.route('/api/samples', methods=['POST'])
# def create_sample():
#     data = request.get_json()
    
#     if not data:
#         abort(400, description="Request body is missing or not valid JSON")
    
#     code = data.get('code')
#     path = data.get('path', '')  
#     name = data.get('name', '') 
    
#     if not code:
#         abort(400, description="Code is required")
    
#     sample = Sample(code=code, path=path, name=name)
    
#     add_sample(sample)
    
#     return jsonify({'message': 'Sample created successfully'}), 201
# @sample_bp.route('/api/samples', methods=['POST'])
# @role_required('admin', 'user')
# def create_sample():
#     current_user = get_jwt_identity()  
#     current_user_email = current_user.get('email') 
#     data = request.form  # Nhận dữ liệu dưới dạng form-data

#     # Lấy thông tin từ form-data
#     name = data.get('name')
#     labels_data = data.getlist('labels')  # Nhận danh sách labels từ body request
    
#     # Tự động sinh mã code bằng UUID
#     code = str(uuid.uuid4())
    
#     if not name:
#         abort(400, description="Name is required")
    
#     # Xử lý ảnh
#     image_file = request.files.get('image')  # Nhận file ảnh từ form-data
#     if not image_file:
#         abort(400, description="Image file is required")
    
#     try:
#         # Upload ảnh lên Cloudinary
#         upload_result = cloudinary.uploader.upload(image_file)
#         image_path = upload_result.get('secure_url')  # Nhận URL an toàn của ảnh đã upload
#     except Exception as e:
#         abort(500, description=f"Image upload failed: {str(e)}")

#     # Tạo đối tượng Sample
#     sample = Sample(code=code, path=image_path, name=name, created_by=current_user_email)
    
#     # Xử lý danh sách labels (nếu có trong request)
#     for label_data in labels_data:
#         label = Label(
#             centerX=label_data.get('centerX'),
#             centerY=label_data.get('centerY'),
#             height=label_data.get('height'),
#             width=label_data.get('width'),
#             traffic_sign=TrafficSign.from_req(label_data.get('traffic_sign_id'))  # Giả sử bạn có phương thức này
#         )
#         sample.labels.append(label)  # Thêm label vào đối tượng sample
    
#     # Thêm sample và các labels vào cơ sở dữ liệu
#     add_sample(sample)

#     return jsonify({'message': 'Sample created successfully'}), 201
@sample_bp.route('/api/samples', methods=['POST'])
@role_required('admin', 'user')
def create_sample():
    current_user = get_jwt_identity()
    current_user_email = current_user.get('email') 
    data = request.form  # Nhận dữ liệu dưới dạng form-data

    # Lấy thông tin từ form-data
    name = data.get('name')  # Tên file
    labels_data = data.get('labels')  # Nhận danh sách labels dưới dạng JSON

    # Tự động sinh mã code bằng UUID
    code = str(uuid.uuid4())
    
    if not name:
        abort(400, description="Name is required")
    
    # Xử lý ảnh
    image_file = request.files.get('image')  # Nhận file ảnh từ form-data
    if not image_file:
        abort(400, description="Image file is required")
    
    try:
        # Upload ảnh lên Cloudinary
        upload_result = cloudinary.uploader.upload(image_file)
        image_path = upload_result.get('secure_url')  # Nhận URL an toàn của ảnh đã upload
    except Exception as e:
        abort(500, description=f"Image upload failed: {str(e)}")

    # Xử lý danh sách labels từ chuỗi JSON
    if labels_data:
        try:
            labels_data = json.loads(labels_data)  # Parse chuỗi JSON thành danh sách
        except Exception as e:
            abort(400, description=f"Invalid labels format: {str(e)}")
    
    # Tạo đối tượng Sample
    sample = Sample(code=code, path=image_path, name=name, created_by=current_user_email)
    
    for label_data in labels_data:
        label = Label(
            centerX=label_data.get('centerX'),
            centerY=label_data.get('centerY'),
            height=label_data.get('height'),
            width=label_data.get('width'),
            traffic_sign=TrafficSign.from_req(label_data.get('traffic_sign_id'))  # Giả sử bạn có phương thức này
        )

        sample.labels.append(label)  # Thêm label vào đối tượng sample
    
    # Thêm sample và các labels vào cơ sở dữ liệu
    add_sample(sample)

    return jsonify({'message': 'Sample created successfully'}), 201


# @sample_bp.route('/api/samples/<int:id>', methods=['PUT'])
# @role_required('admin', 'user')
# def update_sample_route(id):
#     data = request.json
#     sample = get_sample_by_id(id)
#     if sample is None:
#         abort(404, description="Sample not found")

#     # Cập nhật thông tin của Sample nếu có
#     updated = False
#     if 'code' in data:
#         sample.code = data['code']
#         updated = True
#     if 'path' in data:
#         sample.path = data['path']
#         updated = True
#     if 'name' in data:
#         sample.name = data['name']
#         updated = True

#     # Lưu thay đổi vào cơ sở dữ liệu nếu có thay đổi
#     if updated:
#         update_sample(sample)  # Gọi hàm để cập nhật sample trong DB

#     # Xử lý danh sách labels
#     labels_data = data.get('labels', [])
#     existing_labels = {label.id: label for label in sample.labels}

#     for label_data in labels_data:
#         label_id = label_data.get('id')

#         # Kiểm tra nếu label cần xóa
#         if label_data.get('isDeleted'):  # Nếu có trường isDeleted là true
#             if label_id in existing_labels:
#                 # Xóa label khỏi sample
#                 sample.labels = [label for label in sample.labels if label.id != label_id]
#                 delete_label(label_id)  # Gọi hàm để xóa label trong DB
#             continue  # Bỏ qua vòng lặp này, vì label đã được xử lý

#         if label_id in existing_labels:
#             label = existing_labels[label_id]

#             # Cập nhật các thuộc tính của label nếu có
#             if 'centerX' in label_data:
#                 label.centerX = label_data['centerX']
#             if 'centerY' in label_data:
#                 label.centerY = label_data['centerY']
#             if 'height' in label_data:
#                 label.height = label_data['height']
#             if 'width' in label_data:
#                 label.width = label_data['width']
#             if 'traffic_sign_id' in label_data:
#                 label.traffic_sign =  TrafficSign.from_req(label_data['traffic_sign_id'])

#             # Lưu thay đổi vào cơ sở dữ liệu
#             update_label(label)  # Gọi hàm để cập nhật label trong DB
#         else:
#             # Thêm label mới nếu ID không tồn tại
#             new_label = Label(
#                 centerX=label_data.get('centerX'),
#                 centerY=label_data.get('centerY'),
#                 height=label_data.get('height'),
#                 width=label_data.get('width'),
#                 traffic_sign=TrafficSign.from_req(label_data.get('traffic_sign_id')),
#                 sample_id=id
#             )
#             create_label(label= new_label)

#     # Lưu tất cả các thay đổi vào cơ sở dữ liệu
#     update_sample(sample)

#     return jsonify({'message': 'Sample updated successfully'}), 200


@sample_bp.route('/api/samples/<int:id>', methods=['PUT'])
@role_required('admin', 'user')
def update_sample_route(id):
    current_user = get_jwt_identity()
    current_user_email = current_user.get('email') 
    data = request.json
    sample = get_sample_by_id(id)
    
    if sample is None:
        abort(404, description="Sample not found")


    # Xử lý danh sách labels
    labels_data = data.get('labels', [])
    existing_labels = {label.id: label for label in sample.labels}
    print('abc')
    for label_data in labels_data:
        label_id = label_data.get('id')

        # Kiểm tra nếu label cần xóa
        if label_data.get('isDeleted'):  # Nếu có trường isDeleted là true
            if label_id in existing_labels:
                # Xóa label khỏi sample
                sample.labels = [label for label in sample.labels if label.id != label_id]
                delete_label(label_id)  # Gọi hàm để xóa label trong DB
            continue  # Bỏ qua vòng lặp này, vì label đã được xử lý

        if label_id in existing_labels:
            label = existing_labels[label_id]

            # Cập nhật các thuộc tính của label nếu có
            if 'centerX' in label_data:
                label.centerX = label_data['centerX']
            if 'centerY' in label_data:
                label.centerY = label_data['centerY']
            if 'height' in label_data:
                label.height = label_data['height']
            if 'width' in label_data:
                label.width = label_data['width']
            if 'traffic_sign_id' in label_data:
                label.traffic_sign = TrafficSign.from_req(label_data['traffic_sign_id'])
            print('def')
            # Lưu thay đổi vào cơ sở dữ liệu
            update_label(label)  # Gọi hàm để cập nhật label trong DB
        else:
            # Thêm label mới nếu ID không tồn tại
            new_label = Label(
                centerX=label_data.get('centerX'),
                centerY=label_data.get('centerY'),
                height=label_data.get('height'),
                width=label_data.get('width'),
                traffic_sign=TrafficSign.from_req(label_data.get('traffic_sign_id')),
                sample_id=id,
                created_by=current_user_email
            )
            print('gj')

            create_label(label=new_label)



    return jsonify({'message': 'Sample updated successfully'}), 200


@sample_bp.route('/api/samples/<int:id>', methods=['DELETE'])
@role_required('admin')
def delete_sample_route(id):
    # Xóa tất cả các label liên quan đến sample
    delete_labels_by_sample_id(id)
    
    # Xóa sample
    delete_sample(id)
    
    return jsonify({'message': 'Sample and its labels deleted successfully'})



from cloudinary.uploader import upload
import cloudinary
cloudinary.config( 
        cloud_name = "drtibt2pc", 
        api_key = "668131912396815", 
        api_secret = "5PC0jjLExqHglNZCTr0XMM3TkUc",
        secure = True
    )

# List of images to exclude from upload
# excluded_images = ['3.png', '5.png', '6.png', '16.png', '17.png', '334.png']

@sample_bp.route('/api/samples/temp', methods=['GET'])
def create_sample_temp():
    image_folder = "C:\\Users\\ruy_pa_\\OneDrive - ptit.edu.vn\\do_an_2024\\YOLO\\vn1\\valid\\images"

    # Kiểm tra xem thư mục ảnh có tồn tại không
    if not os.path.exists(image_folder):
        abort(400, description="Image folder does not exist")

    try:
        # Lấy danh sách các tệp ảnh trong thư mục ảnh
        image_files = [f for f in os.listdir(image_folder) if f.endswith(('jpg', 'png', 'jpeg'))]

        # Chọn 300 ảnh đầu tiên, bỏ qua ảnh trong danh sách ngoại trừ
        image_files = [f for f in image_files ][:300]
        print(image_files)
        # Lặp qua từng ảnh trong danh sách đã chọn
        for image_file in image_files:
            image_path = os.path.join(image_folder, image_file)

            # Upload ảnh lên Cloudinary
            try:
                upload_result = upload(image_path)
                image_url = upload_result.get('secure_url')  # Lấy URL an toàn của ảnh đã upload

                if not image_url:
                    print(f"Warning: Cloudinary upload failed for image {image_file}")
                    continue  # Bỏ qua nếu không có URL trả về từ Cloudinary

            except Exception as upload_error:
                print(f"Error uploading image {image_file}: {str(upload_error)}")
                continue  # Bỏ qua nếu có lỗi trong quá trình upload

            # Tạo đối tượng Sample (hoặc lấy từ cơ sở dữ liệu)
            sample = get_sample_by_name(image_file)

            if sample:
                # Cập nhật lại path của Sample
                sample.path = image_url
                update_sample_path(sample)
            else:
                print(f"Warning: No sample found for image {image_file}")

        return jsonify({'message': 'Paths updated successfully'}), 200

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        abort(500, description=f"An error occurred: {str(e)}")

    # # Lấy đường dẫn đến thư mục ảnh và thư mục nhãn
    # image_folder = "C:\\Users\\ruy_pa_\\OneDrive - ptit.edu.vn\\do_an_2024\\YOLO\\vn1\\valid\\images"
    # label_folder = "C:\\Users\\ruy_pa_\\OneDrive - ptit.edu.vn\\do_an_2024\\YOLO\\vn1\\valid\\labels"
    
    # if not image_folder or not label_folder:
    #     abort(400, description="Both image folder and label folder are required")
    
    # # Kiểm tra nếu thư mục ảnh và nhãn tồn tại
    # if not os.path.exists(image_folder) or not os.path.exists(label_folder):
    #     abort(400, description="Image or label folder does not exist")

    # try:
    #     # Lấy danh sách các tệp ảnh trong thư mục ảnh
    #     image_files = [f for f in os.listdir(image_folder) if f.endswith(('jpg', 'png', 'jpeg'))]
        
    #     # Lặp qua từng ảnh trong thư mục ảnh
    #     for image_file in image_files:
    #         # Skip the excluded images
    #         if image_file in excluded_images:
    #             continue  # Bỏ qua ảnh nếu tên của ảnh có trong danh sách ngoại trừ
            
    #         image_path = os.path.join(image_folder, image_file)
    #         label_file = os.path.splitext(image_file)[0] + '.txt'  # Giả sử tệp nhãn có cùng tên với ảnh nhưng định dạng .txt
    #         label_path = os.path.join(label_folder, label_file)

    #         # Kiểm tra nếu tệp nhãn có tồn tại
    #         if not os.path.exists(label_path):
    #             continue  # Bỏ qua nếu không có tệp nhãn tương ứng
            
    #         # Upload ảnh lên Cloudinary
    #         upload_result = cloudinary.uploader.upload(image_path)
    #         image_url = upload_result.get('secure_url')  # Lấy URL an toàn của ảnh đã upload

    #         # Đọc tệp nhãn
    #         with open(label_path, 'r') as label_file:
    #             labels_data = label_file.readlines()  # Đọc từng dòng trong tệp nhãn

    #         # Tạo đối tượng Sample
    #         sample = Sample(code=str(uuid.uuid4()), path=image_url, name=image_file)

    #         # Xử lý các nhãn
    #         for label_data in labels_data:
    #             # Mỗi dòng trong tệp nhãn có thể có thông tin nhãn dạng: traffic_sign_id centerX centerY height width
    #             label_info = label_data.strip().split()  # Giả sử các trường cách nhau bằng khoảng trắng

    #             if len(label_info) < 5:
    #                 continue  # Bỏ qua nếu dữ liệu không đầy đủ

    #             # Lấy thông tin nhãn từ tệp
    #             traffic_sign_id = int(label_info[0])
    #             centerX, centerY, height, width = map(float, label_info[1:])

    #             # Tạo đối tượng TrafficSign từ traffic_sign_id
    #             traffic_sign = TrafficSign.from_req(traffic_sign_id)  # Tạo đối tượng TrafficSign từ ID
                
    #             # Tạo đối tượng Label và thêm vào Sample
    #             label = Label(centerX=centerX, centerY=centerY, height=height, width=width, traffic_sign=traffic_sign)
    #             sample.labels.append(label)
            
    #         # Lưu sample vào cơ sở dữ liệu
    #         add_sample(sample)

    #     return jsonify({'message': 'Samples created successfully'}), 201

    # except Exception as e:
    #     abort(500, description=f"An error occurred: {str(e)}")


@sample_bp.route('/api/samples/search', methods=['GET'])
@role_required('admin', 'user')
def search_samples():
    keyword = request.args.get('keyword', default=None, type=str)
    category_id = request.args.get('category_id', default=None, type=int)
    page = request.args.get('page', default=1, type=int)
    page_size = request.args.get('page_size', default=10, type=int)

    # Tạo đối tượng SearchParams
    search_params = SearchParams(keyword=keyword, page=page, page_size=page_size, category_id=category_id)
    samples, total = search_samples_in_db(search_params)

    response = {
        'data': [sample.to_dict() for sample in samples],
        'pagination': {
            'current_page': search_params.page,
            'page_size': search_params.page_size,
            'total_items': total,
            'total_pages': (total + search_params.page_size - 1) // search_params.page_size
        }
    }

    return jsonify(response)
