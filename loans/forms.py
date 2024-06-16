from django import forms
from .models import Loan, Payment,LoanApplication
from django.contrib.auth.models import User



class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount']

    def __init__(self, *args, **kwargs):
        self.loan = kwargs.pop('loan', None)
        super().__init__(*args, **kwargs)

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if self.loan and amount > self.loan.balance:
            raise forms.ValidationError(f"Payment amount exceeds the remaining balance of {self.loan.balance}.")
        return amount



from django import forms
from .models import Loan

class LoanRequestForm(forms.ModelForm):
    PAYMENT_PERIOD_CHOICES = [
        (15, '15 days'),
        (30, '30 days'),
    ]

    payment_period = forms.ChoiceField(choices=PAYMENT_PERIOD_CHOICES)

    class Meta:
        model = Loan
        fields = ['amount', 'payment_period']





from django import forms
from .models import LoanApplication
from datetime import date

from django import forms
from datetime import date
from calendar import month_abbr, monthrange


class MonthNameField(forms.Select):
    def __init__(self, attrs=None):
        months = [(i, month_abbr[i]) for i in range(1, 13)]
        super().__init__(attrs, choices=[('', 'Month')] + months)




class CustomDateWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        years = [(year, year) for year in range(1900, date.today().year + 1)]
        months = [(i, month_abbr[i]) for i in range(1, 13)]
        days = [(i, i) for i in range(1, 32)]

        widgets = (
            forms.Select(attrs={'class': 'form-select w-auto me-2'}, choices=[('', 'Year')] + years),
            MonthNameField(attrs={'class': 'form-select w-auto me-2'}),
            forms.Select(attrs={'class': 'form-select w-auto me-2'}, choices=[('', 'Day')] + days),
        )

        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value.year, value.month, value.day]
        return [None, None, None]

    def value_from_datadict(self, data, files, name):
        year = data.get(name + '_0')
        month = data.get(name + '_1')
        day = data.get(name + '_2')

        if year and month and day:
            try:
                date_value = date(int(year), int(month), int(day))
            except ValueError:
                date_value = None
            return date_value

        return None

    def format_output(self, rendered_widgets):
        return ''.join(rendered_widgets)


class LoanApplicationForm(forms.ModelForm):
    class Meta:
        model = LoanApplication
        fields = [
            'first_name', 'second_name', 'id_number', 'phone_number', 
            'date_of_birth', 'education_level', 'first_guarantor', 
            'contact', 'second_guarantor', 'second_contact'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'second_name': forms.TextInput(attrs={'placeholder': 'Second Name'}),
            'id_number': forms.TextInput(attrs={'placeholder': 'ID Number'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Phone Number'}),
            'date_of_birth': CustomDateWidget(),  # Use CustomDateWidget for date of birth
            'education_level': forms.Select(),
            'first_guarantor': forms.TextInput(attrs={'placeholder': 'First Guarantor'}),
            'contact': forms.TextInput(attrs={'placeholder': 'First Guarantor Contact'}),
            'second_guarantor': forms.TextInput(attrs={'placeholder': 'Second Guarantor'}),
            'second_contact': forms.TextInput(attrs={'placeholder': 'Second Guarantor Contact'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Calculate the date 18 years ago from today
        eighteen_years_ago = date.today().year - 18
        # Set the default year to 18 years ago if date_of_birth is not set
        if not self.initial.get('date_of_birth'):
            self.fields['date_of_birth'].widget = CustomDateWidget()
            self.fields['date_of_birth'].initial = date(eighteen_years_ago, 1, 1)

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if age < 18:
            raise forms.ValidationError("You must be 18 years and above to qualify.")
        return dob



class LoanListForm(forms.ModelForm):
    STATUS_CHOICES = [
        ('approved', 'Approved'),
        ('in review', 'In Review'),
        ('declined', 'Declined'),
    ]

    status = forms.ChoiceField(choices=STATUS_CHOICES)

    class Meta:
        model = Loan
        fields = ['status']


# class AdminLendLoanForm(forms.ModelForm):
#     loan_id = forms.ModelChoiceField(queryset=Loan.objects.filter(status='approved'), label='Loan ID')
#     first_name = forms.CharField(max_length=30, label='Applicant First Name', required=False)
#     last_name = forms.CharField(max_length=30, label='Applicant Last Name', required=False)
#     contact = forms.CharField(max_length=255, label='Contact Information', required=False)
#     loan_amount = forms.DecimalField(max_digits=10, decimal_places=2, label='Loan Amount', required=False)

#     class Meta:
#         model = Loan
#         fields = ['loan_id', 'first_name', 'last_name', 'contact', 'loan_amount']

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['loan_id'].queryset = Loan.objects.filter(status='approved')


class AdminLendLoanForm(forms.ModelForm):
    loan_id = forms.ModelChoiceField(queryset=Loan.objects.filter(status='approved'), label='Loan ID')
    full_name = forms.CharField(max_length=60, label='Applicant Full Name', required=False)
    contact = forms.CharField(max_length=255, label='Contact Information', required=False)
    loan_amount = forms.DecimalField(max_digits=10, decimal_places=2, label='Loan Amount', required=False)

    class Meta:
        model = Loan
        fields = ['loan_id', 'full_name', 'contact', 'loan_amount']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['loan_id'].queryset = Loan.objects.filter(status='approved')

        # Populate form fields if instance is provided (for edit functionality)
        instance = kwargs.get('instance')
        if instance:
            self.initial['loan_id'] = instance.id
            self.initial['full_name'] = instance.get_full_name()  # Assuming get_full_name() is a method in your Loan model
            self.initial['contact'] = instance.loan_application.phone_number if instance.loan_application else ''
            self.initial['loan_amount'] = instance.amount

    def clean_loan_id(self):
        loan_id = self.cleaned_data['loan_id']
        if isinstance(loan_id, Loan):
            return loan_id.id  # Ensure we return the ID of the loan if it's a Loan instance
        return loan_id