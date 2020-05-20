from django.conf.urls import url
from django.urls import path, re_path
from . import views
from django.views.static import serve

app_name = 'articles'
urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_method, name='login'),
    path('logout/', views.logout_method, name='logout'),
    path('register/', views.register, name='register'),
    path('myprofile/', views.my_profile, name='my_profile'),
    url(r'^confirmation/(?P<name>[-\w]+)/', views.confirmation, name="confirmation"),
    path('<int:article_id>/', views.show_article, name='article'),
    path('<int:article_id>/leave_comment/', views.leave_comment, name='leave_comment'),
    path('<str:type_of_article>/', views.articles_list, name='articles_list')
]
