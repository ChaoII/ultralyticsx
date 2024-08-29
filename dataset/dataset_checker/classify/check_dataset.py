from pathlib import Path
from PIL import Image


def is_image(filename):
    try:
        with Image.open(filename) as img:
            img.verify()  # 验证图片是否完整
            return True
    except (IOError, SyntaxError) as e:
        return False


def classify_dataset_check(dataset_dir: Path):
    if not any(dataset_dir.iterdir()):
        return False
    for item in dataset_dir.iterdir():
        if item.is_dir():
            for file in item.iterdir():
                if file.is_file():
                    if not is_image(file):
                        return False
                else:
                    return False
        else:
            return False
    return True
