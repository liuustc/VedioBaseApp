# 元数据自动拉取

## 问题
扫描完成后，所有影片的时长一栏都是空的，过滤也无法生效。

## 原因
扫描时只保存了基本信息（文件路径、标题、文件大小），没有自动拉取元数据。

## 解决方案
扫描完成后自动询问是否拉取元数据：

### 修改前
```python
def on_scan_finished(self, movie_data_list: List[Dict[str, Any]]):
    """扫描完成"""
    self.scan_progress.close()
    self.status_bar.showMessage(f"扫描完成，找到 {len(movie_data_list)} 部电影", 5000)
    self.load_movies()
```

### 修改后
```python
def on_scan_finished(self, movie_data_list: List[Dict[str, Any]]):
    """扫描完成"""
    self.scan_progress.close()
    self.status_bar.showMessage(f"扫描完成，找到 {len(movie_data_list)} 部电影", 5000)
    self.load_movies()

    # 扫描完成后自动拉取元数据
    if movie_data_list:
        reply = QMessageBox.question(
            self, "确认",
            f"扫描完成，找到 {len(movie_data_list)} 部电影。\n是否立即拉取元数据（时长、评分等）？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.fetch_metadata()
```

## 使用方法

1. **扫描目录**：点击"选择目录"按钮
2. **扫描完成**：弹出确认对话框
3. **选择"是"**：自动拉取元数据
4. **选择"否"**：稍后手动点击"拉取元数据"按钮

## 测试结果
✅ 主窗口模块导入成功
✅ 扫描完成后会自动询问是否拉取元数据

## 现在可以正常运行

请使用 `start.bat` 启动应用，扫描完成后会自动询问是否拉取元数据！
