<template>
  <div class="snake-wrapper">
    <!-- 分數列 -->
    <div class="score-bar">
      <div class="score-item">
        <span class="label">分數</span>
        <span class="value" :class="{ 'score-pop': scorePop }">{{ score }}</span>
      </div>
      <div class="score-item">
        <span class="label">最高</span>
        <span class="value gold">{{ bestScore }}</span>
      </div>
      <div class="score-item">
        <span class="label">長度</span>
        <span class="value">{{ snake.length }}</span>
      </div>
    </div>

    <!-- 遊戲畫布 -->
    <div class="canvas-wrap" ref="canvasWrap">
      <canvas ref="canvas" class="game-canvas"
        @touchstart.prevent="onTouchStart"
        @touchend.prevent="onTouchEnd"
      ></canvas>

      <!-- 開始/結束 Overlay -->
      <Transition name="fade">
        <div v-if="gameState !== 'playing'" class="overlay">
          <div class="overlay-card">
            <template v-if="gameState === 'idle'">
              <div class="overlay-emoji">🐍</div>
              <h2>貪食蛇</h2>
              <p>吃蘋果得分，別撞牆！</p>
              <div class="controls-hint">
                <span>📱 滑動控制</span>
                <span>⌨️ 方向鍵</span>
              </div>
              <button class="btn-start" @click="startGame">開始遊戲</button>
            </template>
            <template v-else-if="gameState === 'over'">
              <div class="overlay-emoji">💀</div>
              <h2>遊戲結束</h2>
              <div class="final-score">
                <span>得分</span>
                <span class="big-score">{{ score }}</span>
              </div>
              <div v-if="isNewBest" class="new-best">🏆 新紀錄！</div>
              <button class="btn-start" @click="startGame">再玩一次</button>
              <button class="btn-board" @click="showLeaderboard = true">排行榜</button>
            </template>
          </div>
        </div>
      </Transition>
    </div>

    <!-- 手機方向控制 -->
    <div class="dpad" v-if="gameState === 'playing'">
      <div class="dpad-row">
        <button class="dpad-btn" @touchstart.prevent="setDir('UP')" @mousedown="setDir('UP')">▲</button>
      </div>
      <div class="dpad-row">
        <button class="dpad-btn" @touchstart.prevent="setDir('LEFT')" @mousedown="setDir('LEFT')">◀</button>
        <button class="dpad-btn pause" @touchstart.prevent="togglePause" @mousedown="togglePause">
          {{ paused ? '▶' : '⏸' }}
        </button>
        <button class="dpad-btn" @touchstart.prevent="setDir('RIGHT')" @mousedown="setDir('RIGHT')">▶</button>
      </div>
      <div class="dpad-row">
        <button class="dpad-btn" @touchstart.prevent="setDir('DOWN')" @mousedown="setDir('DOWN')">▼</button>
      </div>
    </div>

    <!-- 排行榜 Modal -->
    <Transition name="slide-up">
      <div v-if="showLeaderboard" class="modal-backdrop" @click.self="showLeaderboard = false">
        <div class="modal">
          <div class="modal-header">
            <h3>🏆 排行榜</h3>
            <button class="close-btn" @click="showLeaderboard = false">✕</button>
          </div>
          <div class="leaderboard">
            <div v-if="loading" class="loading">載入中...</div>
            <div v-else-if="leaderboard.length === 0" class="empty">還沒有紀錄，快來挑戰！</div>
            <div v-else v-for="(item, i) in leaderboard" :key="item.id" class="rank-item">
              <span class="rank-num">
                {{ i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : `#${i+1}` }}
              </span>
              <span class="rank-name">{{ item.user_name }}</span>
              <span class="rank-score">{{ item.score }}</span>
            </div>
          </div>
          <button class="btn-start" @click="showLeaderboard = false">關閉</button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import axios from 'axios'

const props = defineProps({ user: Object })

// === 遊戲設定 ===
const CELL = 20
const COLS = 20
const ROWS = 20

// === Refs ===
const canvas = ref(null)
const canvasWrap = ref(null)
const gameState = ref('idle') // idle | playing | over
const score = ref(0)
const bestScore = ref(0)
const scorePop = ref(false)
const paused = ref(false)
const isNewBest = ref(false)
const showLeaderboard = ref(false)
const leaderboard = ref([])
const loading = ref(false)

// === 遊戲狀態 ===
let snake = ref([{ x: 10, y: 10 }])
let food = ref({ x: 5, y: 5 })
let dir = { x: 1, y: 0 }
let nextDir = { x: 1, y: 0 }
let gameLoop = null
let ctx = null
let speed = 150

// Touch 追蹤
let touchStartX = 0, touchStartY = 0

// === 初始化畫布 ===
const initCanvas = () => {
  const wrap = canvasWrap.value
  const size = Math.min(wrap.clientWidth, 400)
  canvas.value.width = size
  canvas.value.height = size
  ctx = canvas.value.getContext('2d')
}

// === 繪製 ===
const draw = () => {
  if (!ctx) return
  const w = canvas.value.width
  const h = canvas.value.height
  const cellW = w / COLS
  const cellH = h / ROWS

  // 背景
  ctx.fillStyle = '#0d0d1a'
  ctx.fillRect(0, 0, w, h)

  // 格線（淡）
  ctx.strokeStyle = 'rgba(255,255,255,0.03)'
  ctx.lineWidth = 0.5
  for (let i = 0; i <= COLS; i++) {
    ctx.beginPath(); ctx.moveTo(i * cellW, 0); ctx.lineTo(i * cellW, h); ctx.stroke()
  }
  for (let j = 0; j <= ROWS; j++) {
    ctx.beginPath(); ctx.moveTo(0, j * cellH); ctx.lineTo(w, j * cellH); ctx.stroke()
  }

  // 蛇身
  snake.value.forEach((seg, i) => {
    const isHead = i === 0
    const alpha = isHead ? 1 : Math.max(0.3, 1 - i * 0.03)
    const x = seg.x * cellW + 1
    const y = seg.y * cellH + 1
    const sw = cellW - 2
    const sh = cellH - 2
    const r = isHead ? 6 : 4

    if (isHead) {
      // 頭部發光
      ctx.shadowBlur = 15
      ctx.shadowColor = '#a855f7'
    } else {
      ctx.shadowBlur = 0
    }

    const grad = ctx.createLinearGradient(x, y, x + sw, y + sh)
    if (isHead) {
      grad.addColorStop(0, '#a855f7')
      grad.addColorStop(1, '#7c3aed')
    } else {
      grad.addColorStop(0, `rgba(124,58,237,${alpha})`)
      grad.addColorStop(1, `rgba(88,28,220,${alpha})`)
    }
    ctx.fillStyle = grad

    ctx.beginPath()
    ctx.roundRect(x, y, sw, sh, r)
    ctx.fill()
    ctx.shadowBlur = 0
  })

  // 食物（蘋果）
  const fx = food.value.x * cellW + cellW / 2
  const fy = food.value.y * cellH + cellH / 2
  const fr = Math.min(cellW, cellH) / 2 - 2
  ctx.shadowBlur = 20
  ctx.shadowColor = '#22c55e'
  ctx.fillStyle = '#22c55e'
  ctx.beginPath()
  ctx.arc(fx, fy, fr, 0, Math.PI * 2)
  ctx.fill()
  ctx.shadowBlur = 0

  // 暫停遮罩
  if (paused.value) {
    ctx.fillStyle = 'rgba(0,0,0,0.6)'
    ctx.fillRect(0, 0, w, h)
    ctx.fillStyle = '#fff'
    ctx.font = `bold ${w * 0.1}px Outfit`
    ctx.textAlign = 'center'
    ctx.fillText('⏸ 暫停', w / 2, h / 2)
  }
}

// === 遊戲邏輯 ===
const spawnFood = () => {
  const occupied = new Set(snake.value.map(s => `${s.x},${s.y}`))
  let pos
  do {
    pos = { x: Math.floor(Math.random() * COLS), y: Math.floor(Math.random() * ROWS) }
  } while (occupied.has(`${pos.x},${pos.y}`))
  food.value = pos
}

const step = () => {
  if (paused.value) return
  dir = { ...nextDir }
  const head = snake.value[0]
  const newHead = { x: (head.x + dir.x + COLS) % COLS, y: (head.y + dir.y + ROWS) % ROWS }

  // 撞自己（只檢查身體，跳過尾巴因為它會移走）
  const hitSelf = snake.value.slice(0, -1).some(s => s.x === newHead.x && s.y === newHead.y)
  if (hitSelf) { endGame(); return }

  const ate = newHead.x === food.value.x && newHead.y === food.value.y
  const newSnake = [newHead, ...snake.value]
  if (!ate) newSnake.pop()
  else {
    score.value += 10
    scorePop.value = true
    setTimeout(() => scorePop.value = false, 300)
    if (score.value > bestScore.value) { bestScore.value = score.value; isNewBest.value = true }
    spawnFood()
    // 隨分數加速
    if (score.value % 50 === 0 && speed > 80) {
      speed = Math.max(80, speed - 10)
      restartLoop()
    }
  }
  snake.value = newSnake
  draw()
}

const restartLoop = () => {
  clearInterval(gameLoop)
  gameLoop = setInterval(step, speed)
}

const startGame = () => {
  score.value = 0
  isNewBest.value = false
  speed = 150
  snake.value = [{ x: 10, y: 10 }, { x: 9, y: 10 }, { x: 8, y: 10 }]
  dir = { x: 1, y: 0 }
  nextDir = { x: 1, y: 0 }
  spawnFood()
  paused.value = false
  gameState.value = 'playing'
  restartLoop()
  draw()
}

const endGame = () => {
  clearInterval(gameLoop)
  gameState.value = 'over'
  submitScore()
}

const togglePause = () => {
  paused.value = !paused.value
  if (!paused.value) draw()
}

// === 提交分數 ===
const submitScore = async () => {
  if (score.value === 0) return
  const u = props.user || { email: 'guest@doremi326.local', name: '遊客' }
  try {
    await axios.post('/api/scores/', {
      user_email: u.email,
      user_name: u.name,
      score: score.value,
      game: 'snake'
    })
  } catch (e) { /* 靜默失敗 */ }
}

// === 載入排行榜 ===
const fetchLeaderboard = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/scores/leaderboard?game=snake&limit=10')
    leaderboard.value = res.data
  } catch (e) { leaderboard.value = [] }
  loading.value = false
}

watch(showLeaderboard, (v) => { if (v) fetchLeaderboard() })

// === 方向控制 ===
const setDir = (d) => {
  const map = {
    UP:    { x: 0, y: -1 },
    DOWN:  { x: 0, y: 1 },
    LEFT:  { x: -1, y: 0 },
    RIGHT: { x: 1, y: 0 },
  }
  const nd = map[d]
  // 禁止反向
  if (nd.x === -dir.x && nd.y === -dir.y) return
  nextDir = nd
}

const onKeyDown = (e) => {
  if (gameState.value !== 'playing') return
  const keyMap = {
    ArrowUp: 'UP', ArrowDown: 'DOWN', ArrowLeft: 'LEFT', ArrowRight: 'RIGHT',
    w: 'UP', s: 'DOWN', a: 'LEFT', d: 'RIGHT',
  }
  if (e.key === ' ') { togglePause(); return }
  if (keyMap[e.key]) { e.preventDefault(); setDir(keyMap[e.key]) }
}

// === 觸控滑動 ===
const onTouchStart = (e) => {
  touchStartX = e.touches[0].clientX
  touchStartY = e.touches[0].clientY
}

const onTouchEnd = (e) => {
  if (gameState.value === 'idle') { startGame(); return }
  if (gameState.value !== 'playing') return
  const dx = e.changedTouches[0].clientX - touchStartX
  const dy = e.changedTouches[0].clientY - touchStartY
  if (Math.abs(dx) < 10 && Math.abs(dy) < 10) return
  if (Math.abs(dx) > Math.abs(dy)) {
    setDir(dx > 0 ? 'RIGHT' : 'LEFT')
  } else {
    setDir(dy > 0 ? 'DOWN' : 'UP')
  }
}

// === 生命週期 ===
onMounted(async () => {
  await nextTick()
  initCanvas()
  draw()
  window.addEventListener('keydown', onKeyDown)
  window.addEventListener('resize', () => { initCanvas(); draw() })

  // 載入本地最高分
  bestScore.value = parseInt(localStorage.getItem('snake_best') || '0')
})

onUnmounted(() => {
  clearInterval(gameLoop)
  window.removeEventListener('keydown', onKeyDown)
})

watch(bestScore, (v) => localStorage.setItem('snake_best', v))
</script>

<style scoped>
.snake-wrapper {
  width: 100%;
  max-width: 440px;
  padding: 0 16px 32px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

/* 分數列 */
.score-bar {
  width: 100%;
  display: flex;
  justify-content: space-around;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 12px;
  gap: 8px;
}

.score-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.label { font-size: 0.7rem; color: var(--text-dim); font-weight: 600; letter-spacing: 1px; text-transform: uppercase; }
.value { font-size: 1.5rem; font-weight: 700; }
.gold { color: var(--gold); }

.score-pop {
  animation: pop 0.3s ease;
}
@keyframes pop {
  0% { transform: scale(1); }
  50% { transform: scale(1.4); color: #22c55e; }
  100% { transform: scale(1); }
}

/* 畫布 */
.canvas-wrap {
  width: 100%;
  position: relative;
  aspect-ratio: 1;
  border-radius: var(--radius);
  overflow: hidden;
  border: 2px solid rgba(124,58,237,0.3);
  box-shadow: 0 0 30px rgba(124,58,237,0.2), inset 0 0 30px rgba(0,0,0,0.5);
}

.game-canvas {
  width: 100%;
  height: 100%;
  display: block;
  touch-action: none;
}

/* Overlay */
.overlay {
  position: absolute;
  inset: 0;
  background: rgba(10, 10, 15, 0.92);
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(8px);
}

.overlay-card {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  padding: 24px;
}

.overlay-emoji { font-size: 3.5rem; }
h2 { font-size: 1.8rem; font-weight: 700; }
p { color: var(--text-dim); font-size: 0.9rem; }

.controls-hint {
  display: flex;
  gap: 12px;
  font-size: 0.8rem;
  color: var(--text-dim);
  background: var(--surface2);
  padding: 8px 16px;
  border-radius: 999px;
}

.final-score {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}
.final-score span:first-child { font-size: 0.8rem; color: var(--text-dim); }
.big-score { font-size: 3rem; font-weight: 900; color: #a855f7; }

.new-best {
  background: linear-gradient(135deg, #f59e0b, #ef4444);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 700;
  font-size: 1.1rem;
  animation: glow 1s ease infinite alternate;
}
@keyframes glow {
  from { filter: brightness(1); }
  to { filter: brightness(1.3); }
}

.btn-start {
  background: linear-gradient(135deg, #7c3aed, #a855f7);
  color: white;
  padding: 14px 36px;
  border-radius: 999px;
  font-size: 1rem;
  font-weight: 700;
  box-shadow: 0 4px 20px rgba(124,58,237,0.4);
  width: 100%;
}
.btn-start:hover { transform: translateY(-2px); box-shadow: 0 6px 25px rgba(124,58,237,0.5); }

.btn-board {
  background: var(--surface2);
  color: var(--text-dim);
  padding: 10px 24px;
  border-radius: 999px;
  font-size: 0.9rem;
  width: 100%;
  border: 1px solid var(--border);
}

/* D-Pad */
.dpad {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.dpad-row {
  display: flex;
  gap: 4px;
}

.dpad-btn {
  width: 60px;
  height: 60px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  font-size: 1.4rem;
  color: var(--text);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 10px rgba(0,0,0,0.3);
}

.dpad-btn:active {
  background: var(--accent);
  transform: scale(0.9);
}

.dpad-btn.pause {
  background: var(--surface2);
  font-size: 1rem;
}

/* 排行榜 Modal */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.7);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: 100;
  backdrop-filter: blur(4px);
}

.modal {
  width: 100%;
  max-width: 440px;
  background: var(--surface);
  border-radius: var(--radius) var(--radius) 0 0;
  border: 1px solid var(--border);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 { font-size: 1.2rem; font-weight: 700; }

.close-btn {
  background: var(--surface2);
  color: var(--text-dim);
  width: 32px;
  height: 32px;
  border-radius: 50%;
  font-size: 0.9rem;
}

.leaderboard { display: flex; flex-direction: column; gap: 8px; }

.rank-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: var(--surface2);
  border-radius: 12px;
  border: 1px solid var(--border);
}

.rank-num { font-size: 1.2rem; width: 36px; text-align: center; }
.rank-name { flex: 1; font-weight: 600; }
.rank-score { font-weight: 700; color: var(--accent2); font-size: 1.1rem; }

.loading, .empty { text-align: center; color: var(--text-dim); padding: 20px; }

/* 動畫 */
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.slide-up-enter-active, .slide-up-leave-active { transition: all 0.3s ease; }
.slide-up-enter-from, .slide-up-leave-to { transform: translateY(100%); opacity: 0; }
</style>
