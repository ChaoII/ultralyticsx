model_type_option = ["det", "seg", "pose", "obb", "cls"]

model_options_det = [
    "yolov8n",
    "yolov8s",
    "yolov8m",
    "yolov8l",
    "yolov8x"
]

model_options_seg = [
    "yolov8n-seg",
    "yolov8s-seg",
    "yolov8m-seg",
    "yolov8l-seg",
    "yolov8x-seg"
]

model_options_pose = [
    "yolov8n-pose",
    "yolov8s-pose",
    "yolov8m-pose",
    "yolov8l-pose",
    "yolov8x-pose",
    "yolov8x-pose-p6"
]

model_options_obb = [
    "yolov8n-obb",
    "yolov8s-obb",
    "yolov8m-obb",
    "yolov8l-obb",
    "yolov8x-obb",
]

model_options_cls = [
    "yolov8n-cls",
    "yolov8s-cls",
    "yolov8m-cls",
    "yolov8l-cls",
    "yolov8x-cls",
]

type_model_mapping = {
    "det": model_options_det,
    "seg": model_options_seg,
    "cls": model_options_cls,
    "pose": model_options_pose,
    "obb": model_options_obb
}
