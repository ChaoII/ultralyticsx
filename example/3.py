from pprint import pprint

from PIL.ImageQt import QImage

from common.utils.draw_labels import draw_pose_result
from ultralytics import YOLO

model = YOLO(r"C:\Users\84945\Desktop\ultralytics_workspace\project\P000001\T000001000008\weights\best.pt")
# model = YOLO(r"C:\Users\84945\Desktop\ultralytics_workspace\project\P000005\T000005000000\weights\best.onnx")

model.export(format="onnx", opset=11, simplify=False)
# results = model.predict(r"C:\Users\AC\Desktop\DCS\images\001.png")
# print(results)

# metrics = model.val(workers=0, batch=16, split="test")
# pf = "%22s" + "%11i" * 2 + "%11.3g" * len(metrics.keys)  # print format
# print(pf % ("all", model.validator.seen, model.validator.nt_per_class.sum(), *metrics.mean_results()))
# for i, c in enumerate(metrics.ap_class_index):
#     print(pf % (model.validator.names[c], model.validator.nt_per_image[c], model.validator.nt_per_class[c],
#                 *model.metrics.class_result(i)))

# model.validator.print_results()
# pprint(model.validator.get_val_results())
# pprint(model.validator.speed)
# image_path = r"C:\Users\84945\Desktop\ultralytics_workspace\dataset\D000004\split\images\train\000000000036.jpg"
# results = model.predict(image_path)
# pprint(results)
# for result in results:
#     pprint(result.keypoints)
#     pprint(result.boxes)
# result = results[0]
# pix = QImage(image_path)
# draw_pose_result(pix, result.names, result.boxes.data.cpu().tolist(), result.keypoints.data.cpu().tolist())
# pix.save("2.jpg")
