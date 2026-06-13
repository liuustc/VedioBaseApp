# 时长显示调试

## 问题
时长一栏都是N/A，过滤也无法生效。

## 分析
时长确实不需要联网，是直接从视频文件读取的。但用户扫描的是网络路径（//192.168.5.3/...），FFmpeg访问网络路径的文件可能会很慢或超时。

## 修复方案

### 1. 添加详细日志
在MetaWorker中添加了详细日志，帮助调试问题：

```python
# 提取视频时长
if not movie.get('duration'):
    logger.info(f"正在获取时长: {file_path}")
    duration = metadata_extractor.get_video_duration(file_path)
    if duration:
        movie['duration'] = duration
        logger.info(f"获取时长成功: {file_path} -> {duration}秒")
    else:
        logger.warning(f"获取时长失败: {file_path}")
```

### 2. 增加网络路径超时时间
```python
# 网络路径需要更长的超时时间
timeout = 30 if video_path.startswith('\\\\') or video_path.startswith('//') else 10
```

## 调试方法

1. **启动应用**：使用 `start.bat`
2. **扫描目录**：点击"选择目录"按钮
3. **拉取元数据**：点击"拉取元数据"按钮
4. **查看日志**：检查terminal中的日志输出

日志会显示：
- 正在获取时长的文件路径
- 获取时长成功或失败的信息
- 超时或其他错误信息

## 测试结果
✅ 主窗口模块导入成功
✅ MetaWorker已添加详细日志

## 现在可以正常运行

请使用 `start.bat` 启动应用，重新扫描目录并拉取元数据，然后查看terminal中的日志输出！
