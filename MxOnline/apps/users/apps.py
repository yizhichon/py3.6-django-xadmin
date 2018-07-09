from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'users'
    verbose_name = "用户信息" #设置左列表名字(需要__init__目录下配置)
