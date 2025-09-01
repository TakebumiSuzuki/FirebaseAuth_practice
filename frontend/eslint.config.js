import pluginVue from 'eslint-plugin-vue'; // Vueのルールセットを提供するプラグイン
import vueParser from 'vue-eslint-parser'; // .vueファイルを解析するためのパーサー

export default [
  {
    // ① 対象ファイル
    files: ['**/*.js',  '**/*.vue'],

    // ② 言語の解釈方法に関する設定
    languageOptions: {
      //  ESLintは通常JavaScriptしか理解できません。そこで vue-eslint-parser を使うことで、
      // .vue ファイル特有の <template> や <script> といった構造を正しく解析できるようになります。
      // これはVueプロジェクトのESLint設定では必須の項目です。
      parser: vueParser,  // .vueファイルを解析できるようにする
      parserOptions: {
        ecmaVersion: 'latest', // 最新のJavaScript構文を許可
        sourceType: 'module'   // import/export構文を許可
      }
    },

    // ③ 使用するプラグイン
    plugins: {
      vue: pluginVue // 'eslint-plugin-vue' を有効にする
    },

    // ④ 個別のルール設定
    rules: {
      // Vueの推奨ルールをすべて取り込む
      ...pluginVue.configs.recommended.rules,

      // ↓ ここから下は個別のカスタマイズ ↓

      // コンポーネント名は複数単語にすべき、というルールを「警告(warn)」に緩和
      'vue/multi-word-component-names': 'warn',

      // console.log()などを使ってもOKにする（ルールを無効化）
      'no-console': 'off',
    }
  }
];