<template>
  <div class="app-wrapper">
    <header class="header">
      <div class="logo">🎮 <span>Doremi326</span></div>
      <div class="user-area">
        <template v-if="user">
          <div class="user-chip">
            <span class="user-avatar">{{ user.name[0] }}</span>
            <span class="username">{{ user.name }}</span>
          </div>
          <button class="btn-ghost" @click="logout">登出</button>
        </template>
        <template v-else>
          <!-- 真正的 Google 登入按鈕（由 GSI 渲染）-->
          <div v-if="googleReady" id="google-btn"></div>
          <!-- 本地開發 fallback -->
          <button v-else-if="isDevMode" class="btn-login" @click="devLogin">
            🧪 Dev 登入
          </button>
          <span v-else class="login-hint">載入登入中...</span>
        </template>
      </div>
    </header>

    <main class="main">
      <SnakeGame :user="user" />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import SnakeGame from './components/SnakeGame.vue'
import axios from 'axios'

const user = ref(null)
const googleReady = ref(false)
const isDevMode = import.meta.env.VITE_DEV_BYPASS_AUTH === 'true'
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID

// === 本地 Dev 登入（DEV_BYPASS_AUTH=true 時用）===
const devLogin = async () => {
  try {
    const res = await axios.get('/api/auth/dev-login')
    setUser({ email: res.data.user_email, name: res.data.user_name, token: res.data.access_token })
  } catch (e) {
    console.error('Dev login failed', e)
    alert('Dev 登入失敗，確認後端 DEV_BYPASS_AUTH=true')
  }
}

// === 設定 user 狀態 ===
const setUser = (u) => {
  user.value = u
  localStorage.setItem('doremi_user', JSON.stringify(u))
}

const logout = () => {
  user.value = null
  localStorage.removeItem('doremi_user')
  // 重設 Google one-tap
  if (window.google?.accounts?.id) {
    window.google.accounts.id.disableAutoSelect()
  }
}

// === Google OAuth 回呼 ===
const handleGoogleCallback = async (response) => {
  const idToken = response.credential
  try {
    const res = await axios.post('/api/auth/google', { token: idToken })
    setUser({
      email: res.data.user_email,
      name: res.data.user_name,
      token: res.data.access_token,
    })
  } catch (e) {
    console.error('Google login failed', e)
    alert('登入失敗，請稍後再試')
  }
}

// === 初始化 Google GSI ===
const initGoogle = () => {
  if (!window.google?.accounts?.id) {
    // GSI 還沒載入，等一下再試
    setTimeout(initGoogle, 300)
    return
  }
  if (!GOOGLE_CLIENT_ID) {
    console.warn('VITE_GOOGLE_CLIENT_ID not set, Google login disabled')
    return
  }

  window.google.accounts.id.initialize({
    client_id: GOOGLE_CLIENT_ID,
    callback: handleGoogleCallback,
    auto_select: false,
    cancel_on_tap_outside: true,
  })

  // 渲染登入按鈕
  const btnEl = document.getElementById('google-btn')
  if (btnEl) {
    window.google.accounts.id.renderButton(btnEl, {
      type: 'standard',
      shape: 'pill',
      theme: 'filled_black',
      text: 'signin_with',
      size: 'medium',
      logo_alignment: 'left',
      locale: 'zh-TW',
    })
  }

  googleReady.value = true
}

onMounted(() => {
  // 恢復已登入狀態
  const saved = localStorage.getItem('doremi_user')
  if (saved) {
    try { user.value = JSON.parse(saved) } catch {}
  }

  // 初始化 Google
  if (!isDevMode && GOOGLE_CLIENT_ID) {
    initGoogle()
  }
})
</script>

<style scoped>
.app-wrapper {
  width: 100%;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
  padding: 14px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 1.3rem;
  font-weight: 700;
  background: linear-gradient(135deg, #a855f7, #7c3aed);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.user-area {
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 36px;
}

.user-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 4px 12px 4px 4px;
}

.user-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, #7c3aed, #a855f7);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 700;
  color: white;
}

.username {
  font-size: 0.85rem;
  color: var(--text-dim);
  max-width: 90px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.btn-login {
  background: linear-gradient(135deg, #7c3aed, #a855f7);
  color: white;
  padding: 8px 16px;
  border-radius: 999px;
  font-size: 0.85rem;
  font-weight: 600;
  box-shadow: 0 4px 15px rgba(124,58,237,0.4);
}

.btn-ghost {
  background: transparent;
  color: var(--text-dim);
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 0.8rem;
  border: 1px solid var(--border);
}

.login-hint {
  font-size: 0.8rem;
  color: var(--text-dim);
}

/* Google 按鈕容器 */
#google-btn {
  min-width: 160px;
}

.main {
  flex: 1;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}
</style>
