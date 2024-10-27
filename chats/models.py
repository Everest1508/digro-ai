from django.db import models
from django.contrib.auth.models import User
import uuid

class Chat(models.Model):
    name = models.CharField(max_length=50,null=True,blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat {self.uuid} - {self.user.username} at {self.created_at}"

class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    is_image = models.BooleanField(default=False)
    image = models.ImageField(upload_to='images/',null=True,blank=True)
    sender = models.CharField(max_length=50)  # 'user' or 'ai'
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message by {self.sender} at {self.created_at}"
