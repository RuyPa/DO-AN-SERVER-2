# import os

# # Đường dẫn thư mục chứa các file .txt
# directory = r"D:\\dataset\\vn1\\vn1\\valid\\labels"

# # Dictionay để ánh xạ các giá trị đầu tiên theo yêu cầu
# mapping = {
#     '0': '52',
#     '1': '19',
#     '2': '7',
#     '3': '59',
#     '4': '59',
#     '5': '60',
#     '6': '61'
# }

# # Hàm thay đổi chỉ số đầu tiên trong mỗi dòng
# def replace_first_column(line):
#     parts = line.split()  # Tách các phần tử trong dòng
#     if parts[0] in mapping:  # Nếu giá trị đầu tiên là trong mapping
#         parts[0] = mapping[parts[0]]  # Thay thế giá trị đầu tiên
#     return " ".join(parts)  # Kết hợp lại thành dòng mới

# # Đọc các file trong thư mục và thay thế
# for filename in os.listdir(directory):
#     if filename.endswith('.txt'):  # Kiểm tra chỉ các file .txt
#         file_path = os.path.join(directory, filename)
#         with open(file_path, 'r') as file:
#             lines = file.readlines()  # Đọc tất cả các dòng trong file
        
#         # Thay đổi giá trị đầu tiên trong mỗi dòng
#         updated_lines = [replace_first_column(line) + '\n' for line in lines]
        
#         # Lưu kết quả vào file mới
#         with open(file_path, 'w') as file:
#             file.writelines(updated_lines)

# print("Đã thay đổi các giá trị đầu tiên và lưu lại các file.")
import requests

# URL của tệp cần tải về
url = "https://upload.wikimedia.org/wikipedia/commons/thumb"

# Header User-Agent để giả lập trình duyệt
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Tải tệp
response = requests.get(url, headers=headers)

# Kiểm tra nếu tải thành công
if response.status_code == 200:
    with open("downloaded_file.jpg", 'wb') as file:
        file.write(response.content)
    print("Tải tệp thành công.")
else:
    print(f"Không thể tải tệp. Mã lỗi: {response.status_code}")
