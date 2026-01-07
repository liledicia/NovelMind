"""
晋江文学城爬虫服务
从 NovelMindScrawl.py 重构而来
"""
import requests
import re
import time
import random
from bs4 import BeautifulSoup
from datetime import date
from urllib.parse import urljoin, urlparse, parse_qs, quote
from typing import Optional, Dict


class NovelNotFoundException(Exception):
    """小说未找到异常"""
    pass


class CrawlerException(Exception):
    """爬虫异常"""
    pass


class JinjiangCrawler:
    """晋江文学城爬虫类"""

    def __init__(self):
        # 配置User-Agent池（用于反爬）
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
        ]
        self.base_url = "https://www.jjwxc.net/"

    def _get_headers(self) -> dict:
        """获取随机请求头（反爬策略）"""
        return {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive"
        }

    def _extract_novelid(self, novel_url: str) -> Optional[int]:
        """
        从小说链接URL中提取 novelid 参数

        Args:
            novel_url: 小说URL

        Returns:
            int: 小说ID，未找到返回None
        """
        query = parse_qs(urlparse(novel_url).query)
        if "novelid" in query and query["novelid"]:
            return int(query["novelid"][0])
        # 部分链接格式可能不同，做额外处理
        if "novelid=" in novel_url:
            return int(novel_url.split("novelid=")[-1].split("&")[0])
        return None

    def search_novel_by_web(self, novel_name: str) -> Optional[Dict]:
        """
        通过网页搜索找到小说（备用方案，用于AJAX搜索失败时）

        Args:
            novel_name: 小说名称

        Returns:
            dict: 包含 title, author, url, book_id 的字典，未找到返回None

        Raises:
            CrawlerException: 网络请求失败
        """
        try:
            # 使用GBK编码（晋江网站使用GBK编码）
            keyword_gbk = quote(novel_name.encode('gbk'))
            search_url = f"https://www.jjwxc.net/search.php?kw={keyword_gbk}&t=1"

            # 添加延迟避免被封
            time.sleep(random.uniform(2.0, 3.0))

            headers = self._get_headers()
            headers.update({
                "Referer": "https://www.jjwxc.net/"
            })

            resp = requests.get(search_url, headers=headers, timeout=15)
            resp.encoding = "gb18030"  # 晋江使用gb18030编码

            soup = BeautifulSoup(resp.text, "html.parser")

            # 查找小说链接（格式：onebook.php?novelid=xxxxx）
            novel_link = soup.find('a', href=lambda x: x and 'onebook.php?novelid=' in x)

            if not novel_link:
                return None

            # 提取小说信息
            title = novel_link.get_text(strip=True)
            href = novel_link.get('href')

            # 提取novelid
            novel_id_match = re.search(r'novelid=(\d+)', href)
            if not novel_id_match:
                return None

            novel_id = int(novel_id_match.group(1))

            # 查找作者信息（通常在小说链接的同一父元素中）
            author = None
            parent = novel_link.parent
            if parent:
                # 查找作者链接（格式：oneauthor.php?authorid=xxxxx）
                author_links = parent.find_all('a', href=lambda x: x and 'oneauthor.php?authorid=' in x)
                if author_links:
                    author = author_links[0].get_text(strip=True)

            # 如果没找到作者，设置为None（后续从详情页获取）
            if not author:
                author = None

            # 构造完整URL
            if not href.startswith('http'):
                url = f"https://www.jjwxc.net/onebook.php?novelid={novel_id}"
            else:
                url = href

            return {
                "title": title,
                "author": author,
                "url": url,
                "book_id": novel_id
            }

        except Exception as e:
            raise CrawlerException(f"网页搜索小说时出错: {str(e)}")

    def search_novel_by_name(self, novel_name: str) -> Optional[Dict]:
        """
        通过小说名称在晋江搜索找到小说
        优先使用AJAX接口，失败时fallback到网页搜索

        Args:
            novel_name: 小说名称

        Returns:
            dict: 包含 title, author, url, book_id 的字典，未找到返回None

        Raises:
            CrawlerException: 网络请求失败
        """
        # 方法1: 尝试AJAX接口（速度快）
        # type=1 表示搜索文章（作品）
        ajax_url = f"https://www.jjwxc.net/search/search_ajax.php?action=search&keywords={quote(novel_name)}&type=1&getfull=1"

        try:
            # 添加延迟避免被封
            time.sleep(random.uniform(2.0, 3.0))

            headers = self._get_headers()
            headers.update({
                "Referer": "https://www.jjwxc.net/search.php",
                "X-Requested-With": "XMLHttpRequest"
            })

            resp = requests.get(ajax_url, headers=headers, timeout=15)
            resp.encoding = "utf-8"

            # 解析JSON响应
            data = resp.json()

            # 检查响应状态
            if data.get("status") == 200:
                results = data.get("data", [])
                if results:
                    # 取第一个结果
                    first_result = results[0]
                    novel_id = first_result.get("novelid")
                    title = first_result.get("novelname")
                    author = first_result.get("authorname")

                    if novel_id:
                        # 构造小说详情页URL
                        url = f"https://www.jjwxc.net/onebook.php?novelid={novel_id}"

                        print(f"✓ AJAX搜索成功: {title}")
                        return {
                            "title": title,
                            "author": author,
                            "url": url,
                            "book_id": novel_id
                        }

            # AJAX搜索未找到结果，fallback到网页搜索
            print(f"⚠ AJAX搜索未找到《{novel_name}》，尝试网页搜索...")

        except Exception as e:
            # AJAX搜索出错，fallback到网页搜索
            print(f"⚠ AJAX搜索出错: {str(e)}，尝试网页搜索...")

        # 方法2: 使用网页搜索（备用方案）
        try:
            result = self.search_novel_by_web(novel_name)
            if result:
                print(f"✓ 网页搜索成功: {result.get('title')}")
            return result

        except Exception as e:
            raise CrawlerException(f"搜索小说失败（AJAX和网页搜索均失败）: {str(e)}")

    def fetch_novel_detail(self, novel_url: str) -> Dict:
        """
        抓取单本小说的详情页信息
        （从 NovelMindScrawl.py 重构）

        Args:
            novel_url: 小说详情页URL

        Returns:
            dict: 包含小说所有字段的字典

        Raises:
            CrawlerException: 爬取失败
        """
        data = {}

        try:
            # 添加延迟避免被封
            time.sleep(random.uniform(2.0, 3.0))

            resp = requests.get(novel_url, headers=self._get_headers(), timeout=15)
        except Exception as e:
            raise CrawlerException(f"获取小说详情失败: {novel_url}, 原因: {str(e)}")

        # 晋江详情页通常为 GBK 编码
        resp.encoding = "gb18030"
        soup = BeautifulSoup(resp.text, "html.parser")
        page_text = soup.get_text()  # 页面所有文本，用于搜索特定关键字

        # 0. 书名和作者（从页面标题或元数据中提取）
        # 方法1: 从 <title> 标签提取（格式通常为：书名_作者名_晋江文学城）
        page_title = soup.find('title')
        if page_title:
            title_text = page_title.get_text().strip()
            # 解析格式：书名_作者名_晋江文学城
            parts = title_text.split('_')
            if len(parts) >= 2:
                data['title'] = parts[0].strip()
                data['author'] = parts[1].strip()

        # 方法2: 从 itemprop 提取（更准确）
        title_tag = soup.find('span', attrs={'itemprop': 'articleSection'})
        if title_tag:
            data['title'] = title_tag.get_text(strip=True)

        author_tag = soup.find('span', attrs={'itemprop': 'author'})
        if author_tag:
            # 可能是 <span itemprop="author"><a>作者名</a></span>
            author_link = author_tag.find('a')
            if author_link:
                data['author'] = author_link.get_text(strip=True)
            else:
                data['author'] = author_tag.get_text(strip=True)

        # 方法3: 从"作者："文本后的链接提取（常见格式）
        if not data.get('author'):
            # 查找包含"作者："的文本
            for text_node in soup.find_all(string=re.compile(r'作者[:：]')):
                parent = text_node.parent
                if parent:
                    # 查找相邻的作者链接
                    author_link = parent.find('a', href=re.compile(r'oneauthor\.php\?authorid='))
                    if author_link:
                        data['author'] = author_link.get_text(strip=True)
                        break

        # 方法4: 从 meta 标签提取作者（备用）
        if not data.get('author'):
            meta_author = soup.find('meta', attrs={'name': 'Author'})
            if meta_author and meta_author.get('content'):
                data['author'] = meta_author.get('content').strip()

        # 方法5: 从 h1/h2 标签提取书名（备用）
        if not data.get('title'):
            h1_tag = soup.find('h1')
            if h1_tag:
                data['title'] = h1_tag.get_text(strip=True)

        # 1. 封面图片（优先使用晋江官方图床，过滤外部图床）
        data['cover_url'] = None

        def is_jjwxc_image(url: str) -> bool:
            """检查是否为晋江官方图床链接"""
            if not url:
                return False
            jjwxc_domains = [
                'jjwxc.net',  # 晋江官方域名
                'static.jjwxc.net',  # 静态资源
            ]
            return any(domain in url for domain in jjwxc_domains)

        def get_best_cover_url(img_candidates: list) -> Optional[str]:
            """从候选图片中选择最佳封面（优先晋江官方图床）"""
            jjwxc_urls = []
            external_urls = []

            for img_url in img_candidates:
                if not img_url:
                    continue
                full_url = urljoin(self.base_url, img_url)
                if is_jjwxc_image(full_url):
                    jjwxc_urls.append(full_url)
                else:
                    external_urls.append(full_url)

            # 优先返回晋江官方图床，否则返回外部图床
            if jjwxc_urls:
                return jjwxc_urls[0]
            elif external_urls:
                return external_urls[0]
            return None

        # 收集所有可能的封面候选
        cover_candidates = []

        # 方法1: 查找 itemprop="image" 的 img 标签
        cover_img = soup.find('img', attrs={"itemprop": "image"})
        if cover_img and cover_img.get('src'):
            cover_candidates.append(cover_img.get('src'))

        # 方法2: 查找 class 包含 noveldefaultimage 或 noveldisplayimage 的 img
        cover_img = soup.find('img', class_=lambda x: x and ('noveldefaultimage' in x.lower() or 'noveldisplayimage' in x.lower()))
        if cover_img and cover_img.get('src'):
            cover_candidates.append(cover_img.get('src'))

        # 方法3: 查找 td 中包含的图片（晋江常见结构）
        td_with_img = soup.find('td', attrs={'width': '100'})
        if td_with_img:
            img = td_with_img.find('img')
            if img and img.get('src'):
                cover_candidates.append(img.get('src'))

        # 选择最佳封面URL（优先晋江官方图床）
        data['cover_url'] = get_best_cover_url(cover_candidates)

        # 2. 小说简介（文案）
        intro_div = soup.find('div', id='novelintro', attrs={"itemprop": "description"})
        if intro_div:
            data['intro'] = intro_div.get_text("\n", strip=True)

        # 2. 主角/配角/其它信息
        idx = page_text.find("主角：")
        if idx != -1:
            snippet = page_text[idx: idx + 200]
            data['main_chars'] = None
            data['support_chars'] = None
            data['other_info'] = None
            parts = snippet.split('┃')
            for part in parts:
                part = part.strip()
                if part.startswith("主角："):
                    data['main_chars'] = part.replace("主角：", "").strip()
                elif part.startswith("配角："):
                    data['support_chars'] = part.replace("配角：", "").strip()
                elif part.startswith("其它："):
                    data['other_info'] = part.replace("其它：", "").strip()

        # 2.5 标签信息（新增）
        # 尝试多种可能的标签位置
        tags_patterns = [
            r"文章标签[:：]\s*([^\n]+)",
            r"标签[:：]\s*([^\n]+)",
            r"搜索关键字[:：]\s*([^\n]+)"
        ]

        data['tags'] = None
        for pattern in tags_patterns:
            tags_match = re.search(pattern, page_text)
            if tags_match:
                tags_text = tags_match.group(1).strip()
                # 清理标签文本，去除多余的空格和符号
                tags_text = re.sub(r'\s+', ' ', tags_text)
                tags_text = tags_text.replace('┃', '').strip()
                if tags_text and tags_text not in ['无', '暂无', '-', '']:
                    data['tags'] = tags_text
                    break

        # 如果上述方法都没找到，尝试从 span 标签中提取
        if not data['tags']:
            # 查找包含标签的元素
            for span in soup.find_all('span'):
                span_text = span.get_text(strip=True)
                if '文章标签' in span_text or '标签' in span_text:
                    parent = span.parent
                    if parent:
                        full_text = parent.get_text(strip=True)
                        # 提取标签内容
                        if '：' in full_text or ':' in full_text:
                            tags_part = re.split(r'[:：]', full_text, 1)
                            if len(tags_part) > 1:
                                tags_text = tags_part[1].strip()
                                tags_text = re.sub(r'\s+', ' ', tags_text)
                                if tags_text and tags_text not in ['无', '暂无', '-', '']:
                                    data['tags'] = tags_text
                                    break

        # 3. 基本信息列表
        info_ul = soup.find('ul', attrs={'name': 'printright'})
        if info_ul:
            li_tags = info_ul.find_all('li')
            for li in li_tags:
                text = li.get_text(strip=True)
                if text.startswith("文章类型："):
                    data['category'] = text.replace("文章类型：", "")
                elif text.startswith("作品视角："):
                    data['perspective'] = text.replace("作品视角：", "")
                elif text.startswith("所属系列："):
                    data['series'] = text.replace("所属系列：", "")
                elif text.startswith("文章进度："):
                    data['status'] = text.replace("文章进度：", "")
                elif text.startswith("全文字数："):
                    num_str = "".join(filter(str.isdigit, text))
                    data['word_count'] = int(num_str) if num_str else None
                elif text.startswith("版权转化："):
                    if "尚未出版" in text:
                        data['publish_status'] = "尚未出版"
                    else:
                        data['publish_status'] = "已出版" if li.find('img') else text.replace("版权转化：", "")
                elif text.startswith("签约状态："):
                    font_tag = li.find('font')
                    if font_tag:
                        data['sign_status'] = font_tag.get_text(strip=True)
                    else:
                        data['sign_status'] = text.replace("签约状态：", "")

        # 4. 底部统计数据（使用更灵活的匹配方式）
        # 初始化统计数据
        data['review_count'] = None
        data['favorite_count'] = None
        data['nutrient_count'] = None
        data['total_click_count'] = None
        data['score'] = None

        # 方法1: 尝试从整个页面文本中提取
        # 书评数
        m_review = re.search(r"总书评数[：:]\s*(\d+)", page_text)
        if m_review:
            data['review_count'] = int(m_review.group(1))

        # 收藏数
        m_fav = re.search(r"(?:当前)?(?:被)?收藏数[：:]\s*(\d+)", page_text)
        if m_fav:
            data['favorite_count'] = int(m_fav.group(1))

        # 营养液
        m_nutrient = re.search(r"营养液数[：:]\s*(\d+)", page_text)
        if m_nutrient:
            data['nutrient_count'] = int(m_nutrient.group(1))

        # 文章积分
        m_score = re.search(r"文章积分[：:]\s*([\d,]+)", page_text)
        if m_score:
            score_str = m_score.group(1).replace(',', '')
            data['score'] = int(score_str) if score_str.isdigit() else None

        # 点击数
        m_click = re.search(r"(?:非V章节)?总点击数[：:]\s*(\d+)", page_text)
        if m_click:
            data['total_click_count'] = int(m_click.group(1))

        # 5. 最新更新时间和章节数
        if "最新更新" in page_text:
            m3 = re.search(r"最新更新[:：](\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", page_text)
            if m3:
                data['last_update_time'] = m3.group(1)
        chapter_links = soup.find_all('a', href=re.compile(r'novelid=\d+&chapterid=\d+'))
        data['chapter_count'] = len(chapter_links)

        return data

    def crawl_novel_complete(self, novel_name: str) -> Dict:
        """
        完整爬取流程：搜索 → 获取详情

        Args:
            novel_name: 小说名称

        Returns:
            dict: 包含小说完整信息的字典（包括book_id, title, author, url及所有详情字段）

        Raises:
            NovelNotFoundException: 小说未找到
            CrawlerException: 爬取过程出错
        """
        # Step 1: 搜索小说
        search_result = self.search_novel_by_name(novel_name)

        if not search_result:
            raise NovelNotFoundException(f"未找到小说: {novel_name}")

        # Step 2: 获取详情
        detail = self.fetch_novel_detail(search_result['url'])

        # Step 3: 合并数据
        complete_data = {
            **search_result,  # book_id, title, url
            **detail  # 所有详情字段
        }

        return complete_data


if __name__ == "__main__":
    # 测试爬虫功能
    crawler = JinjiangCrawler()

    print("测试1: 搜索小说")
    print("=" * 50)
    result = crawler.search_novel_by_name("天涯客")
    if result:
        print(f"找到小说: {result['title']}")
        print(f"URL: {result['url']}")
        print(f"ID: {result['book_id']}")
    else:
        print("未找到小说")
    print()

    # print("测试2: 完整爬取流程")
    # print("=" * 50)
    # try:
    #     data = crawler.crawl_novel_complete("天涯客")
    #     print(f"书名: {data.get('title')}")
    #     print(f"作者: {data.get('author')}")
    #     print(f"简介: {data.get('intro', '')[:100]}...")
    #     print(f"字数: {data.get('word_count')}")
    #     print(f"状态: {data.get('status')}")
    # except Exception as e:
    #     print(f"爬取失败: {e}")
