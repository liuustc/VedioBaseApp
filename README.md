# 视频库管理工具

一个用于管理本地影视库的Windows桌面应用，支持自动扫描、元数据提取、豆瓣/IMDb评分获取、标签管理等功能。

## 快速开始

### 启动应用
双击 `run_simple.bat` 即可启动应用。

### 首次使用
1. 点击"选择目录"按钮
2. 选择包含视频文件的目录
3. 程序会自动扫描并提取元数据
4. 扫描完成后，电影会显示在列表中

### 后续使用
1. 启动程序后，上次目录会自动显示
2. 直接点击"刷新"按钮即可重新扫描
3. 或者点击"选择目录"选择新目录

## 目录结构

```
VideoBaseApp/
├── run_simple.bat          # 主启动脚本（推荐使用）
├── check_env.bat           # 环境诊断脚本
├── requirements.txt        # Python依赖列表
├── .gitignore             # Git忽略文件
├── src/                   # 源代码目录
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
├── data/                  # 数据文件目录
├── docs/                  # 文档目录
│   ├── README.md          # 项目说明
│   ├── QUICK_START.md     # 快速开始指南
│   └── ...                # 其他文档
├── scripts/               # 脚本目录
│   ├── demo.py            # 功能演示
│   ├── build_exe.py       # 打包脚本
│   ├── diagnose.py        # 诊断脚本
│   └── test_*.py          # 测试脚本
├── tests/                 # 测试目录
└── venv/                  # Python虚拟环境
```

## 主要功能

- **自动扫描**：遍历指定目录，识别视频文件
- **元数据提取**：自动提取视频时长、封面、文件大小
- **评分获取**：支持豆瓣和IMDb双源评分
- **标签管理**：自定义标签，支持多标签关联
- **过滤功能**：按标签、评分等条件筛选
- **上次目录记忆**：自动记录上次打开的目录

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

### Q: 封面全黑
A: 程序会提取3张不同时间段的封面（30分钟、45分钟、60分钟），避免片头片尾

## 获取帮助

如果遇到问题，请提供：
1. 错误消息
2. 运行 `check_env.bat` 的输出
3. 配置文件内容

## 许可证

MIT License
