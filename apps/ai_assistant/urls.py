from django.urls import path
from . import views

app_name = "ai"

urlpatterns = [
    path("", views.chat_page, name="chat"),
    path("api/chat/", views.chat_api, name="chat-api"),
    path("api/rebuild/", views.rebuild_knowledge_base, name="rebuild"),
    path("api/suggested/", views.suggested_questions, name="suggested"),
]
