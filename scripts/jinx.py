#!/usr/bin/env python3
"""🔧 Jinx Project CLI"""

import argparse
import os
import shutil
from pathlib import Path
import sys


def cmd_clear(args):
    """ล้าง __pycache__ และไฟล์ .pyc"""
    count = 0
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            shutil.rmtree(os.path.join(root, '__pycache__'))
            count += 1
        for f in files:
            if f.endswith('.pyc'):
                os.remove(os.path.join(root, f))
                count += 1
    if os.path.exists('.pytest_cache'):
        shutil.rmtree('.pytest_cache')
        count += 1
    if args.all:
        os.system('uv cache clean')
        count += 1
    print(f'✅ ล้างแล้ว {count} รายการ')


def cmd_tree(args):
    """แสดงโครงสร้างโปรเจกต์"""
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', '.venv', '.pytest_cache']]
        level = root.replace('.', '').count(os.sep)
        indent = '  ' * level
        print(f'{indent}📁 {os.path.basename(root)}/')
        subindent = '  ' * (level + 1)
        for f in files:
            if not f.endswith('.pyc'):
                path = os.path.join(root, f)
                size = os.path.getsize(path)
                size_str = f'{size/1024:.1f}KB' if size > 1024 else f'{size}B'
                print(f'{subindent}📄 {f} ({size_str})')


def cmd_test(args):
    """รัน tests"""
    if args.name:
        path = f'tests/test_{args.name}.py'
        if os.path.exists(path):
            os.system(f'uv run pytest {path} -v')
        else:
            print(f'❌ ไม่พบ {path}')
    else:
        os.system('uv run pytest tests/ -v')


def cmd_status(args):
    """ดูสถานะโปรเจกต์"""
    py_files = len(list(Path('.').rglob('*.py')))
    test_files = len(list(Path('tests').rglob('*.py'))) if Path('tests').exists() else 0
    print(f'Python:  {sys.version.split()[0]}')
    print(f'Platform: {sys.platform}')
    print(f'Files:  {py_files} py, {test_files} tests')


def main():
    parser = argparse.ArgumentParser(description='🔧 Jinx Project Manager')
    subparsers = parser.add_subparsers(dest='command', help='คำสั่ง')

    # clear
    p = subparsers.add_parser('clear', help='ล้าง __pycache__ และ .pyc')
    p.add_argument('--all', action='store_true', help='ล้าง uv cache ด้วย')
    p.set_defaults(func=cmd_clear)

    # tree
    p = subparsers.add_parser('tree', help='แสดงโครงสร้างโปรเจกต์')
    p.set_defaults(func=cmd_tree)

    # test
    p = subparsers.add_parser('test', help='รัน tests')
    p.add_argument('name', nargs='?', help='ชื่อ test (ไม่ต้องมี test_ และ .py)')
    p.set_defaults(func=cmd_test)

    # status
    p = subparsers.add_parser('status', help='ดูสถานะโปรเจกต์')
    p.set_defaults(func=cmd_status)

    args = parser.parse_args()
    if args.command:
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()