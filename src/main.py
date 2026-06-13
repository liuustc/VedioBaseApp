"""
主程序入口
整合所有模块，提供命令行和GUI界面
"""
import sys
import os
from pathlib import Path
from typing import Optional
from loguru import logger

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from config import config
from database import database
from scanner import scanner
from metadata import metadata_extractor
from douban_api import douban_api
from imdb_api import imdb_api
from tags import tag_manager


def setup_logging():
    """设置日志"""
    logger.add(
        "video_base_app.log",
        rotation="10 MB",
        retention="10 days",
        level="INFO",
        encoding="utf-8"
    )


def scan_and_process_directory(directory: str):
    """
    扫描目录中的视频文件

    Args:
        directory: 要扫描的目录路径
    """
    logger.info(f"开始扫描目录: {directory}")

    # 扫描视频文件
    video_files = scanner.scan_directory_with_progress(directory)

    if not video_files:
        logger.warning("未找到视频文件")
        return

    # 保存到数据库
    logger.info("开始保存到数据库...")
    for i, video_path in enumerate(video_files):
        logger.info(f"处理 [{i+1}/{len(video_files)}]: {Path(video_path).name}")

        # 获取文件信息
        file_info = scanner.get_file_info(video_path)

        # 只保存基本信息
        movie_data = {
            'file_path': video_path,
            'title': Path(video_path).stem,
            'file_size': file_info['file_size'],
        }

        # 保存到数据库
        try:
            movie_id = database.add_movie(movie_data)
            logger.info(f"电影已保存到数据库，ID: {movie_id}")
        except Exception as e:
            logger.error(f"保存电影失败: {e}")

    logger.info(f"处理完成，共处理 {len(video_files)} 个视频文件")


def show_stats():
    """显示统计信息"""
    stats = database.get_stats()
    print("\n=== 统计信息 ===")
    print(f"电影总数: {stats['total_movies']}")
    print(f"标签总数: {stats['total_tags']}")
    print(f"总文件大小: {stats['total_size'] / (1024**3):.2f} GB")


def list_movies():
    """列出所有电影"""
    movies = database.get_all_movies()
    print(f"\n=== 电影列表 ({len(movies)} 部) ===")
    for movie in movies:
        rating = movie.get('douban_rating') or movie.get('imdb_rating') or 'N/A'
        print(f"{movie['id']}. {movie['title']} | 评分: {rating} | 时长: {movie['duration']}秒")


def list_tags():
    """列出所有标签"""
    tags = tag_manager.get_all_tags()
    print(f"\n=== 标签列表 ({len(tags)} 个) ===")
    for tag in tags:
        print(f"{tag['id']}. {tag['name']} ({tag['color']})")


def add_tag_to_movie(movie_id: int, tag_name: str):
    """为电影添加标签"""
    # 获取或创建标签
    tag = tag_manager.get_tag_by_name(tag_name)
    if not tag:
        tag_id = tag_manager.create_tag(tag_name)
        if not tag_id:
            print(f"创建标签失败: {tag_name}")
            return
    else:
        tag_id = tag['id']

    # 添加标签到电影
    tag_manager.add_tag_to_movie(movie_id, tag_id)
    print(f"已为电影 {movie_id} 添加标签: {tag_name}")


def interactive_mode():
    """交互式命令行模式"""
    print("\n=== 视频库管理工具 ===")
    print("1. 扫描目录")
    print("2. 列出电影")
    print("3. 列出标签")
    print("4. 为电影添加标签")
    print("5. 显示统计")
    print("6. 退出")

    while True:
        try:
            choice = input("\n请选择操作 (1-6): ").strip()

            if choice == '1':
                directory = input("请输入目录路径: ").strip()
                if directory:
                    scan_and_process_directory(directory)
            elif choice == '2':
                list_movies()
            elif choice == '3':
                list_tags()
            elif choice == '4':
                movie_id = int(input("请输入电影ID: ").strip())
                tag_name = input("请输入标签名称: ").strip()
                add_tag_to_movie(movie_id, tag_name)
            elif choice == '5':
                show_stats()
            elif choice == '6':
                print("再见！")
                break
            else:
                print("无效选择，请重新输入")

        except KeyboardInterrupt:
            print("\n再见！")
            break
        except Exception as e:
            print(f"错误: {e}")


def main():
    """主函数"""
    setup_logging()

    if len(sys.argv) > 1:
        # 命令行模式
        command = sys.argv[1]

        if command == 'scan' and len(sys.argv) > 2:
            directory = sys.argv[2]
            scan_and_process_directory(directory)
        elif command == 'list':
            list_movies()
        elif command == 'stats':
            show_stats()
        else:
            print("用法:")
            print("  python main.py scan <目录路径>  - 扫描目录")
            print("  python main.py list            - 列出电影")
            print("  python main.py stats           - 显示统计")
            print("  python main.py                 - 交互式模式")
    else:
        # 交互式模式
        interactive_mode()


if __name__ == '__main__':
    main()
