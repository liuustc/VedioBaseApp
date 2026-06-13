# 运行问题排查

## 编码问题

如果运行批处理文件时出现乱码错误，是因为编码问题。

### 解决方案

**方法1：使用 start.bat（推荐）**
```cmd
cd H:\video_scripts\VideoBaseApp
start.bat
```

**方法2：使用命令提示符**
```cmd
cd H:\video_scripts\VideoBaseApp
venv\Scripts\python.exe run_gui.py
```

**方法3：直接双击 start.bat**

## 如果窗口一闪而过

### 查看错误信息
1. 打开命令提示符（Win+R，输入cmd）
2. 输入：
```cmd
cd /d H:\video_scripts\VideoBaseApp
venv\Scripts\python.exe run_gui.py
```
3. 查看错误信息

### 常见问题

#### 1. Python路径问题
```cmd
# 检查Python是否存在
dir venv\Scripts\python.exe
```

#### 2. 依赖缺失
```cmd
# 检查依赖
venv\Scripts\pip list
```

#### 3. FFmpeg路径问题
检查配置文件：
```cmd
notepad %USERPROFILE%\.VideoBaseApp\config.json
```

## 诊断脚本

运行诊断脚本检查环境：
```cmd
cd /d H:\video_scripts\VideoBaseApp
check_env.bat
```

## 目录结构

```
VideoBaseApp/
├── start.bat               # 主启动脚本（推荐）
├── run_simple.bat          # 启动脚本（备用）
├── check_env.bat           # 环境诊断脚本
├── run_gui.py              # GUI启动脚本
├── src/                    # 源代码
├── docs/                   # 文档
├── scripts/                # 脚本
└── venv/                   # 虚拟环境
```

## 获取帮助

如果问题仍然存在，请提供：
1. 错误消息截图
2. 运行 `check_env.bat` 的输出
3. Python版本：`python --version`
