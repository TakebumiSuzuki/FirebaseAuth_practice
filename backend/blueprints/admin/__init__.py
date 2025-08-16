from flask import Blueprint

admin_bp = Blueprint('admin', __name__, url_prefix='/api/v1/admin')

# このファイルが読み込まれた時に、他のビューファイルも読み込む
# (循環参照を避けるため、最後にインポートするのが一般的)
from . import user_views, product_views

@admin_bp.before_request
def check_is_admin():
    # ここでリクエストしてきたユーザーが管理者権限を持っているかチェックする
    # 例: g.user.is_admin is not True: abort(403)
    pass