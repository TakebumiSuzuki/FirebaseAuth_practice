from flask import Blueprint


admin_products_bp = Blueprint('auth', __name__, url_prefix='/api/v1/admin/products')