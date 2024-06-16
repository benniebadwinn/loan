# from .views import review_create
from loans import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views


app_name = 'loans'

import random
import string

# Function to generate a random alphanumeric string of given length
def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

urlpatterns = [
   
   

   
    path('list/', views.loan_list, name='loan_list'),
    path(generate_random_string(100) + '/', views.request_loan, name='request_loan'),
    path('', views.loan_application, name='loan_application'),
    path('lend-loan/', views.admin_lend_loan, name='admin_lend_loan'),
    path('ajax/get-user-info/', views.get_user_info, name='get_user_info'),
    
    
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


