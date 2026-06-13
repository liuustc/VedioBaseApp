# moviepy导入修复

## 问题
moviepy已安装，但导入方式不对。

## 修复
修改导入方式：

### 修改前
```python
from moviepy.editor import VideoFileClip
```

### 修改后
```python
from moviepy import VideoFileClip
```

## 测试结果
✅ 元数据提取器导入成功
✅ moviepy可用

## 现在可以正常运行

请使用 `start.bat` 启动应用，重新扫描目录并提取时长！
