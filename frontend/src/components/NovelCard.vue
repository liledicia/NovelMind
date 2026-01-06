<template>
  <div class="novel-card">
    <!-- 装饰性背景 -->
    <div class="card-background">
      <div class="bg-pattern"></div>
      <div class="bg-shine"></div>
    </div>

    <!-- 卡片内容 -->
    <div class="card-container">
      <!-- 头部区域 -->
      <div class="card-header">
        <div class="title-section">
          <div class="title-decoration">
            <span class="deco-bracket">[</span>
            <h2 class="novel-title">{{ novel.title }}</h2>
            <span class="deco-bracket">]</span>
          </div>
          <div v-if="source" class="source-badge" :class="'badge-' + source">
            <span class="badge-dot"></span>
            <span class="badge-text">{{ sourceText }}</span>
          </div>
        </div>

        <!-- 作者信息 -->
        <div class="author-section">
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
        <div class="info-item">
          <span class="info-label">章节</span>
          <span class="info-value">{{ novel.chapter_count || 0 }} 章</span>
        </div>
        <div class="info-item">
          <span class="info-label">更新</span>
          <span class="info-value">{{ formatUpdateTime(novel.last_update_time) }}</span>
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
      <div v-if="stats" class="stats-section">
        <div class="stat-card">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="stat-icon">
            <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>
          </svg>
          <div class="stat-info">
            <span class="stat-value">{{ formatNumber(stats.favorite_count || 0) }}</span>
            <span class="stat-label">收藏</span>
          </div>
        </div>
        <div class="stat-card">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="stat-icon">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
          <div class="stat-info">
            <span class="stat-value">{{ formatNumber(stats.review_count || 0) }}</span>
            <span class="stat-label">评论</span>
          </div>
        </div>
        <div class="stat-card">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="stat-icon">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
          </svg>
          <div class="stat-info">
            <span class="stat-value">{{ formatNumber(stats.score || 0) }}</span>
            <span class="stat-label">积分</span>
          </div>
        </div>
      </div>

      <!-- 简介 -->
      <div v-if="novel.intro" class="intro-section">
        <h4 class="intro-title">
          <span class="title-line"></span>
          内容简介
          <span class="title-line"></span>
        </h4>
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
</template>

<script setup>
import { computed, defineProps } from 'vue'
import { formatWordCount, parseTags, formatNumber } from '@/utils/formatter'

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

const sourceText = computed(() => {
  return props.source === 'database' ? '数据库加载' : '实时爬取'
})

const formatUpdateTime = (time) => {
  if (!time) return '未知'
  return time.split(' ')[0]
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
  overflow: hidden;
  animation: cardEnter 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes cardEnter {
  from {
    opacity: 0;
    transform: translateY(30px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.card-background {
  position: absolute;
  inset: 0;
  z-index: 0;
}

.bg-pattern {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(135deg, rgba(5, 150, 105, 0.03) 0%, rgba(16, 185, 129, 0.05) 100%),
    repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(5, 150, 105, 0.01) 10px, rgba(5, 150, 105, 0.01) 20px);
}

.bg-shine {
  position: absolute;
  top: -50%;
  left: -50%;
  right: -50%;
  bottom: -50%;
  background: radial-gradient(circle, rgba(16, 185, 129, 0.1) 0%, transparent 70%);
  animation: shineRotate 20s linear infinite;
}

@keyframes shineRotate {
  to {
    transform: rotate(360deg);
  }
}

.card-container {
  position: relative;
  z-index: 1;
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  padding: 40px;
  border: 1px solid rgba(5, 150, 105, 0.08);
  box-shadow: var(--shadow-lg);
}

.card-header {
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 2px solid transparent;
  border-image: linear-gradient(90deg, transparent, var(--color-secondary), transparent) 1;
}

.title-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 16px;
}

.title-decoration {
  display: flex;
  align-items: center;
  gap: 12px;
}

.deco-bracket {
  font-family: 'Crimson Pro', serif;
  font-size: 32px;
  font-weight: 700;
  color: var(--color-secondary);
  opacity: 0.5;
  animation: bracketPulse 3s ease-in-out infinite;
}

.deco-bracket:first-child {
  animation-delay: 0s;
}

.deco-bracket:last-child {
  animation-delay: 1.5s;
}

@keyframes bracketPulse {
  0%, 100% {
    opacity: 0.3;
    transform: scaleY(1);
  }
  50% {
    opacity: 0.7;
    transform: scaleY(1.1);
  }
}

.novel-title {
  font-family: 'Crimson Pro', 'Noto Serif SC', serif;
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  letter-spacing: 1px;
  position: relative;
}

.source-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  letter-spacing: 0.5px;
  animation: badgeSlideIn 0.5s ease-out 0.3s both;
}

@keyframes badgeSlideIn {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.badge-database {
  background: linear-gradient(135deg, rgba(67, 160, 71, 0.1), rgba(56, 142, 60, 0.15));
  border: 1px solid rgba(67, 160, 71, 0.3);
  color: #2e7d32;
}

.badge-crawled {
  background: linear-gradient(135deg, rgba(25, 118, 210, 0.1), rgba(21, 101, 192, 0.15));
  border: 1px solid rgba(25, 118, 210, 0.3);
  color: #1565c0;
}

.badge-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
  animation: dotPulse 2s ease-in-out infinite;
}

@keyframes dotPulse {
  0%, 100% {
    opacity: 0.5;
  }
  50% {
    opacity: 1;
  }
}

.author-section {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  color: var(--text-secondary);
}

.author-icon {
  width: 20px;
  height: 20px;
  color: var(--color-secondary);
}

.author-name {
  font-weight: 500;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
  padding: 24px;
  background: rgba(5, 150, 105, 0.02);
  border-radius: var(--radius-lg);
  border: 1px dashed rgba(5, 150, 105, 0.1);
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.info-label {
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 500;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

.info-value {
  font-size: 16px;
  color: var(--text-primary);
  font-weight: 600;
}

.info-value.status {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.status.completed {
  background: linear-gradient(135deg, rgba(67, 160, 71, 0.15), rgba(56, 142, 60, 0.2));
  color: #2e7d32;
}

.status.ongoing {
  background: linear-gradient(135deg, rgba(251, 140, 0, 0.15), rgba(245, 124, 0, 0.2));
  color: #e65100;
}

.tags-section {
  margin-bottom: 32px;
}

.tags-label {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
}

.tag-icon {
  width: 18px;
  height: 18px;
  color: var(--color-secondary);
}

.tags-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.tag-chip {
  padding: 6px 14px;
  background: rgba(16, 185, 129, 0.08);
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: 16px;
  font-size: 13px;
  color: var(--text-secondary);
  transition: all 0.2s ease;
  cursor: default;
}

.tag-chip:hover {
  background: rgba(16, 185, 129, 0.15);
  border-color: rgba(16, 185, 129, 0.4);
  transform: translateY(-2px);
}

.stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: linear-gradient(135deg, rgba(5, 150, 105, 0.03), rgba(16, 185, 129, 0.05));
  border-radius: var(--radius-md);
  border: 1px solid rgba(5, 150, 105, 0.08);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
  border-color: var(--color-secondary);
}

.stat-icon {
  width: 32px;
  height: 32px;
  color: var(--color-secondary);
  flex-shrink: 0;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  font-family: 'Crimson Pro', serif;
}

.stat-label {
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 500;
  letter-spacing: 0.5px;
}

.intro-section {
  margin-bottom: 32px;
}

.intro-title {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.title-line {
  flex: 1;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--color-secondary), transparent);
  opacity: 0.3;
}

.intro-text {
  font-size: 15px;
  line-height: 1.9;
  color: var(--text-secondary);
  white-space: pre-wrap;
  max-height: 200px;
  overflow-y: auto;
  padding: 20px;
  background: rgba(248, 246, 241, 0.5);
  border-radius: var(--radius-md);
  border-left: 3px solid var(--color-secondary);
}

.intro-text::-webkit-scrollbar {
  width: 6px;
}

.intro-text::-webkit-scrollbar-track {
  background: rgba(5, 150, 105, 0.05);
  border-radius: 3px;
}

.intro-text::-webkit-scrollbar-thumb {
  background: var(--color-secondary);
  border-radius: 3px;
}

.actions-section {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.action-button {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 14px 32px;
  border: none;
  border-radius: var(--radius-md);
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.action-button::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  transform: translate(-50%, -50%);
  transition: width 0.5s ease, height 0.5s ease;
}

.action-button:hover::before {
  width: 300px;
  height: 300px;
}

.action-button.primary {
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
  color: white;
  box-shadow: var(--shadow-md);
}

.action-button.primary:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-3px);
}

.action-button.primary:active {
  transform: translateY(-1px);
}

.button-icon {
  width: 18px;
  height: 18px;
  position: relative;
  z-index: 1;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .card-container {
    padding: 24px;
  }

  .novel-title {
    font-size: 24px;
  }

  .deco-bracket {
    font-size: 24px;
  }

  .info-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
    padding: 16px;
  }

  .stats-section {
    grid-template-columns: 1fr;
  }

  .stat-card {
    padding: 16px;
  }

  .title-section {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
