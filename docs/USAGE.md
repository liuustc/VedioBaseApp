# 视频库管理工具 - 使用说明

## 快速开始

### 1. 启动应用
```bash
# 方法1：使用批处理文件（推荐）
run.bat

# 方法2：直接运行Python脚本
python run_gui.py

# 方法3：使用虚拟环境
venv\Scripts\python run_gui.py
```

### 2. 首次使用配置
1. 启动应用后，点击工具栏的"设置"按钮
2. 检查FFmpeg路径是否正确（默认：`E:\ffmpeg-2023-05-08-git-2d43c23b81-full_build\bin\ffmpeg.exe`）
3. 如需修改，点击"浏览"选择正确的FFmpeg路径
4. 确认IMDb API密钥（已预置：`286bddae`）
5. 点击"保存"

### 3. 扫描视频目录
1. 点击左侧面板的"选择目录"按钮
2. 选择包含视频文件的目录
3. 应用会自动扫描并提取元数据
4. 扫描完成后，电影会显示在列表中

## 功能详解

### 电影列表
- **显示信息**：封面、标题、时长、评分、标签
- **排序**：点击列标题可排序
- **搜索**：在左侧面板的搜索框中输入关键词
- **双击**：查看电影详情

### 标签管理
1. **创建标签**：
   - 在电影详情对话框的"标签"标签页
   - 输入标签名称，点击"添加"

2. **为电影添加标签**：
   - 双击电影打开详情
   - 在"标签"标签页选择标签

3. **标签过滤**：
   - 在左侧面板勾选标签
   - 只显示包含选中标签的电影

### 评分过滤
- 在左侧面板调整"最低评分"滑块
- 只显示评分高于设定值的电影

### 电影详情
双击电影可查看详细信息：
- **基本信息**：标题、文件路径、时长、评分
- **标签**：当前标签、添加新标签
- **简介**：豆瓣/IMDb简介（如果可用）

## 命令行模式

### 扫描目录
```bash
python src/main.py scan <目录路径>
```

### 列出电影
```bash
python src/main.py list
```

### 显示统计
```bash
python src/main.py stats
```

### 交互式模式
```bash
python src/main.py
```

## 配置文件

配置文件位于：`%USERPROFILE%\.VideoBaseApp\config.json`

可配置项：
- `ffmpeg_path`: FFmpeg可执行文件路径
- `douban_enabled`: 是否启用豆瓣API
- `imdb_enabled`: 是否启用IMDb API
- `imdb_api_key`: IMDb API密钥
- `scan_extensions`: 扫描的视频扩展名
- `max_scan_threads`: 最大扫描线程数

## 数据库

数据库文件位于：`%USERPROFILE%\.VideoBaseApp\movies.db`

## 常见问题

### Q: 豆瓣API返回404错误
A: 豆瓣有反爬机制，可能被限制。建议使用IMDb API作为备选。

### Q: 扫描目录没有找到视频文件
A: 请检查：
1. 目录路径是否正确
2. 视频文件扩展名是否在支持列表中（.mp4, .mkv, .avi等）
3. 目录是否有访问权限

### Q: FFmpeg路径错误
A: 在设置中修改FFmpeg路径，确保指向正确的ffmpeg.exe文件

### Q: 如何打包成exe
A: 运行 `python build_exe.py`（需要安装PyInstaller）

## 技术支持

如有问题，请检查：
1. 日志文件：`%USERPROFILE%\.VideoBaseApp\*.log`
2. 配置文件：`%USERPROFILE%\.VideoBaseApp\config.json`
3. 数据库文件：`%USERPROFILE%\.VideoBaseApp\movies.db`
