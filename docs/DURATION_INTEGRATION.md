# 时长提取集成到刷新列表

## 修改内容

### 1. 新增DurationWorker
创建了一个新的DurationWorker类，专门用于提取时长：

```python
class DurationWorker(QThread):
    """时长提取工作线程"""
    progress_updated = pyqtSignal(int, int, str)
    finished = pyqtSignal(int)
    error = pyqtSignal(str)
```

### 2. 修改refresh_movies方法
在刷新列表时自动提取时长：

```python
def refresh_movies(self):
    """刷新电影列表 - 重新扫描目录并提取时长"""
    if self.current_directory:
        # 如果有当前目录，重新扫描
        self.scan_directory(self.current_directory)
    else:
        # 否则从数据库加载并提取时长
        self.load_movies()
        self.extract_duration_for_all()
```

### 3. 修改on_scan_finished方法
扫描完成后自动提取时长：

```python
def on_scan_finished(self, movie_data_list: List[Dict[str, Any]]):
    """扫描完成"""
    self.scan_progress.close()
    self.status_bar.showMessage(f"扫描完成，找到 {len(movie_data_list)} 部电影", 5000)
    self.load_movies()

    # 扫描完成后自动提取时长
    if movie_data_list:
        self.extract_duration_for_all()
```

### 4. 新增extract_duration_for_all方法
为所有电影提取时长：

```python
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
    ...
```

## 使用方法

1. **扫描目录**：点击"选择目录"按钮
2. **扫描完成**：自动提取时长
3. **刷新列表**：点击"刷新列表"按钮，自动提取时长

## 测试结果
✅ 主窗口模块导入成功
✅ 时长提取已集成到刷新列表步骤中

## 现在可以正常运行

请使用 `start.bat` 启动应用，扫描目录后会自动提取时长！
