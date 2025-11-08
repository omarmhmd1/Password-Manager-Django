from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('addnew/', views.addnew, name='addnew'),
    path('view/<int:id>/', views.view_password, name='view_password'),
    path('delete/<int:id>/', views.delete_password, name='delete_password'),
    path('update/<int:id>/', views.update, name='update'),
    path('search/', views.search, name='search'),
]