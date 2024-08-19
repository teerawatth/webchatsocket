import json
import base64
import uuid
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from chatapp.models import Room, Message, Product

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.username = self.scope['url_route']['kwargs']['username']
        self.product_id = self.scope['url_route']['kwargs']['product_id']
        self.user = self.scope["user"]

        self.room_group_name = f'chat_{self.username}_{self.product_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get("message", "")
        image_data = text_data_json.get("image", None)
        username = text_data_json["username"]

        if image_data:
            format, imgstr = image_data.split(';base64,') 
            ext = format.split('/')[-1] 
            image_data = ContentFile(base64.b64decode(imgstr), name=f'{uuid.uuid4()}.{ext}')

        await self.save_message(message, image_data, username)

        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": "send_message",
                "message": message,
                "image": image_data.name if image_data else None,
                "username": username,
            }
        )
        
    async def send_message(self, event):
        message = event["message"]
        image = event["image"]
        username = event["username"]

        await self.send(text_data=json.dumps({
            "message": message,
            "image": image,
            "username": username
        }))
    
    @sync_to_async
    def save_message(self, message, image_data, username):
        user = User.objects.get(username=username)
        seller = User.objects.get(username=self.username)
        product = Product.objects.get(id=self.product_id)

        try:
            # ลองดึง Room โดยใช้เงื่อนไขทั้ง seller, customer และ product
            room = Room.objects.get(seller=seller, customer=user, product=product)
        except Room.DoesNotExist:
            # ถ้าไม่มี Room ที่ตรงเงื่อนไขทั้งหมด อาจลองดึงเฉพาะ seller และ product
            room = Room.objects.filter(seller=seller, product=product).first()
        except Room.MultipleObjectsReturned:
            # จัดการกรณีที่มีมากกว่าหนึ่ง Room ที่ตรงเงื่อนไข โดยเลือกอันแรก
            room = Room.objects.filter(seller=seller, customer=user, product=product).first()

        # สร้าง Message ใหม่
        message_instance = Message.objects.create(user=user, room=room, content=message)

        if image_data:
            message_instance.image = image_data
            message_instance.save()

        return message_instance
