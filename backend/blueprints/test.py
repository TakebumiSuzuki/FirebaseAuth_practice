from flask import Blueprint, jsonify

# ブループリントの名前を 'auth' から 'test' に変更します
test_bp = Blueprint('test', __name__, url_prefix='')

@test_bp.get('/')
def test():
    # レスポンスも少し変えておくと、修正が反映されたか分かりやすいです
    return jsonify({'message':'This is test blueprint!'}), 200