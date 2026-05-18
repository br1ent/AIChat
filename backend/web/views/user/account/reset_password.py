from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response

class ResetPasswordView(APIView):
    def post(self, request):
        try:
            username = request.data.get('username').strip()
            password = request.data.get('password')
            confirm_password = request.data.get('confirmedPassword')

            if password is None:
                return Response({
                    "result": "密码不能为空!"
                })

            if password != confirm_password:
                return Response({
                    "result": "两次输入的密码不一致!"
                })

            user = User.objects.filter(username=username).first()
            if user is None:
                return Response({
                    "result": "用户不存在,请注册!"
                })

            user.set_password(password)
            user.save()
            return Response({
                "result": "success"
            })
        except:
            return Response({
                "result": "系统异常,请稍后重试!"
            })