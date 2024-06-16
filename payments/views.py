from django.shortcuts import render
from django.conf import settings
from decimal import Decimal
from .forms import B2CTransactionForm
from intasend import APIService
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render, redirect


# Import necessary modules
from django.shortcuts import render
from django.conf import settings
from intasend import APIService
from .forms import B2CTransactionForm  # Assuming B2CTransactionForm is defined in forms.py




# def send_b2c_view(request):
#     if request.method == 'POST':
#         form = B2CTransactionForm(request.POST)
#         if form.is_valid():
#             amount = float(form.cleaned_data['amount'])  # Convert Decimal to float
#             recipient_name = form.cleaned_data['recipient_name']
#             recipient_phone = form.cleaned_data['recipient_phone']
#             narrative = form.cleaned_data['narrative']

#             token = settings.INTASEND_API_TOKEN
#             publishable_key = settings.INTASEND_PUBLISHABLE_KEY
            
#             # Initialize APIService
#             service = APIService(token=token, publishable_key=publishable_key, test=True)  # Set test=True for sandbox

#             # Prepare transaction details
#             transactions = [
#                 {'name': recipient_name, 'account': recipient_phone, 'amount': amount, 'narrative': narrative}
#             ]

#             try:
#                 # Initiate M-Pesa B2C transaction
#                 response = service.transfer.mpesa(currency='KES', transactions=transactions)
#                 print("API Response:", response)

#                 # Check if the response has a field indicating it needs approval
#                 requires_approval = response.get('status') == 'Preview and approve'
#                 tracking_id = response.get('tracking_id')

#                 if not tracking_id:
#                     raise ValueError("Tracking ID not returned by API")

#                 print(f"Tracking ID: {tracking_id}")

#                 if requires_approval:
#                     # Approve the transaction
#                     approved_response = service.transfer.approve(response)
#                     print("Approved Response:", approved_response)
#                 else:
#                     approved_response = "No approval required"

#                 # Assuming you want to fetch some data related to the approved transaction
#                 transaction_info = {
#                     'tracking_id': tracking_id,
#                     'recipient_name': recipient_name,
#                     'recipient_phone': recipient_phone,
#                     'amount': amount,
#                     'narrative': narrative,
#                     'approved_response': approved_response,
#                 }

#                 # Render the transaction details page
#                 return render(request, 'transaction_details.html', transaction_info)

#             except Exception as e:
#                 error_message = str(e)
#                 print("Error sending B2C transaction:", error_message)
#                 return render(request, 'error.html', {'error': error_message})
#         else:
#             # Form is not valid, render the form again with validation errors
#             return render(request, 'payment_form.html', {'form': form})

#     else:
#         # GET request, render the empty form
#         form = B2CTransactionForm()
#         return render(request, 'payment_form.html', {'form': form})


import time  # Import the time module

from django.shortcuts import render
from django.conf import settings
from intasend import APIService
from .forms import B2CTransactionForm
from django.contrib import messages
from django.urls import reverse




def send_b2c_view(request):
    if request.method == 'POST':
        form = B2CTransactionForm(request.POST)
        if form.is_valid():
            amount = float(form.cleaned_data['loan_amount'])  # Convert Decimal to float
            recipient_name = form.cleaned_data['full_name']
            recipient_phone = form.cleaned_data['contact']
            narrative = form.cleaned_data['loan_id']

            token = settings.INTASEND_API_TOKEN
            publishable_key = settings.INTASEND_PUBLISHABLE_KEY
            
            # Initialize APIService
            service = APIService(token=token, publishable_key=publishable_key, test=True)  # Set test=True for sandbox

            # Prepare transaction details
            transactions = [
                {'name': recipient_name, 'account': recipient_phone, 'amount': amount, 'narrative': narrative}
            ]

            try:
                # Initiate M-Pesa B2C transaction
                response = service.transfer.mpesa(currency='KES', transactions=transactions)
                print("API Response:", response)

                # Check if the response has a field indicating it needs approval
                requires_approval = response.get('status') == 'Preview and approve'
                tracking_id = response.get('tracking_id')

                if not tracking_id:
                    raise ValueError("Tracking ID not returned by API")

                print(f"Tracking ID: {tracking_id}")

                if requires_approval:
                    # Approve the transaction
                    approved_response = service.transfer.approve(response)
                    print("Approved Response:", approved_response)
                else:
                    approved_response = "No approval required"

                # Redirect to the loan_application page with a success message
                success_message = "B2C transaction completed successfully."
                messages.success(request, success_message)
                return redirect(reverse('loans:loan_application'))

            except Exception as e:
                error_message = str(e)
                print("Error sending B2C transaction:", error_message)
                return render(request, 'error.html', {'error': error_message})
        else:
            # Form is not valid, render the form again with validation errors
            return render(request, 'payment_form.html', {'form': form})

    else:
        # GET request, render the empty form
        form = B2CTransactionForm()
        return render(request, 'payment_form.html', {'form': form})