import pluginVue from 'eslint-plugin-vue';
import vueParser from 'vue-eslint-parser';

export default [
  {
    files: ['**/*.js',  '**/*.vue'],
    languageOptions: {
      parser: vueParser,  // vue-eslint-parserを明示的に指定
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module'
      }
    },
    plugins: {
      vue: pluginVue
    },
    rules: {
      ...pluginVue.configs.recommended.rules,
      'vue/multi-word-component-names': 'warn',
      'no-console': 'off',
    }
  }
];