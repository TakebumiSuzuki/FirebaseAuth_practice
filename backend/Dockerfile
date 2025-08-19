FROM python:3.12.11-slim-bullseye

# キャッシュファイルである .pyc ファイルを生成させないようにする設定
# 1 は true（真）や「有効」を意味すると考えてよい
ENV PYTHONDONTWRITEBYTECODE=1

# print() 文などが即座に出力ストリームに送られるため、デバッグが非常にしやすくなります。
ENV PYTHONUNBUFFERED=1

# 'appuser'という名前でグループとユーザーを作成します
# --system: ホームディレクトリなし、パスワードなしのシステムアカウントとして作成
# --group: 同名のグループも一緒に作成
RUN adduser --system --group appuser


# WORKDIRの機能: WORKDIR /backend と記述すると、/backend ディレクトリが存在しない場合は自動的に作成してくれます
# コンテナ内での以降のコマンド（RUN, CMD, ENTRYPOINTなど）が実行されるカレントディレクトリを/backendに設定するという意味
WORKDIR /backend

# python:3.12.11-slim-bullseye のような公式イメージは、Pythonのリリースに合わせて、その時点で安定している比較的新しい
# バージョンの pip や setuptools を同梱してくれています。そのため、ほとんどのパッケージはこの標準のpipで問題なく
# インストールできます。つまり、RUN pip install -U pip のように書く必要はほとんどの場合でない。
COPY requirements.txt .

# pip はダウンロードしたパッケージをキャッシュとして一時的に保存します。--no-cache-dirでこれを無効に。
# -r と書くと個別パッケージではなく、requirements.txt に記述されているパッケージを一括インストール。
RUN pip install --no-cache-dir -r requirements.txt


# ソースコードをコピーし、所有者をappuserユーザーに、所有グループをappuserグループに設定
# このオプションがない場合、コピーされたファイルの所有者はrootになってしまいます。
COPY --chown=appuser:appuser . .


# エントリーポイントスクリプトをコピーして実行権限を付与
RUN chmod +x entrypoint.sh

# 実際にネットワークを設定するのではなく、5000番ポートで通信を待ち受ける予定だ、ということを記しているのみ
EXPOSE 5000

#この命令以降に実行されるコマンド（CMDやENTRYPOINTなど）が、appuserユーザーの権限で実行されるように切り替える
# ここでユーザーを切り替えなければ、コンテナはrootユーザーで起動してしまいます。
USER appuser

# ENTRYPOINTでスクリプトを指定
ENTRYPOINT ["./entrypoint.sh"]





# 以下の行はイメージを作る時には実行されない。コンテナをインスタンス化する時に、ボリュームのマウントが完了してから実行される
# --host=0.0.0.0 により、コンテナ内部（127.0.0.1）からのアクセスも含め全ての宛先からの通信を受ける
# USER appuserにより、このコマンドは 'appuser' 権限で実行されます
# CMD [ "flask", "run", "--host=0.0.0.0" ]


# ENV GUNICORN_WORKERS=4
# ENV GUNICORN_THREADS=2
# # デバッグ用: ワーカー数を1に減らして詳細ログを出力
# ENV FLASK_APP=app:create_app()
# # 別の書き方
# CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--timeout", "120", "app:create_app()"]

