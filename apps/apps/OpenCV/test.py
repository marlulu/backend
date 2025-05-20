import os

import cv2
from mtcnn import MTCNN

# 加载 MTCNN 人脸检测器
detector = MTCNN()

# 打开图像
file_path = os.path.join("media", "uploads", "images", "sltp-1.png")

print(file_path)
img = cv2.imread(file_path)
image_path = '../../../media/uploads/images/sltp-1.png'
print(image_path)
image = cv2.imread(image_path)
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#
# 使用 MTCNN 进行人脸检测
faces = detector.detect_faces(image_rgb)

# 对每张检测到的人脸进行表情识别
for face in faces:
    x, y, width, height = face['box']
    x, y = max(0, x), max(0, y)
    print(x, y, width, height)
