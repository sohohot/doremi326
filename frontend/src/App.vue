<template>
  <div class="app-wrapper">
    <header class="header">
      <div class="logo">🎮 <span>Doremi326</span></div>
      <div class="user-area">
        <!-- 已登入 -->
        <template v-if="user">
          <div class="user-chip">
            <span class="user-avatar">{{ user.name?.[0] ?? '?' }}</span>
            <span class="username">{{ user.name }}</span>
          </div>
          <button class="btn-ghost" @click="logout">登出</button>
        </template>

        <!-- 未登入 -->
        <template v-else>
          <!-- Google GSI 按鈕（永遠渲染，GSI 會注入進去）-->
          <div id="google-btn" class="google-btn-wrap"></div>

          <!-- Dev 模式 fallback -->
          <button v-if="isDevMode" class="btn-dev" @click="devLogin">
            🧪 Dev 登入
          </button>
        </template>
      </div>
    </header>

    <main class="main">
      <SnakeGame :user="user" />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import SnakeGame from './components/SnakeGame.vue'
import axios from 'axios'

const user = ref(null)
const isDevMode = import.meta.env.VITE_DEV_BYPASS_AUTH === 'true'
const CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID

// === Google OAuth 回呼 ===
const handleGoogleCallback = async (response) => {
  try {
    const res = await axios.post('/api/auth/google', { token: response.credential })
    setUser({ email: res.data.user_email, name: res.data.user_name, token: res.data.access_token })
  } catch (e) {
    console.error('Google login failed:', e)
  }
}

// === 初始化 Google GSI ===
const initGoogle = () => {
  if (!CLIENT_ID) {
    console.warn('[OAuth] VITE_GOOGLE_CLIENT_ID not set')
    return
  }
  if (!window.google?.accounts?.id) {
    setTimeout(initGoogle, 300)
    return
  }

  window.google.accounts.id.initialize({
    client_id: CLIENT_ID,
    callback: handleGoogleCallback,
    auto_select: false,
  })

  // 等 DOM 確保 #google-btn 存在
  nextTick(() => {
    const el = document.getElementById('google-btn')
    if (el) {
      window.google.accounts.id.renderButton(el, {
        type: 'standard',
        shape: 'pill',
        theme: 'filled_black',
        text: 'signin_with',
        size: 'medium',
        locale: 'zh-TW',
      })
      console.log('[OAuth] Google button rendered')
    } else {
      console.warn('[OAuth] #google-btn element not found')
    }
  })
}

// === Dev 模式登入 ===
const devLogin = async () => {
  try {
    const res = await axios.get('/api/auth/dev-login')
    setUser({ email: res.data.user_email, name: res.data.user_name, token: res.data.access_token })
  } catch (e) {
    console.error('Dev login failed:', e)
  }
}

const setUser = (u) => {
  user.value = u
  localStorage.setItem('doremi_user', JSON.stringify(u))
}

const logout = () => {
  user.value = null
  localStorage.removeItem('doremi_user')
  window.google?.accounts?.id?.disableAutoSelect?.()
  // 重新渲染按鈕
  nextTick(initGoogle)
}

onMounted(async () => {
  // 恢復已登入狀態
  const saved = localStorage.getItem('doremi_user')
  if (saved) {
    try { user.value = JSON.parse(saved) } catch {}
  }

  // 初始化 Google（等 DOM ready）
  await nextTick()
  if (!user.value) initGoogle()
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
  min-height: 56px;
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
  min-width: 160px;
  justify-content: flex-end;
}

/* Google 按鈕容器 - 永遠在 DOM 裡 */
.google-btn-wrap {
  min-width: 160px;
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
  font-size: 0.9rem;
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

.btn-ghost {
  background: transparent;
  color: var(--text-dim);
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 0.8rem;
  border: 1px solid var(--border);
}

.btn-dev {
  background: linear-gradient(135deg, #7c3aed, #a855f7);
  color: white;
  padding: 8px 16px;
  border-radius: 999px;
  font-size: 0.85rem;
  font-weight: 600;
}

.main {
  flex: 1;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}
</style>
