# 目录结构整理

## 整理前
根目录下有大量文件，非常杂乱：
- 20+ 个.md文档
- 10+ 个测试脚本
- 多个.bat和.py文件

## 整理后

### 根目录（只保留运行所需文件）
```
VideoBaseApp/
├── run_simple.bat          # 主启动脚本（推荐使用）
├── check_env.bat           # 环境诊断脚本
├── requirements.txt        # Python依赖列表
├── .gitignore             # Git忽略文件
├── README.md              # 项目说明
├── src/                   # 源代码目录
├── data/                  # 数据文件目录
├── docs/                  # 文档目录
├── scripts/               # 脚本目录
├── tests/                 # 测试目录
└── venv/                  # Python虚拟环境
```

### src/（源代码）
```
src/
├── config.py              # 配置管理
├── database.py            # 数据库操作
├── scanner.py             # 目录扫描
├── metadata.py            # 元数据提取
├── douban_api.py          # 豆瓣API
├── imdb_api.py            # IMDb API
├── tags.py                # 标签管理
├── main.py                # 主程序（命令行）
└── ui/                    # GUI界面
    ├── main_window.py     # 主窗口
    └── dialogs.py         # 对话框
```

### docs/（文档）
```
docs/
├── README.md              # 项目说明
├── QUICK_START.md         # 快速开始指南
├── DIRECTORY_STRUCTURE.md # 本文件
└── ...                    # 其他文档
```

### scripts/（脚本）
```
scripts/
├── demo.py                # 功能演示
├── build_exe.py           # 打包脚本
├── diagnose.py            # 诊断脚本
├── diagnose.bat           # 诊断批处理
├── run_gui.py             # GUI启动脚本
├── run_gui.bat            # GUI批处理
└── test_*.py              # 测试脚本
```

## 使用方法

### 启动应用
```bash
# 方法1：双击 run_simple.bat
# 方法2：命令提示符
cd H:\video_scripts\VideoBaseApp
run_simple.bat
```

### 运行诊断
```bash
# 方法1：双击 check_env.bat
# 方法2：命令提示符
cd H:\video_scripts\VideoBaseApp
check_env.bat
```

### 运行测试
```bash
cd H:\video_scripts\VideoBaseApp
venv\Scripts\python scripts\test_final.py
```

## 优点

1. **根目录简洁**：只保留运行所需的文件
2. **分门别类**：文档、脚本、测试各自独立
3. **易于维护**：结构清晰，便于查找文件
4. **易于扩展**：新增文件可以放到相应目录
