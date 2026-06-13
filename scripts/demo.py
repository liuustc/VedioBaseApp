"""
演示脚本
展示视频库管理工具的核心功能
"""
import sys
from pathlib import Path

# 添加src目录到Python路径
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

from config import config
from database import database
from scanner import scanner
from metadata import metadata_extractor
from douban_api import douban_api
from imdb_api import imdb_api
from tags import tag_manager


def demo_scan_and_process():
    """演示：扫描和处理目录"""
    print("=== 演示：扫描和处理目录 ===")

    # 指定要扫描的目录（请修改为实际目录）
    test_dir = r"H:\video_scripts\VideoBaseApp"

    print(f"扫描目录: {test_dir}")

    # 扫描视频文件
    video_files = scanner.scan_directory(test_dir)
    print(f"找到 {len(video_files)} 个视频文件")

    if video_files:
        # 取前3个演示
        for i, video_path in enumerate(video_files[:3]):
            print(f"\n[{i+1}] {Path(video_path).name}")

            # 获取文件信息
            file_info = scanner.get_file_info(video_path)
            print(f"  文件大小: {file_info['file_size'] / (1024*1024):.2f} MB")

            # 提取元数据
            metadata = metadata_extractor.get_video_info(video_path)
            if metadata['duration']:
                minutes = metadata['duration'] // 60
                seconds = metadata['duration'] % 60
                print(f"  时长: {minutes}:{seconds:02d}")

            # 获取评分
            filename = Path(video_path).stem

            # 豆瓣
            if config.get("douban_enabled", True):
                douban_info = douban_api.search_movie_by_filename(filename)
                if douban_info:
                    print(f"  豆瓣评分: {douban_info.get('rating')}")

            # IMDb
            if config.get("imdb_enabled", True):
                imdb_info = imdb_api.search_movie_by_filename(filename)
                if imdb_info:
                    print(f"  IMDb评分: {douban_info.get('imdb_rating')}")

    print("\n演示完成\n")


def demo_tags():
    """演示：标签管理"""
    print("=== 演示：标签管理 ===")

    # 创建标签
    tag_names = ["科幻", "动作", "喜剧", "经典"]
    tag_ids = []

    for name in tag_names:
        tag_id = tag_manager.create_tag(name)
        if tag_id:
            tag_ids.append(tag_id)
            print(f"创建标签: {name} (ID: {tag_id})")

    # 获取所有标签
    all_tags = tag_manager.get_all_tags()
    print(f"\n当前共有 {len(all_tags)} 个标签:")
    for tag in all_tags:
        print(f"  - {tag['name']}")

    # 清理测试标签
    for tag_id in tag_ids:
        tag_manager.delete_tag(tag_id)
        print(f"删除标签 ID: {tag_id}")

    print("\n演示完成\n")


def demo_database():
    """演示：数据库操作"""
    print("=== 演示：数据库操作 ===")

    # 添加测试电影
    test_movie = {
        'file_path': r"C:\test\demo_movie.mp4",
        'title': "测试电影",
        'file_size': 1024 * 1024 * 100,  # 100MB
        'duration': 7200,  # 2小时
        'cover_path': None,
        'douban_rating': 8.5,
        'rating_source': 'douban',
    }

    try:
        movie_id = database.add_movie(test_movie)
        print(f"添加测试电影成功，ID: {movie_id}")

        # 获取电影
        movie = database.get_movie_by_id(movie_id)
        if movie:
            print(f"获取电影成功: {movie['title']}")

        # 删除测试电影
        conn = database._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM movies WHERE id = ?', (movie_id,))
        conn.commit()
        conn.close()
        print("删除测试电影成功")

    except Exception as e:
        print(f"数据库操作失败: {e}")

    print("\n演示完成\n")


def demo_stats():
    """演示：统计信息"""
    print("=== 演示：统计信息 ===")

    stats = database.get_stats()
    print(f"电影总数: {stats['total_movies']}")
    print(f"标签总数: {stats['total_tags']}")
    if stats['total_size']:
        print(f"总文件大小: {stats['total_size'] / (1024**3):.2f} GB")

    print("\n演示完成\n")


def main():
    """运行所有演示"""
    print("=== 视频库管理工具演示 ===\n")

    demo_database()
    demo_tags()
    demo_scan_and_process()
    demo_stats()

    print("=== 所有演示完成 ===")
    print("\n提示：")
    print("1. 修改 demo_scan_and_process() 中的 test_dir 为实际目录")
    print("2. 运行 GUI: python run_gui.py")
    print("3. 运行命令行: python src/main.py")


if __name__ == '__main__':
    main()
