from django.urls import path
from .views import home,about,feature,pricing

urlpatterns = [
    path("",home,name="home"),
    path("about/",about,name="about"),
    path("feature/",feature,name="features"),
    path("pricing/",pricing,name="pricing"),
]
