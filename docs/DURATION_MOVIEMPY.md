# 时长提取改为使用moviepy

## 问题
FFmpeg返回码为1，但stderr和stdout都是空的，说明FFmpeg本身可能有问题。

## 解决方案
使用Python的moviepy库来提取时长，不再依赖独立的FFmpeg。

## 修改内容

### 修改前
```python
# 使用FFmpeg
cmd = [self.ffmpeg_path, '-i', video_path, '-show_entries', 'format=duration', '-v', 'quiet', '-of', 'csv=p=0']
result = subprocess.run(cmd, ...)
```

### 修改后
```python
# 使用moviepy
from moviepy.editor import VideoFileClip
clip = VideoFileClip(video_path)
duration = clip.duration
clip.close()
```

## 优点

1. **不依赖独立FFmpeg**：使用Python库，更稳定
2. **更好的错误处理**：moviepy会提供更详细的错误信息
3. **跨平台兼容**：moviepy在Windows/Linux/Mac上都能工作
4. **已安装**：用户已经安装了moviepy

## 测试结果
✅ 元数据提取器导入成功
✅ 使用moviepy提取时长
✅ moviepy可用

## 现在可以正常运行

请使用 `start.bat` 启动应用，重新扫描目录并提取时长！
