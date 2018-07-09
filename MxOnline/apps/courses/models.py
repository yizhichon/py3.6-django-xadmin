from datetime import datetime

from DjangoUeditor.models import UEditorField

from django.db import models
from organization.models import CourseOrg, Teacher


class Course(models.Model):
    # 加外键必须加这2个属性null=True,blank=True,前提是后台已经有数据,可以为null,django2.0添加on_delete防止数据库数据不一样
    course_org = models.ForeignKey(CourseOrg, verbose_name="课程机构", null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, verbose_name="课程名")
    desc = models.CharField(max_length=300, verbose_name="课程描述")
    detail = UEditorField(verbose_name="课程详情", width=600, height=300, imagePath="courses/ueditor/",
                                           filePath="courses/ueditor/",default="")
    is_banner = models.BooleanField(default=False, verbose_name="是否轮播")
    tacher = models.ForeignKey(Teacher, verbose_name="讲师", null=True, blank=True, on_delete=models.CASCADE)
    degree = models.CharField(choices=(("cj", "初级"), ("zj", "中级"), ("gj", "高级")), max_length=2, verbose_name="难度")
    learn_times = models.IntegerField(default=0, verbose_name="学习时长(分钟数)")
    students = models.IntegerField(default=0, verbose_name="学习人数")
    fav_nums = models.IntegerField(default=0, verbose_name="收藏人数")
    image = models.ImageField(upload_to="courses/%Y/%m", verbose_name="封面图", max_length=100, null=True, blank=True)
    click_nums = models.IntegerField(default=0, verbose_name="点击数")
    category = models.CharField(default="后端开发", max_length=20, verbose_name="课程类别")
    tag = models.CharField(default="", verbose_name="课程标签", max_length=10)
    youneed_know = models.CharField(default="", max_length=300, verbose_name="课程须知")
    tacher_tell = models.CharField(default="", max_length=300, verbose_name="老师告诉你")

    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "课程"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def get_zj_nums(self):
        # 获取课程章节数
        return self.lesson_set.all().count()

    get_zj_nums.short_description = "章节数"  # 定义xadmin后台列显示名称

    def go_to(self):
        """xadmin后台自定义HTML代码"""
        from django.utils.safestring import mark_safe
        return mark_safe("<a href='http://www.projectsedu.com'>跳转</>")  # 设置A标签进行跳转

    go_to.short_description = "跳转"  # 定义xadmin后台列显示名称

    def get_learn_users(self):
        # 获取用户
        return self.usercourse_set.all()[:5]

    def get_course_lesson(self):
        # 获取课程所有章节
        return self.lesson_set.all()


class BannerCourse(Course):
    class Meta:
        verbose_name = "轮播课程"
        verbose_name_plural = verbose_name
        proxy = True  # 设置True不会生成一张表出来(一个model注册2个管理页面)


class Lesson(models.Model):
    course = models.ForeignKey(Course, verbose_name="课程", on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name="章节名")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "章节"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def get_lesson_video(self):
        # 获取章节视频
        return self.video_set.all()


class Video(models.Model):
    lesson = models.ForeignKey(Lesson, verbose_name="章节", on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name="视频名字")
    learn_times = models.IntegerField(default=0, verbose_name="学习时长(分钟数)")
    url = models.CharField(max_length=200, default="", verbose_name="访问地址")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "视频"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class CourseResource(models.Model):
    course = models.ForeignKey(Course, verbose_name="课程", on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name="名称")
    download = models.FileField(upload_to="course/resource/%Y/%m", verbose_name="资源文件", max_length=100)
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "课程资源"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
