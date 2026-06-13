"""
豆瓣API模块
通过豆瓣搜索获取电影信息
"""
import os
import re
import requests
import time
import random
from typing import Optional, Dict, Any
from loguru import logger
from urllib.parse import quote

from config import config


class DoubanAPI:
    """豆瓣API客户端"""

    def __init__(self):
        self.base_url = "https://movie.douban.com/j/search"
        self.search_url = f"{self.base_url}"
        self.headers = {
            'User-Agent': self._get_random_user_agent(),
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://movie.douban.com/',
        }
        self.timeout = 10
        self.cache = {}  # 简单缓存

    def _get_random_user_agent(self) -> str:
        """获取随机User-Agent"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        ]
        return random.choice(user_agents)

    def search_movie(self, title: str, year: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        搜索电影

        Args:
            title: 电影标题
            year: 年份（可选）

        Returns:
            电影信息字典，失败返回None
        """
        # 检查缓存
        cache_key = f"{title}_{year}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        # 构造搜索关键词
        search_query = title
        if year:
            search_query = f"{title} {year}"

        try:
            # 更新User-Agent
            self.headers['User-Agent'] = self._get_random_user_agent()

            # 豆瓣搜索接口（需要处理反爬）
            url = f"https://movie.douban.com/j/search?q={quote(search_query)}"

            # 添加延迟，避免频繁请求
            time.sleep(random.uniform(1, 3))

            response = requests.get(url, headers=self.headers, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()
                if data.get('items') and len(data['items']) > 0:
                    # 获取第一个结果
                    movie = data['items'][0]

                    # 提取关键信息
                    result = {
                        'title': movie.get('title', title),
                        'year': movie.get('year', year),
                        'rating': self._parse_rating(movie.get('rating', '')),
                        'url': movie.get('url', ''),
                        'cover': movie.get('cover', ''),
                        'douban_id': movie.get('id', ''),
                        'directors': movie.get('directors', []),
                        'casts': movie.get('casts', []),
                        'genres': movie.get('genres', []),
                    }

                    # 缓存结果
                    self.cache[cache_key] = result
                    return result
                else:
                    logger.warning(f"豆瓣未找到电影: {search_query}")
                    return None
            else:
                logger.warning(f"豆瓣搜索失败，状态码: {response.status_code}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"豆瓣搜索请求异常: {e}")
            return None
        except Exception as e:
            logger.error(f"豆瓣搜索解析异常: {e}")
            return None

    def _parse_rating(self, rating_str: str) -> Optional[float]:
        """解析评分字符串"""
        try:
            if rating_str:
                return float(rating_str)
        except (ValueError, TypeError):
            pass
        return None

    def get_movie_detail(self, douban_id: str) -> Optional[Dict[str, Any]]:
        """
        获取电影详情

        Args:
            douban_id: 豆瓣电影ID

        Returns:
            电影详情字典，失败返回None
        """
        if not douban_id:
            return None

        # 检查缓存
        cache_key = f"detail_{douban_id}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            # 豆瓣电影详情页面（需要解析HTML，这里简化处理）
            # 实际应用中可能需要使用第三方库如beautifulsoup4
            # 这里返回基本信息

            # 更新User-Agent
            self.headers['User-Agent'] = self._get_random_user_agent()

            # 添加延迟
            time.sleep(random.uniform(1, 2))

            # 简化处理：返回基本信息
            result = {
                'douban_id': douban_id,
                'intro': '',  # 需要解析HTML获取
                'tags': [],
            }

            # 缓存结果
            self.cache[cache_key] = result
            return result

        except Exception as e:
            logger.error(f"获取豆瓣详情失败: {e}")
            return None

    def search_movie_by_filename(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        根据文件名搜索电影

        Args:
            filename: 视频文件名（不含扩展名）

        Returns:
            电影信息字典，失败返回None
        """
        # 清理文件名：移除常见噪音词
        cleaned_name = self._clean_filename(filename)

        # 尝试提取年份
        year = None
        import re
        year_match = re.search(r'[(\[](\d{4})[)\]]', filename)
        if year_match:
            year = int(year_match.group(1))

        # 搜索电影
        return self.search_movie(cleaned_name, year)

    def _clean_filename(self, filename: str) -> str:
        """清理文件名，移除常见噪音词"""
        # 移除扩展名
        name, _ = os.path.splitext(filename)

        # 移除常见噪音词
        noise_words = [
            '720p', '1080p', '2160p', '4K', 'HD', 'BluRay', 'BD',
            'WEB-DL', 'WEBRip', 'HDTV', 'DVDRip', 'CDRip',
            'x264', 'x265', 'H264', 'H265', 'AVC', 'HEVC',
            'AAC', 'AC3', 'DTS', 'FLAC',
            'chs', 'cht', 'eng', 'sub', 'raw',
            'FANS', 'CCTV', 'TVRip', 'REPACK', 'PROPER'
        ]

        # 移除方括号和括号内的内容（通常包含噪音信息）
        name = re.sub(r'[\[\(][^\]\)]*[\]\)]', '', name)

        # 移除多余空格
        name = ' '.join(name.split())

        return name.strip()


# 全局豆瓣API实例
douban_api = DoubanAPI()
