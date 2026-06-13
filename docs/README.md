# 视频库管理工具

一个用于管理本地影视库的Windows桌面应用，支持自动扫描、元数据提取、豆瓣/IMDb评分获取、标签管理等功能。

## 功能特性

- **自动扫描**：遍历指定目录，识别视频文件
- **元数据提取**：自动提取视频时长、封面、文件大小
- **评分获取**：支持豆瓣和IMDb双源评分
- **标签管理**：自定义标签，支持多标签关联
- **过滤功能**：按标签、评分等条件筛选
- **Windows平台**：原生桌面应用

## 安装依赖

### 1. 创建虚拟环境
```bash
cd H:\video_scripts\VideoBaseApp
python -m venv venv
venv\Scripts\activate
```

### 2. 安装Python包
```bash
pip install -r requirements.txt
```

### 3. 配置FFmpeg
应用使用离线FFmpeg，需要在设置中指定路径：
- 默认路径：`E:\ffmpeg-2023-05-08-git-2d43c23b81-full_build\bin\ffmpeg.exe`
- 可在设置中修改

## 使用方法

### 运行GUI应用
```bash
python run_gui.py
```

### 命令行模式
```bash
# 扫描目录
python src/main.py scan <目录路径>

# 列出电影
python src/main.py list

# 显示统计
python src/main.py stats

# 交互式模式
python src/main.py
```

## 项目结构

```
VideoBaseApp/
├── src/                    # 源代码
│   ├── config.py          # 配置管理
│   ├── database.py        # 数据库操作
│   ├── scanner.py         # 目录扫描
│   ├── metadata.py        # 元数据提取
│   ├── douban_api.py      # 豆瓣API
│   ├── imdb_api.py        # IMDb API
│   ├── tags.py            # 标签管理
│   ├── main.py            # 主程序（命令行）
│   └── ui/                # GUI界面
│       ├── main_window.py # 主窗口
│       └── dialogs.py     # 对话框
├── run_gui.py             # GUI启动脚本
├── requirements.txt       # 依赖列表
└── README.md             # 说明文档
```

## 配置文件

配置文件存储在用户目录：`~/.VideoBaseApp/config.json`

可配置项：
- `ffmpeg_path`: FFmpeg可执行文件路径
- `douban_enabled`: 是否启用豆瓣API
- `imdb_enabled`: 是否启用IMDb API
- `imdb_api_key`: IMDb API密钥
- `scan_extensions`: 扫描的视频扩展名
- `max_scan_threads`: 最大扫描线程数

## 数据库

使用SQLite数据库，存储在用户目录：`~/.VideoBaseApp/movies.db`

表结构：
- `movies`: 电影信息
- `tags`: 标签信息
- `movie_tags`: 电影-标签关联

## 注意事项

1. **豆瓣API限制**：豆瓣有反爬机制，请求频率受限
2. **IMDb API限制**：免费版每天1000次请求
3. **FFmpeg路径**：确保FFmpeg路径正确，否则无法提取时长和封面
4. **首次扫描**：大目录扫描可能需要较长时间

## 开发计划

- [x] 基础扫描和元数据提取
- [x] 豆瓣/IMDb评分获取
- [x] 标签管理系统
- [x] GUI界面
- [ ] 打包为exe
- [ ] 性能优化
- [ ] 更多过滤选项

## 许可证

MIT License
