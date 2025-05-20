import os
import numpy as np
import cv2
from sklearn.preprocessing import LabelEncoder
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from keras.preprocessing.image import ImageDataGenerator
from keras.utils import to_categorical


# 自定义数据加载函数
def load_data(data_dir, custom_order=None):
    x_data = []
    y_data = []
    emotions = os.listdir(data_dir)

    # 如果提供了自定义顺序，使用自定义顺序
    if custom_order is not None:
        emotions = custom_order

    for emotion in emotions:
        emotion_dir = os.path.join(data_dir, emotion)
        if os.path.isdir(emotion_dir):
            for img_name in os.listdir(emotion_dir):
                img_path = os.path.join(emotion_dir, img_name)
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                img = cv2.resize(img, (48, 48))  # resize to 48x48
                x_data.append(img)
                y_data.append(emotion)

    x_data = np.array(x_data).astype('float32') / 255.0  # 归一化
    y_data = np.array(y_data)

    # 标签编码
    le = LabelEncoder()
    y_data = le.fit_transform(y_data)
    y_data = to_categorical(y_data)  # one-hot编码

    return x_data, y_data, le.classes_


# 创建模型
def create_model(input_shape):
    model = Sequential()
    model.add(Conv2D(32, (3, 3), activation='relu', input_shape=input_shape))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Conv2D(128, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Flatten())
    model.add(Dense(128, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(len(classes), activation='softmax'))

    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model


# 数据目录
data_dir = './CK+48'
custom_order = ['anger', 'contempt', 'disgust', 'fear', 'happy', 'sadness', 'surprise']

# 加载数据
x_data, y_data, classes = load_data(data_dir, custom_order)

# 创建模型
input_shape = (48, 48, 1)  # 单通道灰度图像
model = create_model(input_shape)

# 数据增强
datagen = ImageDataGenerator(validation_split=0.2)
train_generator = datagen.flow(x_data.reshape(-1, 48, 48, 1), y_data, batch_size=32, subset='training')
validation_generator = datagen.flow(x_data.reshape(-1, 48, 48, 1), y_data, batch_size=32, subset='validation')

# 训练模型
model.fit(train_generator, validation_data=validation_generator, epochs=50)

# 保存模型
model.save('emotion_model.h5')
