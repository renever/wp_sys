# - * - coding:utf-8 - * -
#临时修改密码的而外接口
#~/owl/owl/auth/urls.py
url(r'^findpwd2/$', 'auth_findpwd2', name='auth_findpwd2'),

#~/owl/owl/auth/views.py
@authenticated_redirect
def auth_findpwd2(request):
    if request.method == "GET":
        email=request.GET.get('email')
        password=request.GET.get('password')
        print email
        print password

        from django.http import HttpResponse

        user = User.objects.get(email=email)

        kw = dict(id=user.id, password=password)
        user.set_password(password)
        user.save()
        response = doodoll.users.update_password(**kw)
        print response.state

        result_str = "Success! %s" % response.state
        return HttpResponse(result_str)

