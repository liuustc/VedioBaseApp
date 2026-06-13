# UI颜色修复

## 问题
左上角选择目录后，目录路径的字是黑色的，和背景混在一起看不清。

## 修复
将目录路径的颜色从黑色改为白色：

### 修改前
```python
self.dir_label.setStyleSheet("color: black;")
```

### 修改后
```python
self.dir_label.setStyleSheet("color: white;")
```

## 修改位置
1. `main_window.py` 第280行：初始化时设置为白色
2. `main_window.py` 第389行：加载上次目录时设置为白色
3. `main_window.py` 第398行：选择目录后设置为白色

## 测试结果
✅ 主窗口模块导入成功
✅ 目录路径颜色已修改为白色

## 现在可以正常运行

请使用 `start.bat` 启动应用，目录路径现在应该清晰可见了！
