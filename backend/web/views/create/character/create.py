from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.character import Character, Voice
from web.models.user import UserProfile


class CreateCharacterView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            user = request.user
            user_profile = UserProfile.objects.get(user=user)

            name = request.data.get('name').strip()
            voice_id = request.data.get('voice_id')
            profile = request.data.get('profile').strip()[:100000]
            photo = request.data.get('photo', None)
            background_image = request.data.get('background_image', None)

            if not name:
                return Response({
                    "result": "角色名字不能为空!"
                })

            if not profile:
                return Response({
                    "result": "角色简介不能为空!"
                })

            if not photo:
                return Response({
                    "result": "角色头像不能为空!"
                })

            if not background_image:
                return Response({
                    "result": "聊天背景不能为空!"
                })

            voice = Voice.objects.get(id=voice_id)

            Character.objects.create(
                author=user_profile,
                name=name,
                voice=voice,
                profile=profile,
                background_image=background_image,
                photo=photo,
            )

            return Response({
                "result": "success"
            })

        except:
            return Response({
                "result": "系统错误,请稍后再试!"
            })