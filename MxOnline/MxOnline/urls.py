"""MxOnline URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
import xadmin
from django.views.generic import TemplateView
from .settings import MEDIA_ROOT #,STATIC_ROOT

from django.views.static import serve  # 配置图片显示
from users.views import LoginView, RegisterView, AciveUserView, ForgetPwdView, ResetView, ModifPwdView,LogoutView,IndexView



urlpatterns = [
    path('xadmin/', xadmin.site.urls),
    path('', IndexView.as_view(), name="index"),
    path('login/', LoginView.as_view(), name="login"),  # 调用函数不加括号,调用类需加括号 .as_view()
    path('logout/', LogoutView.as_view(), name="logout"),  # 退出登录
    path('register/', RegisterView.as_view(), name="register"),
    path('captcha/', include('captcha.urls')),
    path('active/<str:active_code>/', AciveUserView.as_view(), name='user_active'),
    path('forget/', ForgetPwdView.as_view(), name='forget_pwd'),
    path('reset/<str:active_code>/', ResetView.as_view(), name='reset_pwd'),
    path('modify_pwd/', ModifPwdView.as_view(), name='modify_pwd'),
    # include到organization的urls.py # 课程机构url配置
    path('org/', include('organization.urls', namespace='org')),
    # include到courses的urls.py # 课程相关url配置
    path('course/', include('courses.urls', namespace='course')),
    # 正则配置上传文件的访问处理
    re_path(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),
    # 生产环境手动配置静态文件的访问处理
    # re_path(r'^static/(?P<path>.*)$', serve, {"document_root": STATIC_ROOT}),
    # 个人中心url配置
    path('users/', include('users.urls', namespace='users')),
    # 副文本相关url
    path('ueditor/',include('DjangoUeditor.urls')),

]

# 全局404页面配置（django会自动调用这个变量）
hander404 = 'users.views.page_not_found'
# 全局500页面配置（django会自动调用这个变量）
hander500 = 'users.views.page_error'