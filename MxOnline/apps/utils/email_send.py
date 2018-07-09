from users.models import EmailVerifyRecord
from django.core.mail import send_mail
from MxOnline.settings import EMAIL_FROM

from random import Random


# 生成随机字符串
def random_str(randomlength=8):
    str = ''
    chars = 'QqAaZzWwSsXxEeDdCcRrFfVvTtGgBbYyHhNnUuJjMmIiKkOoLlPp0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str += chars[random.randint(0,length)]
    return str


# 邮箱发送
def send_register_email(email,send_type='register'):
    email_record = EmailVerifyRecord()

    if send_type != "update_email":
        code = random_str(16)
    else:
        code = random_str(4)
    email_record.code = code
    email_record.email = email
    email_record.send_type = send_type
    email_record.save()

    email_title = '' # 发送标题
    email_body = '' # 发送内内容

    if send_type == 'register':
        email_title = '幕学在线网注册激活链接'
        email_body = '请点击下面的链接激活你的账号:http://127.0.0.1:8000/active/{0}'.format(code)
        send_status = send_mail(email_title,email_body,EMAIL_FROM,[email])
        if send_status:
            pass
    elif send_type == 'forget':
        email_title = '幕学在线网密码重置链接'
        email_body = '请点击下面的链接重置你的账号:http://127.0.0.1:8000/reset/{0}'.format(code)
        send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
        if send_status:
            pass
    elif send_type == "update_email":
        email_title = '幕学在线幕学邮箱修改验证码'
        email_body = '你的邮箱验证码为:{0}'.format(code)
        send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
        if send_status:
            pass


