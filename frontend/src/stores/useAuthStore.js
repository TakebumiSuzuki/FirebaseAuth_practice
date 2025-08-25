import { defineStore } from "pinia";
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', ()=>{

  const user = ref(null)

  const isLoggedin = computed(()=> Boolean(user.value))

  const isAdminClaim = ref(false)
  const isAdmin = computed(() => isAdminClaim.value)

  const setUser = async (newUser) => {
    user.value = newUser

    if (newUser){
      try {
        // forceRefresh: true により、現在キャッシュされているIDトークンを無視して、Firebaseの認証サーバーに
        // 新しいIDトークンを強制的に要求。これは、バックエンドで設定されたカスタムクレーム（例：管理者権限）の変更を
        // 即座にクライアント側に反映させるため。
        // 例えば、ユーザーがログインした直後に、Cloud Functionsなどで管理者権限（カスタムクレーム）が付与された場合、
        // getIdTokenResult(true)を呼ばないと、その権限がクライアントに反映されるのは最大1時間後
        // （IDトークンの自然な有効期限が切れた後）になってしまいます
        const idTokenResult = await newUser.getIdTokenResult(true);
        // カスタムクレームは "claims" オブジェクトの中にある
        isAdminClaim.value = idTokenResult.claims.is_admin === true;

      } catch (error) {
        console.error("管理者権限の取得に失敗しました:", error);
        isAdminClaim.value = false;
      }
    } else {
      isAdminClaim.value = false;
    }
  }

  return {
    user,
    isLoggedin,
    isAdmin,
    setUser
  }
})

/*
getIdTokenResult() を呼び出した場合（デフォルトは false )、キャッシュされていて、まだ有効期限が切れていないIDトークンがあれば、
それを使ってIdTokenResultオブジェクトを返す
* Firebase Auth SDKは、パフォーマンス向上のために、一度取得したIDトークンをクライアント側（ブラウザ内）に
キャッシュします。IDトークンの有効期限は1時間です。

1. もし有効期限内のトークンがキャッシュにあれば、Firebaseサーバーに通信することなく、そのキャッシュされたトークン情報から
IdTokenResultオブジェクトを生成して即座に返します。

2. もしトークンがキャッシュにない、または有効期限が切れている場合は、SDKが内部に持っている「更新トークン」を使って、
Firebaseサーバーに新しいIDトークンを自動的にリクエストします。そして、新しく取得したトークンをキャッシュし、
その情報からIdTokenResultオブジェクトを生成して返します。
*/

/*

[ signInWith... や onAuthStateChanged などのメソッド　で受け取るuserオブジェクト ]
→ Firebase Authenticationの Userオブジェクト

  主な目的: ユーザーのアカウントそのものを表します。

  情報の由来: Firebase Authenticationの永続的なユーザーデータベース

  主な情報:
  uid: ユーザーの一意なID
  email: メールアドレス
  displayName: 表示名
  photoURL: プロフィール写真のURL
  emailVerified: メールアドレスが確認済みかどうか
  providerData: どの認証プロバイダ（Google, Facebookなど）でログインしたかの情報

  情報の性質: 比較的静的なプロフィール情報です。ユーザーがプロフィールを更新しない限り、内容はあまり変わりません。
  ＊このオブジェクト自体には、カスタムクレームは直接含まれていません。



[ getIdTokenResult()で取得する IdTokenResult オブジェクト ]
→ UserオブジェクトのメソッドであるgetIdTokenResult()を呼び出して取得するのは、IdTokenResultオブジェクト

  主な目的: 現在の認証セッションと、そのユーザーに与えられた権限（クレーム）を表します。

  情報の由来: IDトークン (JWT) の中身。IdTokenResultオブジェクトの中にあるclaimsプロパティは、
  このJWTのペイロード部分をデコード（Base64デコードとJSONパース）して、使いやすいJavaScriptオブジェクトにしたもの

  主な情報:
  token: IDトークン（JWT）文字列。バックエンドのAPIにリクエストを送る際の認証に使います。
  claims: デコードされたIDトークンの内容。カスタムクレームを含みます。
  expirationTime: トークンの有効期限

  情報の性質: 動的なセッション情報です。トークンは1時間ごとに自動で更新されますし、getIdTokenResult(true)を使えばいつでも強制的に最新の状態（最新のカスタムクレーム）を取得できます。


例えていうと、Userオブジェクトは、身分証明書（名前や住所が書いてある）
IdTokenResultオブジェクトは、イベントの入場チケット（「VIPエリア入場可」(=カスタムクレーム) と書いてあり、有効期限がある）

あなたのコードは、まずsetUser(newUser)で身分証明書 (newUserオブジェクト)を受け取り、
その身分証明書を使って最新の入場チケット (getIdTokenResult) を発行してもらい、
「VIPエリア入場可 (is_admin: true)」かどうかを確認している、という流れになります。


IdTokenResultオブジェクトは以下のような構造
  {
    // ...その他のプロパティ
    token: "eyJhbGciOiJSUzI1NiIsImtpZCI6...", // IDトークン（JWT）の文字列そのもの

    claims: {
      // ▼▼▼ Firebaseが標準で設定するクレーム ▼▼▼
      "aud": "my-firebase-project-id",
      "auth_time": 1678886400,
      "exp": 1678890000, // トークンの有効期限 (Unixタイムスタンプ)
      "iat": 1678886400, // トークンの発行日時 (Unixタイムスタンプ)
      "iss": "https://securetoken.google.com/my-firebase-project-id",
      "sub": "USER_UID_HERE", // ユーザーのUID
      "user_id": "USER_UID_HERE",
      // ...など

      // ▼▼▼ あなたが設定したカスタムクレーム ▼▼▼
      "is_admin": true,
      "premium_level": "gold"
    }

  }

*/