
class Category:
    def __init__(self, id=None, name=None, description=None, created_date=None, created_by=None):
        self.id = id
        self.name = name
        self.description = description
        self.created_date = created_date
        self.created_by = created_by

    @staticmethod
    def from_row(row):
        """Tạo đối tượng Category từ một bản ghi cơ sở dữ liệu."""
        return Category(
            id=row['id'],
            name=row['name'],
            description=row['description'],
            created_date=row['created_date'],
            created_by=row['created_by']
        )
    
    @classmethod
    def from_prj(cls, row):
        """Tạo đối tượng Category từ thông tin dự án (nếu có thể dùng)."""
        return cls(
            id=row['category_id'],
            name=row['category_name'],
            description=row['category_description'],
            created_date=row['created_date'],
            created_by=row['created_by']
        )
    
    def to_dict(self):
        """Chuyển đổi Category thành từ điển."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_date': self.created_date,
            'created_by': self.created_by
        }
