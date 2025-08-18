from flask import Blueprint
from backend.decorators import login_required, admin_required


admin_users_bp = Blueprint('auth', __name__, url_prefix='/api/v1/admin/users')



@admin_users_bp.get('')
@login_required
@admin_required
def get_all_users():
    # 全ユーザーリストを取得するAPI (URL: /api/v1/admin/users)
    pass

@admin_users_bp.post('')


@admin_users_bp.delete('/<user_id>')
@login_required
@admin_required
def delete_user(user_id):
    # 特定のユーザーを削除するAPI (URL: /api/v1/admin/users/abc)
    pass