from django.urls import path,include, re_path


from . import views

urlpatterns = [
    path('', views.cdv_index, name='cdv_index'),
    path('submit', views.submit, name='cdv_submit'),

#
]
