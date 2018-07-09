from django.urls import path, re_path, include
from .views import OrgView,AddUserAskView,OrgHomeView,OrgCourseView,OrgDescView,OrgTeachersView,AddFavView
from .views import TeacherListView,TeacherDetaiView

app_name='org'
urlpatterns = [
    # 课程机构列表页
    path('list/', OrgView.as_view(), name='org_list'),
    path('add_ask/',AddUserAskView.as_view(),name="add_ask"),
    path('add_ask/<int:org_id>',OrgHomeView.as_view(),name="org_home"),  # 使用转换器获取参数
    path('course/<int:org_id>',OrgCourseView.as_view(),name="org_course"),
    path('desc/<int:org_id>', OrgDescView.as_view(), name="org_desc"),
    path('teachers/<int:org_id>',OrgTeachersView.as_view(),name="org_teachers"),
    # 机构收藏
    path('add_fav/', AddFavView.as_view(), name="add_fav"),
    # 讲师列表页
    path('teacher/list/', TeacherListView.as_view(), name="teacher_list"),
    # 讲师详情页
    path('teacher/detail/<int:dteacher_id>', TeacherDetaiView.as_view(), name="teacher_detail"),
]
