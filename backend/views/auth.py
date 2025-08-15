from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')


@auth_bp.post('/register')
def register():
    pass

@auth_bp.post('/login')
def login():
    pass

@auth_bp.post('/logout')
def logout():
    pass

