class TrafficSign:
    def __init__(self, id=None, name='', code='', description='', path='', created_by = '', category = None):
        self.id = id
        self.name = name
        self.code = code
        self.description = description
        self.path = path
        self.create_by = created_by
        self.category = category  


    @staticmethod
    def from_row(row, category = None):
        return TrafficSign(
            id=row['id'],
            name=row['name'],
            code=row['code'],
            description=row['description'],
            path=row['path'],
            created_by= row['created_by'],
            category = category  
        )
    
    @classmethod
    def from_prj(cls, row, category = None):
        return cls(
            id=row['traffic_sign_id'],
            name=row['traffic_sign_name'],
            description=row['traffic_sign_description'],
            path=row['traffic_sign_path'],
            created_by = row['created_by'],
            category = category  
        )
    
    @classmethod
    def from_req(cls, traffic_sign_id):
        return cls(
            id= traffic_sign_id
        )
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'path': self.path,
            'created_by': self.create_by,
            'category': self.category.to_dict() if self.category else None  
        }
