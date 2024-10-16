from pathlib import Path
from loguru import logger

from common.utils.utils import is_empty, is_image


def obb_dataset_check(dataset_dir: Path | str):
    if isinstance(dataset_dir, str):
        dataset_dir = Path(dataset_dir)

    if not dataset_dir.is_dir():
        logger.error("输入路径不是一个有效的目录")
        return False

    # 检查文件夹是否包含images和labels和classes.txt
    images_path = dataset_dir / "images"
    labels_path = dataset_dir / "labels"
    classes_file_path = dataset_dir / "classes.txt"
    if not images_path.exists():
        logger.error("源数据集未包含[images]目录")
        return False
    if not labels_path.exists():
        logger.error("源数据集未包含[labels]目录")
        return False
    if not classes_file_path.exists():
        logger.error("数据集中未包含[classes.txt]文件")
        return False

    if is_empty(images_path):
        logger.error("[images]目录为空")
        return False

    if is_empty(labels_path):
        logger.error("[labels]目录为空")
        return False

    labels = []
    for item in labels_path.iterdir():
        if not item.is_file() or item.suffix != ".txt":
            logger.error(f"源数据集[labels]路径中，存在非txt文件或路径{item.name}")
            return False
        labels.append(item.stem)
    for item in images_path.iterdir():
        if not item.is_file() or not is_image(item):
            logger.error(f"源数据集[images]路径中，存在非图片的文件或路径{item.name}")
            return False
        if item.stem not in labels:
            logger.error(f"labels目录下没有对应的label，{item.name}")
            return False
    return True
