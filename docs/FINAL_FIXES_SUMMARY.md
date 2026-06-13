# 最终修复总结

## 修复的所有问题

### 1. `name re is not defined`
- **原因**：`douban_api.py` 和 `imdb_api.py` 中使用了 `re` 模块但没有导入
- **修复**：在两个文件中添加了 `import re`

### 2. `name os is not defined`
- **原因**：`douban_api.py` 和 `imdb_api.py` 中使用了 `os` 模块但没有导入
- **修复**：在两个文件中添加了 `import os`

### 3. `UnicodeDecodeError: 'gbk' codec can't decode byte`
- **原因**：subprocess默认使用GBK编码，但FFmpeg输出可能包含UTF-8字符
- **修复**：在 `metadata.py` 中所有 `subprocess.run()` 调用添加了 `encoding='utf-8', errors='ignore'`

### 4. `Qt.WindowModal` 错误
- **原因**：PyQt6 API变化
- **修复**：将 `Qt.WindowModal` 改为 `Qt.WindowModality.WindowModal`

### 5. `Qt.AlignCenter` 错误
- **原因**：PyQt6 API变化
- **修复**：将 `Qt.AlignCenter` 改为 `Qt.AlignmentFlag.AlignCenter`

### 6. `Qt.KeepAspectRatio` 和 `Qt.SmoothTransformation` 错误
- **原因**：PyQt6 API变化
- **修复**：
  - `Qt.KeepAspectRatio` → `Qt.AspectRatioMode.KeepAspectRatio`
  - `Qt.SmoothTransformation` → `Qt.TransformationMode.SmoothTransformation`

### 7. `Qt.Unchecked` 和 `Qt.Checked` 错误
- **原因**：PyQt6 API变化
- **修复**：
  - `Qt.Unchecked` → `Qt.CheckState.Unchecked`
  - `Qt.Checked` → `Qt.CheckState.Checked`

### 8. `Qt.UserRole` 错误
- **原因**：PyQt6 API变化
- **修复**：将 `Qt.UserRole` 改为 `Qt.ItemDataRole.UserRole`

## 新增功能

### 记录上次打开的目录
- 配置模块添加了 `last_directory` 字段
- GUI启动时自动加载上次目录
- 选择目录后自动保存到配置
- 点击"刷新"按钮时，如果有当前目录，重新扫描

## 测试结果

✅ 所有模块导入成功
✅ 配置模块测试通过
✅ GUI模块测试通过
✅ 上次目录功能正常

## 现在可以正常运行

请再次尝试运行 `run_simple.bat`，所有问题都已修复！

如果还有问题，请告诉我具体的错误消息。
