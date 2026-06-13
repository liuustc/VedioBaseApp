# 功能添加总结

## 新增功能：记录上次打开的目录

### 功能描述
- 程序会自动记录上次打开的视频目录
- 下次启动时自动显示上次目录
- 用户可以直接点击"刷新"按钮更新扫描

### 实现细节

#### 1. 配置模块 (`src/config.py`)
- 添加了 `last_directory` 配置项
- 添加了 `get_last_directory()` 方法
- 添加了 `set_last_directory(directory)` 方法

#### 2. GUI界面 (`src/ui/main_window.py`)
- `load_settings()` 方法：启动时加载上次目录
- `select_directory()` 方法：选择目录后保存到配置
- `refresh_movies()` 方法：如果有当前目录，重新扫描

### 使用方法

1. **首次使用**：
   - 点击"选择目录"按钮
   - 选择视频目录
   - 程序会自动保存该目录

2. **下次使用**：
   - 启动程序后，上次目录会自动显示
   - 直接点击"刷新"按钮即可重新扫描
   - 或者点击"选择目录"选择新目录

### 配置文件示例
```json
{
  "ffmpeg_path": "E:\\ffmpeg-2023-05-08-git-2d43c23b81-full_build\\bin\\ffmpeg.exe",
  "last_directory": "H:\\video_scripts\\VideoBaseApp",
  ...
}
```

### 测试结果
✅ 配置模块测试通过
✅ GUI模块导入成功
✅ 上次目录功能正常

### 注意事项
- 如果上次目录不存在，程序会忽略该目录
- 目录路径会自动保存到用户配置文件中
- 配置文件位于 `%USERPROFILE%\.VideoBaseApp\config.json`
