# 运行说明

## 问题说明

在Bash环境中无法正确运行Windows GUI应用，因为：
1. GUI应用需要Windows图形界面
2. Bash环境无法显示Windows窗口
3. 输出重定向可能不工作

## 正确运行方式

### 方法1：直接双击run.bat（推荐）
1. 在Windows资源管理器中打开 `H:\video_scripts\VideoBaseApp`
2. 双击 `run.bat` 文件
3. 应用窗口应该会显示

### 方法2：使用Windows命令提示符
1. 按 `Win + R`，输入 `cmd`，回车
2. 输入以下命令：
   ```cmd
   cd /d H:\video_scripts\VideoBaseApp
   run.bat
   ```

### 方法3：使用Windows PowerShell
1. 按 `Win + X`，选择 "Windows PowerShell"
2. 输入以下命令：
   ```powershell
   cd H:\video_scripts\VideoBaseApp
   .\run.bat
   ```

## 如果窗口一闪而过

如果双击run.bat后窗口一闪而过，可能是以下原因：

### 1. Python路径问题
检查虚拟环境是否正确创建：
```cmd
cd H:\video_scripts\VideoBaseApp
dir venv\Scripts\python.exe
```

如果文件不存在，重新创建虚拟环境：
```cmd
python -m venv venv
venv\Scripts\pip install -r requirements.txt
```

### 2. 依赖缺失
检查是否安装了所有依赖：
```cmd
cd H:\video_scripts\VideoBaseApp
venv\Scripts\pip list
```

应该看到：
- PyQt6
- moviepy
- requests
- pillow
- opencv-python
- tqdm
- loguru

### 3. FFmpeg路径问题
检查配置文件中的FFmpeg路径：
```cmd
notepad %USERPROFILE%\.VideoBaseApp\config.json
```

确保 `ffmpeg_path` 指向正确的FFmpeg可执行文件。

### 4. 查看错误信息
要查看错误信息，修改run.bat：
1. 打开run.bat
2. 删除 `@echo off`
3. 在最后一行 `pause` 前添加 `echo 错误信息: %errorlevel%`
4. 保存并重新运行

## 直接运行Python脚本

如果run.bat有问题，可以直接运行Python脚本：

```cmd
cd H:\video_scripts\VideoBaseApp
venv\Scripts\python run_gui_debug.py
```

这会显示详细的错误信息。

## 命令行模式

如果GUI无法启动，可以使用命令行模式：

```cmd
cd H:\video_scripts\VideoBaseApp
venv\Scripts\python src\main.py
```

然后选择操作：
1. 扫描目录
2. 列出电影
3. 列出标签
4. 为电影添加标签
5. 显示统计
6. 退出

## 获取帮助

如果问题仍然存在，请提供以下信息：
1. 错误消息（如果有）
2. Python版本：`python --version`
3. 依赖列表：`pip list`
4. 配置文件内容
