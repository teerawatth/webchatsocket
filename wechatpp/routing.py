from django.urls import path , include,re_path
from .consumers import ChatConsumer


websocket_urlpatterns = [
    # path('ws/chat/<int:room_id>/<str:username>/<int:product_id>/', ChatConsumer.as_asgi()),
    # re_path(r'ws/chat/(?P<room_id>\d+)/(?P<username>\w+)/(?P<product_id>\d+)/$', ChatConsumer.as_asgi()),
    re_path(r'ws/chat/(?P<slug>[-\w]+)/(?P<username>\w+)/(?P<product_id>\d+)/$', ChatConsumer.as_asgi()),

]
