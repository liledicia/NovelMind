<template>
  <el-drawer
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    :title="`《${book?.title || ''}》· 前三章试读`"
    direction="rtl"
    size="50%"
    class="preview-drawer"
  >
    <div v-if="loading" class="preview-loading">
      <div class="preview-spinner"></div>
      <p>正在抓取免费章节…首次约需 4~8 秒</p>
    </div>
    <div v-else-if="error" class="preview-empty">
      <p>{{ error }}</p>
      <button class="preview-btn" @click="openOriginal">前往晋江原文阅读</button>
    </div>
    <div v-else-if="chapters.length" class="preview-content">
      <article v-for="ch in chapters" :key="ch.chapter_id" class="preview-chapter">
        <h3 class="preview-chapter-title">
          <span class="preview-chapter-order">第{{ ch.chapter_order }}章</span>
          {{ ch.chapter_name }}
        </h3>
        <p v-if="ch.chapter_intro" class="preview-chapter-intro">{{ ch.chapter_intro }}</p>
        <div class="preview-chapter-body">{{ ch.content }}</div>
        <p v-if="ch.author_say" class="preview-author-say">
          <span class="preview-author-label">作者有话说</span>
          {{ ch.author_say }}
        </p>
      </article>
      <div class="preview-footer">
        <p>试读到此结束，喜欢请前往晋江支持正版</p>
        <button class="preview-btn" @click="openOriginal">前往晋江原文</button>
      </div>
    </div>
    <div v-else class="preview-empty">
      <p>暂未获取到试读章节，可前往晋江原文阅读。</p>
      <button class="preview-btn" @click="openOriginal">前往晋江原文</button>
    </div>
  </el-drawer>
</template>

<script setup>
import { ref, watch, defineProps, defineEmits } from 'vue'
import { getChapters } from '@/api/novels'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  book: { type: Object, default: null }
})
defineEmits(['update:modelValue'])

const chapters = ref([])
const loading = ref(false)
const error = ref('')
let loadedBookId = null  // 记录已加载的书，换书时重新抓取

const fetchChapters = async (bookId) => {
  loading.value = true
  error.value = ''
  chapters.value = []
  try {
    const res = await getChapters(bookId, 3)
    chapters.value = res?.data?.chapters || []
    loadedBookId = bookId
  } catch (e) {
    error.value = '试读章节加载失败，请稍后重试或前往晋江原文阅读。'
  } finally {
    loading.value = false
  }
}

// 抽屉打开时按需抓取：同一本书复用，换书重新抓
watch(
  () => props.modelValue,
  (open) => {
    if (!open) return
    const bookId = props.book?.book_id
    if (!bookId) return
    if (loadedBookId !== bookId) {
      fetchChapters(bookId)
    }
  }
)

const openOriginal = () => {
  const url = props.book?.url || `https://www.jjwxc.net/onebook.php?novelid=${props.book?.book_id}`
  window.open(url, '_blank')
}
</script>

<style scoped>
.preview-loading,
.preview-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
  padding: 60px 24px;
  color: var(--text-secondary);
  text-align: center;
}

.preview-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(139, 163, 181, 0.2);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.preview-content {
  display: flex;
  flex-direction: column;
  gap: 40px;
  padding: 0 4px 24px;
}

.preview-chapter {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.preview-chapter-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(139, 163, 181, 0.15);
  display: flex;
  align-items: baseline;
  gap: 10px;
}

.preview-chapter-order {
  font-size: 13px;
  color: var(--color-accent-pink);
  font-weight: 600;
}

.preview-chapter-intro {
  font-size: 13px;
  font-style: italic;
  color: var(--text-muted);
  margin: 0;
  padding: 10px 14px;
  background: rgba(245, 240, 237, 0.6);
  border-left: 3px solid var(--color-secondary);
  border-radius: 4px;
}

.preview-chapter-body {
  font-size: 15px;
  line-height: 2;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-break: break-word;
}

.preview-author-say {
  font-size: 13px;
  line-height: 1.8;
  color: var(--text-secondary);
  margin: 0;
  padding: 14px 16px;
  background: linear-gradient(135deg, rgba(212, 181, 176, 0.08), rgba(229, 201, 196, 0.05));
  border-radius: var(--radius-md);
  border: 1px dashed rgba(212, 181, 176, 0.4);
}

.preview-author-label {
  display: inline-block;
  margin-right: 8px;
  font-weight: 700;
  color: var(--color-accent-rose);
}

.preview-footer {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding-top: 24px;
  border-top: 1px solid rgba(139, 163, 181, 0.15);
  color: var(--text-muted);
  font-size: 13px;
  text-align: center;
}

.preview-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: none;
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  color: white;
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent-pink));
  box-shadow: 0 4px 16px rgba(139, 163, 181, 0.3);
  transition: all 0.3s ease;
  font-family: 'DM Sans', sans-serif;
}

.preview-btn:hover {
  box-shadow: 0 8px 24px rgba(139, 163, 181, 0.4);
  transform: translateY(-2px);
}
</style>
