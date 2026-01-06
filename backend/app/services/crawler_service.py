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

    def search_novel_by_name(self, novel_name: str) -> Optional[Dict]:
        """
        通过小说名称在晋江搜索找到小说（使用AJAX接口）

        Args:
            novel_name: 小说名称

        Returns:
            dict: 包含 title, author, url, book_id 的字典，未找到返回None

        Raises:
            CrawlerException: 网络请求失败
        """
        # 晋江搜索AJAX接口
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
            if data.get("status") != 200:
                return None

            # 获取搜索结果列表
            results = data.get("data", [])
            if not results:
                return None

            # 取第一个结果
            first_result = results[0]
            novel_id = first_result.get("novelid")
            title = first_result.get("novelname")
            author = first_result.get("authorname")

            if not novel_id:
                return None

            # 构造小说详情页URL
            url = f"https://www.jjwxc.net/onebook.php?novelid={novel_id}"

            return {
                "title": title,
                "author": author,
                "url": url,
                "book_id": novel_id
            }

        except Exception as e:
            raise CrawlerException(f"搜索小说时出错: {str(e)}")

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

        # 1. 小说简介（文案）
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

        # 4. 底部统计数据
        stats_div = soup.find('div', attrs={'align': 'center'})
        if stats_div:
            stats_text = stats_div.get_text()
            m = re.search(r"总书评数：(\d+).*?当前被收藏数：(\d+).*?营养液数：(\d+).*?文章积分：([\d,]+)", stats_text)
            if m:
                data['review_count'] = int(m.group(1))
                data['favorite_count'] = int(m.group(2))
                data['nutrient_count'] = int(m.group(3))
                score_str = m.group(4).replace(',', '')
                data['score'] = int(score_str) if score_str.isdigit() else None
            m2 = re.search(r"非V章节总点击数：(\d+)", stats_text)
            if m2:
                data['total_click_count'] = int(m2.group(1))

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
