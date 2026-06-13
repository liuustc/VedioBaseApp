"""
IMDb API模块
使用OMDb API获取电影信息
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


class IMDbAPI:
    """IMDb API客户端（OMDb）"""

    def __init__(self):
        self.base_url = "http://www.omdbapi.com/"
        self.api_key = config.get_imdb_api_key()
        self.timeout = 10
        self.cache = {}  # 简单缓存
        self.request_count = 0
        self.last_request_time = 0

    def _check_rate_limit(self):
        """检查请求频率限制"""
        current_time = time.time()
        # 每天1000次限制，平均每秒不超过0.01次
        if current_time - self.last_request_time < 0.1:
            time.sleep(0.1)
        self.last_request_time = current_time
        self.request_count += 1

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

        self._check_rate_limit()

        try:
            # 构造请求参数
            params = {
                'apikey': self.api_key,
                's': title,
                'type': 'movie',
                'r': 'json'
            }

            if year:
                params['y'] = year

            response = requests.get(self.base_url, params=params, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()

                if data.get('Response') == 'True' and data.get('Search'):
                    # 获取第一个结果
                    movie = data['Search'][0]

                    result = {
                        'title': movie.get('Title', title),
                        'year': movie.get('Year', year),
                        'imdb_id': movie.get('imdbID', ''),
                        'type': movie.get('Type', ''),
                        'poster': movie.get('Poster', ''),
                        'rating': None,  # 搜索结果不包含评分
                        'imdb_rating': None,
                    }

                    # 获取详细信息（包含评分）
                    if result['imdb_id']:
                        detail = self.get_movie_detail(result['imdb_id'])
                        if detail:
                            result.update(detail)

                    # 缓存结果
                    self.cache[cache_key] = result
                    return result
                else:
                    logger.warning(f"IMDb未找到电影: {title}")
                    return None
            else:
                logger.warning(f"IMDb搜索失败，状态码: {response.status_code}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"IMDb搜索请求异常: {e}")
            return None
        except Exception as e:
            logger.error(f"IMDb搜索解析异常: {e}")
            return None

    def get_movie_detail(self, imdb_id: str) -> Optional[Dict[str, Any]]:
        """
        获取电影详情（包含评分）

        Args:
            imdb_id: IMDb ID（如 tt3896198）

        Returns:
            电影详情字典，失败返回None
        """
        if not imdb_id:
            return None

        # 检查缓存
        cache_key = f"detail_{imdb_id}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        self._check_rate_limit()

        try:
            params = {
                'apikey': self.api_key,
                'i': imdb_id,
                'r': 'json',
                'plot': 'short'  # 简短剧情
            }

            response = requests.get(self.base_url, params=params, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()

                if data.get('Response') == 'True':
                    result = {
                        'imdb_id': imdb_id,
                        'title': data.get('Title', ''),
                        'year': data.get('Year', ''),
                        'imdb_rating': self._parse_rating(data.get('imdbRating', '')),
                        'imdb_votes': data.get('imdbVotes', ''),
                        'rated': data.get('Rated', ''),
                        'released': data.get('Released', ''),
                        'runtime': data.get('Runtime', ''),
                        'genre': data.get('Genre', ''),
                        'director': data.get('Director', ''),
                        'writer': data.get('Writer', ''),
                        'actors': data.get('Actors', ''),
                        'plot': data.get('Plot', ''),
                        'language': data.get('Language', ''),
                        'country': data.get('Country', ''),
                        'awards': data.get('Awards', ''),
                        'poster': data.get('Poster', ''),
                        'metascore': data.get('Metascore', ''),
                        'type': data.get('Type', ''),
                        'dvd': data.get('DVD', ''),
                        'box_office': data.get('BoxOffice', ''),
                        'production': data.get('Production', ''),
                        'website': data.get('Website', ''),
                    }

                    # 缓存结果
                    self.cache[cache_key] = result
                    return result
                else:
                    logger.warning(f"IMDb详情未找到: {imdb_id}")
                    return None
            else:
                logger.warning(f"IMDb详情请求失败，状态码: {response.status_code}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"IMDb详情请求异常: {e}")
            return None
        except Exception as e:
            logger.error(f"IMDb详情解析异常: {e}")
            return None

    def _parse_rating(self, rating_str: str) -> Optional[float]:
        """解析评分字符串"""
        try:
            if rating_str and rating_str != 'N/A':
                return float(rating_str)
        except (ValueError, TypeError):
            pass
        return None

    def search_movie_by_filename(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        根据文件名搜索电影

        Args:
            filename: 视频文件名（不含扩展名）

        Returns:
            电影信息字典，失败返回None
        """
        # 清理文件名
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
        import os
        import re

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

        # 移除方括号和括号内的内容
        name = re.sub(r'[\[\(][^\]\)]*[\]\)]', '', name)

        # 移除多余空格
        name = ' '.join(name.split())

        return name.strip()

    def get_request_count(self) -> int:
        """获取已请求数量"""
        return self.request_count


# 全局IMDbAPI实例
imdb_api = IMDbAPI()
