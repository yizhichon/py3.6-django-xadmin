from django.urls import path
from .views import UserinfoView, UploadImageView, UpdatePwdView, SendEmailCodeView
from .views import UpdateEmailView, MyCourseView, MyFavOrgView,MyFavTeacherView,MyFavCourseView
from .views import MymessageView

app_name = 'users'

urlpatterns = [
    # 用户信息
    path('info/', UserinfoView.as_view(), name='user_info'),
    # 个人中心用户头像修改
    path('image/upload/', UploadImageView.as_view(), name='image_upload'),
    # 用户个人中心修改密码
    path('update/pwd/', UpdatePwdView.as_view(), name='update_pwd'),
    # 用户个人中心发送邮箱验证码
    path('sendemail_code/', SendEmailCodeView.as_view(), name='sendemail_code'),
    # 用户个人中心修改邮箱验证码
    path('update_email/', UpdateEmailView.as_view(), name='update_email'),

    # 个人中心我的课程
    path('mycourse/', MyCourseView.as_view(), name='mycourse'),
    # 个人中心我的收藏(课程机构)
    path('myfav/org/', MyFavOrgView.as_view(), name='myfav_org'),
    # 个人中心我的收藏(授课讲师)
    path('myfav/teacher/', MyFavTeacherView.as_view(), name='myfav_teacher'),
    # 个人中心我的收藏(公开课)
    path('myfav/course/', MyFavCourseView.as_view(), name='myfav_course'),
    # 个人中心我消息
    path('mymessahe/', MymessageView.as_view(), name='mymessahe'),
]
