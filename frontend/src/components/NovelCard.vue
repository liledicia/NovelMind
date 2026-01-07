<template>
  <div class="novel-card">
    <!-- 装饰性背景 -->
    <div class="card-background">
      <div class="bg-paper-texture"></div>
      <div class="bg-bookmark"></div>
    </div>

    <!-- 卡片内容 - 书城风格布局 -->
    <div class="card-container">
      <!-- 左侧：封面展示 -->
      <div class="cover-section">
        <div class="book-cover-wrapper">
          <div class="book-cover-shadow"></div>
          <div class="book-cover">
            <img
              v-if="coverImageUrl && !imageError"
              :src="coverImageUrl"
              :alt="novel.title"
              class="cover-image"
              referrerPolicy="no-referrer"
              @error="handleImageError"
            />
            <div v-else class="cover-placeholder">
              <div class="placeholder-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
                  <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
                </svg>
              </div>
              <div class="placeholder-text">{{ novel.title }}</div>
              <div class="placeholder-author">{{ novel.author }}</div>
            </div>
            <div class="book-spine"></div>
          </div>
        </div>

        <!-- 来源标签 -->
        <div v-if="source" class="source-ribbon" :class="'ribbon-' + source">
          <span class="ribbon-text">{{ sourceText }}</span>
        </div>
      </div>

      <!-- 右侧：小说信息 -->
      <div class="info-section">
        <!-- 标题与作者 -->
        <div class="title-area">
          <h2 class="novel-title">{{ novel.title }}</h2>
          <div class="author-line">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="author-icon">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
            <span class="author-name">{{ novel.author || '未知作者' }}</span>
          </div>
        </div>

        <!-- 核心信息网格 -->
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">类型</span>
            <span class="info-value">{{ novel.category || '未知' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">视角</span>
            <span class="info-value">{{ novel.perspective || '未知' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">状态</span>
            <span class="info-value status" :class="novel.status === '完结' ? 'completed' : 'ongoing'">
              {{ novel.status || '未知' }}
            </span>
          </div>
          <div class="info-item">
            <span class="info-label">字数</span>
            <span class="info-value">{{ formatWordCount(novel.word_count) }}</span>
          </div>
        </div>

        <!-- 标签云 -->
        <div v-if="novel.tags" class="tags-section">
          <div class="tags-label">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="tag-icon">
              <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/>
              <line x1="7" y1="7" x2="7.01" y2="7"/>
            </svg>
            <span>标签</span>
          </div>
          <div class="tags-cloud">
            <span
              v-for="tag in parseTags(novel.tags)"
              :key="tag"
              class="tag-chip"
            >
              {{ tag }}
            </span>
          </div>
        </div>

        <!-- 统计数据 -->
        <div v-if="stats" class="stats-row">
          <div class="stat-item">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="stat-icon">
              <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>
            </svg>
            <span class="stat-value">{{ formatNumber(stats.favorite_count || 0) }}</span>
            <span class="stat-label">收藏</span>
          </div>
          <div class="stat-item">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="stat-icon">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
            <span class="stat-value">{{ formatNumber(stats.review_count || 0) }}</span>
            <span class="stat-label">评论</span>
          </div>
          <div class="stat-item">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="stat-icon">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
            </svg>
            <span class="stat-value">{{ formatNumber(stats.score || 0) }}</span>
            <span class="stat-label">积分</span>
          </div>
        </div>

        <!-- 简介 -->
        <div v-if="novel.intro" class="intro-section">
          <h4 class="intro-title">内容简介</h4>
          <p class="intro-text">{{ novel.intro }}</p>
        </div>

        <!-- 操作按钮 -->
        <div class="actions-section">
          <button @click="openOriginal" class="action-button primary">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="button-icon">
              <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
              <polyline points="15 3 21 3 21 9"/>
              <line x1="10" y1="14" x2="21" y2="3"/>
            </svg>
            前往晋江原文
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, defineProps, ref } from 'vue'
import { formatWordCount, parseTags, formatNumber, getProxiedImageUrl, getJJWXCFallbackCover } from '@/utils/formatter'

const props = defineProps({
  novel: {
    type: Object,
    required: true
  },
  stats: {
    type: Object,
    default: null
  },
  source: {
    type: String,
    default: ''
  }
})

const imageError = ref(false)

const sourceText = computed(() => {
  return props.source === 'database' ? '数据库' : '实时爬取'
})

// 使用代理处理封面图片URL
const coverImageUrl = computed(() => {
  return getProxiedImageUrl(props.novel.cover_url)
})

// 图片加载失败时的处理
const handleImageError = (event) => {
  const currentSrc = event.target.src
  const fallbackUrl = getJJWXCFallbackCover(props.novel.book_id)

  // 避免无限循环：如果已经是fallback URL还失败，就显示占位符
  if (currentSrc !== fallbackUrl && fallbackUrl) {
    console.log(`封面加载失败，尝试fallback: ${props.novel.title}`)
    event.target.src = fallbackUrl
  } else {
    // 显示占位符
    imageError.value = true
  }
}

const openOriginal = () => {
  const url = props.novel.url || `https://www.jjwxc.net/onebook.php?novelid=${props.novel.book_id}`
  window.open(url, '_blank')
}
</script>

<style scoped>
.novel-card {
  position: relative;
  margin-bottom: 50px;
  border-radius: var(--radius-xl);
  overflow: visible;
  animation: cardAppear 0.8s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes cardAppear {
  from {
    opacity: 0;
    transform: translateY(40px) scale(0.96);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* 背景装饰 */
.card-background {
  position: absolute;
  inset: 0;
  z-index: 0;
  border-radius: var(--radius-xl);
  overflow: hidden;
}

.bg-paper-texture {
  position: absolute;
  inset: 0;
  background:
    repeating-linear-gradient(
      0deg,
      transparent,
      transparent 1px,
      rgba(139, 163, 181, 0.015) 1px,
      rgba(139, 163, 181, 0.015) 2px
    ),
    linear-gradient(135deg, var(--bg-card) 0%, rgba(245, 240, 237, 0.98) 100%);
}

.bg-bookmark {
  position: absolute;
  top: 0;
  right: 80px;
  width: 40px;
  height: 80px;
  background: linear-gradient(135deg, var(--color-accent-pink), var(--color-accent-rose));
  clip-path: polygon(0 0, 100% 0, 100% 100%, 50% 85%, 0 100%);
  opacity: 0.4;
  animation: bookmarkSlide 1s ease-out 0.3s both;
}

@keyframes bookmarkSlide {
  from {
    transform: translateY(-100%);
  }
  to {
    transform: translateY(0);
  }
}

/* 卡片容器 - 左右布局 */
.card-container {
  position: relative;
  z-index: 1;
  background: var(--bg-card);
  backdrop-filter: blur(30px);
  padding: 40px;
  border: 1px solid rgba(139, 163, 181, 0.12);
  box-shadow: var(--shadow-lg);
  border-radius: var(--radius-xl);
  display: flex;
  gap: 40px;
  align-items: flex-start;
}

/* ========= 左侧封面区域 ========= */
.cover-section {
  flex-shrink: 0;
  width: 220px;
  position: relative;
}

.book-cover-wrapper {
  position: relative;
  width: 100%;
  animation: coverFloat 3s ease-in-out infinite;
}

@keyframes coverFloat {
  0%, 100% {
    transform: translateY(0) rotateY(0deg);
  }
  50% {
    transform: translateY(-8px) rotateY(-2deg);
  }
}

.book-cover-shadow {
  position: absolute;
  bottom: -12px;
  left: 10%;
  right: 10%;
  height: 20px;
  background: radial-gradient(ellipse, rgba(107, 134, 153, 0.3) 0%, transparent 70%);
  filter: blur(8px);
  animation: shadowPulse 3s ease-in-out infinite;
}

@keyframes shadowPulse {
  0%, 100% {
    opacity: 0.5;
    transform: scale(1);
  }
  50% {
    opacity: 0.8;
    transform: scale(1.1);
  }
}

.book-cover {
  position: relative;
  width: 100%;
  aspect-ratio: 3 / 4;
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: var(--shadow-book);
  background: linear-gradient(135deg, var(--color-light-blue), var(--color-soft-pink));
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.book-cover:hover {
  transform: translateY(-6px) rotateY(-5deg);
  box-shadow:
    6px 12px 32px rgba(107, 134, 153, 0.25),
    3px 6px 16px rgba(212, 181, 176, 0.15);
}

.cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: linear-gradient(135deg, var(--color-light-blue), var(--color-soft-pink));
  text-align: center;
}

.placeholder-icon {
  width: 64px;
  height: 64px;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 16px;
}

.placeholder-text {
  font-family: 'Playfair Display', 'Noto Serif SC', serif;
  font-size: 18px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.95);
  margin-bottom: 8px;
  line-height: 1.4;
  word-break: break-word;
}

.placeholder-author {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.75);
  font-weight: 400;
}

.book-spine {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 8px;
  background: linear-gradient(
    to bottom,
    rgba(0, 0, 0, 0.1),
    rgba(0, 0, 0, 0.05),
    rgba(0, 0, 0, 0.1)
  );
  box-shadow: inset 2px 0 4px rgba(0, 0, 0, 0.2);
}

/* 来源丝带标签 */
.source-ribbon {
  position: absolute;
  top: 16px;
  left: -8px;
  padding: 6px 16px 6px 12px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: white;
  box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.15);
  z-index: 10;
  animation: ribbonSlide 0.6s ease-out 0.4s both;
}

@keyframes ribbonSlide {
  from {
    transform: translateX(-100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.source-ribbon::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: -6px;
  width: 0;
  height: 0;
  border-left: 8px solid transparent;
  border-top: 6px solid rgba(0, 0, 0, 0.2);
}

.ribbon-database {
  background: linear-gradient(135deg, var(--color-primary), var(--color-dark-blue));
}

.ribbon-database::after {
  border-top-color: var(--color-dark-blue);
}

.ribbon-crawled {
  background: linear-gradient(135deg, var(--color-accent-pink), var(--color-accent-rose));
}

.ribbon-crawled::after {
  border-top-color: #C89A94;
}

/* ========= 右侧信息区域 ========= */
.info-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 标题区域 */
.title-area {
  border-bottom: 2px solid;
  border-image: linear-gradient(90deg, var(--color-secondary), var(--color-accent-pink), transparent) 1;
  padding-bottom: 20px;
}

.novel-title {
  font-family: 'Playfair Display', 'Noto Serif SC', serif;
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 12px 0;
  letter-spacing: 0.5px;
  line-height: 1.3;
}

.author-line {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  color: var(--text-secondary);
}

.author-icon {
  width: 18px;
  height: 18px;
  color: var(--color-primary);
}

.author-name {
  font-weight: 500;
}

/* 信息网格 */
.info-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  padding: 20px;
  background: linear-gradient(135deg, var(--bg-overlay), rgba(212, 181, 176, 0.02));
  border-radius: var(--radius-lg);
  border: 1px solid rgba(139, 163, 181, 0.08);
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.info-label {
  font-size: 11px;
  color: var(--text-muted);
  font-weight: 600;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.info-value {
  font-size: 15px;
  color: var(--text-primary);
  font-weight: 600;
}

.info-value.status {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.5px;
  width: fit-content;
}

.status.completed {
  background: linear-gradient(135deg, rgba(139, 163, 181, 0.15), rgba(164, 184, 196, 0.2));
  color: var(--color-dark-blue);
}

.status.ongoing {
  background: linear-gradient(135deg, rgba(212, 181, 176, 0.15), rgba(229, 201, 196, 0.2));
  color: #A67C77;
}

/* 标签区域 */
.tags-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.tags-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
}

.tag-icon {
  width: 16px;
  height: 16px;
  color: var(--color-accent-pink);
}

.tags-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-chip {
  padding: 6px 14px;
  background: rgba(164, 184, 196, 0.1);
  border: 1px solid rgba(164, 184, 196, 0.25);
  border-radius: 20px;
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  cursor: default;
}

.tag-chip:hover {
  background: rgba(212, 181, 176, 0.15);
  border-color: var(--color-accent-pink);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(212, 181, 176, 0.2);
}

/* 统计数据行 */
.stats-row {
  display: flex;
  gap: 24px;
  padding: 16px 0;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: linear-gradient(135deg, rgba(139, 163, 181, 0.05), rgba(212, 181, 176, 0.05));
  border-radius: var(--radius-md);
  border: 1px solid rgba(139, 163, 181, 0.1);
  flex: 1;
  transition: all 0.3s ease;
}

.stat-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(139, 163, 181, 0.15);
  border-color: var(--color-secondary);
}

.stat-icon {
  width: 24px;
  height: 24px;
  color: var(--color-primary);
  flex-shrink: 0;
}

.stat-value {
  font-family: 'Playfair Display', serif;
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin-right: 4px;
}

.stat-label {
  font-size: 11px;
  color: var(--text-muted);
  font-weight: 500;
  letter-spacing: 0.5px;
}

/* 简介区域 */
.intro-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.intro-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  position: relative;
  padding-left: 16px;
}

.intro-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 20px;
  background: linear-gradient(180deg, var(--color-secondary), var(--color-accent-pink));
  border-radius: 2px;
}

.intro-text {
  font-size: 14px;
  line-height: 1.9;
  color: var(--text-secondary);
  white-space: pre-wrap;
  max-height: 160px;
  overflow-y: auto;
  padding: 20px;
  background: rgba(245, 240, 237, 0.6);
  border-radius: var(--radius-md);
  border: 1px solid rgba(139, 163, 181, 0.08);
}

.intro-text::-webkit-scrollbar {
  width: 5px;
}

.intro-text::-webkit-scrollbar-track {
  background: rgba(139, 163, 181, 0.05);
  border-radius: 3px;
}

.intro-text::-webkit-scrollbar-thumb {
  background: var(--color-secondary);
  border-radius: 3px;
}

.intro-text::-webkit-scrollbar-thumb:hover {
  background: var(--color-primary);
}

/* 操作按钮 */
.actions-section {
  display: flex;
  justify-content: flex-start;
  gap: 16px;
  padding-top: 8px;
}

.action-button {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 14px 28px;
  border: none;
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  position: relative;
  overflow: hidden;
  font-family: 'DM Sans', sans-serif;
}

.action-button::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  transform: translate(-50%, -50%);
  transition: width 0.6s ease, height 0.6s ease;
}

.action-button:hover::before {
  width: 300px;
  height: 300px;
}

.action-button.primary {
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent-pink));
  color: white;
  box-shadow: 0 4px 16px rgba(139, 163, 181, 0.3);
}

.action-button.primary:hover {
  box-shadow: 0 8px 24px rgba(139, 163, 181, 0.4);
  transform: translateY(-3px);
}

.action-button.primary:active {
  transform: translateY(-1px);
}

.button-icon {
  width: 16px;
  height: 16px;
  position: relative;
  z-index: 1;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .card-container {
    flex-direction: column;
    align-items: center;
  }

  .cover-section {
    width: 200px;
  }

  .info-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .stats-row {
    flex-direction: column;
  }
}

@media (max-width: 768px) {
  .card-container {
    padding: 24px;
    gap: 28px;
  }

  .cover-section {
    width: 160px;
  }

  .novel-title {
    font-size: 24px;
  }

  .info-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
    padding: 16px;
  }

  .tags-cloud {
    gap: 6px;
  }

  .tag-chip {
    font-size: 11px;
    padding: 5px 12px;
  }
}
</style>
