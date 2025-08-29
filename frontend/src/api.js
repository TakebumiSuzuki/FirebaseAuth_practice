import axios from 'axios';
import { auth } from '@/firebase'

export const apiClient = axios.create({
  // baseURL: 'http://localhost:5000', // Flaskサーバーのアドレス
});


apiClient.interceptors.request.use(
  async (config) => {
    // currentUserは、サインインした際やアプリの起動時にFirebaseのサーバーから取得されブラウザのストレージに
    // キャッシュされた、Firebaseのユーザーデータベースに保存されているユーザー情報
    // これはクライアントのストレージ（IndexedDBなど）にキャッシュされるので、ページリロードしてもログイン状態を維持できる
    // また、これは onAuthStateChanged のコールバックで引数に入れられる user と同じ, Userオブジェクト。
    // サーバーサイドの auth().getUser(uid) というメソッドと混乱しないように
    const user = auth.currentUser;

    if (user) {
      try {
        // 引数がない、つまり forceRefresh=false なので、まずキャッシュされたIDトークンを利用してトークンを即座に返す。
        // もしトークンが有効期限切れ、または期限切れに近い場合、新しくトークンを取得。
        const idToken = await user.getIdToken();
        config.headers.Authorization = `Bearer ${idToken}`;
      } catch (error) {
        console.error('Could not get ID token:', error);
        // ここでエラー処理（例: ログアウトさせるなど）を行うことも可能
      }
    }

    return config;
  },

  (error) => {
    return Promise.reject(error);
  }
);



