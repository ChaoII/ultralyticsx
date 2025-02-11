from pathlib import Path

from PIL import Image


def is_empty(folder_path: Path):
    return not any(folder_path.iterdir())


def is_image(filename):
    try:
        with Image.open(filename) as img:
            img.verify()  # 验证图片是否完整
            return True
    except (IOError, SyntaxError) as e:
        return False


def classify_dataset_check(dataset_dir: Path):
    exist_one_type = False
    if is_empty(dataset_dir):
        return False
    for item in dataset_dir.iterdir():
        if item.is_dir():
            exist_one_type = True
            if is_empty(item):
                return False
            for file in item.iterdir():
                if file.is_file():
                    if not is_image(file):
                        return False
                else:
                    return False
        else:
            continue
    return exist_one_type
