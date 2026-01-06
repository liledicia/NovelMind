/**
 * 格式化字数
 * @param {number} count - 字数
 * @returns {string}
 */
export const formatWordCount = (count) => {
  if (!count) return '未知'
  if (count >= 10000) {
    return `${(count / 10000).toFixed(1)}万字`
  }
  return `${count}字`
}

/**
 * 解析标签字符串为数组
 * @param {string} tagsStr - 标签字符串
 * @returns {Array}
 */
export const parseTags = (tagsStr) => {
  if (!tagsStr) return []
  return tagsStr.split(' ').filter(tag => tag.trim())
}

/**
 * 格式化数字（添加千分位）
 * @param {number} num - 数字
 * @returns {string}
 */
export const formatNumber = (num) => {
  if (!num && num !== 0) return '0'
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}
