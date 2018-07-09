from django.urls import reverse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.views.generic.base import View
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
import json
# Create your views here.

from .models import UserProfile, EmailVerifyRecord
from .forms import LoginForm, RegisterForm, ForgetForm, ModifyPwdForm, UploadImageForm, UserInfoForm
from utils.email_send import send_register_email
from utils.mixin_utils import LoginRequiredMixin
from operation.models import UserCourse, UserFavorite, UserMessage
from organization.models import CourseOrg, Teacher
from courses.models import Course
from .models import Banner

from pure_pagination import Paginator, EmptyPage, PageNotAnInteger


# 重载authenticate,默认username=user_name,password=pass_word
class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(Q(username=username) | Q(email=username))  # 设置并集登录查询,切吧邮箱设为加入登录条件
            if user.check_password(password):  # django默认明文,设置方法给他加密
                return user
        except Exception as e:
            return None


class LogoutView(View):
    """
    用户退出登录
    """

    def get(self, request):
        logout(request)

        return HttpResponseRedirect(reverse("index"))


# 登录逻辑(使用继承类方法) #更推荐
class LoginView(View):
    # 使用get方法直接调用get的方法使用post直接调用post方法
    def get(self, request):
        return render(request, "login.html", {})

    def post(self, request):
        login_form = LoginForm(request.POST)  # 传递过来是字典
        if login_form.is_valid():  # 验证froms是否成功
            user_name = request.POST.get("username", "")
            pass_word = request.POST.get("password", "")
            user = authenticate(username=user_name, password=pass_word)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse("index"))
                else:
                    return render(request, "login.html", {'msg': '用户名未激活!'})
            else:
                return render(request, "login.html", {'msg': '用户名或密码错误!'})
        else:
            return render(request, "login.html", {'login_form': login_form})




# 登录逻辑(使用函数方法)
# def user_login(request):
#     if request.method == "POST":
#         user_name = request.POST.get("username", "")
#         pass_word = request.POST.get("password", "")
#         user = authenticate(username=user_name, password=pass_word)
#         if user is not None:
#             login(request, user)
#             return render(request, "index.html")
#         else:
#             return render(request, "login.html", {'msg': '用户名或密码错误!'})
#     elif request.method == "GET":
#         return render(request, "login.html", {})


# 注册逻辑

# 注册逻辑
# 注册账号
class RegisterView(View):
    def get(self, request):
        register_form = RegisterForm()
        return render(request, 'register.html', {'register_form': register_form})

    def post(self, request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user_name = request.POST.get("email", "")
            if UserProfile.objects.filter(email=user_name):
                return render(request, 'register.html', {'register_form': register_form, 'msg': '邮箱已注册'})
            pass_word = request.POST.get("password", "")
            user_profile = UserProfile()
            user_profile.username = user_name
            user_profile.email = user_name
            user_profile.is_active = False
            user_profile.password = make_password(pass_word)
            user_profile.save()

            # 写入欢迎注册消息
            user_message = UserMessage()
            user_message.user = user_profile.id
            user_message.message = "欢迎注册幕学在线网"
            user_message.save()

            # 调用utils.email_send发送邮件
            send_register_email(user_name, 'register')
            return render(request, "send_success.html", )
        else:
            return render(request, 'register.html', {'register_form': register_form})


# 邮箱点击激活链接吧is_active设为True(激活)
class AciveUserView(View):
    def get(self, request, active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email = record.email
                user = UserProfile.objects.get(email=email)
                user.is_active = True
                user.save()
        else:
            return render(request, 'actice_fail.html')
        return render(request, 'login.html')


# 找回密码逻辑
class ForgetPwdView(View):
    def get(self, request):
        forget_form = ForgetForm()
        return render(request, 'forgetpwd.html', {'forget_form': forget_form})

    def post(self, request):
        forget_form = ForgetForm(request.POST)
        if forget_form.is_valid():
            email = request.POST.get('email')
            # 调用utils.email_send发送邮件
            send_register_email(email, 'forget')
            return render(request, 'send_success.html')
        else:
            return render(request, 'forgetpwd.html', {'forget_form': forget_form})


# 点击邮箱链接重置密码
class ResetView(View):
    def get(self, request, active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email = record.email
                return render(request, 'password_reset.html', {'email': email})
        else:
            return render(request, 'actice_fail.html')
        return render(request, 'login.html')


# 重置密码因为点击邮箱链接需要传参post不需要传参所有重新定义一个类
class ModifPwdView(View):
    """
    修改用户密码
    """

    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get('password1', '')
            pwd2 = request.POST.get('password2', '')
            email = request.POST.get('email', '')
            if pwd1 != pwd2:
                return render(request, 'password_reset.html', {'email': email, 'msg': '密码不一致'})
            user = UserProfile.objects.get(email=email)
            user.password = make_password(pwd2)
            user.save()
            return render(request, 'login.html')
        else:
            email = request.POST.get('email', '')
            return render(request, 'password_reset.html', {'email': email, 'modify_form': modify_form})


"""
个人中心View
"""


class UserinfoView(LoginRequiredMixin, View):
    """
    用户个人信息
    """

    def get(self, request):
        return render(request, "usercenter-info.html", {

        })

    """
    用户信息修改
    """

    def post(self, request):
        user_info_form = UserInfoForm(request.POST, instance=request.user)  # 修改多加字段instance=request.user 否则会增加一段
        if user_info_form.is_valid():
            user_info_form.save()
            return HttpResponse('{"status":"success"}', content_type="application/json")
        else:
            return HttpResponse(json.dumps(user_info_form.errors), content_type="application/json")


class UploadImageView(LoginRequiredMixin, View):
    """
    用户修改头像
    """

    def post(self, request):
        image_form = UploadImageForm(request.POST, request.FILES,
                                     instance=request.user)  # 文件上传至request.FILES,用户上传的文件保存到当面form对象里来使用
        if image_form.is_valid():
            image_form.save()
            return HttpResponse('{"status":"success"}', content_type="application/json")
        else:
            return HttpResponse('{"status":"fail"}', content_type="application/json")


class UpdatePwdView(LoginRequiredMixin, View):
    """
    个人中心修改密码
    """

    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get('password1', '')
            pwd2 = request.POST.get('password2', '')
            if pwd1 != pwd2:
                return HttpResponse('{"status":"fail","msg":"密码不一致！"}', content_type="application/json")
            user = request.user
            user.password = make_password(pwd2)
            user.save()
            return HttpResponse('{"status":"success"}', content_type="application/json")
        else:
            return HttpResponse(json.dumps(modify_form.errors), content_type="application/json")


class SendEmailCodeView(LoginRequiredMixin, View):
    """
    个人中心发送邮箱验证码
    """

    def get(self, request):
        email = request.GET.get('email', '')
        if UserProfile.objects.filter(email=email):
            return HttpResponse('{"email":"邮箱已存在,请修改!"}', content_type="application/json")
        # 调用utils.email_send发送邮件
        send_register_email(email, 'update_email')
        return HttpResponse('{"status":"success"}', content_type="application/json")


class UpdateEmailView(LoginRequiredMixin, View):
    """
    个人中心修改邮箱
    """

    def post(self, request):
        email = request.POST.get('email', '')
        code = request.POST.get('code', '')
        existed_records = EmailVerifyRecord.objects.filter(email=email, code=code, send_type="update_email")
        if existed_records:
            user = request.user
            user.email = email
            user.save()
            return HttpResponse('{"status":"success"}', content_type="application/json")
        else:
            return HttpResponse('{"email":"验证码出错!"}', content_type="application/json")


class MyCourseView(LoginRequiredMixin, View):
    """
    个人中心我的课程
    """

    def get(self, request):
        user_courses = UserCourse.objects.filter(user=request.user)
        return render(request, 'usercenter-mycourse.html', {
            "user_courses": user_courses
        })


class MyFavOrgView(LoginRequiredMixin, View):
    """
    个人中心我的收藏(课程机构)
    """

    def get(self, request):
        org_list = []
        fav_orgs = UserFavorite.objects.filter(user=request.user, fav_type=2)
        for fav_org in fav_orgs:
            org_id = fav_org.fav_id
            org = CourseOrg.objects.get(id=org_id)
            org_list.append(org)
        return render(request, 'usercenter-fav-org.html', {
            "org_list": org_list
        })


class MyFavTeacherView(LoginRequiredMixin, View):
    """
    个人中心我的收藏(授课讲师)
    """

    def get(self, request):
        teacher_list = []
        fav_teachers = UserFavorite.objects.filter(user=request.user, fav_type=3)
        for fav_teacher in fav_teachers:
            teacher_id = fav_teacher.fav_id
            teacher = Teacher.objects.get(id=teacher_id)
            teacher_list.append(teacher)
        return render(request, 'usercenter-fav-teacher.html', {
            "teacher_list": teacher_list
        })


class MyFavCourseView(LoginRequiredMixin, View):
    """
    个人中心我的收藏(公开课)
    """

    def get(self, request):
        course_list = []
        fav_courses = UserFavorite.objects.filter(user=request.user, fav_type=1)
        for fav_course in fav_courses:
            course_id = fav_course.fav_id
            course = Course.objects.get(id=course_id)
            course_list.append(course)
        return render(request, 'usercenter-fav-course.html', {
            "course_list": course_list
        })


class MymessageView(LoginRequiredMixin, View):
    """
    个人中心我的消息
    """

    def get(self, request):
        all_messages = UserMessage.objects.filter(user=request.user.id)

        # 用户进入个人消息清空未读消息记录
        all_unread_messages = UserMessage.objects.filter(user=request.user.id, has_read=False)
        for unread_message in all_unread_messages:
            unread_message.has_read = True
            unread_message.save()

        # 对个人消息进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_messages, 5, request=request)

        messages = p.page(page)

        return render(request, 'usercenter-message.html', {
            "messages": messages
        })


# 处理首页
class IndexView(View):
    def get(self, request):
        # 取出轮播图
        all_banners = Banner.objects.all().order_by('index')
        courses = Course.objects.filter(is_banner=False)[:6]
        banner_courses = Course.objects.filter(is_banner=True)[:3]
        course_orgs = CourseOrg.objects.all()[:15]

        return render(request, 'index.html', {
            "all_banners": all_banners,
            "courses": courses,
            "banner_courses": banner_courses,
            "course_orgs": course_orgs
        })


# 全局 404 处理函数
def page_not_found(request):
    response = render_to_response('404.html', {})
    response.status_code = 404
    return response


# 全局 500 处理函数
def page_error(request):
    response = render_to_response('500.html', {})
    response.status_code = 500
    return response
