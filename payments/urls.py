# integration_app/urls.py

from django.urls import path
from . import views



app_name = 'payments'



urlpatterns = [
    path('send_b2c/', views.send_b2c_view, name='send_b2c'),
    # path('payments/approve-transaction/<str:tracking_id>/', views.approve_transaction_view, name='approve_transaction'),
    # other URLs
]
