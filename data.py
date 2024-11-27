import os

# Đường dẫn thư mục chứa ảnh
source_dir = r"C:\\Users\\ruy_pa_\\Downloads\\data"
# Đường dẫn thư mục để lưu file .txt
destination_dir = r"C:\\Users\\ruy_pa_\\Downloads\\data_des"

# Tạo thư mục đích nếu chưa tồn tại

# Lấy danh sách các file trong thư mục nguồn
for file_name in os.listdir(source_dir):
    # Kiểm tra file có phải là ảnh (theo đuôi file)
    if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
        # Tên file .txt tương ứng
        txt_file_name = os.path.splitext(file_name)[0] + ".txt"
        # Đường dẫn đầy đủ của file .txt trong thư mục đích
        txt_file_path = os.path.join(destination_dir, txt_file_name)
        
        # Tạo file .txt rỗng
        with open(txt_file_path, 'w') as f:
            pass

print(f"Đã tạo file .txt tương ứng cho các ảnh trong thư mục {source_dir}.")
