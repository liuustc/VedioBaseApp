# 快速开始指南

## 启动应用

### 方法1：直接双击（推荐）
1. 在Windows资源管理器中打开 `H:\video_scripts\VideoBaseApp`
2. 双击 `run_simple.bat`

### 方法2：命令提示符
```cmd
cd /d H:\video_scripts\VideoBaseApp
run_simple.bat
```

### 方法3：直接运行Python
```cmd
cd /d H:\video_scripts\VideoBaseApp
venv\Scripts\python.exe run_gui.py
```

## 使用流程

### 首次使用
1. 点击"选择目录"按钮
2. 选择包含视频文件的目录
3. 程序会自动扫描并提取元数据
4. 扫描完成后，电影会显示在列表中

### 后续使用
1. 启动程序后，上次目录会自动显示
2. 直接点击"刷新"按钮即可重新扫描
3. 或者点击"选择目录"选择新目录

## 主要功能

### 电影列表
- 显示封面、标题、时长、评分、标签
- 双击电影查看详细信息
- 支持搜索和过滤

### 标签管理
- 创建自定义标签
- 为电影添加/移除标签
- 按标签过滤电影

### 评分获取
- 支持豆瓣和IMDb双源
- 自动获取电影评分和简介

## 配置文件

配置文件位于：`%USERPROFILE%\.VideoBaseApp\config.json`

可配置项：
- `ffmpeg_path`: FFmpeg路径
- `last_directory`: 上次打开的目录
- `douban_enabled`: 是否启用豆瓣API
- `imdb_enabled`: 是否启用IMDb API
- `imdb_api_key`: IMDb API密钥

## 常见问题

### Q: 窗口一闪而过
A: 请使用 `run_simple.bat` 或直接运行Python脚本查看错误信息

### Q: 扫描失败
A: 检查目录路径是否正确，视频文件格式是否支持

### Q: 评分获取失败
A: 豆瓣API可能受限，IMDb API作为备选

## 获取帮助

如果遇到问题，请提供：
1. 错误消息
2. 运行 `check_env.bat` 的输出
3. 配置文件内容
