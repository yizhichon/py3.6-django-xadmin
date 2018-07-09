from django.shortcuts import render, HttpResponse
from django.views.generic import View
from django.db.models import Q

from .models import Course, CourseResource, Video
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

from operation.models import UserFavorite, CourseComments, UserCourse
from utils.mixin_utils import LoginRequiredMixin


# Create your views here.

# 课程列表页
class CourseListView(View):
    def get(self, request):
        all_courses = Course.objects.all().order_by("-add_time")

        hot_courses = Course.objects.all().order_by("-click_nums")[:3]

        # 课程搜索
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_courses = all_courses.filter(
                Q(name__icontains=search_keywords) | Q(desc__icontains=search_keywords) | Q(
                    detail__icontains=search_keywords))

        # 课程排序
        sort = request.GET.get('sort', '')
        if sort:
            if sort == "students":  # 学习人数
                all_courses = all_courses.order_by('-students')
            elif sort == "hot":  # 点击人数
                all_courses = all_courses.order_by('-click_nums')

        # 对课程进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_courses, 6, request=request)

        courses = p.page(page)

        return render(request, 'course-list.html', {
            "all_courses": courses,
            "sort": sort,
            "hot_courses": hot_courses
        })


# 课程详情页
class CourseDetailView(View):
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        # 增加课程点击数
        course.click_nums += 1
        course.save()

        has_fav_course = False
        has_fav_org = False

        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course.id, fav_type=1):
                has_fav_course = True
            if UserFavorite.objects.filter(user=request.user, fav_id=course.course_org.id, fav_type=2):
                has_fav_org = True

        tag = course.tag
        if tag:
            relate_coures = Course.objects.filter(tag=tag)[:1]
        else:
            relate_coures = []

        return render(request, 'course-detail.html', {
            "course": course,
            "relate_coures": relate_coures,
            "has_fav_course": has_fav_course,
            "has_fav_org": has_fav_org
        })

    """
    用户收藏和取消收藏
    """

    def post(self, request):
        fav_id = request.POST.get('fav_id', 0)  # 防止后边int(fav_id)时出错
        fav_type = request.POST.get('fav_type', 0)  # 防止int(fav_type)出错

        if not request.user.is_authenticated:
            # 未登录时返回json提示未登录，跳转到登录页面是在ajax中做的
            return HttpResponse('{"status":"fail", "msg":"用户未登录"}', content_type='application/json')

        exist_record = UserFavorite.objects.filter(user=request.user, fav_id=int(fav_id), fav_type=int(fav_type))
        if exist_record:
            # 如果记录已经存在，表示用户取消收藏
            exist_record.delete()
            return HttpResponse('{"status":"fail", "msg":"已取消收藏"}', content_type='application/json')
        else:
            user_fav = UserFavorite()
            if int(fav_id) > 0 and int(fav_type) > 0:
                user_fav.user = request.user
                user_fav.fav_id = int(fav_id)
                user_fav.fav_type = int(fav_type)
                user_fav.save()
                return HttpResponse('{"status":"success", "msg":"已收藏"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"fail", "msg":"收藏出错"}', content_type='application/json')


# 课程章节信息
class CourseInfoView(LoginRequiredMixin, View):
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        course.students += 1
        course.save()


        # 查询用户是否已经关联了该课程
        user_cousers = UserCourse.objects.filter(user=request.user, course=course)
        if not user_cousers:
            user_couse = UserCourse(user=request.user, course=course)
            user_couse.save()

        # 获取所有学习该课程的user
        user_courses = UserCourse.objects.filter(course=course)
        user_ids = [user_course.user.id for user_course in user_courses]
        # 获取所有学习该课程的user学习的课程
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        # 取出所有课程id
        course_ids = [user_course.course.id for user_course in all_user_courses]
        # 获取学过该用户学过其他的所有课程
        relate_courses = Course.objects.filter(id__in=course_ids).order_by('-click_nums')[:5]

        all_resources = CourseResource.objects.filter(course=course)


        return render(request, 'course-video.html', {
            "course": course,
            "course_resources": all_resources,
            "relate_courses": relate_courses
        })


# 课程评论
class CourseCommentView(LoginRequiredMixin, View):
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))

        # 查询用户是否已经关联了该课程
        user_courses = UserCourse.objects.filter(user=request.user, course=course)
        if not user_courses:
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()

        """课程相关推荐"""
        # 取出用户和课程之间的关系
        user_cousers = UserCourse.objects.filter(course=course)
        # 提取出所有的用户id
        user_ids = [user_couser.user.id for user_couser in user_cousers]
        # 取出所有学过该课程的用户
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        # 取出所有课程Id
        course_ids = [user_couser.course.id for user_couser in all_user_courses]
        # 获取学过该用户学过其他的所有课程，对点击量进行排序
        relate_courses = Course.objects.filter(id__in=course_ids).order_by("-click_nums")[:5]

        course_resources = CourseResource.objects.filter(course=course)
        all_comments = CourseComments.objects.all()
        return render(request, 'course-comment.html', {
            "course": course,
            "course_resources": course_resources,
            "all_comments": all_comments,
            "relate_courses": relate_courses
        })


# 用户添加课程评论
class AddComentsView(View):

    def post(self, request):
        if not request.user.is_authenticated:
            # 判断用户登录状态
            return HttpResponse('{"status":"fail", "msg":"用户未登录"}', content_type='application/json')
        course_id = request.POST.get("course_id", 0)
        comments = request.POST.get("comments", "")
        if int(course_id) > 0 and comments:
            course_comments = CourseComments()
            course = Course.objects.get(id=int(course_id))
            course_comments.course = course
            course_comments.comments = comments
            course_comments.user = request.user
            course_comments.save()
            return HttpResponse('{"status":"success", "msg":"添加成功"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail", "msg":"添加失败"}', content_type='application/json')
