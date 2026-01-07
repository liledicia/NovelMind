<template>
  <div class="recommendation-list">
    <!-- 标题区域 -->
    <div class="list-header">
      <div class="header-ornament">
        <div class="ornament-line left"></div>
        <div class="ornament-dot"></div>
        <div class="ornament-line right"></div>
      </div>

      <h3 class="list-title">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="title-icon">
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
        </svg>
        为你推荐
      </h3>

      <p class="list-description">
        基于多维度智能匹配 · 共 {{ recommendations.length }} 本相似小说
      </p>
    </div>

    <!-- 筛选器区域 -->
    <div class="filter-section">
      <div class="filter-tabs">
        <button
          v-for="filter in filters"
          :key="filter.value"
          @click="selectedFilter = filter.value"
          :class="['filter-tab', { active: selectedFilter === filter.value }]"
        >
          <span class="tab-icon">{{ filter.icon }}</span>
          <span class="tab-text">{{ filter.label }}</span>
          <span class="tab-count">{{ getFilterCount(filter.value) }}</span>
        </button>
      </div>
    </div>

    <!-- 推荐书架网格 -->
    <div class="recommendations-shelf">
      <div
        v-for="(item, index) in filteredRecommendations"
        :key="item.book_id"
        class="shelf-item"
        :style="{ animationDelay: `${index * 0.05}s` }"
        @click="viewDetail(item)"
      >
        <!-- 左侧：封面 -->
        <div class="item-cover">
          <div class="cover-wrapper">
            <img
              v-if="item.cover_url"
              :src="getCoverUrl(item)"
              :alt="item.title"
              class="cover-image"
              referrerPolicy="no-referrer"
              @error="(e) => handleImageError(e, item)"
            />
            <div v-if="!item.cover_url" class="cover-placeholder">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
                <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
              </svg>
            </div>
            <div class="cover-spine"></div>
          </div>

          <!-- 相似度标签 -->
          <div class="similarity-tag" :class="getSimilarityClass(item.similarity_score)">
            <span class="similarity-value">{{ item.similarity_score }}%</span>
            <span class="similarity-label">相似</span>
          </div>
        </div>

        <!-- 右侧：信息 -->
        <div class="item-info">
          <div class="info-header">
            <h4 class="item-title">{{ item.title }}</h4>
            <div class="item-author">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="author-icon">
                <circle cx="12" cy="7" r="4"/>
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
              </svg>
              <span>{{ item.author || '未知作者' }}</span>
            </div>
          </div>

          <!-- 匹配原因标签 -->
          <div v-if="item.match_reasons && item.match_reasons.length > 0" class="match-tags">
            <span
              v-for="reason in item.match_reasons.slice(0, 2)"
              :key="reason"
              class="match-tag"
            >
              {{ reason }}
            </span>
          </div>

          <!-- 元数据行 -->
          <div class="item-metadata">
            <span v-if="item.status" class="meta-status" :class="item.status === '完结' ? 'completed' : 'ongoing'">
              {{ item.status }}
            </span>
            <span v-if="item.word_count" class="meta-divider">·</span>
            <span v-if="item.word_count" class="meta-words">
              {{ formatWordCount(item.word_count) }}
            </span>
          </div>

          <!-- 统计数据 -->
          <div class="item-stats">
            <div class="stat-group">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>
              </svg>
              <span>{{ formatNumber(item.favorite_count || 0) }}</span>
            </div>
            <div class="stat-group">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
              </svg>
              <span>{{ formatNumber(item.review_count || 0) }}</span>
            </div>
          </div>
        </div>

        <!-- 悬停指示器 -->
        <div class="hover-indicator">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
            <polyline points="15 3 21 3 21 9"/>
            <line x1="10" y1="14" x2="21" y2="3"/>
          </svg>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, defineProps } from 'vue'
import { formatWordCount, formatNumber, getProxiedImageUrl, getJJWXCFallbackCover } from '@/utils/formatter'

const props = defineProps({
  recommendations: {
    type: Array,
    default: () => []
  }
})

// 筛选器选项
const filters = [
  { value: 'all', label: '全部', icon: '📚' },
  { value: 'completed', label: '已完结', icon: '✓' },
  { value: 'ongoing', label: '连载中', icon: '⟳' }
]

const selectedFilter = ref('all')

// 筛选后的推荐列表
const filteredRecommendations = computed(() => {
  if (selectedFilter.value === 'all') {
    return props.recommendations
  }

  return props.recommendations.filter(item => {
    const status = item.status || ''
    if (selectedFilter.value === 'completed') {
      return status === '完结'
    } else if (selectedFilter.value === 'ongoing') {
      return status !== '完结'
    }
    return true
  })
})

// 获取每个筛选器的数量
const getFilterCount = (filterValue) => {
  if (filterValue === 'all') {
    return props.recommendations.length
  }

  const count = props.recommendations.filter(item => {
    const status = item.status || ''
    if (filterValue === 'completed') {
      return status === '完结'
    } else if (filterValue === 'ongoing') {
      return status !== '完结'
    }
    return false
  }).length

  return count
}

const getSimilarityClass = (score) => {
  if (score >= 80) return 'high'
  if (score >= 60) return 'medium'
  return 'low'
}

// 获取代理后的封面URL
const getCoverUrl = (item) => {
  return getProxiedImageUrl(item.cover_url)
}

// 图片加载失败时的处理
const handleImageError = (event, item) => {
  // 如果原始URL失败，尝试使用晋江官方封面作为fallback
  const currentSrc = event.target.src
  const fallbackUrl = getJJWXCFallbackCover(item.book_id)

  // 避免无限循环：如果已经是fallback URL还失败，就隐藏图片
  if (currentSrc !== fallbackUrl && fallbackUrl) {
    console.log(`封面加载失败，尝试fallback: ${item.title}`)
    event.target.src = fallbackUrl
  } else {
    // 隐藏图片，显示占位符
    event.target.style.display = 'none'
  }
}

const viewDetail = (novel) => {
  const url = novel.url || `https://www.jjwxc.net/onebook.php?novelid=${novel.book_id}`
  window.open(url, '_blank')
}
</script>

<style scoped>
.recommendation-list {
  margin-top: 60px;
  animation: listFadeIn 0.7s ease-out 0.2s both;
}

@keyframes listFadeIn {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ========= 标题区域 ========= */
.list-header {
  text-align: center;
  margin-bottom: 48px;
  position: relative;
}

.header-ornament {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-bottom: 20px;
}

.ornament-line {
  width: 60px;
  height: 1px;
  background: linear-gradient(to right, transparent, var(--color-secondary), transparent);
  position: relative;
}

.ornament-line.left {
  background: linear-gradient(to right, transparent, var(--color-secondary));
}

.ornament-line.right {
  background: linear-gradient(to left, transparent, var(--color-accent-pink));
}

.ornament-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-secondary), var(--color-accent-pink));
  animation: dotPulse 2s ease-in-out infinite;
}

@keyframes dotPulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.7;
  }
  50% {
    transform: scale(1.3);
    opacity: 1;
  }
}

.list-title {
  font-family: 'Playfair Display', 'Noto Serif SC', serif;
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 12px 0;
  display: inline-flex;
  align-items: center;
  gap: 12px;
  letter-spacing: 0.5px;
}

.title-icon {
  width: 28px;
  height: 28px;
  color: var(--color-accent-pink);
  animation: iconTwinkle 3s ease-in-out infinite;
}

@keyframes iconTwinkle {
  0%, 100% {
    opacity: 0.6;
    transform: rotate(0deg);
  }
  50% {
    opacity: 1;
    transform: rotate(15deg);
  }
}

.list-description {
  font-size: 14px;
  color: var(--text-secondary);
  letter-spacing: 0.5px;
  opacity: 0.9;
}

/* ========= 筛选器区域 ========= */
.filter-section {
  margin: 40px auto;
  max-width: 700px;
}

.filter-tabs {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

.filter-tab {
  flex: 1;
  min-width: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 24px;
  background: rgba(164, 184, 196, 0.06);
  border: 1.5px solid rgba(164, 184, 196, 0.2);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  position: relative;
  overflow: hidden;
}

.filter-tab::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(212, 181, 176, 0.15), transparent);
  transition: left 0.6s ease;
}

.filter-tab:hover::before {
  left: 100%;
}

.filter-tab:hover {
  background: rgba(164, 184, 196, 0.12);
  border-color: var(--color-secondary);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(139, 163, 181, 0.15);
}

.filter-tab.active {
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent-pink));
  border-color: transparent;
  color: white;
  box-shadow: 0 4px 16px rgba(139, 163, 181, 0.25);
  transform: scale(1.02);
}

.filter-tab.active:hover {
  transform: scale(1.02) translateY(-2px);
}

.tab-icon {
  font-size: 16px;
}

.tab-text {
  font-weight: 600;
  letter-spacing: 0.3px;
}

.tab-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 22px;
  height: 22px;
  padding: 0 6px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 11px;
  font-size: 11px;
  font-weight: 700;
}

.filter-tab:not(.active) .tab-count {
  background: rgba(139, 163, 181, 0.15);
  color: var(--color-primary);
}

/* ========= 推荐书架 ========= */
.recommendations-shelf {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(480px, 1fr));
  gap: 20px;
}

.shelf-item {
  position: relative;
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 20px;
  border: 1px solid rgba(139, 163, 181, 0.1);
  box-shadow: 0 2px 12px rgba(139, 163, 181, 0.08);
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  overflow: hidden;
  display: flex;
  gap: 20px;
  animation: shelfSlideIn 0.5s ease-out both;
}

@keyframes shelfSlideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.shelf-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--color-secondary), var(--color-accent-pink));
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.4s ease;
}

.shelf-item:hover::before {
  transform: scaleX(1);
}

.shelf-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(139, 163, 181, 0.18);
  border-color: var(--color-secondary);
}

/* ========= 左侧封面 ========= */
.item-cover {
  flex-shrink: 0;
  width: 100px;
  position: relative;
}

.cover-wrapper {
  width: 100%;
  aspect-ratio: 3 / 4;
  border-radius: var(--radius-sm);
  overflow: hidden;
  box-shadow:
    3px 5px 16px rgba(107, 134, 153, 0.18),
    1px 2px 8px rgba(212, 181, 176, 0.1);
  background: linear-gradient(135deg, var(--color-light-blue), var(--color-soft-pink));
  transition: all 0.3s ease;
  position: relative;
}

.shelf-item:hover .cover-wrapper {
  transform: translateY(-3px) rotateY(-3deg);
  box-shadow:
    4px 8px 20px rgba(107, 134, 153, 0.22),
    2px 4px 12px rgba(212, 181, 176, 0.15);
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
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.7);
}

.cover-placeholder svg {
  width: 40px;
  height: 40px;
}

.cover-spine {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 6px;
  background: linear-gradient(
    to bottom,
    rgba(0, 0, 0, 0.08),
    rgba(0, 0, 0, 0.04),
    rgba(0, 0, 0, 0.08)
  );
  box-shadow: inset 1px 0 2px rgba(0, 0, 0, 0.15);
}

/* 相似度标签 */
.similarity-tag {
  position: absolute;
  bottom: -8px;
  left: 50%;
  transform: translateX(-50%);
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 10px;
  font-weight: 700;
  color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  align-items: center;
  line-height: 1.2;
  min-width: 50px;
  text-align: center;
  transition: all 0.3s ease;
}

.similarity-tag.high {
  background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
}

.similarity-tag.medium {
  background: linear-gradient(135deg, var(--color-accent-pink), var(--color-accent-rose));
}

.similarity-tag.low {
  background: linear-gradient(135deg, #95A5A6, #7F8C8D);
}

.shelf-item:hover .similarity-tag {
  transform: translateX(-50%) scale(1.05);
}

.similarity-value {
  font-size: 13px;
  font-weight: 700;
}

.similarity-label {
  font-size: 8px;
  opacity: 0.9;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* ========= 右侧信息 ========= */
.item-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-width: 0;
}

.info-header {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.item-title {
  font-family: 'Playfair Display', 'Noto Serif SC', serif;
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  transition: color 0.3s ease;
  letter-spacing: 0.3px;
}

.shelf-item:hover .item-title {
  color: var(--color-primary);
}

.item-author {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-secondary);
}

.author-icon {
  width: 14px;
  height: 14px;
  color: var(--color-accent-pink);
  flex-shrink: 0;
}

/* 匹配标签 */
.match-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.match-tag {
  padding: 4px 10px;
  background: rgba(164, 184, 196, 0.12);
  border: 1px solid rgba(164, 184, 196, 0.25);
  border-radius: 12px;
  font-size: 11px;
  color: var(--text-secondary);
  font-weight: 500;
  transition: all 0.3s ease;
}

.shelf-item:hover .match-tag {
  background: rgba(212, 181, 176, 0.18);
  border-color: var(--color-accent-pink);
}

/* 元数据 */
.item-metadata {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.meta-status {
  padding: 3px 10px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 11px;
  letter-spacing: 0.3px;
}

.meta-status.completed {
  background: linear-gradient(135deg, rgba(139, 163, 181, 0.15), rgba(164, 184, 196, 0.2));
  color: var(--color-dark-blue);
  border: 1px solid rgba(139, 163, 181, 0.25);
}

.meta-status.ongoing {
  background: linear-gradient(135deg, rgba(212, 181, 176, 0.15), rgba(229, 201, 196, 0.2));
  color: #A67C77;
  border: 1px solid rgba(212, 181, 176, 0.25);
}

.meta-divider {
  color: var(--text-muted);
  opacity: 0.5;
}

.meta-words {
  color: var(--text-muted);
  font-size: 12px;
}

/* 统计数据 */
.item-stats {
  display: flex;
  gap: 16px;
  padding-top: 8px;
  border-top: 1px solid rgba(139, 163, 181, 0.08);
}

.stat-group {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: var(--text-muted);
}

.stat-group svg {
  width: 13px;
  height: 13px;
  color: var(--color-secondary);
  flex-shrink: 0;
}

/* 悬停指示器 */
.hover-indicator {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent-pink));
  border-radius: 50%;
  color: white;
  opacity: 0;
  transform: scale(0.8);
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  box-shadow: 0 4px 12px rgba(139, 163, 181, 0.3);
}

.hover-indicator svg {
  width: 16px;
  height: 16px;
}

.shelf-item:hover .hover-indicator {
  opacity: 1;
  transform: scale(1);
}

/* ========= 响应式设计 ========= */
@media (max-width: 1024px) {
  .recommendations-shelf {
    grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
    gap: 16px;
  }

  .shelf-item {
    padding: 16px;
  }

  .item-cover {
    width: 90px;
  }
}

@media (max-width: 768px) {
  .list-title {
    font-size: 26px;
  }

  .filter-tabs {
    flex-direction: column;
  }

  .filter-tab {
    min-width: 100%;
  }

  .recommendations-shelf {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .shelf-item {
    padding: 16px;
    gap: 16px;
  }

  .item-cover {
    width: 80px;
  }

  .item-title {
    font-size: 16px;
  }

  .hover-indicator {
    display: none;
  }
}

@media (max-width: 480px) {
  .shelf-item {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .item-cover {
    width: 120px;
  }

  .similarity-tag {
    position: static;
    transform: none;
    margin-top: 10px;
  }

  .item-info {
    align-items: center;
  }

  .item-metadata {
    justify-content: center;
  }

  .item-stats {
    justify-content: center;
  }
}
</style>
