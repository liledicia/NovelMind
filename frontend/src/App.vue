<template>
  <div id="app">
    <div class="app-background">
      <div class="bg-gradient"></div>
      <div class="bg-texture"></div>
      <div class="floating-shapes">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
        <div class="shape shape-3"></div>
      </div>
    </div>

    <el-container class="app-container">
      <el-header class="app-header">
        <div class="header-content">
          <div class="logo-section">
            <div class="logo-icon">
              <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                <path d="M20,30 L50,15 L80,30 L80,70 L50,85 L20,70 Z" fill="none" stroke="currentColor" stroke-width="3"/>
                <path d="M35,40 L65,40 M35,50 L65,50 M35,60 L55,60" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
              </svg>
            </div>
            <div class="logo-text">
              <h1>NovelMind</h1>
              <p class="subtitle">晋江小说·智能推荐引擎</p>
            </div>
          </div>

          <div class="header-decoration">
            <div class="deco-line"></div>
          </div>
        </div>
      </el-header>

      <el-main class="app-main">
        <Home />
      </el-main>

      <el-footer class="app-footer">
        <div class="footer-content">
          <div class="footer-left">
            <span class="footer-brand">NovelMind</span>
            <span class="footer-divider">•</span>
            <span>基于深度学习的推荐算法</span>
          </div>
          <div class="footer-right">
            <span>© 2026 All Rights Reserved</span>
          </div>
        </div>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup>
import Home from './views/Home.vue'
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600;700&family=Noto+Serif+SC:wght@400;600;700&display=swap');

:root {
  /* 莫兰迪蓝粉色调 */
  --color-primary: #8BA3B5;
  --color-secondary: #A4B8C4;
  --color-accent-pink: #D4B5B0;
  --color-accent-rose: #E5C9C4;
  --color-dark-blue: #6B8699;
  --color-light-blue: #C5D5E0;
  --color-soft-pink: #F0E5E3;
  --color-warm-beige: #F5F0ED;

  /* 文字颜色 */
  --text-primary: #2C3E50;
  --text-secondary: #5D6D7E;
  --text-muted: #95A5A6;
  --text-light: #ffffff;
  --text-accent: #8BA3B5;

  /* 背景颜色 */
  --bg-primary: #FDFBF9;
  --bg-secondary: #F5F0ED;
  --bg-card: rgba(253, 251, 249, 0.98);
  --bg-overlay: rgba(139, 163, 181, 0.03);

  /* 间距 */
  --spacing-xs: 0.5rem;
  --spacing-sm: 1rem;
  --spacing-md: 1.5rem;
  --spacing-lg: 2rem;
  --spacing-xl: 3rem;

  /* 圆角 */
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 14px;
  --radius-xl: 20px;

  /* 阴影 - 柔和细腻 */
  --shadow-sm: 0 2px 12px rgba(139, 163, 181, 0.08);
  --shadow-md: 0 4px 20px rgba(139, 163, 181, 0.12);
  --shadow-lg: 0 8px 32px rgba(139, 163, 181, 0.15);
  --shadow-xl: 0 16px 48px rgba(139, 163, 181, 0.18);
  --shadow-book: 4px 8px 24px rgba(107, 134, 153, 0.2),
                 2px 4px 12px rgba(212, 181, 176, 0.1);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: 'DM Sans', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
}

.app-background {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 0;
}

.bg-gradient {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background:
    linear-gradient(165deg,
      var(--bg-primary) 0%,
      var(--color-soft-pink) 30%,
      var(--color-light-blue) 60%,
      var(--color-warm-beige) 100%
    );
}

.bg-texture {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image:
    radial-gradient(circle at 20% 30%, rgba(164, 184, 196, 0.08) 0%, transparent 50%),
    radial-gradient(circle at 80% 70%, rgba(212, 181, 176, 0.08) 0%, transparent 50%),
    repeating-linear-gradient(
      0deg,
      transparent,
      transparent 2px,
      rgba(139, 163, 181, 0.01) 2px,
      rgba(139, 163, 181, 0.01) 4px
    );
  opacity: 0.7;
}

.floating-shapes {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
  pointer-events: none;
}

.shape {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  animation: float 25s ease-in-out infinite;
  opacity: 0.12;
}

.shape-1 {
  width: 450px;
  height: 450px;
  background: radial-gradient(circle, var(--color-secondary) 0%, transparent 70%);
  top: -120px;
  left: -120px;
  animation-delay: 0s;
}

.shape-2 {
  width: 550px;
  height: 550px;
  background: radial-gradient(circle, var(--color-accent-pink) 0%, transparent 70%);
  bottom: -180px;
  right: -180px;
  animation-delay: -8s;
}

.shape-3 {
  width: 380px;
  height: 380px;
  background: radial-gradient(circle, var(--color-accent-rose) 0%, transparent 70%);
  top: 45%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation-delay: -16s;
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(50px, -30px) scale(1.1);
  }
  66% {
    transform: translate(-30px, 40px) scale(0.95);
  }
}

.app-container {
  position: relative;
  z-index: 1;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: rgba(253, 251, 249, 0.92);
  backdrop-filter: blur(24px) saturate(180%);
  border-bottom: 1px solid rgba(139, 163, 181, 0.12);
  padding: 24px 40px !important;
  height: auto !important;
  box-shadow: 0 2px 16px rgba(139, 163, 181, 0.06);
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logo-icon {
  width: 50px;
  height: 50px;
  color: var(--color-primary);
  animation: logoFloat 3s ease-in-out infinite;
}

@keyframes logoFloat {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-5px) rotate(2deg);
  }
}

.logo-text h1 {
  font-family: 'Playfair Display', 'Noto Serif SC', serif;
  font-size: 38px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-accent-pink) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 0.5px;
  margin: 0;
  line-height: 1.2;
}

.subtitle {
  font-family: 'DM Sans', 'PingFang SC', sans-serif;
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 400;
  letter-spacing: 3px;
  margin-top: 4px;
  text-transform: uppercase;
  opacity: 0.8;
}

.header-decoration {
  display: flex;
  align-items: center;
  gap: 8px;
}

.deco-line {
  width: 80px;
  height: 2px;
  background: linear-gradient(90deg, transparent 0%, var(--color-accent-pink) 50%, transparent 100%);
  animation: lineGlow 2s ease-in-out infinite;
}

@keyframes lineGlow {
  0%, 100% {
    opacity: 0.4;
  }
  50% {
    opacity: 0.9;
  }
}

.app-main {
  flex: 1;
  padding: 60px 40px !important;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
}

.app-footer {
  background: rgba(139, 163, 181, 0.04);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(139, 163, 181, 0.1);
  padding: 24px 40px !important;
  height: auto !important;
}

.footer-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  color: var(--text-secondary);
}

.footer-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.footer-brand {
  font-family: 'Playfair Display', serif;
  font-weight: 600;
  color: var(--color-primary);
  font-size: 16px;
}

.footer-divider {
  color: var(--text-muted);
}

.footer-right {
  font-size: 13px;
  color: var(--text-muted);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .app-header {
    padding: 20px !important;
  }

  .header-content {
    flex-direction: column;
    gap: 16px;
  }

  .logo-text h1 {
    font-size: 28px;
  }

  .subtitle {
    font-size: 12px;
  }

  .header-decoration {
    display: none;
  }

  .app-main {
    padding: 30px 20px !important;
  }

  .footer-content {
    flex-direction: column;
    gap: 12px;
    text-align: center;
  }

  .shape {
    display: none;
  }
}
</style>
