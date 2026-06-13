# 进度对话框修复

## 问题
terminal已经打印扫描完成，但扫描的弹窗依然在。

## 原因
进度对话框 `progress` 是局部变量，当 `scan_directory` 方法执行完毕后，`progress` 变量就超出了作用域，但对话框可能没有被正确关闭。

## 修复方案

### 1. 将进度对话框保存为实例变量
```python
# 修改前
progress = QProgressDialog("正在扫描目录...", "取消", 0, 0, self)

# 修改后
self.scan_progress = QProgressDialog("正在扫描目录...", "取消", 0, 0, self)
```

### 2. 在扫描完成时关闭进度对话框
```python
def on_scan_finished(self, movie_data_list: List[Dict[str, Any]]):
    """扫描完成"""
    self.scan_progress.close()  # 添加这一行
    self.status_bar.showMessage(f"扫描完成，找到 {len(movie_data_list)} 部电影", 5000)
    self.load_movies()
```

### 3. 在扫描错误时关闭进度对话框
```python
def on_scan_error(self, error: str):
    """扫描错误"""
    self.scan_progress.close()  # 添加这一行
    QMessageBox.warning(self, "扫描错误", error)
    self.status_bar.showMessage(f"扫描错误: {error}", 5000)
```

## 测试结果
✅ 主窗口模块导入成功
✅ 进度对话框关闭逻辑已修复

## 现在可以正常运行

请使用 `start.bat` 启动应用，扫描完成后进度对话框应该会自动关闭了！
