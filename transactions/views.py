from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import redis  # Make sure you have the redis package installed (pip install redis)

from.models import Transaction
from .forms import TransactionForm
from django.contrib import messages  
from .forms import UserRegistrationForm
from django.contrib.auth import login
import logging
logger = logging.getLogger(__name__)



@login_required
def home(request):
    return render(request, 'transactions/home.html')


@login_required
def transaction_list(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    return render(request, 'transactions/transaction_list.html', {'transactions': transactions})

@login_required
def transaction_detail(request, transaction_id):
    transaction = get_object_or_404(Transaction, transaction_id=transaction_id, user=request.user)
    return render(request, 'transactions/transaction_detail.html', {'transaction': transaction})


@login_required

def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            try:
                transaction = form.save(commit=False)
                transaction.user = request.user
                transaction.save()
                logger.info(f"Transaction {transaction.transaction_id} created successfully for user {request.user.username}")
                messages.success(request, f"Transaction {transaction.transaction_id} created successfully.")
                return redirect('transaction_detail', transaction_id=transaction.transaction_id)
            except Exception as e:
                logger.error(f"Error creating transaction for user {request.user.username}: {str(e)}")
                messages.error(request, "An error occurred while creating the transaction. Please try again.")
        else:
            logger.warning(f"Invalid form submission for user {request.user.username}: {form.errors}")
            messages.error(request, "Please correct the errors below.")
    else:
        form = TransactionForm()
    return render(request, 'transactions/add_transaction.html', {'form': form})

@login_required
def delete_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, transaction_id=transaction_id, user=request.user)
    transaction.delete()
    messages.success(request, f"Successfully deleted transaction with ID {transaction_id}.")
    return redirect('transaction_list')


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Account created for {user.username}!")
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})



def portfolio_view(request):
    return render(request, 'transactions/portfolio.html')

def portfolio_api(request):
    """
    API endpoint that returns the current portfolio data.
    This function retrieves the latest calculated values from Redis.
    """
    try:
        # Connect to Redis
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        
        # Get the latest portfolio data from Redis
        current_value = r.get('portfolio:current_value')
        total_invested = r.get('portfolio:total_invested')
        total_profit = r.get('portfolio:total_profit')
        btc_price = r.get('portfolio:btc_price')
        
        # Convert string values to float (or None if not found)
        current_value = float(current_value) if current_value else 0
        total_invested = float(total_invested) if total_invested else 0
        total_profit = float(total_profit) if total_profit else 0
        btc_price = float(btc_price) if btc_price else 0
        
        # Create the response data
        data = {
            'current_value': current_value,
            'total_invested': total_invested,
            'total_profit': total_profit,
            'btc_price': btc_price
        }
        
        return JsonResponse(data)
    
    except Exception as e:
        # Log the error
        print(f"Error in portfolio_api: {str(e)}")
        
        # Return an error response
        return JsonResponse({
            'error': str(e),
            'message': 'Failed to retrieve portfolio data'
        }, status=500)