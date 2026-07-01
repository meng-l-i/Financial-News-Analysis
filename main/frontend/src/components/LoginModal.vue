<template>
  <div class="modal-overlay" v-if="visible">
    <div class="modal">
      <h2>CC Platform</h2>
      <p class="modal-sub">请输入账号密码登录</p>
      <form @submit.prevent="handleLogin">
        <label>
          <span>账号</span>
          <input v-model="username" type="text" autocomplete="username" />
        </label>
        <label>
          <span>密码</span>
          <input v-model="password" type="password" autocomplete="current-password" />
        </label>
        <p v-if="errorMsg" class="login-error">{{ errorMsg }}</p>
        <button type="submit" :disabled="loading">
          {{ loading ? '登录中...' : '登 录' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { login, setToken } from '../api/index.js'

export default {
  name: 'LoginModal',
  emits: ['logged-in'],
  setup(props, { emit }) {
    const visible = ref(true)
    const username = ref('root')
    const password = ref('root')
    const loading = ref(false)
    const errorMsg = ref('')

    async function handleLogin() {
      loading.value = true
      errorMsg.value = ''
      try {
        const res = await login(username.value, password.value)
        if (res.code === 200 && res.token) {
          setToken(res.token)
          visible.value = false
          emit('logged-in', res.token)
        } else {
          errorMsg.value = res.message || '登录失败'
        }
      } catch (e) {
        errorMsg.value = '网络错误: ' + e.message
      } finally {
        loading.value = false
      }
    }

    return { visible, username, password, loading, errorMsg, handleLogin }
  },
}
</script>
