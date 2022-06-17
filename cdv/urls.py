from django.urls import path,include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

from . import views



urlpatterns = [
    path('', views.cdv_index, name='cdv_index'),
    path('submit', views.submit, name='cdv_submit'),
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
