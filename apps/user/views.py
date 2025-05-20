import os

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, QueryDict
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import json


# 仅用于开发环境，生产环境建议使用Django的CSRF保护机制
@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            username = data.get('username')
            password = data.get('password')
            email = data.get('email')

            if User.objects.filter(username=username).exists():
                return JsonResponse({'success': False, 'message': '用户名已存在'}, status=400)

            user = User.objects.create_user(username=username, password=password, email=email)
            return JsonResponse({'success': True, 'message': '注册成功'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

@csrf_exempt
def login_user(request):
    try:
        if request.method == 'POST':
            if request.user.is_authenticated:
                return JsonResponse({'code': 200, 'message': '已经登陆'}, status=200)

            data = json.loads(request.body.decode('utf-8'))
            username = data.get('username')
            password = data.get('password')

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                user = request.user
                serializer_data = {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
                return JsonResponse({'code': 200, 'message': '登录成功', 'data': serializer_data}, status=200)
            else:
                return JsonResponse({'code': 400, 'message': '用户名或密码错误'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@csrf_exempt
def get_user_info(request):
    user = request.user
    if request.method == 'GET':
        serializer_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'date_joined': user.date_joined,
        }
        return JsonResponse({
            'code': 200,
            'data': serializer_data  # 可选：检查用户状态
        })
@csrf_exempt
def logout_user(request):
    logout(request)
    return JsonResponse({'code': 200, 'message': '已退出登录'})



@csrf_exempt
def get_session_info(request):
    session_id = request.COOKIES.get('sessionid')
    return JsonResponse({
        'code': 200,
        'token': session_id,
        'is_authenticated': request.user.is_authenticated,
        'is_superuser': request.user.is_superuser,
        'username': request.user.username,
        'id': request.user.id,
    })


@csrf_exempt
def get_users(request):
    if request.user.is_superuser:
        groups = User.objects.all().order_by('id')
        data = list(groups.values())
        return JsonResponse({'code': 200, 'message': 'success', 'data': data})
    else:
        groups = User.objects.filter(id=request.user.id)
        data = list(groups.values())
        return JsonResponse({'code': 200, 'message': 'success', 'data': data})