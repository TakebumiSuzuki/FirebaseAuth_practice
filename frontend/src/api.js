import axios from 'axios';
import { getAuth, onAuthStateChanged } from 'firebase/auth';

export const apiClient = axios.create({
  baseURL: 'http://localhost:5000/api', // Flaskサーバーのアドレス
});


apiClient.interceptors.request.use(async (config) => {
  const auth = getAuth();
  const user = auth.currentUser;

  if (user) {
    try {
      // Firebaseから最新のIDトークンを取得
      // トークンが期限切れの場合、SDKが自動で更新してくれます
      const idToken = await user.getIdToken();
      // ヘッダーにトークンをセット
      config.headers.Authorization = `Bearer ${idToken}`;
    } catch (error) {
      console.error('Could not get ID token:', error);
      // ここでエラー処理（例: ログアウトさせるなど）を行うことも可能
    }
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});



