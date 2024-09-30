from common.component.model_type_widget import ModelType

model_options_cls = [
    "yolov8n-cls",
    "yolov8s-cls",
    "yolov8m-cls",
    "yolov8l-cls",
    "yolov8x-cls",
]

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

model_options_obb = [
    "yolov8n-obb",
    "yolov8s-obb",
    "yolov8m-obb",
    "yolov8l-obb",
    "yolov8x-obb",
]

model_options_pose = [
    "yolov8n-pose",
    "yolov8s-pose",
    "yolov8m-pose",
    "yolov8l-pose",
    "yolov8x-pose",
    "yolov8x-pose-p6"
]

model_type_list_map = {
    ModelType.CLASSIFY: model_options_cls,
    ModelType.DETECT: model_options_det,
    ModelType.SEGMENT: model_options_seg,
    ModelType.OBB: model_options_obb,
    ModelType.POSE: model_options_pose,
}
