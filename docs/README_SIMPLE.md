# 视频库管理工具 - 快速开始

## 问题解决

您遇到的错误是由于批处理文件编码问题导致的。请按以下步骤操作：

## 正确运行方式

### 方法1：使用简化版批处理文件（推荐）
1. 在Windows资源管理器中打开 `H:\video_scripts\VideoBaseApp`
2. 双击 `run_simple.bat` 文件

### 方法2：使用Windows命令提示符
1. 按 `Win + R`，输入 `cmd`，回车
2. 输入以下命令：
   ```cmd
   cd /d H:\video_scripts\VideoBaseApp
   run_simple.bat
   ```

### 方法3：直接运行Python脚本
1. 打开命令提示符
2. 输入：
   ```cmd
   cd /d H:\video_scripts\VideoBaseApp
   venv\Scripts\python.exe run_gui.py
   ```

## 诊断环境

如果仍然有问题，运行诊断脚本：
```cmd
cd /d H:\video_scripts\VideoBaseApp
check_env.bat
```

## 命令行模式

如果GUI无法启动，可以使用命令行模式：
```cmd
cd /d H:\video_scripts\VideoBaseApp
venv\Scripts\python.exe src\main.py
```

## 文件说明

- `run_simple.bat` - 简化的启动脚本（无中文）
- `check_env.bat` - 环境诊断脚本
- `run_gui.py` - GUI启动脚本
- `src\main.py` - 命令行主程序

## 注意事项

1. 确保在Windows中运行，不要在Bash/WSL中运行
2. 确保虚拟环境已正确创建
3. 如果窗口一闪而过，检查错误信息

## 获取帮助

如果问题仍然存在，请提供：
1. 运行 `check_env.bat` 的输出
2. 错误消息截图
