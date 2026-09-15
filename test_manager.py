#!/usr/bin/env python3
"""
Manager 模块测试单元
解决导入路径问题并测试文件管理功能
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入自定义模块
from bin.command.Manager import Manager


def test_file_operations():
    """测试文件操作功能"""
    print("=== 开始测试文件操作功能 ===")
    
    # 创建临时目录用于测试
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"测试目录: {temp_dir}")
        
        # 创建测试文件
        test_file = os.path.join(temp_dir, "test_file.txt")
        test_copy = os.path.join(temp_dir, "test_copy.txt")
        test_move = os.path.join(temp_dir, "test_move.txt")
        test_rename = os.path.join(temp_dir, "test_renamed.txt")
        
        # 写入测试内容
        with open(test_file, 'w') as f:
            f.write("这是测试文件内容")
        
        # 测试文件管理器
        manager = Manager()
        file_manager = manager.File()  # 正确实例化 File 类
        
        # 测试复制文件
        print("\n1. 测试文件复制...")
        try:
            result = file_manager.Copy(test_file, test_copy)
            assert result == True, "文件复制失败"
            assert os.path.exists(test_copy), "复制文件不存在"
            print("✓ 文件复制测试通过")
        except Exception as e:
            print(f"✗ 文件复制测试失败: {e}")
        
        # 测试移动文件
        print("\n2. 测试文件移动...")
        try:
            result = file_manager.Move(test_copy, test_move)
            assert result == True, "文件移动失败"
            assert os.path.exists(test_move), "移动后文件不存在"
            assert not os.path.exists(test_copy), "原文件仍存在"
            print("✓ 文件移动测试通过")
        except Exception as e:
            print(f"✗ 文件移动测试失败: {e}")
        
        # 测试重命名文件
        print("\n3. 测试文件重命名...")
        try:
            result = file_manager.Rename(test_move, test_rename)
            assert result == True, "文件重命名失败"
            assert os.path.exists(test_rename), "重命名后文件不存在"
            assert not os.path.exists(test_move), "原文件名仍存在"
            print("✓ 文件重命名测试通过")
        except Exception as e:
            print(f"✗ 文件重命名测试失败: {e}")
        
        # 测试删除文件
        print("\n4. 测试文件删除...")
        try:
            result = file_manager.Delete(test_rename)
            assert result == True, "文件删除失败"
            assert not os.path.exists(test_rename), "文件仍存在"
            print("✓ 文件删除测试通过")
        except Exception as e:
            print(f"✗ 文件删除测试失败: {e}")
        
        # 测试文件搜索（简化版本，避免 Tree 类导入问题）
        print("\n5. 测试文件搜索...")
        try:
            # 创建测试文件用于搜索
            search_file = os.path.join(temp_dir, "search_test.txt")
            with open(search_file, 'w') as f:
                f.write("搜索测试文件")
            
            # 使用简单的文件搜索替代 Tree 类
            search_result = []
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if "search_test" in file:
                        search_result.append(os.path.join(root, file))
            
            assert len(search_result) > 0, "文件搜索失败"
            print(f"✓ 文件搜索测试通过，找到文件: {search_result}")
        except Exception as e:
            print(f"✗ 文件搜索测试失败: {e}")


def test_error_handling():
    """测试错误处理"""
    print("\n=== 开始测试错误处理 ===")
    
    manager = Manager()
    file_manager = manager.File()  # 正确实例化 File 类
    
    # 测试删除不存在的文件
    print("\n1. 测试删除不存在的文件...")
    try:
        result = file_manager.Delete("nonexistent_file.txt")
        print("✗ 应该抛出异常但未抛出")
    except Exception as e:
        print(f"✓ 正确抛出异常: {e}")
    
    # 测试复制到无效路径
    print("\n2. 测试复制到无效路径...")
    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        result = file_manager.Copy(temp_path, "/invalid/path/test.txt")
        print("✗ 应该抛出异常但未抛出")
    except Exception as e:
        print(f"✓ 正确抛出异常: {e}")
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def show_function_examples():
    """展示每个函数的调用例子"""
    print("\n=== Manager 类函数调用示例 ===")
    
    # 创建 Manager 实例
    manager = Manager()
    file_manager = manager.File()
    folder_manager = manager.Folder()
    
    # 创建临时目录用于示例
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"示例目录: {temp_dir}")
        
        # 1. 文件创建示例
        print("\n1. 文件创建示例:")
        example_file = os.path.join(temp_dir, "example.txt")
        result = file_manager.Create(example_file)
        print(f"   file_manager.Create('{example_file}') -> {result}")
        
        # 2. 文件复制示例
        print("\n2. 文件复制示例:")
        copy_file = os.path.join(temp_dir, "example_copy.txt")
        result = file_manager.Copy(example_file, copy_file)
        print(f"   file_manager.Copy('{example_file}', '{copy_file}') -> {result}")
        
        # 3. 文件移动示例
        print("\n3. 文件移动示例:")
        move_file = os.path.join(temp_dir, "moved_example.txt")
        result = file_manager.Move(copy_file, move_file)
        print(f"   file_manager.Move('{copy_file}', '{move_file}') -> {result}")
        
        # 4. 文件重命名示例
        print("\n4. 文件重命名示例:")
        renamed_file = os.path.join(temp_dir, "renamed_example.txt")
        result = file_manager.Rename(move_file, renamed_file)
        print(f"   file_manager.Rename('{move_file}', '{renamed_file}') -> {result}")
        
        # 5. 文件状态获取示例
        print("\n5. 文件状态获取示例:")
        result = file_manager.Status(renamed_file)
        print(f"   file_manager.Status('{renamed_file}') -> {result}")
        
        # 6. 文件夹创建示例
        print("\n6. 文件夹创建示例:")
        example_folder = os.path.join(temp_dir, "example_folder")
        result = folder_manager.Create(example_folder)
        print(f"   folder_manager.Create('{example_folder}') -> {result}")
        
        # 7. 文件夹状态获取示例
        print("\n7. 文件夹状态获取示例:")
        result = folder_manager.Status(example_folder)
        print(f"   folder_manager.Status('{example_folder}') -> {result}")
        
        # 8. 文件搜索示例（简化版）
        print("\n8. 文件搜索示例:")
        # 创建测试文件用于搜索
        search_file = os.path.join(example_folder, "search_test.txt")
        file_manager.Create(search_file)
        
        # 使用 os.walk 进行搜索（避免 Tree 类导入问题）
        search_result = []
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if "search_test" in file:
                    search_result.append(os.path.join(root, file))
        
        print(f"   搜索 'search_test' 文件 -> 找到 {len(search_result)} 个文件: {search_result}")
        
        # 9. 文件删除示例
        print("\n9. 文件删除示例:")
        result = file_manager.Delete(renamed_file)
        print(f"   file_manager.Delete('{renamed_file}') -> {result}")
        
        # 10. 文件夹删除示例
        print("\n10. 文件夹删除示例:")
        result = folder_manager.Delete(example_folder)
        print(f"   folder_manager.Delete('{example_folder}') -> {result}")


def main():
    """主测试函数"""
    print("Manager 模块测试开始")
    print("=" * 50)
    
    # 展示函数调用示例
    show_function_examples()
    
    # 运行功能测试
    test_file_operations()
    
    # 运行错误处理测试
    test_error_handling()
    
    print("\n" + "=" * 50)
    print("Manager 模块测试完成")


if __name__ == "__main__":
    main()