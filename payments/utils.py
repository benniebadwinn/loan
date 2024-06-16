# utils.py

from intasend import APIService
from django.conf import settings
from .models import Transaction

def send_b2c_transaction(amount, recipient_phone):
    token = settings.TASSEND_API_TOKEN
    publishable_key = settings.TASSEND_PUBLISHABLE_KEY
    
    try:
        service = APIService(token=token, publishable_key=publishable_key, test=True)
        
        response = service.payouts.mobile(
            recipients=[{
                "phone_number": recipient_phone,
                "currency": "KES",
                "amount": float(amount)
            }]
        )
        
        # Assuming API response provides transaction ID and status
        transaction = Transaction.objects.create(
            amount=amount,
            recipient_phone=recipient_phone,
            transaction_id=response.get('transaction_id'),
            status=response.get('status', 'Pending')
        )
        
        return transaction
    except Exception as e:
        print(f"Error sending B2C transaction: {e}")
        return None
