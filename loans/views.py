from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Loan, Payment
from .forms import PaymentForm,LoanRequestForm, LoanListForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Loan
from .forms import LoanRequestForm
from django.shortcuts import render, redirect
from .forms import LoanRequestForm
from .models import Loan, Blacklist
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import LoanApplicationForm
from .models import Loan, Blacklist, LoanApplication
from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Loan, LoanApplication
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from django.contrib import messages
from django.http import JsonResponse
from .forms import AdminLendLoanForm  # Import the new form
from .models import Loan, User
from django.core.serializers import serialize
from django.http import JsonResponse
from django.core.serializers import serialize
from django.http import JsonResponse







@login_required
def loan_application(request):
    # Check if the user has already applied for a loan
    existing_application = LoanApplication.objects.filter(user=request.user).exists()
    if existing_application:
        return redirect('loans:request_loan')
    
    if request.method == 'POST':
        form = LoanApplicationForm(request.POST)
        if form.is_valid():
            loan_application = form.save(commit=False)
            loan_application.user = request.user  # Set the user to the logged-in user
            loan_application.save()
            messages.success(request, 'Your loan application has been submitted successfully.')
            return redirect('loans:request_loan')
    else:
        form = LoanApplicationForm()
    return render(request, 'loans/loan_application_form.html', {'form': form})



@login_required
def request_loan(request):
    blacklist_message = None

    # Check if the user is in the blacklist
    try:
        blacklist_entry = Blacklist.objects.get(user=request.user)
        blacklist_message = f"{blacklist_entry.reason}"
    except Blacklist.DoesNotExist:
        pass

    # Check if the user has an existing loan
    existing_loan = Loan.objects.filter(user=request.user, balance__gt=0).first()
    if existing_loan:
        return redirect('loans:loan_list')

    # Ensure the user has a loan application
    try:
        loan_application = LoanApplication.objects.get(user=request.user)
    except LoanApplication.DoesNotExist:
        messages.error(request, 'You must complete a loan application before requesting a loan.')
        return redirect('loans:loan_application')

    if request.method == 'POST':
        form = LoanRequestForm(request.POST)
        if form.is_valid():
            if not blacklist_message:
                loan = form.save(commit=False)
                loan.user = request.user
                loan.loan_application = loan_application  # Link the loan to the loan application

                # Set the initial maximum loan amount
                max_loan_amount = 2000
                
                # Check if the user has repaid the initial loan
                if Loan.objects.filter(user=request.user, balance=0).exists():
                    # Increase the maximum loan amount if the user has repaid
                    max_loan_amount = 5000

                # Set the maximum loan amount for the current loan request
                loan_limit = max_loan_amount

                # Check if the requested loan amount exceeds the maximum loan limit
                requested_amount = form.cleaned_data.get('amount')
                if requested_amount > loan_limit:
                    messages.error(request, f'The maximum loan amount you can request is {loan_limit}.')
                    return redirect('loans:request_loan')

                # Set the interest rate based on the payment period
                payment_period = int(form.cleaned_data.get('payment_period'))
                if payment_period == 15:
                    loan.interest_rate = 20.0
                elif payment_period == 30:
                    loan.interest_rate = 25.0

                # Set the loan amount before interest
                loan.applied_amount = requested_amount

                # Calculate the interest amount
                interest_amount = loan.applied_amount * Decimal(loan.interest_rate) / Decimal(100)

                # Calculate the total loan amount to be paid (including interest)
                loan.amount = loan.applied_amount + interest_amount

                # Automatically calculate and set the due date
                loan.due_date = timezone.now().date() + timedelta(days=payment_period)

                # Calculate initial balance
                loan.balance = loan.amount

                # Set loan status to 'in review'
                loan.status = 'in review'

                loan.save()
                messages.success(request, 'Your loan request has been submitted successfully and is now in review.')
                return redirect('loans:loan_list')
    else:
        form = LoanRequestForm()

    return render(request, 'loans/request_loan.html', {
        'form': form,
        'blacklist_message': blacklist_message,
    })





@login_required
def loan_list(request):
    loans = Loan.objects.all().values()  # Convert queryset to dictionary

    if not loans.exists():
        return redirect('loans:request_loan')

    now = timezone.now()
    ten_days_from_now = now + timezone.timedelta(days=10)
    blacklist_reason = 'Default'

    for loan in loans:
        if loan['due_date'] and loan['due_date'] < now:
            loan['days_overdue'] = (now - loan['due_date']).days
            if loan['due_date'] <= ten_days_from_now:
                blacklist_entry, created = Blacklist.objects.get_or_create(user=request.user)
                if not created:
                    blacklist_entry.reason = blacklist_reason
                    blacklist_entry.save()
                else:
                    blacklist_entry.reason = blacklist_reason
                    blacklist_entry.save()

    # Create the form instance
    form = LoanListForm()

    if request.method == 'POST':
        form = LoanListForm(request.POST)
        if form.is_valid():
            loan_id = request.POST.get('loan_id')  # Assuming you have a hidden input for loan_id in your form
            loan = get_object_or_404(Loan, id=loan_id)
            # Update loan status (if still using status field in Loan model)
            loan.status = form.cleaned_data['status']
            loan.save()
            # Optionally, add success message
            # messages.success(request, 'Loan status updated successfully.')

    return render(request, 'loans/loan_list.html', {'loans': list(loans), 'now': now, 'form': form})







@login_required
def pay_loan(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id, user=request.user)
    if request.method == 'POST':
        form = PaymentForm(request.POST, loan=loan)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.loan = loan
            payment.save()
            loan.amount_paid += payment.amount
            loan.balance = loan.amount - loan.amount_paid
            loan.paid = loan.balance <= 0
            loan.save()
            messages.success(request, 'Your payment has been processed successfully.')
            return redirect('loans:request_loan')
        else:
            messages.error(request, 'Payment amount exceeds the remaining balance. Kindly pay the correct amount.')
    else:
        form = PaymentForm(loan=loan)
    return render(request, 'loans/pay_loan.html', {'form': form, 'loan': loan})




def admin_lend_loan(request):
    approved_loans = Loan.objects.filter(status='approved')

    if request.method == 'POST':
        form = AdminLendLoanForm(request.POST)
        if form.is_valid():
            loan_id = form.cleaned_data['loan_id']
            full_name = form.cleaned_data['full_name']
            contact = form.cleaned_data['contact']
            loan_amount = form.cleaned_data['loan_amount']

            # Get the Loan instance
            loan = get_object_or_404(Loan, id=loan_id)

            # Ensure there is a LoanApplication linked to the Loan instance
            if not loan.loan_application:
                loan_application = LoanApplication.objects.create(
                    first_name='',  # Replace with appropriate first name
                    second_name='',  # Replace with appropriate last name
                    phone_number='',  # Replace with appropriate phone number
                )
                loan.loan_application = loan_application

            # Update fields based on form data
            if full_name:
                first_name, last_name = full_name.split(' ', 1)
                loan.loan_application.first_name = first_name
                loan.loan_application.second_name = last_name

            if contact:
                loan.loan_application.phone_number = contact

            if loan_amount:
                loan.amount = loan_amount

            # Calculate and set applied_amount before saving
            loan.applied_amount = loan.calculate_applied_amount()  # Assuming calculate_applied_amount() method in Loan model
            
            # Save the Loan instance
            loan.save()

            return redirect('payments:send_b2c')
    else:
        form = AdminLendLoanForm()

    return render(request, 'loans/admin_lend_loan.html', {'form': form, 'approved_loans': approved_loans})




def get_user_info(request):
    loan_id = request.GET.get('loan_id')
    
    try:
        loan = Loan.objects.get(id=loan_id, status='approved')
        loan_application = loan.loan_application  # Assuming 'loan_application' is the related model
        full_name = f"{loan_application.first_name} {loan_application.second_name}"  # Combine first name and second name
        data = {
            'full_name': full_name.strip(),  # Remove leading/trailing whitespace
            'username': loan.user.username,  # Assuming 'user' is the related user object in Loan model
            'contact': loan_application.phone_number,
            'loan_amount': loan.amount,
        }
        return JsonResponse(data)
    except Loan.DoesNotExist:
        return JsonResponse({'error': 'Loan not found or not approved'}, status=404)


