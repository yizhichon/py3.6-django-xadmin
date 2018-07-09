from django import forms
from captcha.fields import CaptchaField

from .models import UserProfile


# 判断登录form表达逻辑继承django定义好的froms表单
class LoginForm(forms.Form):
    username = forms.CharField(required=True,error_messages={"required": "邮箱不能为空!"})  # required=True必填字段
    password = forms.CharField(required=True, min_length=5,error_messages={"required": "密码不能为空并且不能小于5位数!"})


# 判断注册form表达逻辑继承django定义好的froms表单
class RegisterForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, min_length=5)
    captcha = CaptchaField(error_messages={'invalid': '验证码错误'})

# 找回密码form表单,验证码
class ForgetForm(forms.Form):
    email = forms.EmailField(required=True)
    captcha = CaptchaField(error_messages={'invalid': '验证码错误'})


# 修改密码表单
class ModifyPwdForm(forms.Form):
    password1 = forms.CharField(required=True, min_length=5)
    password2 = forms.CharField(required=True, min_length=5)

# 个人中心处理文件上传,views需要传2个参数
class UploadImageForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['image']

# 个人中心修改表单信息
class UserInfoForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["nick_name","gender","birday","address","mobile"]