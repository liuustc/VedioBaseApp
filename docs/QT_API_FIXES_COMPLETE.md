# PyQt6 API 完整修复清单

## 已修复的所有Qt API问题

### 1. main_window.py

| 原代码 | 修复后代码 | 位置 |
|--------|-----------|------|
| `Qt.WindowModal` | `Qt.WindowModality.WindowModal` | 第355行 |
| `Qt.AlignCenter` | `Qt.AlignmentFlag.AlignCenter` | 多处 |
| `Qt.KeepAspectRatio` | `Qt.AspectRatioMode.KeepAspectRatio` | 第143行 |
| `Qt.SmoothTransformation` | `Qt.TransformationMode.SmoothTransformation` | 第143行 |
| `Qt.Unchecked` | `Qt.CheckState.Unchecked` | 第411行 |
| `Qt.Checked` | `Qt.CheckState.Checked` | 第425行 |
| `Qt.UserRole` | `Qt.ItemDataRole.UserRole` | 多处 |

### 2. dialogs.py

| 原代码 | 修复后代码 | 位置 |
|--------|-----------|------|
| `Qt.AlignCenter` | `Qt.AlignmentFlag.AlignCenter` | 第112行 |
| `Qt.KeepAspectRatio` | `Qt.AspectRatioMode.KeepAspectRatio` | 第203行 |
| `Qt.SmoothTransformation` | `Qt.TransformationMode.SmoothTransformation` | 第203行 |
| `Qt.UserRole` | `Qt.ItemDataRole.UserRole` | 多处 |

## PyQt6 API 变化总结

### 对齐相关
- `Qt.AlignCenter` → `Qt.AlignmentFlag.AlignCenter`
- `Qt.AlignLeft` → `Qt.AlignmentFlag.AlignLeft`
- `Qt.AlignRight` → `Qt.AlignmentFlag.AlignRight`

### 比例模式
- `Qt.KeepAspectRatio` → `Qt.AspectRatioMode.KeepAspectRatio`
- `Qt.IgnoreAspectRatio` → `Qt.AspectRatioMode.IgnoreAspectRatio`

### 变换模式
- `Qt.SmoothTransformation` → `Qt.TransformationMode.SmoothTransformation`
- `Qt.FastTransformation` → `Qt.TransformationMode.FastTransformation`

### 窗口模态
- `Qt.WindowModal` → `Qt.WindowModality.WindowModal`
- `Qt.ApplicationModal` → `Qt.WindowModality.ApplicationModal`

### 复选框状态
- `Qt.Unchecked` → `Qt.CheckState.Unchecked`
- `Qt.PartiallyChecked` → `Qt.CheckState.PartiallyChecked`
- `Qt.Checked` → `Qt.CheckState.Checked`

### 数据角色
- `Qt.UserRole` → `Qt.ItemDataRole.UserRole`
- `Qt.DisplayRole` → `Qt.ItemDataRole.DisplayRole`
- `Qt.DecorationRole` → `Qt.ItemDataRole.DecorationRole`

## 测试结果

✅ 所有UI模块导入成功
✅ 无Qt API错误

## 现在可以正常运行

所有Qt API问题已修复，可以正常运行 `run_simple.bat` 了！
