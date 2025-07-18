from django.contrib import admin
from .models import CustomerProfile, BankTransaction

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user', 'account_balance', 'age', 'gender', 'phone_number', 'account_created']
    list_filter = ['gender', 'age', 'account_created']
    search_fields = ['full_name', 'user__username', 'email_address', 'phone_number']
    readonly_fields = ['user', 'account_created', 'last_updated']
    ordering = ['-account_created']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'full_name', 'age', 'gender')
        }),
        ('Contact Information', {
            'fields': ('email_address', 'phone_number')
        }),
        ('Account Information', {
            'fields': ('account_balance', 'account_created', 'last_updated')
        }),
    )

@admin.register(BankTransaction)
class BankTransactionAdmin(admin.ModelAdmin):
    list_display = ['customer', 'transaction_type', 'amount', 'balance_after', 'transaction_date']
    list_filter = ['transaction_type', 'transaction_date']
    search_fields = ['customer__username', 'description']
    readonly_fields = ['customer', 'transaction_type', 'amount', 'transaction_date', 'description', 'balance_after']
    ordering = ['-transaction_date']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False