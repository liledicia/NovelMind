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

/**
 * 处理图片URL - 修复混合内容和防盗链问题
 * @param {string} imageUrl - 原始图片URL
 * @returns {string} - 处理后的图片URL
 */
export const getProxiedImageUrl = (imageUrl) => {
  if (!imageUrl) return ''

  // 修复新浪图床的 HTTP 协议问题（混合内容阻止）
  // 将 http://ww*.sinaimg.cn 转换为 https://wx*.sinaimg.cn
  if (imageUrl.startsWith('http://') && imageUrl.includes('sinaimg.cn')) {
    // http://ww2.sinaimg.cn -> https://wx2.sinaimg.cn
    // http://ww3.sinaimg.cn -> https://wx3.sinaimg.cn
    imageUrl = imageUrl
      .replace('http://', 'https://')
      .replace(/ww(\d+)\.sinaimg\.cn/, 'wx$1.sinaimg.cn')
  }

  return imageUrl
}

/**
 * 获取晋江官方封面URL作为fallback
 * @param {number|string} novelId - 小说ID
 * @returns {string} - 晋江官方封面URL
 */
export const getJJWXCFallbackCover = (novelId) => {
  if (!novelId) return ''
  // 使用晋江官方的动态封面API（只需要novelid参数）
  return `https://i9-static.jjwxc.net/novelimage.php?novelid=${novelId}`
}
