"""
对话框类
包括电影详情对话框、设置对话框等
"""
import os
from pathlib import Path
from typing import List, Dict, Any

from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton,
    QComboBox, QSpinBox, QDoubleSpinBox, QColorDialog,
    QGroupBox, QFormLayout, QCheckBox, QListWidget,
    QListWidgetItem, QMessageBox, QScrollArea
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QImage, QColor

from config import config
from database import database
from tags import tag_manager


class MovieDetailsDialog(QDialog):
    """电影详情对话框"""

    def __init__(self, movie_id: int, parent=None):
        super().__init__(parent)
        self.movie_id = movie_id
        self.movie = database.get_movie_by_id(movie_id)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle(f"电影详情 - {self.movie.get('title', '')}")
        self.setGeometry(200, 200, 700, 800)

        layout = QVBoxLayout(self)

        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        content_layout = QVBoxLayout(scroll_content)

        # 1. 基本信息区
        basic_group = QGroupBox("基本信息")
        basic_layout = QFormLayout()

        self.title_edit = QLineEdit()
        basic_layout.addRow("标题:", self.title_edit)

        self.path_label = QLabel()
        self.path_label.setWordWrap(True)
        basic_layout.addRow("文件路径:", self.path_label)

        # 播放按钮
        play_btn = QPushButton("播放")
        play_btn.setMinimumHeight(32)
        play_btn.clicked.connect(self.play_video)
        basic_layout.addRow("", play_btn)

        self.size_label = QLabel()
        basic_layout.addRow("文件大小:", self.size_label)

        self.duration_label = QLabel()
        basic_layout.addRow("时长:", self.duration_label)

        basic_group.setLayout(basic_layout)
        content_layout.addWidget(basic_group)

        # 2. 评分区
        rating_group = QGroupBox("评分")
        rating_layout = QFormLayout()

        douban_layout = QHBoxLayout()
        self.douban_rating_edit = QDoubleSpinBox()
        self.douban_rating_edit.setRange(0, 10)
        self.douban_rating_edit.setSingleStep(0.1)
        douban_layout.addWidget(self.douban_rating_edit)
        douban_layout.addWidget(QLabel("/ 10"))
        douban_layout.addStretch()
        rating_layout.addRow("豆瓣评分:", douban_layout)

        imdb_layout = QHBoxLayout()
        self.imdb_rating_edit = QDoubleSpinBox()
        self.imdb_rating_edit.setRange(0, 10)
        self.imdb_rating_edit.setSingleStep(0.1)
        imdb_layout.addWidget(self.imdb_rating_edit)
        imdb_layout.addWidget(QLabel("/ 10"))
        imdb_layout.addStretch()
        rating_layout.addRow("IMDb评分:", imdb_layout)

        user_rating_layout = QHBoxLayout()
        self.user_rating_edit = QDoubleSpinBox()
        self.user_rating_edit.setRange(0, 10)
        self.user_rating_edit.setSingleStep(0.5)
        self.user_rating_edit.setDecimals(1)
        user_rating_layout.addWidget(self.user_rating_edit)
        user_rating_layout.addWidget(QLabel("/ 10"))
        user_rating_layout.addStretch()
        rating_layout.addRow("我的评分:", user_rating_layout)

        rating_group.setLayout(rating_layout)
        content_layout.addWidget(rating_group)

        # 3. 观看状态区
        status_group = QGroupBox("观看状态")
        status_layout = QHBoxLayout()

        self.status_buttons = {}
        for status in ["未看过", "已看过", "想看", "在看"]:
            btn = QPushButton(status)
            btn.setCheckable(True)
            btn.setMinimumHeight(32)
            btn.clicked.connect(lambda checked, s=status: self.switch_watch_status(s))
            status_layout.addWidget(btn)
            self.status_buttons[status] = btn

        status_group.setLayout(status_layout)
        content_layout.addWidget(status_group)

        # 4. 标签区
        tags_group = QGroupBox("标签管理")
        tags_layout = QVBoxLayout()

        # 当前标签
        current_layout = QHBoxLayout()
        current_layout.addWidget(QLabel("当前标签:"))
        self.current_tags_list = QListWidget()
        self.current_tags_list.setMaximumHeight(100)
        current_layout.addWidget(self.current_tags_list)

        remove_btn = QPushButton("移除选中")
        remove_btn.clicked.connect(self.remove_tag)
        current_layout.addWidget(remove_btn)
        tags_layout.addLayout(current_layout)

        # 添加标签
        add_layout = QHBoxLayout()
        self.new_tag_edit = QLineEdit()
        self.new_tag_edit.setPlaceholderText("输入新标签名称")
        add_layout.addWidget(self.new_tag_edit)
        self.add_tag_btn = QPushButton("添加")
        self.add_tag_btn.clicked.connect(self.add_tag)
        add_layout.addWidget(self.add_tag_btn)
        tags_layout.addLayout(add_layout)

        # 所有标签
        all_layout = QHBoxLayout()
        all_layout.addWidget(QLabel("所有标签(双击添加):"))
        self.all_tags_list = QListWidget()
        self.all_tags_list.setMaximumHeight(100)
        self.all_tags_list.itemDoubleClicked.connect(self.add_existing_tag)
        all_layout.addWidget(self.all_tags_list)
        tags_layout.addLayout(all_layout)

        tags_group.setLayout(tags_layout)
        content_layout.addWidget(tags_group)

        # 5. 简介区
        intro_group = QGroupBox("简介")
        intro_layout = QVBoxLayout()

        intro_layout.addWidget(QLabel("豆瓣简介:"))
        self.douban_intro_edit = QTextEdit()
        self.douban_intro_edit.setReadOnly(True)
        self.douban_intro_edit.setMaximumHeight(120)
        intro_layout.addWidget(self.douban_intro_edit)

        intro_layout.addWidget(QLabel("IMDb简介:"))
        self.imdb_intro_edit = QTextEdit()
        self.imdb_intro_edit.setReadOnly(True)
        self.imdb_intro_edit.setMaximumHeight(120)
        intro_layout.addWidget(self.imdb_intro_edit)

        intro_group.setLayout(intro_layout)
        content_layout.addWidget(intro_group)

        # 设置滚动区域
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        # 底部按钮
        button_layout = QHBoxLayout()
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save_changes)
        button_layout.addWidget(save_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def load_data(self):
        """加载数据"""
        if not self.movie:
            return

        # 基本信息 - 路径统一显示为正斜杠
        self.title_edit.setText(self.movie.get('title', ''))
        file_path = self.movie.get('file_path', '').replace('\\', '/')
        self.path_label.setText(file_path)
        file_size = self.movie.get('file_size', 0)
        if file_size:
            size_mb = file_size / (1024 * 1024)
            self.size_label.setText(f"{size_mb:.2f} MB")
        else:
            self.size_label.setText("N/A")

        duration = self.movie.get('duration')
        if duration:
            minutes = duration // 60
            seconds = duration % 60
            self.duration_label.setText(f"{minutes}:{seconds:02d}")
        else:
            self.duration_label.setText("N/A")

        # 评分
        self.douban_rating_edit.setValue(self.movie.get('douban_rating') or 0)
        self.imdb_rating_edit.setValue(self.movie.get('imdb_rating') or 0)
        self.user_rating_edit.setValue(self.movie.get('user_rating') or 0)

        # 标签和观看状态
        self.load_tags()
        self.update_watch_status_buttons()

        # 简介
        self.douban_intro_edit.setText(self.movie.get('douban_intro') or '')
        self.imdb_intro_edit.setText(self.movie.get('imdb_intro') or '')

    def load_tags(self):
        """加载标签"""
        # 当前标签
        self.current_tags_list.clear()
        current_tags = tag_manager.get_movie_tags(self.movie_id)
        for tag in current_tags:
            item = QListWidgetItem(tag['name'])
            item.setData(Qt.ItemDataRole.UserRole, tag['id'])
            self.current_tags_list.addItem(item)

        # 所有标签
        self.all_tags_list.clear()
        all_tags = tag_manager.get_all_tags()
        for tag in all_tags:
            item = QListWidgetItem(tag['name'])
            item.setData(Qt.ItemDataRole.UserRole, tag['id'])
            self.all_tags_list.addItem(item)

    def add_tag(self):
        """添加新标签"""
        tag_name = self.new_tag_edit.text().strip()
        if not tag_name:
            return

        # 检查是否已存在
        existing = tag_manager.get_tag_by_name(tag_name)
        if existing:
            tag_id = existing['id']
        else:
            tag_id = tag_manager.create_tag(tag_name)
            if not tag_id:
                QMessageBox.warning(self, "错误", "创建标签失败")
                return

        # 添加到电影
        tag_manager.add_tag_to_movie(self.movie_id, tag_id)
        self.new_tag_edit.clear()
        self.load_tags()

    def add_existing_tag(self, item):
        """添加现有标签"""
        tag_id = item.data(Qt.UserRole)
        tag_manager.add_tag_to_movie(self.movie_id, tag_id)
        self.load_tags()

    def remove_tag(self):
        """移除标签"""
        current_item = self.current_tags_list.currentItem()
        if current_item:
            tag_id = current_item.data(Qt.UserRole)
            tag_manager.remove_tag_from_movie(self.movie_id, tag_id)
            self.load_tags()

    def switch_watch_status(self, new_status: str):
        """切换观看状态"""
        watch_statuses = ["未看过", "已看过", "想看", "在看"]

        # 移除所有观看状态标签
        for status in watch_statuses:
            tag = tag_manager.get_tag_by_name(status)
            if tag:
                tag_manager.remove_tag_from_movie(self.movie_id, tag['id'])

        # 添加新的观看状态标签
        new_tag = tag_manager.get_tag_by_name(new_status)
        if new_tag:
            tag_manager.add_tag_to_movie(self.movie_id, new_tag['id'])

        # 更新按钮状态
        self.update_watch_status_buttons()

        # 重新加载标签列表
        self.load_tags()

    def update_watch_status_buttons(self):
        """更新观看状态按钮的选中状态"""
        current_tags = tag_manager.get_movie_tags(self.movie_id)
        current_tag_names = [tag['name'] for tag in current_tags]

        for status, btn in self.status_buttons.items():
            btn.setChecked(status in current_tag_names)

    def play_video(self):
        """使用系统默认播放器播放视频"""
        file_path = self.movie.get('file_path', '')
        if not file_path:
            QMessageBox.warning(self, "错误", "文件路径为空")
            return

        if not os.path.exists(file_path):
            QMessageBox.warning(self, "错误", f"文件不存在:\n{file_path}")
            return

        try:
            os.startfile(file_path)
        except Exception as e:
            QMessageBox.warning(self, "播放失败", f"无法播放文件:\n{e}")

    def save_changes(self):
        """保存更改"""
        try:
            # 更新基本信息
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
                self.title_edit.text(),
                self.douban_rating_edit.value() or None,
                self.imdb_rating_edit.value() or None,
                self.user_rating_edit.value() or None,
                self.movie_id
            ))

            conn.commit()
            conn.close()

            QMessageBox.information(self, "成功", "电影信息已保存")
            self.accept()

        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存失败: {e}")


class SettingsDialog(QDialog):
    """设置对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("设置")
        self.setGeometry(300, 300, 500, 400)

        layout = QVBoxLayout(self)

        # FFmpeg设置
        ffmpeg_group = QGroupBox("FFmpeg设置")
        ffmpeg_layout = QFormLayout()
        self.ffmpeg_path_edit = QLineEdit()
        ffmpeg_layout.addRow("FFmpeg路径:", self.ffmpeg_path_edit)
        self.ffmpeg_browse_btn = QPushButton("浏览...")
        self.ffmpeg_browse_btn.clicked.connect(self.browse_ffmpeg)
        ffmpeg_layout.addRow("", self.ffmpeg_browse_btn)
        ffmpeg_group.setLayout(ffmpeg_layout)
        layout.addWidget(ffmpeg_group)

        # API设置
        api_group = QGroupBox("API设置")
        api_layout = QFormLayout()
        self.douban_enabled_check = QCheckBox("启用豆瓣API")
        api_layout.addRow("", self.douban_enabled_check)
        self.imdb_enabled_check = QCheckBox("启用IMDb API")
        api_layout.addRow("", self.imdb_enabled_check)
        self.imdb_api_key_edit = QLineEdit()
        api_layout.addRow("IMDb API密钥:", self.imdb_api_key_edit)
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)

        # 扫描设置
        scan_group = QGroupBox("扫描设置")
        scan_layout = QFormLayout()
        self.max_threads_spin = QSpinBox()
        self.max_threads_spin.setRange(1, 16)
        scan_layout.addRow("最大线程数:", self.max_threads_spin)
        scan_group.setLayout(scan_layout)
        layout.addWidget(scan_group)

        # 按钮
        button_layout = QHBoxLayout()
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def load_settings(self):
        """加载设置"""
        self.ffmpeg_path_edit.setText(config.get_ffmpeg_path())
        self.douban_enabled_check.setChecked(config.get("douban_enabled", True))
        self.imdb_enabled_check.setChecked(config.get("imdb_enabled", True))
        self.imdb_api_key_edit.setText(config.get_imdb_api_key())
        self.max_threads_spin.setValue(config.get("max_scan_threads", 4))

    def browse_ffmpeg(self):
        """浏览FFmpeg路径"""
        path, _ = QFileDialog.getOpenFileName(
            self, "选择FFmpeg可执行文件",
            "", "Executable files (*.exe);;All files (*)"
        )
        if path:
            self.ffmpeg_path_edit.setText(path)

    def save_settings(self):
        """保存设置"""
        config.set_ffmpeg_path(self.ffmpeg_path_edit.text())
        config.set("douban_enabled", self.douban_enabled_check.isChecked())
        config.set("imdb_enabled", self.imdb_enabled_check.isChecked())
        config.set_imdb_api_key(self.imdb_api_key_edit.text())
        config.set("max_scan_threads", self.max_threads_spin.value())
        config.save_config()

        QMessageBox.information(self, "成功", "设置已保存")
        self.accept()
