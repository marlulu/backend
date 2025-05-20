# Create your views here.
import math
import os
from pathlib import Path

import cv2
import numpy as np
from PIL.Image import Image
from keras.models import load_model
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.forms import model_to_dict
from django.http import JsonResponse
from django.template.defaultfilters import length
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import json

from mtcnn import MTCNN

from DjangoProject import settings
from apps.apps.models import StudyGroup, Picture, Label, Notices, Annotation, PictureSlices


# 标签
@csrf_exempt
def handle_label(request):
    if (request.method == 'POST'):
        body = json.loads(request.body)
        if body.get('type') == 'add':
            exist = Label.objects.filter(title=body.get('name')).exists()
            if exist:
                return JsonResponse({'code': 400, 'message': '标签已存在'})
            else:
                label = Label.objects.create(
                    title=body.get('name'),
                    author_id=request.user.id,
                )
                label.save()
                return JsonResponse({'code': 200, 'message': '添加标签成功'}, status=200)
        elif body.get('type') == 'delete':
            label = Label.objects.filter(title=body.get('name'))
            label.delete()
            return JsonResponse({'code': 200, 'message': '删除标签成功'}, status=200)

@csrf_exempt
def get_labels(request):
    if (request.method == 'GET'):
            labels = Label.objects.all()
            data = list(labels.values())[::-1]
            # 返回成功响应
            return JsonResponse({'code': 200, 'message': 'success', 'data': data})

# 项目组
@csrf_exempt
def handle_study_group(request):
    if (request.method == 'POST'):
        body = json.loads(request.body)
        if body.get('type') == 'add':
            exist = StudyGroup.objects.filter(title=body.get('name')).exists()
            if exist:
                return JsonResponse({'code': 400, 'message': '项目组已存在'})
            else:
                study_group = StudyGroup.objects.create(
                    title=body.get('name'),
                    source=request.user.username,
                    author_id=request.user.id,
                    is_active=False,
                )
                study_group.save()
                return JsonResponse({'code': 200, 'message': '添加成功'}, status=200)
        elif body.get('type') == 'delete':
            study_group = StudyGroup.objects.get(title=body.get('name'))
            study_group.delete()
            return JsonResponse({'code': 200, 'message': '删除成功'}, status=200)
        elif body.get('type') == 'edit':
            if StudyGroup.objects.filter(title=body.get('name')).exists():
                if StudyGroup.objects.filter(is_active=True).exists():
                    before_study_group = StudyGroup.objects.get(is_active=True)
                    before_study_group.is_active = False
                    before_study_group.save()
                study_group = StudyGroup.objects.get(title=body.get('name'))
                study_group.is_active = True
                study_group.save()
                return JsonResponse({'code': 200, 'message': '设置成功'}, status=200)
            else:
                return JsonResponse({'code': 400, 'message': '不存在该项目组'}, status=400)

@csrf_exempt
def get_study_groups(request):
    if (request.method == 'GET'):
        groups = StudyGroup.objects.all()
        data = list(groups.values())[::-1]
        # 返回成功响应
        return JsonResponse({'code': 200, 'message': 'success', 'data': data})

@csrf_exempt
def get_users(request):
    if (request.method == 'GET'):
        groups = User.objects.all()
        data = list(groups.values())[::-1]
        # 返回成功响应
        return JsonResponse({'code': 200, 'message': 'success', 'data': data})

@csrf_exempt
def get_notices(request):
    if (request.method == 'GET'):
        groups = Notices.objects.filter(user_id=request.user.id)
        data = list(groups.values())
        # 返回成功响应
        return JsonResponse({'code': 200, 'message': 'success', 'data': data})

@csrf_exempt
def delete_notices(request):
    body = json.loads(request.body)
    notice = Notices.objects.get(id=body.get('id'))
    notice.delete()
    return JsonResponse({'code': 200, 'message': '删除成功'}, status=200)

# 导入图片

def upload_image(request):
    uploaded_file = request.FILES['file']
    if StudyGroup.objects.filter(is_active=True).exists():
        exist = Picture.objects.filter(title=uploaded_file.name).exists()
        if exist:
            return JsonResponse({'code': 400, 'message': '已存在同名图片，请重新导入'})
        else:
            group = StudyGroup.objects.get(is_active=True)
            image_instance = Picture(picture_file=uploaded_file,
                                     study_group=group,
                                     title=uploaded_file.name,
                                     author=request.user,
                                     is_confirm=request.user.is_superuser
                                     )
            image_instance.save()
            if (request.user.is_superuser):
                return JsonResponse({'code': 200, 'message': '导入成功'})
            else:
                notice = Notices.objects.create(
                    description='请审核' + request.user.username + '上传的' + os.path.splitext(uploaded_file.name)[0],
                    type='info',
                    user_id='1',
                    status="系统消息"
                )
                notice.save()
                return JsonResponse({'code': 200, 'message': '导入成功，等待管理员审核'})
    else:
        notice = Notices.objects.create(
            description='请设置当前环境的项目组',
            type='info',
            user_id='1',
            status="系统消息"
        )
        notice.save()
        return JsonResponse({'code': 400, 'message': '请联系管理员设置项目组'})

@csrf_exempt
def get_images(request):

    # 初始化查询集
    title = request.GET.get('name', '')
    number = request.GET.get('number', '')
    source = request.GET.get('source', '')
    group = request.GET.get('group', '')
    page_number = request.GET.get('page')

    # 构建 Q 对象
    query = Q()
    if title:
        query &= Q(title__icontains=title)
    if number:
        number = int(number)
        query &= Q(annotation_num=number)
    if source:
        query &= Q(source__icontains=source)
    if group:
        group = int(group)
        query &= Q(study_group_id=group)


    all_objects = Picture.objects.all()


    filtered_objects = all_objects.filter(query).order_by('-create_at')

    if int(page_number) < 0:
        value = list(filtered_objects.values())
        for item in value:
            item['name'] = os.path.splitext(item['title'])[0]
            study_group = StudyGroup.objects.get(id=item['study_group_id'])
            item['study_group'] = study_group.title
            user = User.objects.get(id=item['author_id'])
            item['user'] = user.username

        return JsonResponse({'code': 200, 'message': '获取成功', 'data': value})

    paginator = Paginator(filtered_objects, 14)

    try:
        pictures_page = paginator.page(page_number)
    except PageNotAnInteger:
        pictures_page = paginator.page(1)
    except EmptyPage:
        pictures_page = paginator.page(paginator.num_pages)

    value =  list(pictures_page.object_list.values())
    for item in value:
        item['name'] = os.path.splitext(item['title'])[0]
        study_group = StudyGroup.objects.get(id=item['study_group_id'])
        item['study_group'] = study_group.title
        user = User.objects.get(id=item['author_id'])
        item['user'] = user.username

    data = {
        'data': value,
        'total': paginator.count,
        'current_page': pictures_page.number,
        'total_pages': paginator.num_pages,
    }

    return JsonResponse({'code': 200, 'message': '获取成功', 'data': data})

def get_image(request):
    userId = request.GET.get('id')
    picture = Picture.objects.filter(id=userId)
    data = list(picture.values())[0]
    data['name'] = os.path.splitext(data['title'])[0]
    data['annotator'] = request.user.id

    return JsonResponse({'code': 200, 'message': '获取成功', 'data': data})

@csrf_exempt
def check_image(request):
    body = json.loads(request.body)
    picture = Picture.objects.get(id=body.get('id'))
    picture.is_confirm = True
    picture.save()
    notice = Notices.objects.create(
        description='审核通过，图片' + body.get('name') + '可以进行标注',
        type='success',
        user_id=body.get('author_id'),
        status="系统消息"
    )
    notice.save()
    return JsonResponse({'code': 200, 'message': '审核完成'}, status=200)

@csrf_exempt
def delete_image(request):
    body = json.loads(request.body)
    picture = Picture.objects.get(id=body.get('id'))
    picture.delete()
    if body.get('is_confirm'):
        return JsonResponse({'code': 200, 'message': '删除成功'}, status=200)
    else:
        notice = Notices.objects.create(
            description='审核不通过，请重新上传',
            type='warning',
            user_id=body.get('author_id'),
            status="系统消息"
        )
        notice.save()
        return JsonResponse({'code': 200, 'message': '审核完成'}, status=200)

# 标注
@csrf_exempt
def add_annotation(request):
    body = json.loads(request.body)
    picture = Picture.objects.get(id=body.get('pictureId'))
    annotation = Annotation.objects.create(
        picture=picture,
        left=body.get('x'),
        top=body.get('y'),
        width=body.get('w'),
        height=body.get('h'),
        target=body.get('target', '学生'),
        annotator=request.user.username,
        label_id=body.get('labelValue'),
        label=body.get('label'),
        color=request.user.first_name
    )
    annotation.save()
    data = model_to_dict(annotation)
    picture.annotation_num = picture.annotation_num + 1
    picture.save()
    return JsonResponse({'code': 200, 'message': '添加成功', 'data': data}, status=200)

@csrf_exempt
def get_annotations(request):
    picId = request.GET.get('picId', '')
    username = request.GET.get('username', '')
    picture = Picture.objects.get(id=picId)
    target = request.GET.get('target', '')
    labelValue = request.GET.get('labelValue', '')
    confirm = request.GET.get('confirm', -1)
    align = request.GET.get('align', -1)

    query = Q()
    query &= Q(picture=picture)
    if username:
        query &= Q(annotator=username)
    if target:
        query &= Q(target=target)
    if labelValue:
        number = int(labelValue)
        query &= Q(label_id=number)
    if int(confirm) > -1:
        query &= Q(confirm=confirm)
    if int(align) > -1:
        query &= Q(align=align)

    annotations = Annotation.objects.filter(query).order_by('-createdAt')
    data = list(annotations.values())
    return JsonResponse({'code': 200, 'message': '成功', 'data': data}, status=200)

@csrf_exempt
def edit_annotation(request):
    body = json.loads(request.body)
    if body.get('id'):
        annotation = Annotation.objects.get(id=body.get('id'))
        if body.get('left'):
            annotation.left = body.get('left')
            annotation.top = body.get('top')
            annotation.width = body.get('width')
            annotation.height = body.get('height')
        if body.get('align_user', ''):
            annotation.align_user = body.get('align_user')
        annotation.target = body.get('target')
        if body.get('label'):
            annotation.label = body.get('label')
        annotation.labelValue = body.get('labelValue')
        annotation.save()
        annotation.refresh_from_db()

        data = model_to_dict(annotation)
        data['pictureId'] = data['picture']
        data['labelValue'] = data['label_id']

        return JsonResponse({'code': 200, 'message': '完成', 'data': data}, status=200)
    return JsonResponse({'code': 200, 'message': '完成'}, status=200)

@csrf_exempt
def confirm_annotations(request):
    data = json.loads(request.body)
    picId = data.get('picId', '')
    picture = Picture.objects.get(id=picId)
    ids = data.get('ids', [])
    confirm = data.get('confirm', 1)
    if length(ids) > 0:
        annotations = Annotation.objects.filter(id__in=ids)
        index = 0
        for annotation in annotations:
            annotation.confirm = int(confirm)
            name = os.path.splitext(picture.title)[0] + '-(' + str(annotation.left) + ',' + str(annotation.top)  + ')'
            slice = PictureSlices.objects.create(
                name=name,
                label=annotation.label,
                group=picture.study_group.title,
                pic=picture.title,
                annotation=annotation,
            )
            index += 1
            slice.save()
        Annotation.objects.bulk_update(annotations, ['confirm'])
    return JsonResponse({'code': 200, 'message': '成功'}, status=200)

@csrf_exempt
def delete_annotations(request):
    data = json.loads(request.body)
    ids = data.get('ids', [])
    if length(ids) > 0:
        Annotation.objects.filter(id__in=ids).delete()
        picture = Picture.objects.get(id=data.get('picId'))
        picture.annotation_num = picture.annotation_num - length(ids)
        picture.save()
    return JsonResponse({'code': 200, 'message': '成功'}, status=200)

@csrf_exempt
def auto_annotations(request):
    data = json.loads(request.body)
    picture = Picture.objects.get(id=data.get('pictureId'))
    labels = data.get('labels')
    picture_name = os.path.basename(data.get('picture_file'))
    # 加载 MTCNN 人脸检测器
    detector = MTCNN()
    # 打开图像
    script_dir = os.path.dirname(os.path.abspath(__file__))

    image_path = os.path.join(script_dir, '..', '..', 'media', 'uploads', 'images', picture_name)
    model_path = os.path.join(script_dir, 'OpenCV', 'CK+', 'emotion_model_my.h5')
    image_path = os.path.normpath(image_path)
    model_path = os.path.normpath(model_path)


    model = load_model(model_path)

    image = cv2.imread(image_path)
    # 检查图像是否成功加载
    if image is None:
        print("图像未成功加载，请检查路径。")
        return
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # 加载模型
    emotions = [14, 19, 16, 17, 8, 12, 18]  # 根据需求调整情感标签
    # 使用 MTCNN 进行人脸检测
    faces = detector.detect_faces(image_rgb)
    # 对每张检测到的人脸进行表情识别
    for face in faces:
        x, y, width, height = face['box']
        x, y = max(0, x), max(0, y)
        face_img = image_rgb[y:y + height, x:x + width]

        # 预处理人脸图像
        face_img_gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        face_img_resized = cv2.resize(face_img_gray, (48, 48))
        face_img_normalized = face_img_resized.astype('float32') / 255.0
        face_img_reshaped = face_img_normalized.reshape(1, 48, 48, 1)  # 1个样本，48x48，1个通道

        # 进行情感预测
        emotion_prediction = model.predict(face_img_reshaped)
        emotion_index = np.argmax(emotion_prediction)
        emotion_label = emotions[emotion_index]

        annotation = {"left": x, "top": y, "width": width, "height": height}
        label_value = emotion_label

        label = [item for item in labels if item['value'] == label_value]

        annotation = Annotation.objects.create(
            picture=picture,
            left=x,
            top=y,
            width=width,
            height=height,
            target='学生',
            annotator=request.user.username,
            label_id=label_value,
            label=label[0]['label'],
            color=request.user.first_name,
        )
        annotation.save()
        picture.annotation_num = picture.annotation_num + 1
        picture.save()

    annotations = Annotation.objects.filter(picture=picture)
    data = list(annotations.values())
    return JsonResponse({'code': 200, 'message': '成功', 'data': data}, status=200)




def stretch(node, neighbors, stretch_type):
    width = node['width']
    height = node['height']
    if stretch_type == 0:
        # 寻找最小的宽度和高度
        for item in neighbors:
            width = min(width, item['width'])
            height = min(height, item['height'])
    elif stretch_type == 1:
        # 求平均宽度和高度
        width_sum = 0
        height_sum = 0
        for item in neighbors:
            width_sum += item['width']
            height_sum += item['height']
        width = (width + width_sum) / (len(neighbors) + 1)
        height = (height + height_sum) / (len(neighbors) + 1)
    elif stretch_type == 2:
        # 寻找最大的宽度和高度
        for item in neighbors:
            width = max(width, item['width'])
            height = max(height, item['height'])

    # 更新node的宽度和高度
    for item in neighbors:
        item['width'] = width
        item['height'] = height
    node['width'] = width
    node['height'] = height


def filter_kwargs(kwargs):
    return {k: v for k, v in kwargs.items() if v is not None and v != ''}


def update_annotation(annotation, **kwargs):
    filter_data = filter_kwargs(kwargs)
    for key, value in filter_data.items():
        if hasattr(annotation, key):
            setattr(annotation, key, value)
    annotation.save()


def save_align_result(node, params={}):
    annotation = Annotation.objects.get(id=node.get('id'))
    aligned_label = node['aligned_label'] if len(node['aligned_label']) > 0 else []
    update_annotation(annotation, **params, width=node['width'], height=node['height'],
                                           align=1, aligned_label=aligned_label)


def private_to_part_align(annotations, direction, stretch_type, user):
    # 先选出标准节点
    if 'left' in direction:
        annotations.sort(key=lambda x: x['left'])
    elif 'top' in direction:
        annotations.sort(key=lambda x: x['top'])
    elif 'right' in direction:
        annotations.sort(key=lambda x: x['left'] + x['width'], reverse=True)
    elif 'bottom' in direction:
        annotations.sort(key=lambda x: x['top'] + x['height'], reverse=True)
    else:
        raise Exception('direction error')
    # 选取标准节点节点
    node = annotations.pop(0)
    neighbors = annotations
    # 然后拉伸
    stretch(node, neighbors, stretch_type)
    params = {'left': node['left'], 'top': node['top']}
    aligned_label_set = {item['annotator'] for item in neighbors}
    aligned_label_set.add(node['annotator'])
    for neighbor in neighbors:
        neighbor.update({'width': node['width'], 'height': node['height']})
        neighbor['aligned_label'] = [item for item in aligned_label_set if item != neighbor['annotator']]
        # 保存
        save_align_result(neighbor, params)
    save_align_result(node, params)


@csrf_exempt
def all_align(request):
    data = json.loads(request.body)
    picture = Picture.objects.get(id=data.get('picId'))
    print(data)
    try:
        ids = data.get('ids')
        direction = data.get('direction')
        stretch = data.get('stretch')
        if not ids or not direction or stretch is None:
            return JsonResponse('参数错误,ids,direction都必需', status=400)
        if len(ids) < 2:
            return
        annotations = Annotation.objects.filter(id__in=ids).values()
        # 局部对齐
        private_to_part_align(list(annotations), direction, stretch, request.user)
        return JsonResponse({'code': 200, 'msg': '手动对齐成功'})
    except Exception as e:
        return JsonResponse({'code': 0, 'msg': str(e)})






@csrf_exempt
def get_sclies(request):
    name = request.GET.get('name', '')
    group = request.GET.get('group', '')
    source = request.GET.get('source', '')
    page_number = request.GET.get('page')

    query = Q()
    if name:
        query &= Q(name__icontains=name)
    if group:
        query &= Q(group=group)
    if source:
        query &= Q(pic__icontains=source)

    all_objects = PictureSlices.objects.all()

    filtered_objects = all_objects.filter(query).order_by('-create_at')
    paginator = Paginator(filtered_objects, 14)

    try:
        pictures_page = paginator.page(page_number)
    except PageNotAnInteger:
        pictures_page = paginator.page(1)
    except EmptyPage:
        pictures_page = paginator.page(paginator.num_pages)

    value = list(pictures_page.object_list.values())
    for item in value:
        annotation = Annotation.objects.get(id=item['annotation_id'])
        picture = Picture.objects.get(id=annotation.picture.id)
        item['picture_file'] = picture.picture_file.url

    data = {
        'data': value,
        'total': paginator.count,
        'current_page': pictures_page.number,
        'total_pages': paginator.num_pages,
    }

    return JsonResponse({'code': 200, 'message': '获取成功', 'data': data})





@csrf_exempt
def export_slices(request):
    data = json.loads(request.body)

    name = data.get('name', '')
    group = data.get('group', '')
    source = data.get('source', '')

    query = Q()
    if name:
        query &= Q(name__icontains=name)
    if group:
        query &= Q(group=group)
    if source:
        query &= Q(pic__icontains=source)

    all_objects = PictureSlices.objects.all()

    filtered_objects = all_objects.filter(query).order_by('-create_at')

    value = list(filtered_objects.values())

    picture_name = os.path.basename(data.get('picture_name'))

    script_dir = os.path.dirname(os.path.abspath(__file__))

    image_path = os.path.join(script_dir, '..', '..', 'media', 'uploads', 'images', picture_name)
    image_path = os.path.normpath(image_path)
    # 读取图片
    # 处理中文路径
    image = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), -1)
    # 检查图片是否正确读取
    if image is None:
        print(f"Error: Could not read the image from {script_dir}")
        return
    for item in value:
        annotation = Annotation.objects.get(id=item['annotation_id'])
        slice = PictureSlices.objects.get(id=item['id'])
        # 根据给定的坐标和尺寸裁剪图片
        cropped_image = image[annotation.top:annotation.top + annotation.height, annotation.left:annotation.left + annotation.width]
        # 保存裁剪后的图片
        # cv2.imencode(保存格式, 保存图片)[1].tofile(保存路径)
        # # 确保目录存在
        image_name = item['name'] + '.png'
        image_path = os.path.join('E:\\', 'output', 'media', request.user.username, item['group'], item['pic'], item['label'], image_name)
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        cv2.imencode('.png', cropped_image)[1].tofile(image_path)
        slice.delete()

    return JsonResponse({'code': 200, 'message': '导出成功'})

@csrf_exempt
def get_all_data(request):
    rada_data = 1
    pic_data = 1
    slice_data = 1
    annotation_data = 1

    data = {
        'rada_data': 1,
        'pic_data': 1,
        'slice_data': 1,
        'annotation_data': 1,
    }

    return JsonResponse({'code': 200, 'message': '成功', 'data': data})

@csrf_exempt
def get_person_data(request):
    id = request.user.id
    annotation_data = 1
    slice_data = 1

    data = {
        'annotation_data': 1,
        'slice_data': 1,
    }

    return JsonResponse({'code': 200, 'message': '成功', 'data': data})