<template>
  <div class="recommendation-list">
    <!-- 标题区域 -->
    <div class="list-header">
      <div class="header-decoration">
        <div class="deco-diamond"></div>
        <div class="deco-lines">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>

      <h3 class="list-title">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="title-icon">
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
        </svg>
        为你推荐
      </h3>

      <p class="list-description">
        基于标签、类型、风格等多维度智能匹配 • 共 {{ recommendations.length }} 本相似小说
      </p>

      <div class="header-decoration bottom">
        <div class="deco-lines">
          <span></span>
          <span></span>
          <span></span>
        </div>
        <div class="deco-diamond"></div>
      </div>
    </div>

    <!-- 推荐卡片网格 -->
    <div class="recommendations-grid">
      <div
        v-for="(item, index) in recommendations"
        :key="item.book_id"
        class="rec-card"
        :style="{ animationDelay: `${index * 0.08}s` }"
        @click="viewDetail(item)"
      >
        <!-- 相似度徽章 -->
        <div class="similarity-badge">
          <svg class="circular-progress" viewBox="0 0 100 100">
            <circle class="bg-circle" cx="50" cy="50" r="45"/>
            <circle
              class="progress-circle"
              cx="50"
              cy="50"
              r="45"
              :style="{ strokeDashoffset: getStrokeDashoffset(item.similarity_score) }"
              :class="getSimilarityClass(item.similarity_score)"
            />
          </svg>
          <div class="similarity-value">
            <span class="percentage">{{ item.similarity_score }}</span>
            <span class="percent-sign">%</span>
          </div>
        </div>

        <!-- 卡片内容 -->
        <div class="rec-content">
          <h4 class="rec-title" :title="item.title">{{ item.title }}</h4>

          <div class="rec-author">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="author-icon">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
            <span>{{ item.author || '未知作者' }}</span>
          </div>

          <!-- 匹配原因 -->
          <div v-if="item.match_reasons && item.match_reasons.length > 0" class="match-reasons">
            <span
              v-for="reason in item.match_reasons.slice(0, 3)"
              :key="reason"
              class="reason-tag"
            >
              {{ reason }}
            </span>
          </div>

          <!-- 小说属性 -->
          <div class="rec-meta">
            <span v-if="item.status" class="meta-status" :class="item.status === '完结' ? 'completed' : 'ongoing'">
              {{ item.status }}
            </span>
            <span v-if="item.word_count" class="meta-words">
              {{ formatWordCount(item.word_count) }}
            </span>
          </div>

          <!-- 统计数据 -->
          <div class="rec-stats">
            <div class="stat-item">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>
              </svg>
              <span>{{ formatNumber(item.favorite_count || 0) }}</span>
            </div>
            <div class="stat-item">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
              </svg>
              <span>{{ formatNumber(item.review_count || 0) }}</span>
            </div>
          </div>
        </div>

        <!-- hover 效果遮罩 -->
        <div class="card-overlay">
          <div class="overlay-content">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="view-icon">
              <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
              <polyline points="15 3 21 3 21 9"/>
              <line x1="10" y1="14" x2="21" y2="3"/>
            </svg>
            <span>查看详情</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'
import { formatWordCount, formatNumber } from '@/utils/formatter'

const props = defineProps({
  recommendations: {
    type: Array,
    default: () => []
  }
})

const getSimilarityClass = (score) => {
  if (score >= 80) return 'high'
  if (score >= 60) return 'medium'
  return 'low'
}

const getStrokeDashoffset = (percentage) => {
  const circumference = 2 * Math.PI * 45
  return circumference - (percentage / 100) * circumference
}

const viewDetail = (novel) => {
  const url = novel.url || `https://www.jjwxc.net/onebook.php?novelid=${novel.book_id}`
  window.open(url, '_blank')
}
</script>

<style scoped>
.recommendation-list {
  margin-top: 60px;
  animation: listFadeIn 0.6s ease-out 0.3s both;
}

@keyframes listFadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.list-header {
  text-align: center;
  margin-bottom: 50px;
  position: relative;
}

.header-decoration {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-bottom: 20px;
}

.header-decoration.bottom {
  margin-top: 20px;
  margin-bottom: 0;
}

.deco-diamond {
  width: 10px;
  height: 10px;
  background: var(--color-secondary);
  transform: rotate(45deg);
  animation: diamondRotate 4s ease-in-out infinite;
}

@keyframes diamondRotate {
  0%, 100% {
    transform: rotate(45deg) scale(1);
    opacity: 0.6;
  }
  50% {
    transform: rotate(225deg) scale(1.2);
    opacity: 1;
  }
}

.deco-lines {
  display: flex;
  gap: 6px;
}

.deco-lines span {
  display: block;
  width: 30px;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--color-secondary), transparent);
  animation: lineExpand 3s ease-in-out infinite;
}

.deco-lines span:nth-child(2) {
  animation-delay: 0.3s;
}

.deco-lines span:nth-child(3) {
  animation-delay: 0.6s;
}

@keyframes lineExpand {
  0%, 100% {
    opacity: 0.3;
    transform: scaleX(0.8);
  }
  50% {
    opacity: 0.8;
    transform: scaleX(1.2);
  }
}

.list-title {
  font-family: 'Crimson Pro', 'Noto Serif SC', serif;
  font-size: 36px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 12px;
  display: inline-flex;
  align-items: center;
  gap: 12px;
  letter-spacing: 1px;
}

.title-icon {
  width: 32px;
  height: 32px;
  color: var(--color-secondary);
  animation: iconSpin 3s ease-in-out infinite;
}

@keyframes iconSpin {
  0%, 100% {
    transform: rotate(0deg);
  }
  50% {
    transform: rotate(180deg);
  }
}

.list-description {
  font-size: 15px;
  color: var(--text-secondary);
  letter-spacing: 0.5px;
}

.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 30px;
}

.rec-card {
  position: relative;
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 24px;
  border: 1px solid rgba(5, 150, 105, 0.08);
  box-shadow: var(--shadow-sm);
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  animation: cardSlideUp 0.5s ease-out both;
}

@keyframes cardSlideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.rec-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--color-primary), var(--color-secondary), var(--color-accent));
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.4s ease;
}

.rec-card:hover::before {
  transform: scaleX(1);
}

.rec-card:hover {
  transform: translateY(-8px);
  box-shadow: var(--shadow-lg);
  border-color: var(--color-secondary);
}

.similarity-badge {
  position: relative;
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
}

.circular-progress {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.bg-circle {
  fill: none;
  stroke: rgba(5, 150, 105, 0.08);
  stroke-width: 8;
}

.progress-circle {
  fill: none;
  stroke-width: 8;
  stroke-dasharray: 283;
  transition: stroke-dashoffset 1s ease-out, stroke 0.3s ease;
  stroke-linecap: round;
}

.progress-circle.high {
  stroke: #4caf50;
}

.progress-circle.medium {
  stroke: #ff9800;
}

.progress-circle.low {
  stroke: #9e9e9e;
}

.similarity-value {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  font-family: 'Crimson Pro', serif;
}

.percentage {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
}

.percent-sign {
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 600;
}

.rec-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.rec-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  transition: color 0.3s ease;
}

.rec-card:hover .rec-title {
  color: var(--color-accent);
}

.rec-author {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: var(--text-secondary);
}

.author-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.match-reasons {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.reason-tag {
  padding: 4px 10px;
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: 12px;
  font-size: 11px;
  color: var(--text-secondary);
  font-weight: 500;
  transition: all 0.2s ease;
}

.rec-card:hover .reason-tag {
  background: rgba(16, 185, 129, 0.15);
  border-color: rgba(16, 185, 129, 0.4);
}

.rec-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
}

.meta-status {
  padding: 4px 10px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 11px;
  letter-spacing: 0.5px;
}

.meta-status.completed {
  background: rgba(67, 160, 71, 0.1);
  color: #2e7d32;
  border: 1px solid rgba(67, 160, 71, 0.2);
}

.meta-status.ongoing {
  background: rgba(251, 140, 0, 0.1);
  color: #e65100;
  border: 1px solid rgba(251, 140, 0, 0.2);
}

.meta-words {
  color: var(--text-muted);
  font-size: 12px;
}

.rec-stats {
  display: flex;
  gap: 16px;
  padding-top: 12px;
  border-top: 1px solid rgba(5, 150, 105, 0.08);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-muted);
}

.stat-item svg {
  width: 14px;
  height: 14px;
  color: var(--color-secondary);
}

.card-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(5, 150, 105, 0.95), rgba(52, 211, 153, 0.95));
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
  border-radius: inherit;
}

.rec-card:hover .card-overlay {
  opacity: 1;
}

.overlay-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: white;
  transform: translateY(20px);
  transition: transform 0.3s ease;
}

.rec-card:hover .overlay-content {
  transform: translateY(0);
}

.view-icon {
  width: 40px;
  height: 40px;
  animation: iconBounce 2s ease-in-out infinite;
}

@keyframes iconBounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
}

.overlay-content span {
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .recommendations-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 24px;
  }
}

@media (max-width: 768px) {
  .list-title {
    font-size: 28px;
  }

  .list-description {
    font-size: 14px;
  }

  .recommendations-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 20px;
  }

  .rec-card {
    padding: 20px;
  }

  .similarity-badge {
    width: 70px;
    height: 70px;
  }

  .percentage {
    font-size: 20px;
  }
}

@media (max-width: 480px) {
  .recommendations-grid {
    grid-template-columns: 1fr;
  }
}
</style>
