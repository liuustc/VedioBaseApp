# 问题修复总结

## 问题1：`name re is not defined`

### 原因
`douban_api.py` 和 `imdb_api.py` 中使用了 `re` 模块（正则表达式）但没有导入。

### 修复
在两个文件中添加了 `import re`：

**douban_api.py:**
```python
import os
import re  # 添加这一行
import requests
```

**imdb_api.py:**
```python
import os
import re  # 添加这一行
import requests
```

## 问题2：`UnicodeDecodeError: 'gbk' codec can't decode byte`

### 原因
在Windows上，subprocess默认使用GBK编码读取输出，但FFmpeg的输出可能包含UTF-8字符（如中文路径、错误信息等）。

### 修复
在 `metadata.py` 中的所有 `subprocess.run()` 调用中添加编码参数：

```python
# 修复前
result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

# 修复后
result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore', timeout=10)
```

修复的位置：
1. `check_ffmpeg()` 方法
2. `get_video_duration()` 方法
3. `extract_cover()` 方法

## 测试结果

✅ `metadata` 模块导入成功
✅ `douban_api` 模块导入成功
✅ `imdb_api` 模块导入成功

## 现在可以正常运行

请再次尝试运行 `run_simple.bat`，应该可以正常扫描目录了。

### 如果还有问题

如果仍然遇到错误，请告诉我：
1. 具体的错误消息
2. 错误发生的时机
3. 是否能看到完整的错误堆栈信息
