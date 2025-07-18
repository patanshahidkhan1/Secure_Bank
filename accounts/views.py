from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from decimal import Decimal, InvalidOperation
from .models import CustomerProfile, BankTransaction

def home_page(request):
    """Welcome page view"""
    return render(request, 'accounts/home.html')

def auth_page(request):
    """Login and Signup page view"""
    if request.user.is_authenticated:
        return redirect('user_dashboard')
    
    if request.method == 'POST':
        if 'login_submit' in request.POST:
            # Handle Login
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '')
            
            if not username or not password:
                messages.error(request, 'Please fill in all login fields.')
            else:
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.username}!')
                    return redirect('user_dashboard')
                else:
                    messages.error(request, 'Wrong password. Try again.')
        
        elif 'signup_submit' in request.POST:
            # Handle Signup
            username = request.POST.get('signup_username', '').strip()
            full_name = request.POST.get('full_name', '').strip()
            age = request.POST.get('age', '')
            gender = request.POST.get('gender', '')
            email = request.POST.get('email_address', '').strip()
            phone = request.POST.get('phone_number', '').strip()
            password = request.POST.get('signup_password', '')
            
            # Validation
            if not all([username, full_name, age, gender, email, phone, password]):
                messages.error(request, 'Please fill in all signup fields.')
            elif User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists. Please choose another.')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email already registered. Please use another email.')
            else:
                try:
                    age_int = int(age)
                    if age_int < 18 or age_int > 100:
                        messages.error(request, 'Age must be between 18 and 100.')
                    else:
                        # Create user and profile
                        with transaction.atomic():
                            user = User.objects.create_user(
                                username=username, 
                                password=password, 
                                email=email,
                                first_name=full_name.split()[0] if full_name.split() else full_name
                            )
                            CustomerProfile.objects.create(
                                user=user,
                                full_name=full_name,
                                age=age_int,
                                gender=gender,
                                email_address=email,
                                phone_number=phone
                            )
                        messages.success(request, 'Account created successfully! Please login.')
                except ValueError:
                    messages.error(request, 'Please enter a valid age.')
                except Exception as e:
                    messages.error(request, 'Error creating account. Please try again.')
    
    return render(request, 'accounts/auth.html')

@login_required
def user_dashboard(request):
    """User dashboard view"""
    try:
        profile = request.user.customer_profile
    except CustomerProfile.DoesNotExist:
        # Create profile if doesn't exist
        profile = CustomerProfile.objects.create(
            user=request.user,
            full_name=request.user.get_full_name() or request.user.username,
            age=25,
            gender='Male',
            email_address=request.user.email or '',
            phone_number=''
        )
    
    return render(request, 'accounts/dashboard.html', {'profile': profile})

@login_required
def balance_view(request):
    """View balance and transaction history"""
    try:
        profile = request.user.customer_profile
    except CustomerProfile.DoesNotExist:
        profile = CustomerProfile.objects.create(
            user=request.user,
            full_name=request.user.get_full_name() or request.user.username,
            age=25,
            gender='Male',
            email_address=request.user.email or '',
            phone_number=''
        )
    
    # Get recent transactions
    recent_transactions = BankTransaction.objects.filter(customer=request.user)[:10]
    
    return render(request, 'accounts/balance.html', {
        'profile': profile,
        'recent_transactions': recent_transactions
    })

@login_required
def deposit_money(request):
    """Deposit money view"""
    try:
        profile = request.user.customer_profile
    except CustomerProfile.DoesNotExist:
        profile = CustomerProfile.objects.create(
            user=request.user,
            full_name=request.user.get_full_name() or request.user.username,
            age=25,
            gender='Male',
            email_address=request.user.email or '',
            phone_number=''
        )
    
    if request.method == 'POST':
        try:
            # Get form data
            total_amount_str = request.POST.get('total_amount', '0').strip()
            notes_500_str = request.POST.get('notes_500', '0').strip()
            notes_200_str = request.POST.get('notes_200', '0').strip()
            notes_100_str = request.POST.get('notes_100', '0').strip()
            
            # Convert to appropriate types
            total_amount = Decimal(total_amount_str)
            notes_500 = int(notes_500_str)
            notes_200 = int(notes_200_str)
            notes_100 = int(notes_100_str)
            
            # Validation
            if total_amount <= 0:
                messages.error(request, 'Total amount must be greater than 0.')
                return render(request, 'accounts/deposit.html', {'profile': profile})
            
            if notes_500 < 0 or notes_200 < 0 or notes_100 < 0:
                messages.error(request, 'Number of notes cannot be negative.')
                return render(request, 'accounts/deposit.html', {'profile': profile})
            
            # Calculate amount from notes
            calculated_amount = Decimal(notes_500 * 500) + Decimal(notes_200 * 200) + Decimal(notes_100 * 100)
            
            if calculated_amount == total_amount:
                with transaction.atomic():
                    # Update balance
                    profile.account_balance += total_amount
                    profile.save()
                    
                    # Create transaction record
                    BankTransaction.objects.create(
                        customer=request.user,
                        transaction_type='deposit',
                        amount=total_amount,
                        description=f'Cash Deposit: {notes_500}×₹500 + {notes_200}×₹200 + {notes_100}×₹100',
                        balance_after=profile.account_balance
                    )
                
                messages.success(request, f'₹{total_amount} deposited successfully! New balance: ₹{profile.account_balance}')
                return redirect('user_dashboard')
            else:
                messages.error(request, f'Amount mismatch! Entered: ₹{total_amount}, Calculated from notes: ₹{calculated_amount}')
                
        except (ValueError, InvalidOperation):
            messages.error(request, 'Please enter valid numbers only.')
        except Exception as e:
            messages.error(request, 'An error occurred during deposit. Please try again.')
    
    return render(request, 'accounts/deposit.html', {'profile': profile})

@login_required
def withdraw_money(request):
    """Withdraw money view"""
    try:
        profile = request.user.customer_profile
    except CustomerProfile.DoesNotExist:
        profile = CustomerProfile.objects.create(
            user=request.user,
            full_name=request.user.get_full_name() or request.user.username,
            age=25,
            gender='Male',
            email_address=request.user.email or '',
            phone_number=''
        )
    
    if request.method == 'POST':
        try:
            amount_str = request.POST.get('withdraw_amount', '0').strip()
            amount = Decimal(amount_str)
            
            # Validation
            if amount <= 0:
                messages.error(request, 'Withdrawal amount must be greater than 0.')
            elif amount > profile.account_balance:
                messages.error(request, f'Insufficient balance. Available: ₹{profile.account_balance}')
            else:
                with transaction.atomic():
                    # Update balance
                    profile.account_balance -= amount
                    profile.save()
                    
                    # Create transaction record
                    BankTransaction.objects.create(
                        customer=request.user,
                        transaction_type='withdraw',
                        amount=amount,
                        description=f'Cash Withdrawal of ₹{amount}',
                        balance_after=profile.account_balance
                    )
                
                messages.success(request, f'₹{amount} withdrawn successfully! Remaining balance: ₹{profile.account_balance}')
                return redirect('user_dashboard')
                
        except (ValueError, InvalidOperation):
            messages.error(request, 'Please enter a valid amount.')
        except Exception as e:
            messages.error(request, 'An error occurred during withdrawal. Please try again.')
    
    return render(request, 'accounts/withdraw.html', {'profile': profile})

def user_logout(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home_page')