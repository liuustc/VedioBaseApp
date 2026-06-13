# UI修改总结

## 修改1：UI关闭后自动关闭terminal

### 实现方法
在MainWindow类中添加closeEvent方法：

```python
def closeEvent(self, event):
    """关闭事件 - 退出应用程序"""
    QApplication.quit()
    event.accept()
```

### 效果
关闭GUI窗口后，Python进程会自动退出，terminal也会自动关闭。

## 修改2：时长过滤功能

### 实现方法
在左侧面板添加时长过滤控件：

```python
# 时长过滤
duration_group = QGroupBox("时长过滤")
duration_layout = QHBoxLayout()
duration_layout.addWidget(QLabel("最小时长(分钟):"))
self.duration_spin = QSpinBox()
self.duration_spin.setRange(0, 1440)  # 最大24小时
self.duration_spin.setSingleStep(10)
self.duration_spin.setValue(0)
self.duration_spin.valueChanged.connect(self.filter_movies)
duration_layout.addWidget(self.duration_spin)
duration_group.setLayout(duration_layout)
layout.addWidget(duration_group)
```

### 过滤逻辑
在filter_movies方法中添加时长过滤：

```python
# 获取最小时长（分钟转换为秒）
min_duration = self.duration_spin.value() * 60

# 时长过滤
duration = movie.get('duration', 0) or 0
if duration < min_duration:
    continue
```

### 使用方法
1. 在左侧面板找到"时长过滤"
2. 设置最小时长（单位：分钟）
3. 列表会自动过滤掉低于该时长的影片

## 测试结果
✅ 主窗口模块导入成功
✅ UI关闭后自动关闭terminal - 已添加
✅ 时长过滤功能 - 已添加

## 现在可以正常运行

请使用 `start.bat` 启动应用：
1. 关闭窗口后terminal会自动关闭
2. 可以按时长过滤影片
