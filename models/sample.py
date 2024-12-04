# class Sample:
#     def __init__(self, id=None, code='', path='', name=''):
#         self.id = id
#         self.code = code
#         self.path = path
#         self.name = name

#     @staticmethod
#     def from_row(row):
#         """Tạo đối tượng Sample từ một bản ghi cơ sở dữ liệu."""
#         return Sample(
#             id=row['id'],
#             code=row['code'],
#             path=row['path'],
#             name=row['name']
#         )

#     def to_dict(self):
#         """Chuyển đối tượng Sample thành từ điển."""
#         return {
#             'id': self.id,
#             'code': self.code,
#             'path': self.path,
#             'name': self.name
#         }
from models.label import Label

class Sample:
    def __init__(self, id=None, code='', path='', name='',created_by = '', labels=None):
        self.id = id
        self.code = code
        self.path = path
        self.name = name
        self.created_by = created_by

        self.labels = labels if labels else []  # Danh sách các labels, mặc định là danh sách trống

    @staticmethod
    def from_row(row, labels=[]):
        return Sample(
            id=row['id'],
            code=row['code'],
            path=row['path'],
            name=row['name'],
            created_by= row['created_by'],

            labels=labels  # Nhận danh sách các labels từ service
        )
    
    @classmethod
    def from_prj(cls, row):
        return cls(
            id=row['sample_id'],
            code=row['sample_code'],
            path=row['sample_path'],
            name=row['sample_name'],
            created_by = row['created_by'],

        )
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'path': self.path,
            'name': self.name,
            'created_by': self.created_by,

            'labels': [label.to_dict() for label in self.labels]  # Chuyển đổi danh sách labels sang dạng từ điển
        }
