"""
主窗口类
PyQt6 GUI界面
"""
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from loguru import logger

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QListWidget, QListWidgetItem, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QToolBar, QStatusBar,
    QLabel, QPushButton, QLineEdit, QComboBox, QCheckBox,
    QFileDialog, QMessageBox, QProgressDialog, QTabWidget,
    QGroupBox, QFormLayout, QSpinBox, QDoubleSpinBox,
    QColorDialog, QTreeWidgetItem, QTreeWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer
from PyQt6.QtGui import QIcon, QPixmap, QImage, QAction, QColor, QFont

from config import config
from database import database
from scanner import scanner, is_junk_file
from metadata import metadata_extractor
from douban_api import douban_api
from imdb_api import imdb_api
from tags import tag_manager


class ScanWorker(QThread):
    """扫描工作线程 - 只扫描文件并保存基本信息"""
    progress_updated = pyqtSignal(int, int, str)  # current, total, filename
    finished = pyqtSignal(list)  # movie_data_list
    error = pyqtSignal(str)

    def __init__(self, directory: str):
        super().__init__()
        self.directory = directory

    def run(self):
        try:
            # 扫描视频文件
            video_files = scanner.scan_directory(self.directory)

            if not video_files:
                self.finished.emit([])
                return

            movie_data_list = []

            for i, video_path in enumerate(video_files):
                self.progress_updated.emit(i + 1, len(video_files), Path(video_path).name)

                # 获取文件信息
                file_info = scanner.get_file_info(video_path)

                # 从文件修改时间转换为datetime字符串
                from datetime import datetime
                modified_time = file_info.get('modified_time', 0)
                download_time = datetime.fromtimestamp(modified_time).strftime('%Y-%m-%d %H:%M:%S') if modified_time else None

                # 只保存基本信息
                movie_data = {
                    'file_path': video_path,
                    'title': Path(video_path).stem,
                    'file_size': file_info['file_size'],
                    'download_time': download_time,
                }

                # 检查数据库中是否已存在该电影
                existing = database.get_movie_by_path(video_path)
                if existing:
                    # 已存在则跳过，保留原有数据
                    movie_data = existing
                else:
                    # 保存到数据库
                    try:
                        movie_id = database.add_movie(movie_data)
                        movie_data['id'] = movie_id
                    except Exception as e:
                        self.error.emit(f"保存电影失败: {e}")

                movie_data_list.append(movie_data)

            self.finished.emit(movie_data_list)

        except Exception as e:
            self.error.emit(f"扫描失败: {e}")


class DurationWorker(QThread):
    """时长提取工作线程"""
    progress_updated = pyqtSignal(int, int, str)  # current, total, filename
    finished = pyqtSignal(int)  # processed count
    error = pyqtSignal(str)

    def __init__(self, movies=None):
        super().__init__()
        self._should_stop = False
        self._movies = movies  # 可以指定要处理的影片列表

    def stop(self):
        self._should_stop = True

    def run(self):
        try:
            # 获取电影列表
            movies = self._movies if self._movies is not None else database.get_all_movies()
            if not movies:
                self.finished.emit(0)
                return

            processed = 0
            for i, movie in enumerate(movies):
                if self._should_stop:
                    break

                self.progress_updated.emit(i + 1, len(movies), movie.get('title', ''))

                # 跳过已有时长的电影
                if movie.get('duration'):
                    continue

                file_path = movie['file_path']
                if not os.path.exists(file_path):
                    continue

                try:
                    # 提取视频时长
                    logger.info(f"正在获取时长: {file_path}")
                    duration = metadata_extractor.get_video_duration(file_path)
                    if duration:
                        movie['duration'] = duration
                        logger.info(f"获取时长成功: {file_path} -> {duration}秒")
                        # 更新数据库
                        database.add_movie(movie)
                        processed += 1
                    else:
                        logger.warning(f"获取时长失败: {file_path}")

                except Exception as e:
                    logger.error(f"获取时长失败 {file_path}: {e}")

            self.finished.emit(processed)

        except Exception as e:
            self.error.emit(f"获取时长失败: {e}")


class MetaWorker(QThread):
    """元数据拉取工作线程 - 拉取时长、评分等信息"""
    progress_updated = pyqtSignal(int, int, str)  # current, total, filename
    finished = pyqtSignal(int)  # processed count
    error = pyqtSignal(str)

    def __init__(self, movies=None):
        super().__init__()
        self._should_stop = False
        self._movies = movies  # 可以指定要处理的影片列表

    def stop(self):
        self._should_stop = True

    def run(self):
        try:
            # 获取电影列表
            movies = self._movies if self._movies is not None else database.get_all_movies()
            if not movies:
                self.finished.emit(0)
                return

            processed = 0
            for i, movie in enumerate(movies):
                if self._should_stop:
                    break

                self.progress_updated.emit(i + 1, len(movies), movie.get('title', ''))

                # 跳过已有元数据的电影
                if movie.get('duration') and movie.get('douban_rating'):
                    continue

                file_path = movie['file_path']
                if not os.path.exists(file_path):
                    continue

                try:
                    # 提取视频时长
                    if not movie.get('duration'):
                        logger.info(f"正在获取时长: {file_path}")
                        duration = metadata_extractor.get_video_duration(file_path)
                        if duration:
                            movie['duration'] = duration
                            logger.info(f"获取时长成功: {file_path} -> {duration}秒")
                        else:
                            logger.warning(f"获取时长失败: {file_path}")

                    # 获取评分信息
                    filename = Path(file_path).stem

                    # 尝试豆瓣
                    if not movie.get('douban_rating') and config.get("douban_enabled", True):
                        douban_info = douban_api.search_movie_by_filename(filename)
                        if douban_info:
                            movie['douban_rating'] = douban_info.get('rating')
                            movie['rating_source'] = 'douban'

                    # 如果豆瓣失败，尝试IMDb
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

                except Exception as e:
                    logger.error(f"拉取元数据失败 {file_path}: {e}")

            self.finished.emit(processed)

        except Exception as e:
            self.error.emit(f"拉取元数据失败: {e}")


class MovieListWidget(QTableWidget):
    """电影列表控件"""

    def __init__(self):
        super().__init__()
        self.sort_column = -1  # 当前排序列
        self.sort_order = Qt.SortOrder.AscendingOrder  # 当前排序顺序
        self.movies_data = []  # 保存原始电影数据
        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        self.setColumnCount(7)
        self.setHorizontalHeaderLabels(['ID', '标题', '下载时间', '文件大小', '时长', '我的评分', '评分'])
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # 注意：不启用setSortingEnabled，使用自定义排序逻辑

        # 设置列宽模式 - 允许用户拖动调整
        header = self.horizontalHeader()
        header.setStretchLastSection(False)
        header.setMinimumSectionSize(150)  # 最小列宽150，防止标题被过度压缩
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)      # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)    # 标题 - 自动伸展
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)      # 下载时间
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)      # 文件大小
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)      # 时长
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)      # 我的评分
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)      # 评分

        # 设置固定列宽
        self.setColumnWidth(0, 50)   # ID
        self.setColumnWidth(1, 400)  # 标题 - 初始宽度400
        self.setColumnWidth(2, 150)  # 下载时间
        self.setColumnWidth(3, 100)  # 文件大小
        self.setColumnWidth(4, 80)   # 时长
        self.setColumnWidth(5, 80)   # 我的评分
        self.setColumnWidth(6, 80)   # 评分

        # 连接表头点击信号
        self.horizontalHeader().sectionClicked.connect(self.on_header_clicked)

    def on_header_clicked(self, column):
        """表头点击事件"""
        # 如果点击同一列，切换排序顺序
        if column == self.sort_column:
            if self.sort_order == Qt.SortOrder.AscendingOrder:
                self.sort_order = Qt.SortOrder.DescendingOrder
            else:
                self.sort_order = Qt.SortOrder.AscendingOrder
        else:
            self.sort_column = column
            self.sort_order = Qt.SortOrder.AscendingOrder

        # 执行排序
        self.sort_items(column, self.sort_order)

    def sort_items(self, column, order):
        """排序项目"""
        if not self.movies_data:
            return

        def get_sort_key(movie, col):
            """获取排序键值，确保类型正确"""
            if col == 0:  # ID
                val = movie.get('id')
                return int(val) if val is not None else 0
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

        # 排序
        reverse = (order == Qt.SortOrder.DescendingOrder)
        sorted_movies = sorted(
            self.movies_data,
            key=lambda x: get_sort_key(x, column),
            reverse=reverse
        )

        # 更新显示
        self.update_movies(sorted_movies)

    def update_movies(self, movies: List[Dict[str, Any]]):
        """更新电影列表"""
        self.movies_data = movies  # 保存原始数据
        self.setRowCount(len(movies))

        for row, movie in enumerate(movies):
            # ID
            id_item = QTableWidgetItem()
            id_item.setData(Qt.ItemDataRole.DisplayRole, movie.get('id', 0))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.setItem(row, 0, id_item)

            # 标题 - 截断过长标题，保留完整标题用于tooltip
            title = movie.get('title', '')
            display_title = title[:60] + '...' if len(title) > 60 else title
            title_item = QTableWidgetItem(display_title)
            title_item.setToolTip(title)  # 鼠标悬停显示完整标题
            title_item.setData(Qt.ItemDataRole.UserRole, title)  # 存储完整标题
            self.setItem(row, 1, title_item)

            # 下载时间
            download_time = movie.get('download_time', '')
            # 只显示日期和时间，不显示秒
            if download_time and len(download_time) > 16:
                display_time = download_time[:16]
            else:
                display_time = download_time or 'N/A'
            time_item = QTableWidgetItem(display_time)
            time_item.setToolTip(download_time)  # 鼠标悬停显示完整时间
            time_item.setData(Qt.ItemDataRole.UserRole, download_time)  # 存储原始值用于排序
            time_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.setItem(row, 2, time_item)

            # 文件大小
            file_size = movie.get('file_size', 0) or 0
            if file_size >= 1024 * 1024 * 1024:  # GB
                size_str = f"{file_size / (1024**3):.2f} GB"
            elif file_size >= 1024 * 1024:  # MB
                size_str = f"{file_size / (1024**2):.1f} MB"
            else:
                size_str = 'N/A'
            size_item = QTableWidgetItem(size_str)
            size_item.setData(Qt.ItemDataRole.UserRole, file_size)  # 存储原始值用于排序
            size_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.setItem(row, 3, size_item)

            # 时长
            duration = movie.get('duration', 0) or 0
            if duration:
                minutes = duration // 60
                seconds = duration % 60
                duration_str = f"{minutes}:{seconds:02d}"
            else:
                duration_str = 'N/A'
            duration_item = QTableWidgetItem(duration_str)
            duration_item.setData(Qt.ItemDataRole.UserRole, duration)  # 存储原始值用于排序
            duration_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.setItem(row, 4, duration_item)

            # 我的评分
            user_rating = movie.get('user_rating') or 0
            user_rating_str = f"{user_rating:.1f}" if user_rating else 'N/A'
            user_rating_item = QTableWidgetItem(user_rating_str)
            user_rating_item.setData(Qt.ItemDataRole.UserRole, user_rating)  # 存储原始值用于排序
            user_rating_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.setItem(row, 5, user_rating_item)

            # 评分
            rating = movie.get('douban_rating') or movie.get('imdb_rating') or 0
            rating_str = f"{rating:.1f}" if rating else 'N/A'
            rating_item = QTableWidgetItem(rating_str)
            rating_item.setData(Qt.ItemDataRole.UserRole, rating)  # 存储原始值用于排序
            rating_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.setItem(row, 6, rating_item)


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.current_directory = None
        self.setup_ui()
        self.load_settings()

    def closeEvent(self, event):
        """关闭事件 - 退出应用程序"""
        QApplication.quit()
        event.accept()

    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("视频库管理工具")
        self.setGeometry(100, 100, 1200, 800)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QHBoxLayout(central_widget)

        # 左侧面板
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 1)

        # 右侧面板
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 3)

        # 创建工具栏
        self.create_toolbar()

        # 创建状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # 加载数据
        self.load_movies()

    def create_left_panel(self):
        """创建左侧面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # 目录选择
        dir_group = QGroupBox("目录")
        dir_layout = QHBoxLayout()
        self.dir_label = QLabel("未选择目录")
        self.dir_label.setStyleSheet("color: white;")
        dir_layout.addWidget(self.dir_label)
        self.select_dir_btn = QPushButton("选择目录")
        self.select_dir_btn.clicked.connect(self.select_directory)
        dir_layout.addWidget(self.select_dir_btn)
        dir_group.setLayout(dir_layout)
        layout.addWidget(dir_group)

        # 搜索
        search_group = QGroupBox("搜索")
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索电影...")
        self.search_input.textChanged.connect(self.search_movies)
        search_layout.addWidget(self.search_input)
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)

        # 观看状态过滤
        watch_status_group = QGroupBox("观看状态")
        watch_status_layout = QVBoxLayout()

        self.watch_status_combo = QComboBox()
        self.watch_status_combo.addItems(["全部", "未看过", "已看过", "想看", "在看"])
        self.watch_status_combo.currentIndexChanged.connect(self.filter_movies)
        watch_status_layout.addWidget(self.watch_status_combo)

        watch_status_group.setLayout(watch_status_layout)
        layout.addWidget(watch_status_group)

        # 标签过滤
        tags_group = QGroupBox("标签过滤")
        tags_layout = QVBoxLayout()
        self.tags_tree = QTreeWidget()
        self.tags_tree.setHeaderLabel("标签")
        self.tags_tree.itemChanged.connect(self.on_tag_filter_changed)
        tags_layout.addWidget(self.tags_tree)
        tags_group.setLayout(tags_layout)
        layout.addWidget(tags_group)

        # 评分过滤
        rating_group = QGroupBox("评分过滤")
        rating_layout = QVBoxLayout()

        # 评分来源选择
        rating_source_layout = QHBoxLayout()
        rating_source_layout.addWidget(QLabel("评分来源:"))
        self.rating_source_combo = QComboBox()
        self.rating_source_combo.addItems(["豆瓣/IMDb", "我的评分"])
        self.rating_source_combo.currentIndexChanged.connect(self.filter_movies)
        rating_source_layout.addWidget(self.rating_source_combo)
        rating_layout.addLayout(rating_source_layout)

        # 最低评分
        rating_value_layout = QHBoxLayout()
        rating_value_layout.addWidget(QLabel("最低评分:"))
        self.rating_spin = QDoubleSpinBox()
        self.rating_spin.setRange(0, 10)
        self.rating_spin.setSingleStep(0.5)
        self.rating_spin.valueChanged.connect(self.filter_movies)
        rating_value_layout.addWidget(self.rating_spin)
        rating_layout.addLayout(rating_value_layout)

        rating_group.setLayout(rating_layout)
        layout.addWidget(rating_group)

        # 时长过滤
        duration_group = QGroupBox("时长过滤")
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("最小时长(分钟):"))
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(0, 1440)  # 最大24小时
        self.duration_spin.setSingleStep(10)
        self.duration_spin.setValue(30)
        self.duration_spin.valueChanged.connect(self.filter_movies)
        duration_layout.addWidget(self.duration_spin)
        duration_group.setLayout(duration_layout)
        layout.addWidget(duration_group)

        layout.addStretch()
        return panel

    def create_right_panel(self):
        """创建右侧面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # 电影列表
        self.movie_list = MovieListWidget()
        self.movie_list.itemDoubleClicked.connect(self.on_movie_double_clicked)
        layout.addWidget(self.movie_list)

        # 底部按钮
        button_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("刷新列表")
        self.refresh_btn.clicked.connect(self.refresh_movies)
        button_layout.addWidget(self.refresh_btn)

        self.fetch_meta_btn = QPushButton("拉取元数据")
        self.fetch_meta_btn.clicked.connect(self.fetch_metadata)
        button_layout.addWidget(self.fetch_meta_btn)

        self.edit_btn = QPushButton("编辑")
        self.edit_btn.clicked.connect(self.edit_movie)
        button_layout.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("删除")
        self.delete_btn.clicked.connect(self.delete_movie)
        button_layout.addWidget(self.delete_btn)

        layout.addLayout(button_layout)

        return panel

    def create_toolbar(self):
        """创建工具栏"""
        toolbar = QToolBar("主工具栏")
        self.addToolBar(toolbar)

        # 扫描动作
        scan_action = QAction(QIcon(), "扫描目录", self)
        scan_action.triggered.connect(self.select_directory)
        toolbar.addAction(scan_action)

        # 刷新动作
        refresh_action = QAction(QIcon(), "刷新", self)
        refresh_action.triggered.connect(self.refresh_movies)
        toolbar.addAction(refresh_action)

        toolbar.addSeparator()

        # 设置动作
        settings_action = QAction(QIcon(), "设置", self)
        settings_action.triggered.connect(self.show_settings)
        toolbar.addAction(settings_action)

    def load_settings(self):
        """加载设置"""
        # 加载FFmpeg路径
        ffmpeg_path = config.get_ffmpeg_path()
        if not os.path.exists(ffmpeg_path):
            self.status_bar.showMessage(f"警告: FFmpeg路径不存在: {ffmpeg_path}", 5000)

        # 加载上次打开的目录
        last_directory = config.get_last_directory()
        if last_directory and os.path.exists(last_directory):
            self.current_directory = last_directory
            self.dir_label.setText(last_directory)
            self.dir_label.setStyleSheet("color: white;")
            self.status_bar.showMessage(f"已加载上次目录: {last_directory}", 3000)

    def select_directory(self):
        """选择目录"""
        directory = QFileDialog.getExistingDirectory(self, "选择视频目录")
        if directory:
            self.current_directory = directory
            self.dir_label.setText(directory)
            self.dir_label.setStyleSheet("color: white;")
            # 保存到配置
            config.set_last_directory(directory)
            self.scan_directory(directory)

    def scan_directory(self, directory: str):
        """扫描目录"""
        # 显示进度对话框
        self.scan_progress = QProgressDialog("正在扫描目录...", "取消", 0, 0, self)
        self.scan_progress.setWindowModality(Qt.WindowModality.WindowModal)
        self.scan_progress.setMinimumDuration(0)

        # 创建扫描线程
        self.scan_worker = ScanWorker(directory)
        self.scan_worker.progress_updated.connect(self.update_scan_progress)
        self.scan_worker.finished.connect(self.on_scan_finished)
        self.scan_worker.error.connect(self.on_scan_error)
        self.scan_worker.start()

    def update_scan_progress(self, current: int, total: int, filename: str):
        """更新扫描进度"""
        self.status_bar.showMessage(f"扫描中 [{current}/{total}]: {filename}")

    def on_scan_finished(self, movie_data_list: List[Dict[str, Any]]):
        """扫描完成"""
        self.scan_progress.close()
        self.status_bar.showMessage(f"扫描完成，找到 {len(movie_data_list)} 部电影", 5000)
        self.load_movies()

        # 扫描完成后自动提取时长
        if movie_data_list:
            self.extract_duration_for_all()

    def on_scan_error(self, error: str):
        """扫描错误"""
        self.scan_progress.close()
        QMessageBox.warning(self, "扫描错误", error)
        self.status_bar.showMessage(f"扫描错误: {error}", 5000)

    def fetch_metadata(self):
        """拉取元数据 - 仅对当前列表中的影片生效"""
        # 获取当前列表中显示的影片
        movies = self.movie_list.movies_data
        if not movies:
            QMessageBox.information(self, "提示", "列表为空，请先扫描目录或调整过滤条件")
            return

        reply = QMessageBox.question(
            self, "确认",
            f"将为当前列表中的 {len(movies)} 部电影拉取元数据（时长、评分等），是否继续？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # 创建进度对话框
        self.meta_progress = QProgressDialog("正在拉取元数据...", "取消", 0, len(movies), self)
        self.meta_progress.setWindowModality(Qt.WindowModality.WindowModal)
        self.meta_progress.setMinimumDuration(0)
        self.meta_progress.setMinimumWidth(400)

        # 创建元数据拉取线程，传递当前列表的影片
        self.meta_worker = MetaWorker(movies)
        self.meta_worker.progress_updated.connect(self.update_meta_progress)
        self.meta_worker.finished.connect(self.on_meta_finished)
        self.meta_worker.error.connect(self.on_meta_error)
        self.meta_progress.canceled.connect(self.meta_worker.stop)
        self.meta_worker.start()

    def update_meta_progress(self, current: int, total: int, filename: str):
        """更新元数据拉取进度"""
        self.meta_progress.setValue(current)
        display_name = filename if len(filename) <= 40 else filename[:37] + "..."
        self.meta_progress.setLabelText(f"正在处理 [{current}/{total}]\n{display_name}")

    def on_meta_finished(self, processed: int):
        """元数据拉取完成"""
        self.meta_progress.close()
        self.status_bar.showMessage(f"元数据拉取完成，处理了 {processed} 部电影", 5000)
        self.load_movies()

    def on_meta_error(self, error: str):
        """元数据拉取错误"""
        self.meta_progress.close()
        QMessageBox.warning(self, "拉取错误", error)
        self.status_bar.showMessage(f"拉取错误: {error}", 5000)

    def extract_duration_for_all(self):
        """为所有电影提取时长"""
        movies = database.get_all_movies()
        if not movies:
            return

        # 检查是否有时长为空的电影
        movies_without_duration = [m for m in movies if not m.get('duration')]
        if not movies_without_duration:
            return

        # 创建进度对话框
        self.duration_progress = QProgressDialog("正在提取时长...", "取消", 0, len(movies_without_duration), self)
        self.duration_progress.setWindowModality(Qt.WindowModality.WindowModal)
        self.duration_progress.setMinimumDuration(0)
        self.duration_progress.setMinimumWidth(400)

        # 创建时长提取线程
        self.duration_worker = DurationWorker()
        self.duration_worker.progress_updated.connect(self.update_duration_progress)
        self.duration_worker.finished.connect(self.on_duration_finished)
        self.duration_worker.error.connect(self.on_duration_error)
        self.duration_progress.canceled.connect(self.duration_worker.stop)
        self.duration_worker.start()

    def update_duration_progress(self, current: int, total: int, filename: str):
        """更新时长提取进度"""
        self.duration_progress.setValue(current)
        # 截断过长的文件名，避免对话框宽度跳动
        display_name = filename if len(filename) <= 40 else filename[:37] + "..."
        self.duration_progress.setLabelText(f"正在提取时长 [{current}/{total}]\n{display_name}")

    def on_duration_finished(self, processed: int):
        """时长提取完成"""
        self.duration_progress.close()
        if processed > 0:
            self.status_bar.showMessage(f"时长提取完成，处理了 {processed} 部电影", 5000)
            self.load_movies()
        else:
            self.status_bar.showMessage("所有电影已有时长，无需提取", 3000)

    def on_duration_error(self, error: str):
        """时长提取错误"""
        self.duration_progress.close()
        QMessageBox.warning(self, "时长提取错误", error)
        self.status_bar.showMessage(f"时长提取错误: {error}", 5000)

    def load_movies(self):
        """加载电影列表"""
        movies = database.get_all_movies()
        self.movie_list.update_movies(movies)
        self.update_tags_tree()

    def refresh_movies(self):
        """刷新电影列表 - 重新扫描目录并提取时长"""
        if self.current_directory:
            # 如果有当前目录，重新扫描
            self.scan_directory(self.current_directory)
        else:
            # 否则从数据库加载并提取时长
            self.load_movies()
            self.extract_duration_for_all()

    def search_movies(self, query: str):
        """搜索电影"""
        if query:
            movies = database.search_movies(query)
        else:
            movies = database.get_all_movies()
        self.movie_list.update_movies(movies)

    def update_tags_tree(self):
        """更新标签树，保留选中状态"""
        # 记录当前选中的标签ID
        selected_tag_ids = set()
        root = self.tags_tree.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            if item.checkState(0) == Qt.CheckState.Checked:
                tag_id = item.data(0, Qt.ItemDataRole.UserRole)
                selected_tag_ids.add(tag_id)

        # 清除并重建树
        self.tags_tree.clear()
        tags = tag_manager.get_all_tags()

        for tag in tags:
            # 获取该标签下的电影数量
            movies_count = len(tag_manager.get_movies_by_tag(tag['id']))
            item = QTreeWidgetItem(self.tags_tree)
            item.setText(0, f"{tag['name']} ({movies_count})")
            item.setData(0, Qt.ItemDataRole.UserRole, tag['id'])

            # 恢复选中状态
            if tag['id'] in selected_tag_ids:
                item.setCheckState(0, Qt.CheckState.Checked)
            else:
                item.setCheckState(0, Qt.CheckState.Unchecked)

    def on_tag_filter_changed(self, item, column):
        """标签过滤改变"""
        self.filter_movies()

    def filter_movies(self):
        """过滤电影"""
        # 获取选中的标签
        selected_tag_ids = []
        root = self.tags_tree.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            if item.checkState(0) == Qt.CheckState.Checked:
                tag_id = item.data(0, Qt.ItemDataRole.UserRole)
                selected_tag_ids.append(tag_id)

        # 获取观看状态过滤
        watch_status = self.watch_status_combo.currentText()

        # 获取评分过滤参数
        min_rating = self.rating_spin.value()
        rating_source = self.rating_source_combo.currentIndex()  # 0=豆瓣/IMDb, 1=我的评分

        # 获取最小时长（分钟转换为秒）
        min_duration = self.duration_spin.value() * 60

        # 获取所有电影
        movies = database.get_all_movies()

        # 过滤垃圾文件和去重
        filtered_movies = []
        seen_titles = {}  # 用于去重

        for movie in movies:
            # 过滤垃圾文件
            file_path = movie.get('file_path', '')
            if is_junk_file(file_path):
                continue

            # 去重：同名电影只保留一个（优先保留有时长的）
            title = movie.get('title', '')
            if title in seen_titles:
                existing = seen_titles[title]
                # 如果当前记录有时长而之前没有，替换
                if movie.get('duration') and not existing.get('duration'):
                    seen_titles[title] = movie
                continue
            seen_titles[title] = movie

        # 应用其他过滤条件
        for movie in seen_titles.values():
            # 观看状态过滤
            if watch_status != "全部":
                movie_tags = tag_manager.get_movie_tags(movie['id'])
                movie_tag_names = [tag['name'] for tag in movie_tags]
                if watch_status not in movie_tag_names:
                    continue

            # 评分过滤
            if rating_source == 0:
                # 豆瓣/IMDb评分
                rating = movie.get('douban_rating') or movie.get('imdb_rating') or 0
            else:
                # 我的评分
                rating = movie.get('user_rating') or 0

            if rating < min_rating:
                continue

            # 时长过滤
            duration = movie.get('duration', 0) or 0
            if duration < min_duration:
                continue

            # 标签过滤
            if selected_tag_ids:
                movie_tags = tag_manager.get_movie_tags(movie['id'])
                movie_tag_ids = [tag['id'] for tag in movie_tags]
                if not any(tag_id in selected_tag_ids for tag_id in movie_tag_ids):
                    continue

            filtered_movies.append(movie)

        self.movie_list.update_movies(filtered_movies)

    def on_movie_double_clicked(self, item):
        """双击电影项"""
        row = item.row()
        movie_id = int(self.movie_list.item(row, 0).text())
        self.show_movie_details(movie_id)

    def show_movie_details(self, movie_id: int):
        """显示电影详情"""
        movie = database.get_movie_by_id(movie_id)
        if not movie:
            return

        # 创建详情对话框
        from .dialogs import MovieDetailsDialog
        dialog = MovieDetailsDialog(movie_id, self)
        dialog.exec()

        # 详情页关闭后刷新标签树和电影列表
        self.update_tags_tree()
        self.filter_movies()

    def edit_movie(self):
        """编辑电影"""
        current_row = self.movie_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请先选择一部电影")
            return

        movie_id = int(self.movie_list.item(current_row, 0).text())
        self.show_movie_details(movie_id)

    def delete_movie(self):
        """删除电影"""
        current_row = self.movie_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请先选择一部电影")
            return

        movie_id = int(self.movie_list.item(current_row, 0).text())
        movie = database.get_movie_by_id(movie_id)

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除电影 '{movie['title']}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # 从数据库删除
                conn = database._get_connection()
                cursor = conn.cursor()
                cursor.execute('DELETE FROM movies WHERE id = ?', (movie_id,))
                conn.commit()
                conn.close()

                self.status_bar.showMessage(f"已删除电影: {movie['title']}", 3000)
                self.load_movies()
            except Exception as e:
                QMessageBox.warning(self, "错误", f"删除失败: {e}")

    def show_settings(self):
        """显示设置对话框"""
        from .dialogs import SettingsDialog
        dialog = SettingsDialog(self)
        dialog.exec()
        self.load_settings()


def run_gui():
    """运行GUI"""
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    run_gui()
