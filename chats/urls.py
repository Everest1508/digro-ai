from django.urls import path
from .views import chat_view,uuid_chat,chat_api
urlpatterns = [
    path('',chat_view,name='chat'),
    path('<str:uuid>/',uuid_chat,name="uuid_chat"),
    path('api/v1/',chat_api,name='chat_api'),
]
