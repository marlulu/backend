# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from colorfield.fields import ColorField
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.auth import get_user_model

from DjangoProject import settings

UserMode = get_user_model()

# Create your models here.

class Label(models.Model):
    title = models.CharField(max_length=120)
    color = models.CharField(max_length=120, blank=True, null=True)
    author = models.ForeignKey(get_user_model(), null=True, blank=True, editable=False, on_delete=models.CASCADE)

class StudyGroup(models.Model):
    title = models.CharField(max_length=100)
    source = models.CharField(max_length=100, blank=True, null=True)
    author = models.ForeignKey(get_user_model(), null=True, blank=True, editable=False, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)


class Notices(models.Model):
    description = models.CharField(max_length=300)
    type = models.CharField(max_length=120)
    status = models.CharField(max_length=120, default='系统消息')
    user = models.ForeignKey(get_user_model(), null=True, blank=True, editable=False, on_delete=models.CASCADE)

class Picture(models.Model):
    title = models.CharField(max_length=100, unique=True)
    create_at = models.DateTimeField(auto_now_add=True, null=True)
    picture_file = models.ImageField(upload_to='uploads/images/')
    annotation_num = models.IntegerField(default=0)
    study_group = models.ForeignKey(StudyGroup, on_delete=models.PROTECT, null=True)
    author = models.ForeignKey(get_user_model(), null=True, blank=True, editable=False, on_delete=models.CASCADE)
    is_confirm = models.BooleanField(default=True)


class Annotation(models.Model):
    picture = models.ForeignKey(Picture, on_delete=models.CASCADE)
    left = models.IntegerField(default=0)
    top = models.IntegerField(default=0)
    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
    annotator = models.CharField(max_length=50, default='')
    createdAt = models.DateTimeField(auto_now_add=True, null=True)
    aligned_label = ArrayField(models.TextField(), default=list, blank=True)
    align = models.IntegerField(default=0)
    confirm = models.IntegerField(default=0)
    target = models.CharField(max_length=50, default='')
    align_user = models.CharField(max_length=50, default='')
    label_id = models.IntegerField(default=0)
    label = models.CharField(max_length=50, default='')
    color = models.CharField(max_length=50, default='# 1D8CF8')

class PictureSlices(models.Model):
    name = models.CharField(max_length=120)
    pic = models.CharField(max_length=120, default='')
    label = models.CharField(max_length=120, default='')
    group = models.CharField(max_length=120, default='')
    create_at = models.DateTimeField(auto_now_add=True, null=True)
    annotation = models.ForeignKey(Annotation, on_delete=models.PROTECT, null=True)