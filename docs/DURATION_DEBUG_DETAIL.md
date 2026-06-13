# 时长获取详细调试

## 问题
获取时长失败，但日志没有显示具体原因。

## 修复
添加更详细的日志，包括返回码、stderr和stdout：

```python
logger.warning(f"获取时长失败: 返回码={result.returncode}, stderr={result.stderr}, stdout={result.stdout}")
```

## 调试方法

1. **启动应用**：使用 `start.bat`
2. **扫描目录**：点击"选择目录"按钮
3. **查看日志**：检查terminal中的日志输出

日志会显示：
- 返回码：FFmpeg的返回码
- stderr：FFmpeg的错误输出
- stdout：FFmpeg的标准输出

## 可能的原因

1. **网络路径访问问题**：FFmpeg无法访问网络路径
2. **FFmpeg版本问题**：某些FFmpeg版本可能不支持某些视频格式
3. **视频文件损坏**：视频文件可能损坏或无法读取
4. **权限问题**：没有权限访问视频文件

## 测试结果
✅ 元数据提取器导入成功
✅ 已添加更详细的日志

## 现在可以正常运行

请使用 `start.bat` 启动应用，重新扫描目录并查看详细的日志输出！
