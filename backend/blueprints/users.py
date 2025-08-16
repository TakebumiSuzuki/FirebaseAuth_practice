from flask import Blueprint

users_bp = Blueprint('users', __name__, url_prefix='/api/v1/users')

@users_bp.get('/me')
def get_me():
    pass

@users_bp.patch('/me')
def update_me():
    pass

@users_bp.delete('/me')
def delete_me():
    pass

