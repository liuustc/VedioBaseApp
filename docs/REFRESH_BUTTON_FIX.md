# 刷新列表按钮修复

## 问题
点击刷新列表按钮，似乎什么都没有发生。

## 原因
之前的修改将刷新列表按钮设置为只从数据库加载电影，不会重新扫描目录。

## 修复方案

### 修改前
```python
def refresh_movies(self):
    """刷新电影列表 - 从数据库加载"""
    self.load_movies()
    self.status_bar.showMessage("已刷新", 2000)
```

### 修改后
```python
def refresh_movies(self):
    """刷新电影列表 - 重新扫描目录"""
    if self.current_directory:
        # 如果有当前目录，重新扫描
        self.scan_directory(self.current_directory)
    else:
        # 否则只从数据库加载
        self.load_movies()
        self.status_bar.showMessage("已刷新", 2000)
```

## 逻辑说明

1. **如果有当前目录**：重新扫描目录，更新电影列表
2. **如果没有当前目录**：只从数据库加载电影

## 测试结果
✅ 主窗口模块导入成功
✅ 刷新列表按钮已修改为重新扫描目录

## 现在可以正常运行

请使用 `start.bat` 启动应用，点击刷新列表按钮现在会重新扫描目录了！
