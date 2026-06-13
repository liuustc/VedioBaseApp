# 数据库迁移问题修复

## 问题
`no such column: cover_paths` - 数据库中缺少 `cover_paths` 字段

## 原因
在数据库中添加了新字段 `cover_paths`，但旧的数据库文件中没有这个字段。

## 解决方案

### 1. 添加数据库迁移功能
在 `database.py` 中添加了 `_migrate_database()` 方法：

```python
def _migrate_database(self, conn):
    """数据库迁移：添加缺失的字段"""
    cursor = conn.cursor()

    # 检查并添加cover_paths字段
    try:
        cursor.execute("PRAGMA table_info(movies)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'cover_paths' not in columns:
            cursor.execute("ALTER TABLE movies ADD COLUMN cover_paths TEXT")
            logger.info("已添加cover_paths字段到movies表")
    except Exception as e:
        logger.error(f"数据库迁移失败: {e}")
```

### 2. 修改表创建逻辑
- 移除了 `cover_paths` 字段从 `CREATE TABLE` 语句
- 改为在表创建后通过 `ALTER TABLE` 添加缺失字段

### 3. 添加loguru导入
在 `database.py` 中添加了 `from loguru import logger`

## 测试结果
✅ 数据库模块导入成功
✅ 数据库迁移功能正常
✅ 所有模块测试通过

## 使用方法
无需手动操作，程序会自动：
1. 检查数据库结构
2. 添加缺失的字段
3. 继续正常运行

## 注意事项
- 如果数据库损坏，可以删除 `%USERPROFILE%\.VideoBaseApp\movies.db` 重新创建
- 程序会自动创建新数据库并添加所有字段

## 现在可以正常运行

请再次尝试运行 `run_simple.bat`，所有问题都已修复！
