<template>
  <div class="search-bar">
    <div class="search-hero">
      <div class="search-decoration">
        <div class="deco-circle"></div>
        <div class="deco-line-group">
          <span class="line"></span>
          <span class="line"></span>
          <span class="line"></span>
        </div>
      </div>

      <h2 class="search-title">探索你的下一本好书</h2>
      <p class="search-description">从 150+ 精选小说中发现，未收录作品将实时爬取</p>
    </div>

    <div class="search-container">
      <div class="search-input-wrapper" @click="focusInput">
        <div class="input-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/>
            <path d="m21 21-4.35-4.35"/>
          </svg>
        </div>
        <input
          ref="inputRef"
          v-model="searchQuery"
          type="text"
          placeholder="输入小说名称，如：全职高手、魔道祖师..."
          @keyup.enter="handleSearch"
          class="search-input"
          :disabled="loading"
        />
        <button
          v-if="searchQuery"
          @click.stop="searchQuery = ''"
          class="clear-button"
          type="button"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>

      <button
        @click="handleSearch"
        :disabled="!searchQuery.trim() || loading"
        class="search-button"
      >
        <span v-if="!loading" class="button-content">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="button-icon">
            <circle cx="11" cy="11" r="8"/>
            <path d="m21 21-4.35-4.35"/>
          </svg>
          开始搜索
        </span>
        <span v-else class="button-content">
          <span class="loading-spinner"></span>
          搜索中
        </span>
      </button>
    </div>

    <div v-if="hint" class="search-hint">
      <div class="hint-icon">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <circle cx="12" cy="12" r="10" opacity="0.2"/>
          <path d="M12 16v-4m0-4h.01M22 12c0 5.523-4.477 10-10 10S2 17.523 2 12 6.477 2 12 2s10 4.477 10 10z" fill="none" stroke="currentColor" stroke-width="2"/>
        </svg>
      </div>
      <span>{{ hint }}</span>
    </div>

    <!-- 快捷搜索建议 -->
    <div v-if="!loading && !searchQuery" class="quick-suggestions">
      <span class="suggestions-label">热门搜索：</span>
      <button
        v-for="suggestion in suggestions"
        :key="suggestion"
        @click="quickSearch(suggestion)"
        class="suggestion-tag"
      >
        {{ suggestion }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, defineEmits, defineProps } from 'vue'

const props = defineProps({
  loading: {
    type: Boolean,
    default: false
  },
  hint: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['search'])

const searchQuery = ref('')
const inputRef = ref(null)
const suggestions = ['全职高手', '魔道祖师', '天官赐福', '默读', '撒野']

const handleSearch = () => {
  const query = searchQuery.value.trim()
  if (query) {
    emit('search', query)
  }
}

const quickSearch = (query) => {
  searchQuery.value = query
  handleSearch()
}

const focusInput = () => {
  if (inputRef.value) {
    inputRef.value.focus()
  }
}
</script>

<style scoped>
.search-bar {
  width: 100%;
  max-width: 900px;
  margin: 0 auto 60px;
}

.search-hero {
  text-align: center;
  margin-bottom: 40px;
  position: relative;
}

.search-decoration {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 16px;
  opacity: 0.6;
}

.deco-circle {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-secondary);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 0.5;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.2);
  }
}

.deco-line-group {
  display: flex;
  gap: 4px;
}

.line {
  display: block;
  width: 20px;
  height: 2px;
  background: var(--color-secondary);
  opacity: 0.6;
  animation: lineSlide 3s ease-in-out infinite;
}

.line:nth-child(2) {
  animation-delay: 0.2s;
}

.line:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes lineSlide {
  0%, 100% {
    transform: scaleX(1);
    opacity: 0.4;
  }
  50% {
    transform: scaleX(1.5);
    opacity: 0.8;
  }
}

.search-title {
  font-family: 'Crimson Pro', 'Noto Serif SC', serif;
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 12px;
  letter-spacing: 0.5px;
  animation: fadeInUp 0.6s ease-out;
}

.search-description {
  font-size: 15px;
  color: var(--text-secondary);
  letter-spacing: 0.3px;
  animation: fadeInUp 0.6s ease-out 0.1s both;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.search-container {
  display: flex;
  gap: 16px;
  align-items: stretch;
  animation: fadeInUp 0.6s ease-out 0.2s both;
}

.search-input-wrapper {
  position: relative;
  flex: 1;
  display: flex;
  align-items: center;
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  border: 2px solid transparent;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.search-input-wrapper::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  padding: 2px;
  background: linear-gradient(135deg, var(--color-secondary), var(--color-accent));
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.search-input-wrapper:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

.search-input-wrapper:focus-within {
  box-shadow: var(--shadow-xl);
  transform: translateY(-2px);
}

.search-input-wrapper:focus-within::before {
  opacity: 1;
}

.input-icon {
  position: absolute;
  left: 20px;
  width: 22px;
  height: 22px;
  color: var(--color-primary);
  opacity: 0.5;
  transition: all 0.3s ease;
  pointer-events: none;
}

.search-input-wrapper:focus-within .input-icon {
  opacity: 1;
  transform: scale(1.1);
}

.search-input {
  width: 100%;
  padding: 18px 50px 18px 56px;
  border: none;
  outline: none;
  background: transparent;
  font-size: 16px;
  color: var(--text-primary);
  font-family: inherit;
}

.search-input::placeholder {
  color: var(--text-muted);
  opacity: 0.7;
}

.search-input:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.clear-button {
  position: absolute;
  right: 16px;
  width: 24px;
  height: 24px;
  border: none;
  background: var(--text-muted);
  color: white;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.6;
  transition: all 0.2s ease;
  padding: 0;
}

.clear-button:hover {
  opacity: 1;
  transform: rotate(90deg);
  background: var(--color-primary);
}

.clear-button svg {
  width: 12px;
  height: 12px;
}

.search-button {
  min-width: 140px;
  padding: 18px 32px;
  border: none;
  border-radius: var(--radius-lg);
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-accent) 100%);
  color: var(--text-light);
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: var(--shadow-md);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.search-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.search-button:hover::before {
  left: 100%;
}

.search-button:hover:not(:disabled) {
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

.search-button:active:not(:disabled) {
  transform: translateY(0);
}

.search-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.button-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.button-icon {
  width: 18px;
  height: 18px;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.search-hint {
  margin-top: 20px;
  padding: 14px 20px;
  background: rgba(26, 58, 82, 0.05);
  border-radius: var(--radius-md);
  border-left: 3px solid var(--color-secondary);
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: var(--text-secondary);
  animation: slideIn 0.4s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.hint-icon {
  width: 20px;
  height: 20px;
  color: var(--color-secondary);
  flex-shrink: 0;
}

.quick-suggestions {
  margin-top: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 10px;
  animation: fadeInUp 0.6s ease-out 0.4s both;
}

.suggestions-label {
  font-size: 13px;
  color: var(--text-muted);
  margin-right: 4px;
}

.suggestion-tag {
  padding: 6px 16px;
  border: 1px solid rgba(26, 58, 82, 0.15);
  background: rgba(255, 255, 255, 0.8);
  border-radius: 20px;
  font-size: 13px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.suggestion-tag:hover {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .search-title {
    font-size: 24px;
  }

  .search-description {
    font-size: 14px;
  }

  .search-container {
    flex-direction: column;
    gap: 12px;
  }

  .search-button {
    width: 100%;
  }

  .quick-suggestions {
    justify-content: flex-start;
  }

  .search-input {
    padding: 16px 50px 16px 50px;
    font-size: 15px;
  }
}
</style>
