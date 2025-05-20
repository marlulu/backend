from django.conf.urls.static import static
from django.urls import path

from DjangoProject import settings
from apps.apps.views import handle_study_group, get_study_groups, upload_image, get_images, handle_label, get_labels, \
    get_users, get_notices, delete_notices, check_image, delete_image, get_image, add_annotation, edit_annotation, \
    delete_annotations, get_annotations, confirm_annotations, auto_annotations, all_align, get_sclies, \
    export_slices, get_person_data, get_all_data

urlpatterns = [
    path('handle_label', handle_label, name="handle_label"),
    path('get_labels', get_labels, name="get_labels"),

    path('handle_study_group', handle_study_group, name="handle_study_group"),
    path('get_study_groups', get_study_groups, name="get_study_groups"),

    path('get_users', get_users, name="get_users"),

    path('get_notices', get_notices, name="get_notices"),
    path('delete_notices', delete_notices, name="delete_notices"),

    path('upload_image', upload_image, name="upload_image"),
    path('check_image', check_image, name="check_image"),
    path('delete_image', delete_image, name="delete_image"),
    path('get_images', get_images, name="get_images"),
    path('get_image', get_image, name="get_image"),

    path('add_annotation', add_annotation, name="add_annotation"),
    path('edit_annotation', edit_annotation, name="edit_annotation"),
    path('delete_annotations', delete_annotations, name="delete_annotations"),
    path('get_annotations', get_annotations, name="get_annotations"),
    path('confirm_annotations', confirm_annotations, name="confirm_annotations"),
    path('auto_annotations', auto_annotations, name="auto_annotations"),

    path('all_align', all_align, name="all_align"),

    path('get_sclies', get_sclies, name="get_sclies"),
    path('export_slices', export_slices, name="export_slices"),

    path('get_all_data', get_all_data, name="get_all_data"),
    path('get_person_data', get_person_data, name="get_person_data"),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)