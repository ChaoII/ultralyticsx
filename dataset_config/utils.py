import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from ultralytics import settings
import yaml
from loguru import logger
from pycocotools.coco import COCO
from tqdm import tqdm
from PySide6.QtWidgets import QWidget, QApplication

ROOT_DIR = os.path.join(os.path.expanduser("~"), ".gradio")
RUNS_DIR = os.path.join(ROOT_DIR, "runs")
settings.update({"runs_dir": RUNS_DIR})





class LoadDatasetInfo:
    dataset_dir: str
    train_image_num: int = 0
    train_obj_num: int = 0
    val_image_num: int = 0
    val_obj_num: int = 0
    test_image_num: int = 0
    test_obj_num: int = 0
    labels: dict
    dst_yaml_path: str


def unzip_file(zip_path, extract_path=None):
    """
    解压缩ZIP文件

    :param zip_path: ZIP文件的路径
    :param extract_path: 解压缩到的目标文件夹路径，如果为None，则解压到ZIP文件所在目录
    """
    # 如果未指定解压目录，则默认解压到ZIP文件所在目录
    if extract_path is None:
        extract_path = os.path.dirname(zip_path)

        # 确保目标解压目录存在
    if not os.path.exists(extract_path):
        os.makedirs(extract_path)

        # 使用with语句来确保zipfile对象被正确关闭
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        total_files = len(zip_ref.infolist())
        with tqdm(total=total_files, unit='file', desc='解压缩中') as pbar:
            for file in zip_ref.infolist():
                # 解压缩文件
                zip_ref.extract(file, extract_path)
                # 更新进度条
                pbar.update(1)
    return extract_path


def move_to_dst_dir(src_file: str):
    # 精确到微秒
    time_stamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    # 创建目录
    gradio_project_dir = os.path.join(ROOT_DIR, "projects", time_stamp)
    gradio_dataset_dir = os.path.join(gradio_project_dir, "dataset")
    os.makedirs(gradio_dataset_dir, exist_ok=True)
    # 将上传的文件移动到当前目录
    shutil.move(src_file, gradio_dataset_dir)
    return os.path.join(gradio_dataset_dir, os.path.split(src_file)[-1])


def convert(coco_dataset_zip_file):
    new_zip_path = move_to_dst_dir(coco_dataset_zip_file)
    # 解压缩
    dataset_dir = unzip_file(new_zip_path)
    dataset_info = LoadDatasetInfo()
    zip_filename = Path(new_zip_path).stem
    # 创建输出目录
    annotations_dir = os.path.join(dataset_dir, zip_filename, "annotations")
    labels = get_labels(annotations_dir)
    project_dir = os.path.dirname(dataset_dir)
    dst_yaml_path = rebuild_data_yaml(project_dir, dataset_dir, labels)
    dataset_info.dataset_dir = Path(dataset_dir).resolve().as_posix()
    dataset_info.dst_yaml_path = Path(dst_yaml_path).resolve().as_posix()
    labels_str = ""
    for k, v in labels.items():
        labels_str += f"{k}: {v}\n"
    dataset_info.labels = labels_str
    for file_name in os.listdir(annotations_dir):
        if file_name.__contains__("train"):
            images_num, object_num = convert_coco_to_yolo(os.path.join(annotations_dir, file_name),
                                                          dataset_dir, "train")
            dataset_info.train_image_num = images_num
            dataset_info.train_obj_num = object_num

        elif file_name.__contains__("val"):
            images_num, object_num = convert_coco_to_yolo(os.path.join(annotations_dir, file_name),
                                                          dataset_dir, "val")
            dataset_info.val_image_num = images_num
            dataset_info.val_obj_num = object_num
        elif file_name.__contains__("test"):
            images_num, object_num = convert_coco_to_yolo(os.path.join(annotations_dir, file_name),
                                                          dataset_dir, "test")
            dataset_info.test_image_num = images_num
            dataset_info.test_obj_num = object_num
        else:
            logger.error("annotation file must contain train val or test")

    shutil.rmtree(os.path.join(dataset_dir, zip_filename))

    return (
        dataset_info.dataset_dir, dataset_info.train_image_num, dataset_info.train_obj_num,
        dataset_info.val_image_num, dataset_info.val_obj_num, dataset_info.test_image_num,
        dataset_info.test_obj_num, dataset_info.labels, dataset_info.dst_yaml_path)


def get_labels(annotations_dir):
    labels = dict()
    for file_name in os.listdir(annotations_dir):
        if file_name.__contains__("train"):
            coco = COCO(os.path.join(annotations_dir, file_name))
            categories = coco.loadCats(coco.getCatIds())
            labels = {category['id']: category['name'] for category in categories}
    return labels


def convert_coco_to_yolo(coco_annotation_file, out_dir, mode="train"):
    coco = COCO(coco_annotation_file)
    output_dir = Path(out_dir)
    labels_dir = output_dir / 'labels' / mode
    images_dir = output_dir / 'images' / mode
    labels_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)

    # 读取类别
    categories = coco.loadCats(coco.getCatIds())
    category_id_to_index = {category['id']: i for i, category in enumerate(categories)}

    # 读取图片信息
    image_ids = coco.getImgIds()
    images = coco.loadImgs(image_ids)

    object_num = 0
    # 转换每一张图片的标注
    for image in tqdm(images):
        image_id = image['id']
        file_name = image['file_name']

        # 获取图像的宽高
        image_width = image['width']
        image_height = image['height']

        # 获取该图像的标注
        annotation_ids = coco.getAnnIds(imgIds=[image_id])
        annotations = coco.loadAnns(annotation_ids)
        # 创建标注文件
        yolo_annotations = []
        for annotation in annotations:
            category_id = annotation['category_id']
            bbox = annotation['bbox']
            # COCO格式的bbox是 [x_min, y_min, width, height]
            x_min, y_min, bbox_width, bbox_height = bbox
            x_center = x_min + bbox_width / 2
            y_center = y_min + bbox_height / 2
            # 归一化坐标
            x_center /= image_width
            y_center /= image_height
            bbox_width /= image_width
            bbox_height /= image_height
            # 获取类别索引
            category_index = category_id_to_index[category_id]
            # 添加标注
            yolo_annotations.append(f"{category_index} {x_center} {y_center} {bbox_width} {bbox_height}")
        object_num += len(yolo_annotations)
        # 写入标注文件
        label_file_path = labels_dir / f"{Path(file_name).stem}.txt"
        with open(label_file_path, 'w') as label_file:
            label_file.write("\n".join(yolo_annotations))
        # 复制图像文件到目标目录
        shutil.copy(Path(coco_annotation_file).parent.parent / "images" / image["file_name"], images_dir)
    logger.info(f"数据集[{Path(coco_annotation_file).stem}]转换完成")
    return len(images), object_num


def rebuild_data_yaml(project_dir, dataset_dir, labels: dict):
    dst_yaml_path = os.path.join(project_dir, "coco_cpy.yaml")
    dataset_config = dict()
    with open(dst_yaml_path, 'w', encoding="utf8") as file:
        dataset_config.update({"path": dataset_dir})
        dataset_config.update({"train": "images/train"})
        dataset_config.update({"val": "images/val"})
        dataset_config.update({"test": "images/test"})
        dataset_config.update({"names": labels})
        yaml.dump(dataset_config, file, default_flow_style=False, allow_unicode=True, sort_keys=False)
    return dst_yaml_path


if __name__ == '__main__':
    convert(r"C:\Users\AC\AppData\Local\Temp\gradio\7c8d324344f9b7c4895bf818ee9d09f4bf072dab\det_coco_examples.zip")
