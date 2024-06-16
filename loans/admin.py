from django.contrib import admin
from .models import Blacklist, Loan, Payment, LoanApplication,Lendloan


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('loan', 'amount', 'date_paid', 'loan_id_display')
    
    def loan_id_display(self, obj):
        return obj.loan.id
    loan_id_display.short_description = 'Loan ID'

admin.site.register(Lendloan)

admin.site.register(Blacklist)
admin.site.register(Loan)
admin.site.register(Payment)
admin.site.register(LoanApplication)
