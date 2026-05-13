from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from web.models.friend import Message


class GetHistoryView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            last_message_id = int(request.query_params["last_message_id"])
            friend_id = int(request.query_params["friend_id"])
            queryset = Message.user_message.filter(friend_id=friend_id, friend__me__user=request.user)
            if last_message_id > 0:
                queryset = queryset.filter(pk__lt=last_message_id)

            messages_raw = queryset.order_by("-id")[:10]
            messages = []
            for m in messages_raw:
                message.append({
                    "id": m.id,
                    "user_message": m.user_message,
                    "output": m.output,
                })
            return Response({
                "result": "success",
                "messages": messages,
            })
        except:
            return Response({
                "result": "系统出错了,请稍后再试!"
            })