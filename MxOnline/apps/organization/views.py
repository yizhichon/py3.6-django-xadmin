from django.shortcuts import render
from django.views.generic import View
from django.shortcuts import render_to_response
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.db.models import Q
# Create your views here.

from .models import CourseOrg, CityDict, Teacher
from .forms import UserAskForm
from operation.models import UserFavorite
from courses.models import Course
from courses.models import Course


# 课程机构列表功能
class OrgView(View):
    '''
    课程机构列表功能
    '''

    def get(self, request):
        # 课程机构
        all_orgs = CourseOrg.objects.all()

        # 课程机构排名
        hot_orgs = all_orgs.order_by("-click_nums")[:3]

        # 城市
        all_citys = CityDict.objects.all()

        # 机构搜索
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_orgs = all_orgs.filter(
                Q(name__icontains=search_keywords) | Q(desc__icontains=search_keywords))

        # 取出筛选城市
        city_id = request.GET.get('city', '')
        if city_id:
            all_orgs = all_orgs.filter(city_id=int(city_id))

        # 类别赛选
        catgory = request.GET.get('ct', '')
        if catgory:
            all_orgs = all_orgs.filter(catgory=catgory)

        # 学习人数和课程数排序
        sort = request.GET.get('sort', '')
        if sort:
            if sort == "students":  # 学习人数
                all_orgs = all_orgs.order_by('-students')
            elif sort == "courses":  # 课程数
                all_orgs = all_orgs.order_by('-course_nums')

        org_name = all_orgs.count()
        # 对课程机构进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_orgs, 5, request=request)

        orgs = p.page(page)

        return render(request, 'org-list.html', {
            "all_orgs": orgs,
            "all_citys": all_citys,
            "org_count": org_name,
            "city_id": city_id,
            "catgory": catgory,
            "hot_orgs": hot_orgs,
            "sort": sort
        })


# 我要学习表单处理
class AddUserAskView(View):
    '''
    用户添加咨询
    '''

    def post(self, request):
        userask_form = UserAskForm(request.POST)
        if userask_form.is_valid():
            # ModelForm可以直接将表单数据提交到数据库并保存
            user_ask = userask_form.save(commit=True)
            return HttpResponse('{"status":"success"}', content_type="application/json")
        else:
            return HttpResponse('{"status":"fail","msg":"添加出错"}', content_type="application/json")


# 机构首页
class OrgHomeView(View):
    def get(self, request, org_id):
        current_page = "home"
        course_org = CourseOrg.objects.get(id=int(org_id))
        course_org.click_nums += 1
        course_org.save()

        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        all_courses = course_org.course_set.all()[:3]
        all_teachers = course_org.teacher_set.all()[1:2]
        return render(request, 'org-detail-homepage.html', {
            "all_courses": all_courses,
            "all_teachers": all_teachers,
            "course_org": course_org,
            "current_page": current_page,
            "has_fav": has_fav,
        })


# 机构课程列表页
class OrgCourseView(View):
    def get(self, request, org_id):
        current_page = "course"
        course_org = CourseOrg.objects.get(id=int(org_id))
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        all_courses = course_org.course_set.all()
        return render(request, 'org-detail-course.html', {
            "all_courses": all_courses,
            "course_org": course_org,
            "current_page": current_page,
            "has_fav": has_fav
        })


# 机构介绍
class OrgDescView(View):
    def get(self, request, org_id):
        current_page = "desc"
        course_org = CourseOrg.objects.get(id=int(org_id))
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        return render(request, 'org-detail-desc.html', {
            "course_org": course_org,
            "current_page": current_page,
            "has_fav": has_fav
        })


# 机构教师
class OrgTeachersView(View):
    def get(self, request, org_id):
        current_page = "teacher"
        course_org = CourseOrg.objects.get(id=int(org_id))
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        all_teachers = course_org.teacher_set.all()
        return render(request, 'org-detail-teachers.html', {
            "all_teachers": all_teachers,
            "course_org": course_org,
            "current_page": current_page,
            "has_fav": has_fav
        })


# 收藏,取消收藏
class AddFavView(View):
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
            # 取消收藏对数据库进行修改
            if int(fav_type) == 1:
                course = Course.objects.get(id=int(fav_id))
                course.fav_nums -= 1
                # 如果小于0则让他等于0写入数据库
                if course.fav_nums < 0:
                    course.fav_nums = 0
                course.save()
            elif int(fav_type) == 2:
                course_org = CourseOrg.objects.get(id=int(fav_id))
                course_org.fav_nums -= 1
                if course_org.fav_nums < 0:
                    course_org.fav_nums = 0
                course_org.save()
            elif int(fav_type) == 3:
                teacher = Teacher.objects.get(id=int(fav_id))
                teacher.fav_nums -= 1
                if teacher.fav_nums < 0:
                    teacher.fav_nums = 0
                teacher.save()
            return HttpResponse('{"status":"fail", "msg":"已取消收藏"}', content_type='application/json')
        else:
            user_fav = UserFavorite()
            if int(fav_id) > 0 and int(fav_type) > 0:
                user_fav.user = request.user
                user_fav.fav_id = int(fav_id)
                user_fav.fav_type = int(fav_type)
                user_fav.save()

                # 收藏对数据库进行修改
                if int(fav_type) == 1:
                    course = Course.objects.get(id=int(fav_id))
                    course.fav_nums += 1
                    course.save()
                elif int(fav_type) == 2:
                    course_org = CourseOrg.objects.get(id=int(fav_id))
                    course_org.fav_nums += 1
                    course_org.save()
                elif int(fav_type) == 3:
                    teacher = Teacher.objects.get(id=int(fav_id))
                    teacher.fav_nums += 1
                    teacher.save()

                return HttpResponse('{"status":"success", "msg":"已收藏"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"fail", "msg":"收藏出错"}', content_type='application/json')


# 讲师列表页
class TeacherListView(View):
    def get(self, request):
        all_teachers = Teacher.objects.all()

        # 讲师排名
        hot_teachers = all_teachers.order_by("-click_nums")[:5]

        # 讲师搜索
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_teachers = all_teachers.filter(
                Q(name__icontains=search_keywords) | Q(work_company__icontains=search_keywords) | Q(
                    work_position__icontains=search_keywords))

        # 讲师人气排序
        sort = request.GET.get('sort', '')
        if sort:
            if sort == "hot":  # 点击人数
                all_teachers = all_teachers.order_by('-click_nums')

        # 对课讲师进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_teachers, 5, request=request)

        teachers = p.page(page)
        return render(request, "teachers-list.html", {
            "all_teachers": teachers,
            "hot_teachers": hot_teachers,
            "sort": sort,
        })


class TeacherDetaiView(View):
    def get(self, request, dteacher_id):
        # 讲师信息
        teacher = Teacher.objects.get(id=int(dteacher_id))
        teacher.click_nums += 1
        teacher.save()
        # 所有课程
        all_courses = Course.objects.filter(tacher=teacher)
        # 讲师排名
        hot_teachers = Teacher.objects.all().order_by("-click_nums")[:4]

        # 教师收藏
        has_teacher_faved = False
        if UserFavorite.objects.filter(user=request.user, fav_type=3, fav_id=teacher.id):
            has_teacher_faved = True

        # 机构收藏
        has_org_faved = False
        if UserFavorite.objects.filter(user=request.user, fav_type=2, fav_id=teacher.org.id):
            has_org_faved = True

        return render(request, "teacher-detail.html", {
            "teacher": teacher,
            "all_courses": all_courses,
            "hot_teachers": hot_teachers,
            "has_teacher_faved": has_teacher_faved,
            "has_org_faved": has_org_faved
        })
