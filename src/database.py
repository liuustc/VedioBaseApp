"""
数据库操作模块
使用SQLite存储电影信息、标签等数据
"""
import sqlite3
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import threading
from loguru import logger


class Database:
    """数据库管理类"""

    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            # 默认数据库路径在用户目录
            db_dir = Path.home() / ".VideoBaseApp"
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = db_dir / "movies.db"

        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_database()

    def _init_database(self):
        """初始化数据库，创建表"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 电影表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS movies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE NOT NULL,
                    title TEXT,
                    file_size INTEGER,
                    duration INTEGER,
                    douban_rating REAL,
                    imdb_rating REAL,
                    user_rating REAL,
                    rating_source TEXT DEFAULT 'douban',
                    douban_intro TEXT,
                    imdb_intro TEXT,
                    imdb_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # 检查并添加user_rating字段（数据库迁移）
            try:
                cursor.execute("SELECT user_rating FROM movies LIMIT 1")
            except sqlite3.OperationalError:
                # 字段不存在，添加它
                cursor.execute("ALTER TABLE movies ADD COLUMN user_rating REAL")
                logger.info("数据库迁移：添加user_rating字段")

            # 检查并添加download_time字段（数据库迁移）
            try:
                cursor.execute("SELECT download_time FROM movies LIMIT 1")
            except sqlite3.OperationalError:
                # 字段不存在，添加它
                cursor.execute("ALTER TABLE movies ADD COLUMN download_time TIMESTAMP")
                logger.info("数据库迁移：添加download_time字段")

            # 标签表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    color TEXT DEFAULT '#3498db',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # 电影-标签关联表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS movie_tags (
                    movie_id INTEGER,
                    tag_id INTEGER,
                    PRIMARY KEY (movie_id, tag_id),
                    FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE,
                    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
                )
            ''')

            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_movies_file_path ON movies(file_path)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_movies_title ON movies(title)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name)')

            # 创建基础标签
            self._create_default_tags(cursor)

            conn.commit()
            conn.close()

    def _get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)

    def _create_default_tags(self, cursor):
        """创建默认标签"""
        default_tags = [
            ('未看过', '#e74c3c'),  # 红色
            ('已看过', '#2ecc71'),  # 绿色
            ('想看', '#f39c12'),    # 橙色
            ('在看', '#3498db'),    # 蓝色
        ]

        for name, color in default_tags:
            cursor.execute(
                "INSERT OR IGNORE INTO tags (name, color) VALUES (?, ?)",
                (name, color)
            )

    def _add_default_tag_to_movie(self, cursor, movie_id: int, tag_name: str):
        """为电影添加默认标签"""
        try:
            # 获取标签ID
            cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
            tag_row = cursor.fetchone()
            if tag_row:
                tag_id = tag_row[0]
                # 检查是否已存在
                cursor.execute(
                    "SELECT 1 FROM movie_tags WHERE movie_id = ? AND tag_id = ?",
                    (movie_id, tag_id)
                )
                if not cursor.fetchone():
                    cursor.execute(
                        "INSERT INTO movie_tags (movie_id, tag_id) VALUES (?, ?)",
                        (movie_id, tag_id)
                    )
                    logger.info(f"为电影 {movie_id} 添加默认标签: {tag_name}")
        except Exception as e:
            logger.error(f"添加默认标签失败: {e}")

    def _normalize_path(self, file_path: str) -> str:
        """规范化文件路径，统一使用正斜杠"""
        return file_path.replace('\\', '/')

    # 电影操作
    def add_movie(self, movie_data: Dict[str, Any]) -> int:
        """添加电影"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()

            # 规范化路径
            normalized_path = self._normalize_path(movie_data['file_path'])
            movie_data['file_path'] = normalized_path

            # 检查是否已存在（使用规范化后的路径）
            cursor.execute("SELECT id FROM movies WHERE file_path = ?", (normalized_path,))
            existing = cursor.fetchone()
            if existing:
                # 更新现有记录
                cursor.execute('''
                    UPDATE movies SET
                        title = ?,
                        file_size = ?,
                        duration = ?,
                        douban_rating = ?,
                        imdb_rating = ?,
                        user_rating = ?,
                        download_time = ?,
                        rating_source = ?,
                        douban_intro = ?,
                        imdb_intro = ?,
                        imdb_id = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE file_path = ?
                ''', (
                    movie_data.get('title'),
                    movie_data.get('file_size'),
                    movie_data.get('duration'),
                    movie_data.get('douban_rating'),
                    movie_data.get('imdb_rating'),
                    movie_data.get('user_rating'),
                    movie_data.get('download_time'),
                    movie_data.get('rating_source', 'douban'),
                    movie_data.get('douban_intro'),
                    movie_data.get('imdb_intro'),
                    movie_data.get('imdb_id'),
                    movie_data['file_path']
                ))
                movie_id = existing[0]
            else:
                # 插入新记录
                cursor.execute('''
                    INSERT INTO movies (
                        file_path, title, file_size, duration,
                        douban_rating, imdb_rating, user_rating, download_time, rating_source,
                        douban_intro, imdb_intro, imdb_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    movie_data['file_path'],
                    movie_data.get('title'),
                    movie_data.get('file_size'),
                    movie_data.get('duration'),
                    movie_data.get('douban_rating'),
                    movie_data.get('imdb_rating'),
                    movie_data.get('user_rating'),
                    movie_data.get('download_time'),
                    movie_data.get('rating_source', 'douban'),
                    movie_data.get('douban_intro'),
                    movie_data.get('imdb_intro'),
                    movie_data.get('imdb_id')
                ))
                movie_id = cursor.lastrowid

                # 为新电影添加"未看过"标签
                self._add_default_tag_to_movie(cursor, movie_id, '未看过')

            conn.commit()
            conn.close()
            return movie_id

    def get_movie_by_id(self, movie_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取电影"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT m.*, GROUP_CONCAT(t.name) as tag_names
                FROM movies m
                LEFT JOIN movie_tags mt ON m.id = mt.movie_id
                LEFT JOIN tags t ON mt.tag_id = t.id
                WHERE m.id = ?
                GROUP BY m.id
            ''', (movie_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None

    def get_movie_by_path(self, file_path: str) -> Optional[Dict[str, Any]]:
        """根据文件路径获取电影"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM movies WHERE file_path = ?', (file_path,))
            row = cursor.fetchone()
            conn.close()

            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None

    def get_all_movies(self) -> List[Dict[str, Any]]:
        """获取所有电影（去重后）"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()

            # 先清理重复记录，保留ID最大的（最新的）
            cursor.execute('''
                DELETE FROM movies WHERE id NOT IN (
                    SELECT MAX(id) FROM movies GROUP BY REPLACE(REPLACE(file_path, '/', '\\'), '\\', '/')
                )
            ''')
            deleted = cursor.rowcount
            if deleted > 0:
                logger.info(f"清理了 {deleted} 条重复记录")

            cursor.execute('''
                SELECT m.*, GROUP_CONCAT(t.name) as tag_names
                FROM movies m
                LEFT JOIN movie_tags mt ON m.id = mt.movie_id
                LEFT JOIN tags t ON mt.tag_id = t.id
                GROUP BY m.id
                ORDER BY m.title
            ''')
            rows = cursor.fetchall()

            # 提交删除操作
            conn.commit()
            conn.close()

            if rows:
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
            return []

    def search_movies(self, query: str) -> List[Dict[str, Any]]:
        """搜索电影"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT m.*, GROUP_CONCAT(t.name) as tag_names
                FROM movies m
                LEFT JOIN movie_tags mt ON m.id = mt.movie_id
                LEFT JOIN tags t ON mt.tag_id = t.id
                WHERE m.title LIKE ? OR m.file_path LIKE ?
                GROUP BY m.id
                ORDER BY m.title
            ''', (f'%{query}%', f'%{query}%'))
            rows = cursor.fetchall()
            conn.close()

            if rows:
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
            return []

    # 标签操作
    def add_tag(self, name: str, color: str = '#3498db') -> int:
        """添加标签"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()

            # 检查是否已存在
            cursor.execute("SELECT id FROM tags WHERE name = ?", (name,))
            existing = cursor.fetchone()
            if existing:
                return existing[0]

            cursor.execute('INSERT INTO tags (name, color) VALUES (?, ?)', (name, color))
            tag_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return tag_id

    def get_tag_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """根据名称获取标签"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM tags WHERE name = ?', (name,))
            row = cursor.fetchone()
            conn.close()

            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None

    def get_all_tags(self) -> List[Dict[str, Any]]:
        """获取所有标签"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM tags ORDER BY name')
            rows = cursor.fetchall()
            conn.close()

            if rows:
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
            return []

    def update_tag(self, tag_id: int, name: str, color: str):
        """更新标签"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE tags SET name = ?, color = ? WHERE id = ?', (name, color, tag_id))
            conn.commit()
            conn.close()

    def delete_tag(self, tag_id: int):
        """删除标签"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM tags WHERE id = ?', (tag_id,))
            conn.commit()
            conn.close()

    # 电影-标签关联操作
    def add_movie_tag(self, movie_id: int, tag_id: int):
        """添加电影标签关联"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO movie_tags (movie_id, tag_id) VALUES (?, ?)', (movie_id, tag_id))
                conn.commit()
            except sqlite3.IntegrityError:
                # 已存在，忽略
                pass
            conn.close()

    def remove_movie_tag(self, movie_id: int, tag_id: int):
        """移除电影标签关联"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM movie_tags WHERE movie_id = ? AND tag_id = ?', (movie_id, tag_id))
            conn.commit()
            conn.close()

    def get_movie_tags(self, movie_id: int) -> List[Dict[str, Any]]:
        """获取电影的所有标签"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT t.* FROM tags t
                JOIN movie_tags mt ON t.id = mt.tag_id
                WHERE mt.movie_id = ?
            ''', (movie_id,))
            rows = cursor.fetchall()
            conn.close()

            if rows:
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
            return []

    def get_movies_by_tag(self, tag_id: int) -> List[Dict[str, Any]]:
        """根据标签获取电影"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT m.* FROM movies m
                JOIN movie_tags mt ON m.id = mt.movie_id
                WHERE mt.tag_id = ?
                ORDER BY m.title
            ''', (tag_id,))
            rows = cursor.fetchall()
            conn.close()

            if rows:
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
            return []

    def update_user_rating(self, movie_id: int, rating: float) -> bool:
        """更新用户评分"""
        with self.lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE movies SET user_rating = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                    (rating, movie_id)
                )
                conn.commit()
                conn.close()
                logger.info(f"更新用户评分: movie_id={movie_id}, rating={rating}")
                return True
            except Exception as e:
                logger.error(f"更新用户评分失败: {e}")
                return False

    # 统计信息
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()

            stats = {}
            # 电影总数
            cursor.execute('SELECT COUNT(*) FROM movies')
            stats['total_movies'] = cursor.fetchone()[0]

            # 标签总数
            cursor.execute('SELECT COUNT(*) FROM tags')
            stats['total_tags'] = cursor.fetchone()[0]

            # 总文件大小
            cursor.execute('SELECT SUM(file_size) FROM movies')
            total_size = cursor.fetchone()[0]
            stats['total_size'] = total_size if total_size else 0

            conn.close()
            return stats


# 全局数据库实例
database = Database()
