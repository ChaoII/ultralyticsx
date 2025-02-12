from pathlib import Path
import subprocess

# 定义要排除的目录
exclude_dirs = ['ultralytics']
root_dir = Path('.')
py_files = []


def collect_py_files(directory):
    for item in directory.iterdir():
        if item.is_dir():
            # 如果是目录且不在排除列表中，则递归调用
            if item.name not in exclude_dirs:
                collect_py_files(item)
        # 不能包含资源文件
        elif item.is_file() and item.suffix == '.py' and item.stem != "resources":
            # 如果是 .py 文件，则添加到列表中
            py_files.append(str(item))


collect_py_files(root_dir)

# 将文件列表写入 sources.list 文件
with open('sources.list', 'w') as f:
    for py_file in py_files:
        f.write(py_file + '\n')

subprocess.run(['pyside6-lupdate', '@sources.list', '-no-obsolete', '-ts', 'resources/i18n/ultralytics_ui.zh_CN.ts'])
# pyside6-lrelease resources/i18n/ultralytics_ui.zh_CN.ts
