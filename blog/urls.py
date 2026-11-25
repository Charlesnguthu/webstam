from django.urls import path
from . import views

app_name = "blog"
urlpatterns = [path("", views.index, name="index"), path("category/<slug:slug>/", views.index, name="category"), path("feed.xml", views.ArticleFeed(), name="feed"), path("<slug:slug>/", views.detail, name="detail")]
