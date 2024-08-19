from django.urls import path

from . import views


urlpatterns = [
    path('chat/<slug:slug>/<str:username>/<int:product_id>/', views.room, name='room'),
    path('', views.product_list, name='product_list'),  # หน้าแรก: แสดงรายการสินค้า
    path('add/', views.product_add, name='product_add'),  # หน้าสำหรับเพิ่มสิ
    path('chats/', views.chat_list, name='chat_list'),
    path('create-or-redirect-room/<int:product_id>/', views.create_or_redirect_room, name='create_or_redirect_room'),



    path('register/', views.register, name='register'),  # หน้าสมัครสมาชิก
    path('login/', views.login_view, name='login'),  # หน้าล็อกอิน
    path('logout/', views.logout_view, name='logout'), 
]