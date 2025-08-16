from . import admin_bp

@admin_bp.route('/users', methods=['GET'])
def get_all_users():
    # 全ユーザーリストを取得するAPI (URL: /api/v1/admin/users)
    pass

@admin_bp.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    # 特定のユーザーを削除するAPI (URL: /api/v1/admin/users/abc)
    pass