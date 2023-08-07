"""
    Base node class
""" 
class Node():
    def __init__(self, idx, **attrs):
        self.id = idx
        self.attrs = attrs
    
    def __hash__(self):
        return hash(str(self))
    
    def get_id(self):
        return self.id

"""
    Node of type Item class
"""
class ItemNode(Node):
    def __init__(self, idx, **attrs):
        super().__init__(idx, **attrs)
    
    def __str__(self):
        return f'Item({self.id})'
    
    def __repr__(self):
        return str(self)
    
    def __hash__(self):
        return super().__hash__()
    
    def __eq__(self, other):
        if isinstance(self, ItemNode) and isinstance(other, ItemNode):
            return self.id == other.id
        return False

"""
    Node of type User class
"""
class UserNode(Node):
    def __init__(self, idx, **attrs):
        super().__init__(idx, **attrs)
    
    def __str__(self):
        return f'User({self.id})'

    def __repr__(self):
        return str(self)
    
    def __hash__(self):
        return super().__hash__()
    
    def __eq__(self, other):
        if isinstance(self, UserNode) and isinstance(other, UserNode):
            return self.id == other.id
        return False

"""
    Node of type Property class
"""
class PropertyNode(Node):
    def __init__(self, idx, property_type, **attrs):
        super().__init__(idx, **attrs)
        self.property_type = property_type
    
    def __str__(self):
        return f'Property({self.id}, {self.property_type})'
    
    def __repr__(self):
        return str(self)
    
    def __hash__(self):
        return super().__hash__()
    
    def __eq__(self, other):
        if isinstance(self, PropertyNode) and isinstance(other, PropertyNode) and self.property_type == other.property_type:
            return self.id == other.id
        return False
    
    def get_property_type(self):
        return self.property_type