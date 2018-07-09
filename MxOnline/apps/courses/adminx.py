import xadmin
from .models import Course, Lesson, Video, CourseResource, BannerCourse
from organization.models import CourseOrg


# 嵌套编辑
class LessonInline(object):
    model = Lesson
    extra = 0


# 嵌套编辑
class CourseResourceInline(object):
    model = CourseResource
    extra = 0


# 一个model注册2个管理页面
class CourseAdmin(object):
    list_display = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students', 'fav_nums', 'image', 'click_nums',
                    'add_time', 'get_zj_nums', 'go_to']
    search_fields = ['name', 'desc', 'detail', 'degree', 'students', 'fav_nums', 'image', 'click_nums']
    list_filter = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students', 'fav_nums', 'image', 'click_nums',
                   'add_time']
    ordering = ['-click_nums']  # 设置排序
    readonly_fields = ['click_nums']  # 设置只读
    list_editable = ['degree', 'desc']  # 可以直接在列表页进行编辑修改
    exclude = ['fav_nums']  # 设置不显示 不能与readonly_fields冲突
    inlines = [LessonInline, CourseResourceInline]  # 嵌套编辑 一个页面管理多个model,不能多层嵌套(嵌套完章节不能再章节里嵌套视频)
    refresh_times = [3, 5]  # 设置页面刷新时间 单位/秒
    # detail就是要显示为富文本的字段名
    style_fields = {"detail": "ueditor"}

    # 完成数据过滤
    def queryset(self):
        qs = super(CourseAdmin, self).queryset()
        qs = qs.filter(is_banner=False)
        return qs

    """
    重载models,保存之后从新更新
    保存课程的时候统计课程机构的课程数 
    当添加一门课程的时候，希望课程机构里面的课程数 +1"""

    def save_models(self):
        # 在保存课程的时候统计课程机构的课程数
        # obj实际是一个course对象
        obj = self.new_obj
        # 如果这里不保存，新增课程，统计的课程数会少一个
        obj.save()
        # 确定课程的课程机构存在。
        if obj.course_org is not None:
            # 找到添加的课程的课程机构
            course_org = obj.course_org
            # 课程机构的课程数量等于添加课程后的数量
            course_org.course_nums = Course.objects.filter(course_org=course_org).count()
            course_org.save()


# 一个model注册2个管理页面
class BannerCourseAdmin(object):
    list_display = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students', 'fav_nums', 'image', 'click_nums',
                    'add_time']
    search_fields = ['name', 'desc', 'detail', 'degree', 'students', 'fav_nums', 'image', 'click_nums']
    list_filter = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students', 'fav_nums', 'image', 'click_nums',
                   'add_time']
    ordering = ['-click_nums']  # 设置排序
    readonly_fields = ['click_nums']  # 设置只读
    exclude = ['fav_nums']  # 设置不显示 不能与readonly_fields冲突
    inlines = [LessonInline, CourseResourceInline]  # 嵌套编辑 一个页面管理多个模型,不能多层嵌套(嵌套完章节不能再章节里嵌套视频)

    # 完成数据过滤
    def queryset(self):
        qs = super(BannerCourseAdmin, self).queryset()
        qs = qs.filter(is_banner=True)
        return qs


class LessonAdmin(object):
    list_display = ['course', 'name', 'add_time']
    search_fields = ['course', 'name']
    list_filter = ['course__name', 'name', 'add_time']  # 外键需要加双下划线


class VideoAdmin(object):
    list_display = ['lesson', 'name', 'add_time']
    search_fields = ['lesson', 'name']
    list_filter = ['lesson', 'name', 'add_time']


class CourseResourceAdmin(object):
    list_display = ['course', 'name', 'download', 'add_time']
    search_fields = ['course', 'name', 'download']
    list_filter = ['course', 'name', 'download', 'add_time']


xadmin.site.register(Course, CourseAdmin)
xadmin.site.register(BannerCourse, BannerCourseAdmin)  # 一个model注册2个管理页面
xadmin.site.register(Lesson, LessonAdmin)
xadmin.site.register(Video, VideoAdmin)
xadmin.site.register(CourseResource, CourseResourceAdmin)
