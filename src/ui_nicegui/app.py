"""
NiceGUI 主应用
严格复刻 PyQt6 版本的全部功能
"""
from nicegui import ui, app
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import sys
import os
import asyncio

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import config
from database import database
from scanner import scanner, is_junk_file
from tags import tag_manager
from metadata import metadata_extractor
from douban_api import douban_api
from imdb_api import imdb_api


class VideoBaseApp:
    """NiceGUI 视频库管理应用 - 完整复刻 PyQt6 版本"""

    def __init__(self):
        self.current_directory: Optional[str] = None
        self.movies_data: List[Dict[str, Any]] = []  # 原始电影数据
        self.filtered_movies: List[Dict[str, Any]] = []  # 过滤后的数据
        self.sort_column: int = -1  # 当前排序列
        self.sort_ascending: bool = True  # 排序方向
        # 过滤状态
        self.search_query: str = ''
        self.watch_status_filter: str = '全部'
        self.selected_tag_ids: List[int] = []
        self.rating_source: int = 0  # 0=豆瓣/IMDb, 1=我的评分
        self.min_rating: float = 0.0
        self.min_duration: int = 30  # 分钟

    def run(self, port: int = 8080):
        """启动应用"""
        self.setup_pages()
        ui.run(title='VideoBaseApp - 视频库管理', port=port, reload=False)

    def setup_pages(self):
        """设置页面路由"""

        @ui.page('/')
        def index():
            self.render_main_page()

        @ui.page('/movie/{movie_id}')
        def movie_detail(movie_id: int):
            self.render_detail_page(movie_id)

        @ui.page('/settings')
        def settings_page():
            self.render_settings_page()

    # ==================== 主页面 ====================

    def render_main_page(self):
        """渲染主页面 - 复刻 Qt 版本布局"""
        ui.add_head_html('''
        <style>
            body { background: #1a1a2e; color: #eee; font-family: 'Segoe UI', sans-serif; }
            .header-gradient { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
            .filter-panel { background: #16213e; border-radius: 8px; padding: 0 16px 16px 16px; }
            .filter-group { margin-bottom: 16px; }
            .filter-group-title { font-size: 14px; font-weight: bold; color: #8e8ea0; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; }
            .movie-row { cursor: pointer; transition: background 0.2s; }
            .movie-row:hover { background: #1e3a5f !important; }
            .sort-indicator { font-size: 10px; margin-left: 4px; }
            .action-bar { background: #16213e; border-radius: 8px; padding: 12px 16px; margin-top: 12px; }
            .stat-label { color: #8e8ea0; font-size: 13px; }
        </style>
        ''')

        with ui.column().classes('w-full min-h-screen'):
            # 顶部导航栏
            with ui.row().classes('w-full header-gradient p-4 items-center justify-between'):
                ui.label('🎬 VideoBaseApp').classes('text-h4 text-white font-bold')
                with ui.row().classes('items-center gap-2'):
                    ui.button('设置', on_click=lambda: ui.navigate.to('/settings'),
                              icon='settings').props('flat color=white')

            # 主内容区 - 左右分栏
            with ui.row().classes('w-full p-4 gap-4 items-start'):
                # 左侧过滤面板
                self._render_filter_panel()

                # 右侧电影列表
                with ui.column().classes('flex-1 gap-2'):
                    # 统计信息
                    self.stats_label = ui.label('加载中...').classes('stat-label')

                    # 电影表格
                    self._render_movie_table()

                    # 底部操作按钮
                    self._render_action_bar()

        # 加载数据
        self._load_initial_data()

    def _render_filter_panel(self):
        """渲染左侧过滤面板 - 复刻 Qt 版本"""
        last_dir = config.get_last_directory()
        with ui.column().classes('filter-panel w-72').style('min-width: 280px'):
            # 目录选择
            with ui.column().classes('filter-group'):
                ui.label('目录').classes('filter-group-title')
                self.dir_input = ui.input(
                    placeholder='输入视频目录路径...',
                    value=last_dir
                ).classes('w-full mb-2').props('dense dark')
                with ui.row().classes('w-full gap-2'):
                    ui.button('扫描目录', on_click=self._on_scan_clicked, icon='folder_open').props('dense color=primary')

            # 搜索
            with ui.column().classes('filter-group'):
                ui.label('搜索').classes('filter-group-title')
                self.search_input = ui.input(
                    placeholder='搜索电影...',
                    on_change=lambda e: self._on_search_changed(e.value)
                ).classes('w-full').props('dense dark')

            # 观看状态过滤
            with ui.column().classes('filter-group'):
                ui.label('观看状态').classes('filter-group-title')
                self.watch_status_select = ui.select(
                    ['全部', '未看过', '已看过', '想看', '在看'],
                    value='全部',
                    on_change=lambda e: self._on_watch_status_changed(e.value)
                ).classes('w-full').props('dense dark')

            # 标签过滤
            with ui.column().classes('filter-group'):
                ui.label('标签过滤').classes('filter-group-title')
                self.tags_container = ui.column().classes('w-full')

            # 评分过滤
            with ui.column().classes('filter-group'):
                ui.label('评分过滤').classes('filter-group-title')
                with ui.column().classes('w-full gap-2'):
                    with ui.row().classes('w-full items-center gap-2'):
                        ui.label('来源:').classes('text-caption')
                        self.rating_source_select = ui.select(
                            ['豆瓣/IMDb', '我的评分'],
                            value='豆瓣/IMDb',
                            on_change=lambda e: self._on_rating_source_changed(e.value)
                        ).classes('flex-1').props('dense dark')
                    with ui.row().classes('w-full items-center gap-2'):
                        ui.label('最低:').classes('text-caption')
                        self.rating_spin = ui.number(
                            value=0, min=0, max=10, step=0.5,
                            on_change=lambda e: self._on_min_rating_changed(e.value)
                        ).classes('flex-1').props('dense dark')

            # 时长过滤
            with ui.column().classes('filter-group'):
                ui.label('时长过滤').classes('filter-group-title')
                with ui.row().classes('w-full items-center gap-2'):
                    ui.label('最少(分钟):').classes('text-caption')
                    self.duration_spin = ui.number(
                        value=30, min=0, max=1440, step=10,
                        on_change=lambda e: self._on_min_duration_changed(e.value)
                    ).classes('flex-1').props('dense dark')

    def _render_movie_table(self):
        """渲染电影表格 - 复刻 Qt 版本的列"""
        columns = [
            {'name': 'id', 'label': 'ID', 'field': 'id', 'sortable': True, 'align': 'center'},
            {'name': 'title', 'label': '标题', 'field': 'title', 'sortable': True, 'align': 'left'},
            {'name': 'download_time', 'label': '下载时间', 'field': 'download_time_display', 'sortable': True, 'align': 'center'},
            {'name': 'file_size', 'label': '文件大小', 'field': 'file_size_display', 'sortable': True, 'align': 'center'},
            {'name': 'duration', 'label': '时长', 'field': 'duration_display', 'sortable': True, 'align': 'center'},
            {'name': 'user_rating', 'label': '我的评分', 'field': 'user_rating_display', 'sortable': True, 'align': 'center'},
            {'name': 'rating', 'label': '评分', 'field': 'rating_display', 'sortable': True, 'align': 'center'},
        ]

        self.movie_table = ui.table(
            columns=columns,
            rows=[],
            row_key='id',
            selection='single',
            pagination={'rowsPerPage': 50}
        ).classes('w-full').props('dark flat bordered')

        # 绑定行点击事件 - 使用 Quasar 的 row-click 事件
        self.movie_table.on('row-click', self._on_row_click)

    def _render_action_bar(self):
        """渲染底部操作按钮 - 复刻 Qt 版本"""
        with ui.row().classes('action-bar w-full items-center justify-between'):
            with ui.row().classes('items-center gap-2'):
                ui.button('刷新列表', on_click=self._refresh_movies, icon='refresh').props('color=primary')
                ui.button('拉取元数据', on_click=self._fetch_metadata, icon='download').props('color=secondary')
            with ui.row().classes('items-center gap-2'):
                ui.button('编辑', on_click=self._edit_selected_movie, icon='edit').props('color=info')
                ui.button('删除', on_click=self._delete_selected_movie, icon='delete').props('color=negative')

    # ==================== 详情页面 ====================

    def render_detail_page(self, movie_id: int):
        """渲染详情页面 - 严格复刻 Qt 版本的 MovieDetailsDialog"""
        movie = database.get_movie_by_id(movie_id)
        if not movie:
            ui.label('电影不存在').classes('text-h5')
            ui.button('返回首页', on_click=lambda: ui.navigate.to('/'))
            return

        self.current_movie = movie
        self.current_movie_id = movie_id

        ui.add_head_html('''
        <style>
            body { background: #1a1a2e; color: #eee; font-family: 'Segoe UI', sans-serif; }
            .header-gradient { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
            .detail-card { background: #16213e; border-radius: 12px; padding: 20px; margin-bottom: 16px; }
            .detail-title { font-size: 16px; font-weight: bold; color: #667eea; margin-bottom: 12px; }
            .info-label { color: #8e8ea0; font-size: 13px; }
            .info-value { color: #eee; font-size: 15px; margin-bottom: 8px; }
            .status-btn { min-width: 80px; }
            .status-btn-active { border: 2px solid #667eea !important; }
        </style>
        ''')

        with ui.column().classes('w-full min-h-screen'):
            # 顶部导航
            with ui.row().classes('w-full header-gradient p-4 items-center'):
                ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to('/')).props('flat color=white')
                ui.label(f'🎬 电影详情').classes('text-h5 text-white font-bold ml-4')

            # 详情内容
            with ui.column().classes('w-full p-6 max-w-4xl mx-auto'):
                # 1. 基本信息区
                self._render_basic_info(movie)

                # 2. 评分区
                self._render_rating_section(movie)

                # 3. 观看状态区
                self._render_watch_status(movie_id)

                # 4. 标签管理区
                self._render_tag_management(movie_id)

                # 5. 简介区
                self._render_intro_section(movie)

                # 底部按钮
                with ui.row().classes('w-full justify-center gap-4 mt-6 mb-8'):
                    ui.button('保存', on_click=self._save_movie_changes, icon='save').props('size=lg color=primary')
                    ui.button('取消', on_click=lambda: ui.navigate.to('/'), icon='cancel').props('size=lg color=grey')

    def _render_basic_info(self, movie: Dict):
        """渲染基本信息区 - 复刻 Qt 版本"""
        with ui.card().classes('w-full detail-card'):
            ui.label('基本信息').classes('detail-title')

            # 标题（可编辑）
            with ui.row().classes('w-full items-center gap-4 mb-4'):
                ui.label('标题:').classes('info-label w-20')
                self.title_input = ui.input(
                    value=movie.get('title', ''),
                    placeholder='输入标题...'
                ).classes('flex-1').props('dense dark')

            # 文件路径
            with ui.row().classes('w-full items-center gap-4 mb-4'):
                ui.label('文件路径:').classes('info-label w-20')
                file_path = movie.get('file_path', '').replace('\\', '/')
                ui.label(file_path).classes('info-value flex-1').style('word-break: break-all')

            # 播放按钮
            with ui.row().classes('w-full mb-4'):
                ui.space()
                ui.button('▶ 播放', on_click=lambda: self._play_video(movie['file_path']),
                          icon='play_arrow').props('color=primary')

            # 文件大小和时长
            with ui.grid(columns=2).classes('w-full gap-4'):
                with ui.column():
                    ui.label('文件大小:').classes('info-label')
                    ui.label(self._format_size(movie.get('file_size'))).classes('info-value')
                with ui.column():
                    ui.label('时长:').classes('info-label')
                    ui.label(self._format_duration(movie.get('duration'))).classes('info-value')

    def _render_rating_section(self, movie: Dict):
        """渲染评分区 - 复刻 Qt 版本的三个评分输入"""
        with ui.card().classes('w-full detail-card'):
            ui.label('评分').classes('detail-title')

            with ui.grid(columns=3).classes('w-full gap-4'):
                # 豆瓣评分
                with ui.column():
                    ui.label('豆瓣评分:').classes('info-label')
                    with ui.row().classes('items-center gap-2'):
                        self.douban_rating_input = ui.number(
                            value=movie.get('douban_rating') or 0,
                            min=0, max=10, step=0.1
                        ).classes('w-24').props('dense dark')
                        ui.label('/ 10').classes('text-caption')

                # IMDb 评分
                with ui.column():
                    ui.label('IMDb评分:').classes('info-label')
                    with ui.row().classes('items-center gap-2'):
                        self.imdb_rating_input = ui.number(
                            value=movie.get('imdb_rating') or 0,
                            min=0, max=10, step=0.1
                        ).classes('w-24').props('dense dark')
                        ui.label('/ 10').classes('text-caption')

                # 我的评分
                with ui.column():
                    ui.label('我的评分:').classes('info-label')
                    with ui.row().classes('items-center gap-2'):
                        self.user_rating_input = ui.number(
                            value=movie.get('user_rating') or 0,
                            min=0, max=10, step=0.5
                        ).classes('w-24').props('dense dark')
                        ui.label('/ 10').classes('text-caption')

    def _render_watch_status(self, movie_id: int):
        """渲染观看状态区 - 复刻 Qt 版本的四个切换按钮"""
        with ui.card().classes('w-full detail-card'):
            ui.label('观看状态').classes('detail-title')

            # 获取当前标签
            current_tags = tag_manager.get_movie_tags(movie_id)
            current_tag_names = [tag['name'] for tag in current_tags]

            with ui.row().classes('w-full gap-2'):
                for status in ['未看过', '已看过', '想看', '在看']:
                    is_active = status in current_tag_names
                    btn = ui.button(
                        status,
                        on_click=lambda s=status: self._switch_watch_status(movie_id, s)
                    ).props(f'outline {"color=primary" if is_active else "color=grey"} status-btn')

    def _render_tag_management(self, movie_id: int):
        """渲染标签管理区 - 复刻 Qt 版本"""
        with ui.card().classes('w-full detail-card'):
            ui.label('标签管理').classes('detail-title')

            # 当前标签
            with ui.row().classes('w-full items-center gap-2 mb-4'):
                ui.label('当前标签:').classes('info-label w-20')
                self.current_tags_row = ui.row().classes('flex-1 items-center gap-2')
                self._update_current_tags_display(movie_id)

            # 添加新标签
            with ui.row().classes('w-full items-center gap-2 mb-4'):
                ui.label('添加标签:').classes('info-label w-20')
                all_tags = tag_manager.get_all_tags()
                tag_names = [t['name'] for t in all_tags]
                self.new_tag_select = ui.select(
                    tag_names,
                    label='选择标签'
                ).classes('flex-1').props('dense dark')
                ui.button('添加', on_click=lambda: self._add_tag_to_movie(movie_id),
                          icon='add').props('color=primary dense')

            # 所有标签（双击添加）
            with ui.row().classes('w-full items-center gap-2'):
                ui.label('所有标签:').classes('info-label w-20')
                ui.label('点击标签添加').classes('text-caption text-grey-5')
            with ui.row().classes('w-full gap-2 mt-2 flex-wrap'):
                for tag in all_tags:
                    chip = ui.chip(
                        tag['name'],
                        on_click=lambda t=tag: self._add_existing_tag(movie_id, t['id'])
                    ).props('clickable')
                    if tag.get('color'):
                        chip.style(f'background-color: {tag["color"]}30; color: {tag["color"]}')

    def _render_intro_section(self, movie: Dict):
        """渲染简介区 - 复刻 Qt 版本"""
        douban_intro = movie.get('douban_intro') or ''
        imdb_intro = movie.get('imdb_intro') or ''

        if not douban_intro and not imdb_intro:
            return

        with ui.card().classes('w-full detail-card'):
            ui.label('简介').classes('detail-title')

            if douban_intro:
                ui.label('豆瓣简介:').classes('info-label')
                ui.label(douban_intro).classes('info-value mb-4').style('white-space: pre-wrap')

            if imdb_intro:
                ui.label('IMDb简介:').classes('info-label')
                ui.label(imdb_intro).classes('info-value').style('white-space: pre-wrap')

    # ==================== 设置页面 ====================

    def render_settings_page(self):
        """渲染设置页面 - 复刻 Qt 版本的 SettingsDialog"""
        ui.add_head_html('''
        <style>
            body { background: #1a1a2e; color: #eee; font-family: 'Segoe UI', sans-serif; }
            .header-gradient { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
            .settings-card { background: #16213e; border-radius: 12px; padding: 20px; margin-bottom: 16px; }
        </style>
        ''')

        with ui.column().classes('w-full min-h-screen'):
            # 顶部导航
            with ui.row().classes('w-full header-gradient p-4 items-center'):
                ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to('/')).props('flat color=white')
                ui.label('⚙️ 设置').classes('text-h5 text-white font-bold ml-4')

            # 设置内容
            with ui.column().classes('w-full p-6 max-w-2xl mx-auto'):
                # FFmpeg 设置
                with ui.card().classes('w-full settings-card'):
                    ui.label('FFmpeg 设置').classes('text-h6 text-primary mb-4')
                    self.ffmpeg_path_input = ui.input(
                        label='FFmpeg 路径',
                        value=config.get_ffmpeg_path()
                    ).classes('w-full').props('dense dark')
                    with ui.row().classes('mt-2'):
                        ui.button('浏览...', on_click=self._browse_ffmpeg).props('color=primary')

                # API 设置
                with ui.card().classes('w-full settings-card'):
                    ui.label('API 设置').classes('text-h6 text-primary mb-4')
                    self.douban_enabled_check = ui.switch(
                        '启用豆瓣 API',
                        value=config.get('douban_enabled', True)
                    ).props('dark')
                    self.imdb_enabled_check = ui.switch(
                        '启用 IMDb API',
                        value=config.get('imdb_enabled', True)
                    ).props('dark')
                    self.imdb_api_key_input = ui.input(
                        label='IMDb API 密钥',
                        value=config.get_imdb_api_key()
                    ).classes('w-full mt-2').props('dense dark')

                # 扫描设置
                with ui.card().classes('w-full settings-card'):
                    ui.label('扫描设置').classes('text-h6 text-primary mb-4')
                    self.max_threads_spin = ui.number(
                        label='最大线程数',
                        value=config.get('max_scan_threads', 4),
                        min=1, max=16, step=1
                    ).classes('w-48').props('dense dark')

                # 按钮
                with ui.row().classes('w-full justify-center gap-4 mt-4'):
                    ui.button('保存设置', on_click=self._save_settings, icon='save').props('size=lg color=primary')
                    ui.button('取消', on_click=lambda: ui.navigate.to('/'), icon='cancel').props('size=lg color=grey')

    # ==================== 事件处理 ====================

    def _load_initial_data(self):
        """加载初始数据"""
        # 加载上次目录
        last_dir = config.get_last_directory()
        if last_dir:
            self.current_directory = last_dir

        self._load_movies()
        self._update_tags_filter()

    def _load_movies(self):
        """加载所有电影"""
        self.movies_data = database.get_all_movies()
        self._apply_filters()

    def _apply_filters(self):
        """应用所有过滤条件 - 复刻 Qt 版本的 filter_movies()"""
        # 去重和过滤垃圾文件
        seen_titles = {}
        for movie in self.movies_data:
            file_path = movie.get('file_path', '')
            if is_junk_file(file_path):
                continue

            title = movie.get('title', '')
            if title in seen_titles:
                existing = seen_titles[title]
                if movie.get('duration') and not existing.get('duration'):
                    seen_titles[title] = movie
                continue
            seen_titles[title] = movie

        # 应用过滤条件
        filtered = []
        for movie in seen_titles.values():
            # 搜索过滤
            if self.search_query:
                query = self.search_query.lower()
                title = (movie.get('title') or '').lower()
                file_path = (movie.get('file_path') or '').lower()
                if query not in title and query not in file_path:
                    continue

            # 观看状态过滤
            if self.watch_status_filter != '全部':
                movie_tags = tag_manager.get_movie_tags(movie['id'])
                movie_tag_names = [tag['name'] for tag in movie_tags]
                if self.watch_status_filter not in movie_tag_names:
                    continue

            # 评分过滤
            if self.rating_source == 0:
                rating = movie.get('douban_rating') or movie.get('imdb_rating') or 0
            else:
                rating = movie.get('user_rating') or 0

            if rating < self.min_rating:
                continue

            # 时长过滤
            duration = movie.get('duration', 0) or 0
            if duration < self.min_duration * 60:
                continue

            # 标签过滤
            if self.selected_tag_ids:
                movie_tags = tag_manager.get_movie_tags(movie['id'])
                movie_tag_ids = [tag['id'] for tag in movie_tags]
                if not any(tag_id in self.selected_tag_ids for tag_id in movie_tag_ids):
                    continue

            filtered.append(movie)

        # 应用排序
        if self.sort_column >= 0:
            filtered = self._sort_movies(filtered)

        self.filtered_movies = filtered
        self._update_table()

    def _sort_movies(self, movies: List[Dict]) -> List[Dict]:
        """排序电影列表"""
        def get_sort_key(movie, col):
            if col == 0:  # ID
                return int(movie.get('id', 0))
            elif col == 1:  # 标题
                val = movie.get('title', '')
                return str(val).lower() if val else ''
            elif col == 2:  # 下载时间
                val = movie.get('download_time', '')
                return str(val) if val else ''
            elif col == 3:  # 文件大小
                val = movie.get('file_size')
                return int(val) if val is not None else 0
            elif col == 4:  # 时长
                val = movie.get('duration')
                return int(val) if val is not None else 0
            elif col == 5:  # 我的评分
                val = movie.get('user_rating')
                return float(val) if val is not None else 0.0
            elif col == 6:  # 评分
                val = movie.get('douban_rating') or movie.get('imdb_rating')
                return float(val) if val is not None else 0.0
            return 0

        return sorted(
            movies,
            key=lambda x: get_sort_key(x, self.sort_column),
            reverse=not self.sort_ascending
        )

    def _update_table(self):
        """更新表格显示"""
        rows = []
        for movie in self.filtered_movies:
            # 下载时间格式化 - 只显示日期和时间，不显示秒
            download_time = movie.get('download_time', '') or ''
            if download_time and len(download_time) > 16:
                display_time = download_time[:16]
            else:
                display_time = download_time or 'N/A'

            # 评分
            rating = movie.get('douban_rating') or movie.get('imdb_rating')
            rating_str = f"{rating:.1f}" if rating else 'N/A'

            rows.append({
                'id': movie.get('id'),
                'title': movie.get('title', '未知'),
                'download_time_display': display_time,
                'file_size_display': self._format_size(movie.get('file_size')),
                'duration_display': self._format_duration(movie.get('duration')),
                'rating_display': rating_str,
                'user_rating_display': self._format_user_rating(movie.get('user_rating')),
            })

        self.movie_table.rows = rows
        self.movie_table.update()

        # 更新统计
        self.stats_label.text = f'共 {len(rows)} 部电影'

    def _update_tags_filter(self):
        """更新标签过滤树 - 复刻 Qt 版本的 update_tags_tree()"""
        self.tags_container.clear()
        tags = tag_manager.get_all_tags()

        with self.tags_container:
            for tag in tags:
                movies_count = len(tag_manager.get_movies_by_tag(tag['id']))
                is_checked = tag['id'] in self.selected_tag_ids
                ui.switch(
                    f"{tag['name']} ({movies_count})",
                    value=is_checked,
                    on_change=lambda e, tid=tag['id']: self._on_tag_filter_toggled(tid, e.value)
                ).props('dense dark')

    def _update_current_tags_display(self, movie_id: int):
        """更新当前标签显示"""
        self.current_tags_row.clear()
        current_tags = tag_manager.get_movie_tags(movie_id)

        with self.current_tags_row:
            for tag in current_tags:
                chip = ui.chip(tag['name'], removable=True)
                chip.on('remove', lambda t=tag: self._remove_tag_from_movie(movie_id, t['id']))
                if tag.get('color'):
                    chip.style(f'background-color: {tag["color"]}30; color: {tag["color"]}')

    # ==================== 事件回调 ====================

    def _on_scan_clicked(self):
        """点击扫描按钮"""
        directory = self.dir_input.value
        if not directory:
            ui.notify('请输入目录路径', type='warning')
            return
        self._scan_directory(directory)

    def _on_search_changed(self, value: str):
        """搜索变化"""
        self.search_query = value
        self._apply_filters()

    def _on_watch_status_changed(self, value: str):
        """观看状态过滤变化"""
        self.watch_status_filter = value
        self._apply_filters()

    def _on_tag_filter_toggled(self, tag_id: int, checked: bool):
        """标签过滤切换"""
        if checked:
            if tag_id not in self.selected_tag_ids:
                self.selected_tag_ids.append(tag_id)
        else:
            if tag_id in self.selected_tag_ids:
                self.selected_tag_ids.remove(tag_id)
        self._apply_filters()

    def _on_rating_source_changed(self, value: str):
        """评分来源变化"""
        self.rating_source = 0 if value == '豆瓣/IMDb' else 1
        self._apply_filters()

    def _on_min_rating_changed(self, value: float):
        """最低评分变化"""
        self.min_rating = value or 0
        self._apply_filters()

    def _on_min_duration_changed(self, value: float):
        """最小时长变化"""
        self.min_duration = int(value or 0)
        self._apply_filters()

    def _on_row_click(self, event):
        """行点击事件 - 跳转到详情页"""
        try:
            # Quasar row-click 事件参数格式: (evt, row, index)
            # NiceGUI 会将其作为 tuple 传入 event.args
            args = event.args

            # 提取行数据 - 通常在第二个位置
            row_data = None
            if isinstance(args, (list, tuple)) and len(args) >= 2:
                # args[0] 是原始事件对象, args[1] 是行数据
                row_data = args[1]
            elif isinstance(args, dict):
                row_data = args

            # 从行数据中获取 movie_id
            if isinstance(row_data, dict):
                movie_id = row_data.get('id')
                if movie_id:
                    ui.navigate.to(f'/movie/{movie_id}')
                    return

            # 如果上面的方法都失败，尝试从 selection 获取
            if self.movie_table.selected:
                selected = self.movie_table.selected
                if isinstance(selected, list) and len(selected) > 0:
                    movie_id = selected[0].get('id')
                elif isinstance(selected, dict):
                    movie_id = selected.get('id')
                else:
                    movie_id = None
                if movie_id:
                    ui.navigate.to(f'/movie/{movie_id}')

        except Exception as e:
            print(f'行点击事件处理错误: {e}, args={event.args}')

    def _refresh_movies(self):
        """刷新电影列表"""
        if self.current_directory:
            self._scan_directory(self.current_directory)
        else:
            self._load_movies()
            ui.notify('列表已刷新', type='info')

    def _scan_directory(self, directory: str):
        """扫描目录 - 带进度提示"""
        if not directory or not Path(directory).exists():
            ui.notify('请输入有效的目录路径', type='warning')
            return

        self.current_directory = directory
        config.set_last_directory(directory)

        # 创建进度对话框
        dialog = ui.dialog()
        with dialog, ui.card():
            ui.label('正在扫描目录...').classes('text-h6')
            progress = ui.linear_progress(value=0).classes('w-full')
            status_label = ui.label('准备中...').classes('text-caption')

        async def do_scan():
            dialog.open()
            try:
                video_files = scanner.scan_directory(directory)
                total = len(video_files)
                count = 0

                for i, video_path in enumerate(video_files):
                    try:
                        file_info = scanner.get_file_info(video_path)
                        modified_time = file_info.get('modified_time', 0)
                        download_time = datetime.fromtimestamp(modified_time).strftime(
                            '%Y-%m-%d %H:%M:%S') if modified_time else None

                        # 检查是否已存在
                        existing = database.get_movie_by_path(video_path)
                        if not existing:
                            movie_data = {
                                'file_path': video_path,
                                'title': Path(video_path).stem,
                                'file_size': file_info['file_size'],
                                'download_time': download_time,
                            }
                            database.add_movie(movie_data)
                            count += 1

                        # 更新进度
                        progress.value = (i + 1) / total
                        status_label.text = f'处理中 [{i + 1}/{total}]: {Path(video_path).name}'
                        await asyncio.sleep(0)  # 让出事件循环，允许 UI 更新

                    except Exception as e:
                        print(f'保存失败: {e}')

                dialog.close()
                ui.notify(f'扫描完成，添加了 {count} 部电影', type='positive')
                self._load_movies()
                self._update_tags_filter()

            except Exception as e:
                dialog.close()
                ui.notify(f'扫描失败: {e}', type='negative')

        asyncio.create_task(do_scan())

    def _fetch_metadata(self):
        """拉取元数据 - 复刻 Qt 版本的 MetaWorker"""
        movies = self.filtered_movies
        if not movies:
            ui.notify('列表为空，请先扫描目录或调整过滤条件', type='warning')
            return

        # 确认对话框
        confirm_dialog = ui.dialog()
        with confirm_dialog, ui.card():
            ui.label(f'将为当前列表中的 {len(movies)} 部电影拉取元数据（时长、评分等）').classes('text-h6')
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('取消', on_click=confirm_dialog.close).props('color=grey')
                ui.button('确认', on_click=lambda: start_fetch()).props('color=primary')

        # 进度对话框
        progress_dialog = ui.dialog()
        with progress_dialog, ui.card():
            ui.label('正在拉取元数据...').classes('text-h6')
            progress = ui.linear_progress(value=0).classes('w-full')
            status_label = ui.label('准备中...').classes('text-caption')

        async def do_fetch():
            progress_dialog.open()
            try:
                processed = 0
                for i, movie in enumerate(movies):
                    try:
                        file_path = movie['file_path']
                        if not os.path.exists(file_path):
                            continue

                        # 获取时长
                        if not movie.get('duration'):
                            duration = metadata_extractor.get_video_duration(file_path)
                            if duration:
                                movie['duration'] = duration

                        # 获取评分
                        filename = Path(file_path).stem
                        if not movie.get('douban_rating') and config.get("douban_enabled", True):
                            douban_info = douban_api.search_movie_by_filename(filename)
                            if douban_info:
                                movie['douban_rating'] = douban_info.get('rating')
                                movie['rating_source'] = 'douban'

                        if not movie.get('douban_rating') and config.get("imdb_enabled", True):
                            imdb_info = imdb_api.search_movie_by_filename(filename)
                            if imdb_info:
                                movie['imdb_rating'] = imdb_info.get('imdb_rating')
                                movie['imdb_id'] = imdb_info.get('imdb_id')
                                movie['rating_source'] = 'imdb'
                                movie['imdb_intro'] = imdb_info.get('plot')

                        # 更新数据库
                        database.add_movie(movie)
                        processed += 1

                        # 更新进度
                        progress.value = (i + 1) / len(movies)
                        display_name = movie.get('title', '')[:40]
                        status_label.text = f'处理中 [{i + 1}/{len(movies)}]: {display_name}'
                        await asyncio.sleep(0)  # 让出事件循环，允许 UI 更新

                    except Exception as e:
                        print(f'拉取元数据失败: {e}')

                progress_dialog.close()
                ui.notify(f'元数据拉取完成，处理了 {processed} 部电影', type='positive')
                self._load_movies()

            except Exception as e:
                progress_dialog.close()
                ui.notify(f'拉取失败: {e}', type='negative')

        def start_fetch():
            confirm_dialog.close()
            asyncio.create_task(do_fetch())

        confirm_dialog.open()

    def _edit_selected_movie(self):
        """编辑选中的电影"""
        selected = self.movie_table.selected
        if not selected:
            ui.notify('请先选择一部电影', type='warning')
            return

        # 获取选中行的 ID
        if isinstance(selected, list) and len(selected) > 0:
            movie_id = selected[0].get('id')
        elif isinstance(selected, dict):
            movie_id = selected.get('id')
        else:
            ui.notify('请先选择一部电影', type='warning')
            return

        if movie_id:
            ui.navigate.to(f'/movie/{movie_id}')

    def _delete_selected_movie(self):
        """删除选中的电影"""
        selected = self.movie_table.selected
        if not selected:
            ui.notify('请先选择一部电影', type='warning')
            return

        # 获取选中行的 ID
        if isinstance(selected, list) and len(selected) > 0:
            movie_id = selected[0].get('id')
        elif isinstance(selected, dict):
            movie_id = selected.get('id')
        else:
            ui.notify('请先选择一部电影', type='warning')
            return

        if not movie_id:
            return

        movie = database.get_movie_by_id(movie_id)
        if not movie:
            return

        # 确认对话框
        dialog = ui.dialog()
        with dialog, ui.card():
            ui.label(f'确定要删除电影 "{movie["title"]}" 吗？').classes('text-h6')
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('取消', on_click=dialog.close).props('color=grey')
                ui.button('删除', on_click=lambda: do_delete()).props('color=negative')

        def do_delete():
            try:
                conn = database._get_connection()
                cursor = conn.cursor()
                cursor.execute('DELETE FROM movies WHERE id = ?', (movie_id,))
                conn.commit()
                conn.close()
                dialog.close()
                ui.notify(f'已删除电影: {movie["title"]}', type='positive')
                self._load_movies()
                self._update_tags_filter()
            except Exception as e:
                dialog.close()
                ui.notify(f'删除失败: {e}', type='negative')

        dialog.open()

    def _save_movie_changes(self):
        """保存电影更改 - 复刻 Qt 版本的 save_changes()"""
        try:
            movie_id = self.current_movie_id

            conn = database._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE movies SET
                    title = ?,
                    douban_rating = ?,
                    imdb_rating = ?,
                    user_rating = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                self.title_input.value,
                self.douban_rating_input.value or None,
                self.imdb_rating_input.value or None,
                self.user_rating_input.value or None,
                movie_id
            ))
            conn.commit()
            conn.close()

            ui.notify('电影信息已保存', type='positive')
            ui.navigate.to('/')

        except Exception as e:
            ui.notify(f'保存失败: {e}', type='negative')

    def _switch_watch_status(self, movie_id: int, new_status: str):
        """切换观看状态 - 复刻 Qt 版本的 switch_watch_status()"""
        watch_statuses = ['未看过', '已看过', '想看', '在看']

        # 移除所有观看状态标签
        for status in watch_statuses:
            tag = tag_manager.get_tag_by_name(status)
            if tag:
                tag_manager.remove_tag_from_movie(movie_id, tag['id'])

        # 添加新的观看状态标签
        new_tag = tag_manager.get_tag_by_name(new_status)
        if new_tag:
            tag_manager.add_tag_to_movie(movie_id, new_tag['id'])

        # 刷新页面
        ui.navigate.to(f'/movie/{movie_id}')

    def _add_tag_to_movie(self, movie_id: int):
        """添加标签到电影"""
        tag_name = self.new_tag_select.value
        if not tag_name:
            ui.notify('请选择标签', type='warning')
            return

        tag = tag_manager.get_tag_by_name(tag_name)
        if tag:
            tag_manager.add_tag_to_movie(movie_id, tag['id'])
            ui.notify(f'已添加标签: {tag_name}', type='positive')
            ui.navigate.to(f'/movie/{movie_id}')

    def _add_existing_tag(self, movie_id: int, tag_id: int):
        """添加现有标签"""
        tag_manager.add_tag_to_movie(movie_id, tag_id)
        ui.notify('已添加标签', type='positive')
        ui.navigate.to(f'/movie/{movie_id}')

    def _remove_tag_from_movie(self, movie_id: int, tag_id: int):
        """从电影移除标签"""
        tag_manager.remove_tag_from_movie(movie_id, tag_id)
        ui.notify('已移除标签', type='info')
        ui.navigate.to(f'/movie/{movie_id}')

    def _play_video(self, file_path: str):
        """播放视频"""
        try:
            file_path = file_path.replace('/', '\\')
            if os.path.exists(file_path):
                os.startfile(file_path)
                ui.notify('正在打开视频...', type='info')
            else:
                ui.notify(f'文件不存在: {file_path}', type='negative')
        except Exception as e:
            ui.notify(f'播放失败: {e}', type='negative')

    def _browse_ffmpeg(self):
        """浏览 FFmpeg 路径 - 使用上传或手动输入"""
        ui.notify('请直接在输入框中输入 FFmpeg 可执行文件的完整路径', type='info')

    def _save_settings(self):
        """保存设置"""
        try:
            config.set_ffmpeg_path(self.ffmpeg_path_input.value)
            config.set('douban_enabled', self.douban_enabled_check.value)
            config.set('imdb_enabled', self.imdb_enabled_check.value)
            config.set_imdb_api_key(self.imdb_api_key_input.value)
            config.set('max_scan_threads', int(self.max_threads_spin.value))
            config.save_config()

            ui.notify('设置已保存', type='positive')
            ui.navigate.to('/')
        except Exception as e:
            ui.notify(f'保存设置失败: {e}', type='negative')

    # ==================== 工具方法 ====================

    def _format_size(self, size_bytes: Optional[int]) -> str:
        """格式化文件大小"""
        if not size_bytes:
            return 'N/A'
        if size_bytes >= 1024 ** 3:
            return f"{size_bytes / (1024 ** 3):.2f} GB"
        elif size_bytes >= 1024 ** 2:
            return f"{size_bytes / (1024 ** 2):.1f} MB"
        return f"{size_bytes / 1024:.1f} KB"

    def _format_duration(self, seconds: Optional[int]) -> str:
        """格式化时长"""
        if not seconds:
            return 'N/A'
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}:{secs:02d}"

    def _format_user_rating(self, rating: Optional[float]) -> str:
        """格式化用户评分"""
        if rating:
            return f"{rating:.1f}"
        return 'N/A'


def run_nicegui(port: int = 8080):
    """启动 NiceGUI 应用"""
    app_instance = VideoBaseApp()
    app_instance.run(port=port)
