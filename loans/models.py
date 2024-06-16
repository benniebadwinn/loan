from django.db import models
from django.contrib.auth.models import User
from django.db import models
from decimal import Decimal





class Blacklist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    reason = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.user.username} - {self.reason}"





class LoanApplication(models.Model):
    EDUCATION_LEVEL_CHOICES = [
        ('Primary', 'Primary Level'),
        ('Secondary', 'Secondary Level'),
        ('Diploma', 'Diploma'),
        ('Degree', 'Degree'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    second_name = models.CharField(max_length=50)
    id_number = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=15)
    date_of_birth = models.DateField()
    education_level = models.CharField(max_length=50, choices=EDUCATION_LEVEL_CHOICES)
    first_guarantor = models.CharField(max_length=100)
    contact = models.CharField(max_length=15)
    second_guarantor = models.CharField(max_length=100)
    second_contact = models.CharField(max_length=15)  # Renamed for consistency

    def __str__(self):
        return f"{self.first_name} {self.second_name}"





class Loan(models.Model):
    STATUS_CHOICES = [
        ('approved', 'Approved'),
        ('in review', 'In Review'),
        ('declined', 'Declined'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    applied_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Loan amount after interest
    loan_application = models.OneToOneField(LoanApplication, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)   # Loan amount before interest
    interest_rate = models.DecimalField(max_digits=4, decimal_places=2)
    date_created = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    paid = models.BooleanField(default=False)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in review')

    def calculate_applied_amount(self):
        return self.amount + (self.amount * self.interest_rate / Decimal(100))

    def calculate_balance(self):
        return self.calculate_applied_amount() - self.amount_paid

    def __str__(self):
        return f"Loan ID: {self.id} - User: {self.user.username} - Status: {self.get_status_display()}"






class Payment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_paid = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Loan ID: {self.loan.id} - {self.loan.user.username} - {self.amount} - Date Paid: {self.date_paid.strftime('%Y-%m-%d %H:%M:%S')}"



class Lendloan(models.Model):
    # other fields
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved')])


    def __str__(self):
        return f"{self.id} - {self.user.username} - {self.status}"




