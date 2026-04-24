from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('buy/', views.buy, name='buy'),
    path('about/', views.about, name='about'),
    path('detail/<int:plot_id>/', views.plot_detail, name='detail'),
    path('map/', views.map_view, name='map_view'),
    path('contact/', views.contact, name='contact'),
    path('login/', views.login_view, name='login'),
    path('sell/', views.sell, name='sell'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('delete/<int:id>/', views.delete_plot, name='delete_plot'),
    path('edit/<int:id>/', views.edit_plot, name='edit_plot'),
    path('wishlist/<int:id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('report/<int:plot_id>/', views.download_report, name='download_report'),
    path('logout/', views.logout_view, name='logout')


]
