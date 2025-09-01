FROM node:22.17.1-alpine3.22

# 1. まず作業ディレクトリを作成する（この時点ではrootユーザー）
WORKDIR /frontend

# 2. 依存関係ファイルをコピーし、所有者を'node'ユーザーに変更する
# nodeイメージに組み込まれている 'node' ユーザー (uid 1000) を利用
# でも結局、COPY --chown=node:node . . この行で所有者を一括で変えているので
# ここで --chown=node:node と書く必要はないとのこと。
COPY --chown=node:node package.json package-lock.json ./

# 3. 依存関係をインストールする（rootユーザーのまま）。cはクリーンインストール
RUN npm ci

# npm ci で root が作成した node_modules ディレクトリの所有権を、
# これからプロセスを実行する 'node' ユーザーに渡す。-Rは recursive
RUN chown -R node:node /frontend/node_modules

# 4. ソースコード全体をコピーし、所有者を'node'ユーザーに変更する
COPY --chown=node:node . .

# 5. すべての準備が終わった後、最後に非特権ユーザーに切り替える
USER node

# 6. ポートを公開
EXPOSE 5173

# 7. アプリケーションを起動（このコマンドは'node'ユーザーで実行される）
# localhostだけでなく、コンテナ外部からのアクセスを受け付けるために--hostが必要
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]