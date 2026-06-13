# QApplication导入修复

## 问题
```
NameError: name 'QApplication' is not defined
```

## 原因
在closeEvent方法中使用了QApplication，但没有导入它。

## 修复
在导入列表中添加QApplication：

### 修改前
```python
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QListWidget, QListWidgetItem, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QToolBar, QStatusBar,
    QLabel, QPushButton, QLineEdit, QComboBox, QCheckBox,
    QFileDialog, QMessageBox, QProgressDialog, QTabWidget,
    QGroupBox, QFormLayout, QSpinBox, QDoubleSpinBox,
    QColorDialog, QTreeWidgetItem, QTreeWidget
)
```

### 修改后
```python
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QListWidget, QListWidgetItem, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QToolBar, QStatusBar,
    QLabel, QPushButton, QLineEdit, QComboBox, QCheckBox,
    QFileDialog, QMessageBox, QProgressDialog, QTabWidget,
    QGroupBox, QFormLayout, QSpinBox, QDoubleSpinBox,
    QColorDialog, QTreeWidgetItem, QTreeWidget
)
```

## 测试结果
✅ 主窗口模块导入成功
✅ QApplication已添加到导入列表

## 现在可以正常运行

请使用 `start.bat` 启动应用，关闭窗口后terminal会自动关闭！
