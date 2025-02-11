
import onnx
import onnxruntime as ort
print(ort.__version__)

ort_sess = ort.InferenceSession(r'C:\Users\AC\CLionProjects\wrzs_hys\build\ttt.onnx')
# ort_sess = ort.InferenceSession(r'../slim.onnx')

# try:
#     model = onnx.load(r"C:\Users\AC\CLionProjects\wrzs_hys\build\ppyoloe.onnx")
#     onnx.checker.check_model(model)
# except onnx.checker.ValidationError as e:
#     print('The model is invalid: %s' % e)
#
# print(onnx.helper.printable_graph(model.graph))

