from django import forms
from loans.models import Loan


class B2CTransactionForm(forms.ModelForm):
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