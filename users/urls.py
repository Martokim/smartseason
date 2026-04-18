from django.urls import paht 
from . import views 

app_name='users'

urlpatterns = [
    path('login/',views.login_view, name='login'),
    path('logout/',views.logout_view, name='logout'),
]