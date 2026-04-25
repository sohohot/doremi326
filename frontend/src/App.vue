<template>
  <div class="app-wrapper">
    <header class="header">
      <div class="logo">🎮 <span>Doremi326</span></div>
      <div class="user-area">
        <template v-if="user">
          <img v-if="user.avatar" :src="user.avatar" class="avatar" />
          <span class="username">{{ user.name }}</span>
          <button class="btn-ghost" @click="logout">登出</button>
        </template>
        <template v-else>
          <button class="btn-login" @click="devLogin">
            <span>🎯 遊客登入</span>
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
import { ref, onMounted } from 'vue'
import SnakeGame from './components/SnakeGame.vue'
import axios from 'axios'

const user = ref(null)

const devLogin = async () => {
  try {
    const res = await axios.get('/api/auth/dev-login')
    user.value = {
      email: res.data.user_email,
      name: res.data.user_name,
      token: res.data.access_token,
    }
    localStorage.setItem('doremi_user', JSON.stringify(user.value))
  } catch (e) {
    console.error('Login failed', e)
  }
}

const logout = () => {
  user.value = null
  localStorage.removeItem('doremi_user')
}

onMounted(() => {
  const saved = localStorage.getItem('doremi_user')
  if (saved) user.value = JSON.parse(saved)
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
  padding: 16px 20px;
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
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 2px solid var(--accent);
}

.username {
  font-size: 0.9rem;
  color: var(--text-dim);
  max-width: 100px;
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

.btn-login:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(124,58,237,0.5);
}

.btn-ghost {
  background: transparent;
  color: var(--text-dim);
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 0.8rem;
  border: 1px solid var(--border);
}

.main {
  flex: 1;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}
</style>
