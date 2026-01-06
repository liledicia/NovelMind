<template>
  <div class="home-page">
    <!-- 搜索栏 -->
    <SearchBar
      :loading="loading"
      :hint="searchHint"
      @search="handleSearch"
    />

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-content">
        <div class="loading-spinner-large">
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
        </div>
        <p class="loading-text">{{ loadingMessage }}</p>
      </div>
    </div>

    <!-- 搜索结果提示 -->
    <transition name="alert-slide">
      <div
        v-if="searchResult && !loading"
        class="search-alert"
        :class="alertClass"
      >
        <div class="alert-icon">
          <svg v-if="searchResult.source === 'database'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
          </svg>
        </div>
        <div class="alert-content">
          <h4 class="alert-title">{{ alertTitle }}</h4>
          <p class="alert-message">{{ alertMessage }}</p>
        </div>
      </div>
    </transition>

    <!-- 小说详情卡片 -->
    <transition name="card-appear" mode="out-in">
      <NovelCard
        v-if="currentNovel && !loading"
        :novel="currentNovel"
        :stats="currentStats"
        :source="searchResult?.source"
      />
    </transition>

    <!-- 推荐列表 -->
    <transition name="recommendations-appear" mode="out-in">
      <RecommendationList
        v-if="recommendations.length > 0 && !loading"
        :recommendations="recommendations"
      />
    </transition>

    <!-- 错误提示 -->
    <transition name="error-shake">
      <div v-if="error" class="error-alert">
        <div class="error-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
        </div>
        <div class="error-content">
          <h4 class="error-title">搜索失败</h4>
          <p class="error-message">{{ error }}</p>
        </div>
        <button @click="error = null" class="error-close">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>
    </transition>

    <!-- 空状态 -->
    <transition name="empty-fade">
      <div v-if="!loading && !currentNovel && !error" class="empty-state">
        <div class="empty-illustration">
          <svg viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="100" cy="100" r="80" stroke="currentColor" stroke-width="2" opacity="0.2"/>
            <path d="M100 60 L140 100 L100 140 L60 100 Z" stroke="currentColor" stroke-width="2" fill="none" opacity="0.3"/>
            <circle cx="100" cy="100" r="8" fill="currentColor" opacity="0.4"/>
          </svg>
        </div>
        <h3 class="empty-title">开始探索你的阅读世界</h3>
        <p class="empty-description">
          在搜索框中输入小说名称，我们会为你推荐相似的精彩作品
        </p>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import SearchBar from '@/components/SearchBar.vue'
import NovelCard from '@/components/NovelCard.vue'
import RecommendationList from '@/components/RecommendationList.vue'
import { searchNovel, getRecommendations } from '@/api/novels'

const loading = ref(false)
const currentNovel = ref(null)
const currentStats = ref(null)
const recommendations = ref([])
const searchResult = ref(null)
const error = ref(null)
const loadingMessage = ref('正在搜索...')

const searchHint = computed(() => {
  if (loading.value) {
    return '正在处理，请稍候...'
  }
  if (searchResult.value?.source === 'crawled') {
    return '实时爬取成功，数据已保存至数据库'
  }
  return '支持搜索已收录的 150+ 本小说，未找到将实时爬取'
})

const alertTitle = computed(() => {
  if (searchResult.value?.source === 'database') {
    return '从数据库找到'
  }
  return '实时爬取成功'
})

const alertClass = computed(() => {
  return searchResult.value?.source === 'database' ? 'alert-success' : 'alert-info'
})

const alertMessage = computed(() => {
  if (searchResult.value?.source === 'database') {
    return `已找到小说《${currentNovel.value?.title}》，正在生成推荐...`
  }
  return `成功爬取《${currentNovel.value?.title}》的最新数据并保存到数据库`
})

const handleSearch = async (query) => {
  loading.value = true
  error.value = null
  currentNovel.value = null
  recommendations.value = []
  searchResult.value = null
  loadingMessage.value = '正在搜索小说...'

  try {
    // Step 1: 搜索小说
    ElMessage.info(`正在搜索《${query}》...`)
    const response = await searchNovel(query)

    if (!response.success) {
      throw new Error(response.message || '搜索失败')
    }

    searchResult.value = response
    currentNovel.value = response.data
    currentStats.value = response.stats

    ElMessage.success(`找到小说《${response.data.title}》`)

    // Step 2: 获取推荐
    if (response.data.book_id) {
      loadingMessage.value = '正在生成智能推荐...'
      try {
        const recResponse = await getRecommendations(response.data.book_id, 10)

        if (recResponse.success && recResponse.data.recommendations) {
          recommendations.value = recResponse.data.recommendations
          ElMessage.success(`为你推荐了 ${recResponse.data.recommendations.length} 本相似小说`)
        }
      } catch (recError) {
        console.error('获取推荐失败:', recError)
        ElMessage.warning('推荐功能暂时不可用')
      }
    }

  } catch (err) {
    console.error('搜索错误:', err)

    if (err.response?.status === 404) {
      error.value = `未找到小说《${query}》，请检查小说名称是否正确`
      ElMessage.error(error.value)
    } else if (err.response?.status === 500) {
      error.value = '服务器错误，请稍后重试'
      ElMessage.error(error.value)
    } else {
      error.value = err.message || '搜索失败，请检查网络连接'
      ElMessage.error(error.value)
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.home-page {
  width: 100%;
  min-height: 60vh;
}

.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.loading-content {
  text-align: center;
}

.loading-spinner-large {
  position: relative;
  width: 100px;
  height: 100px;
  margin: 0 auto 24px;
}

.spinner-ring {
  position: absolute;
  width: 100%;
  height: 100%;
  border: 3px solid transparent;
  border-radius: 50%;
  animation: spin 1.5s cubic-bezier(0.5, 0, 0.5, 1) infinite;
}

.spinner-ring:nth-child(1) {
  border-top-color: var(--color-primary);
  animation-delay: 0s;
}

.spinner-ring:nth-child(2) {
  border-top-color: var(--color-secondary);
  animation-delay: -0.5s;
}

.spinner-ring:nth-child(3) {
  border-top-color: var(--color-accent);
  animation-delay: -1s;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.loading-text {
  font-size: 16px;
  color: var(--text-secondary);
  font-weight: 500;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 0.6;
  }
  50% {
    opacity: 1;
  }
}

.search-alert {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 20px 24px;
  border-radius: var(--radius-lg);
  margin-bottom: 30px;
  border-left: 4px solid;
  backdrop-filter: blur(10px);
}

.alert-success {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(5, 150, 105, 0.05));
  border-color: #10b981;
}

.alert-info {
  background: linear-gradient(135deg, rgba(25, 118, 210, 0.1), rgba(21, 101, 192, 0.05));
  border-color: #2196f3;
}

.alert-icon {
  width: 28px;
  height: 28px;
  flex-shrink: 0;
}

.alert-success .alert-icon {
  color: #10b981;
}

.alert-info .alert-icon {
  color: #2196f3;
}

.alert-content {
  flex: 1;
}

.alert-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.alert-message {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

.error-alert {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 20px 24px;
  background: linear-gradient(135deg, rgba(244, 67, 54, 0.1), rgba(211, 47, 47, 0.05));
  border-radius: var(--radius-lg);
  border-left: 4px solid #f44336;
  margin-bottom: 30px;
  backdrop-filter: blur(10px);
}

.error-icon {
  width: 28px;
  height: 28px;
  color: #f44336;
  flex-shrink: 0;
}

.error-content {
  flex: 1;
}

.error-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.error-message {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

.error-close {
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0;
  transition: all 0.2s ease;
}

.error-close:hover {
  color: #f44336;
  transform: rotate(90deg);
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-illustration {
  width: 200px;
  height: 200px;
  margin: 0 auto 32px;
  color: var(--color-secondary);
  opacity: 0.4;
  animation: float 6s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-20px);
  }
}

.empty-title {
  font-family: 'Crimson Pro', 'Noto Serif SC', serif;
  font-size: 28px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.empty-description {
  font-size: 16px;
  color: var(--text-secondary);
  max-width: 500px;
  margin: 0 auto;
  line-height: 1.6;
}

/* 过渡动画 */
.alert-slide-enter-active,
.alert-slide-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.alert-slide-enter-from {
  opacity: 0;
  transform: translateY(-20px);
}

.alert-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.card-appear-enter-active {
  animation: cardEnter 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.card-appear-leave-active {
  animation: cardLeave 0.3s ease-out;
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

@keyframes cardLeave {
  to {
    opacity: 0;
    transform: translateY(-20px) scale(0.98);
  }
}

.recommendations-appear-enter-active {
  animation: recAppear 0.6s ease-out 0.2s both;
}

@keyframes recAppear {
  from {
    opacity: 0;
    transform: translateY(40px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.error-shake-enter-active {
  animation: shake 0.5s ease-out;
}

@keyframes shake {
  0%, 100% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-10px);
  }
  75% {
    transform: translateX(10px);
  }
}

.empty-fade-enter-active,
.empty-fade-leave-active {
  transition: all 0.5s ease;
}

.empty-fade-enter-from,
.empty-fade-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .empty-illustration {
    width: 150px;
    height: 150px;
  }

  .empty-title {
    font-size: 24px;
  }

  .empty-description {
    font-size: 15px;
  }

  .loading-spinner-large {
    width: 80px;
    height: 80px;
  }
}
</style>
