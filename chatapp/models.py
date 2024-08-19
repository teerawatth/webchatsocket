from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

class Room(models.Model):
    name = models.CharField(max_length=20)
    slug = models.SlugField(max_length=100, unique=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    seller = models.ForeignKey(User, related_name='seller_rooms', on_delete=models.CASCADE, null=True, blank=True)
    customer = models.ForeignKey(User, related_name='customer_rooms', on_delete=models.CASCADE, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f'chat-about-{self.product.name}-between-{self.seller.username}-and-{self.customer.username}')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Room: {self.slug} | Product: {self.product.name}"


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True)  # เปลี่ยนเป็น blank=True เพื่อให้รองรับการส่งข้อความหรือภาพอย่างเดียว
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='chat_images/', null=True, blank=True)  # เพิ่มฟิลด์สำหรับบันทึกภาพ
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.user.username} in room {self.room.name}"
