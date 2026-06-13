"""
标签管理模块
管理电影标签的创建、编辑、删除等操作
"""
from typing import List, Optional, Dict, Any
from loguru import logger

from database import database


class TagManager:
    """标签管理器"""

    def __init__(self):
        pass

    def create_tag(self, name: str, color: str = '#3498db') -> Optional[int]:
        """
        创建标签

        Args:
            name: 标签名称
            color: 标签颜色（十六进制）

        Returns:
            标签ID，失败返回None
        """
        try:
            tag_id = database.add_tag(name, color)
            logger.info(f"创建标签成功: {name} (ID: {tag_id})")
            return tag_id
        except Exception as e:
            logger.error(f"创建标签失败: {e}")
            return None

    def get_tag(self, tag_id: int) -> Optional[Dict[str, Any]]:
        """获取标签信息"""
        try:
            tags = database.get_all_tags()
            for tag in tags:
                if tag['id'] == tag_id:
                    return tag
            return None
        except Exception as e:
            logger.error(f"获取标签失败: {e}")
            return None

    def get_tag_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """根据名称获取标签"""
        try:
            return database.get_tag_by_name(name)
        except Exception as e:
            logger.error(f"根据名称获取标签失败: {e}")
            return None

    def get_all_tags(self) -> List[Dict[str, Any]]:
        """获取所有标签"""
        try:
            return database.get_all_tags()
        except Exception as e:
            logger.error(f"获取所有标签失败: {e}")
            return []

    def update_tag(self, tag_id: int, name: str, color: str) -> bool:
        """
        更新标签

        Args:
            tag_id: 标签ID
            name: 新名称
            color: 新颜色

        Returns:
            是否成功
        """
        try:
            database.update_tag(tag_id, name, color)
            logger.info(f"更新标签成功: ID={tag_id}, name={name}")
            return True
        except Exception as e:
            logger.error(f"更新标签失败: {e}")
            return False

    def delete_tag(self, tag_id: int) -> bool:
        """
        删除标签

        Args:
            tag_id: 标签ID

        Returns:
            是否成功
        """
        try:
            database.delete_tag(tag_id)
            logger.info(f"删除标签成功: ID={tag_id}")
            return True
        except Exception as e:
            logger.error(f"删除标签失败: {e}")
            return False

    def add_tag_to_movie(self, movie_id: int, tag_id: int):
        """为电影添加标签"""
        try:
            database.add_movie_tag(movie_id, tag_id)
            logger.info(f"为电影 {movie_id} 添加标签 {tag_id}")
        except Exception as e:
            logger.error(f"为电影添加标签失败: {e}")

    def remove_tag_from_movie(self, movie_id: int, tag_id: int):
        """从电影移除标签"""
        try:
            database.remove_movie_tag(movie_id, tag_id)
            logger.info(f"从电影 {movie_id} 移除标签 {tag_id}")
        except Exception as e:
            logger.error(f"从电影移除标签失败: {e}")

    def get_movie_tags(self, movie_id: int) -> List[Dict[str, Any]]:
        """获取电影的所有标签"""
        try:
            return database.get_movie_tags(movie_id)
        except Exception as e:
            logger.error(f"获取电影标签失败: {e}")
            return []

    def get_movies_by_tag(self, tag_id: int) -> List[Dict[str, Any]]:
        """根据标签获取电影"""
        try:
            return database.get_movies_by_tag(tag_id)
        except Exception as e:
            logger.error(f"根据标签获取电影失败: {e}")
            return []

    def search_tags(self, query: str) -> List[Dict[str, Any]]:
        """搜索标签"""
        try:
            all_tags = self.get_all_tags()
            return [tag for tag in all_tags if query.lower() in tag['name'].lower()]
        except Exception as e:
            logger.error(f"搜索标签失败: {e}")
            return []


# 全局标签管理器实例
tag_manager = TagManager()
