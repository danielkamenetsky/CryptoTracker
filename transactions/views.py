from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
import redis  # Make sure you have the redis package installed (pip install redis)
from django.core.management import call_command
import io

from.models import Transaction
from .forms import TransactionForm
from django.contrib import messages  
from .forms import UserRegistrationForm
from django.contrib.auth import login
import logging
import datetime
from django.utils import timezone
import random  # Temporary for demo data
from django.conf import settings

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
        # Connect to Redis using the helper function
        r = settings.get_redis_connection()
        
        if not r:
            # Redis is not available - return sample data
            return JsonResponse({
                'current_value': 50000,
                'total_invested': 45000,
                'total_profit': 5000,
                'btc_price': 65000,
                'note': 'Using sample data (Redis not available)'
            })
        
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
        
        # Return sample data as fallback
        return JsonResponse({
            'current_value': 50000,
            'total_invested': 45000,
            'total_profit': 5000,
            'btc_price': 65000,
            'note': f'Using sample data due to error: {str(e)}'
        })

def portfolio_history_api(request):
    """
    API endpoint that returns historical portfolio data for charting.
    """
    try:
        # Get the time period from the request (default to '1m' - one month)
        period = request.GET.get('period', '1m')
        
        # Define time ranges based on period
        now = timezone.now()
        if period == '1d':
            # Last 24 hours, hourly data points
            start_date = now - datetime.timedelta(days=1)
            interval = datetime.timedelta(hours=1)
            format_string = '%H:%M'  # Hour:Minute
        elif period == '1w':
            # Last 7 days, daily data points
            start_date = now - datetime.timedelta(weeks=1)
            interval = datetime.timedelta(days=1)
            format_string = '%a'  # Abbreviated weekday
        elif period == '1m':
            # Last 30 days, daily data points
            start_date = now - datetime.timedelta(days=30)
            interval = datetime.timedelta(days=1)
            format_string = '%d %b'  # Day Month
        elif period == '1y':
            # Last 365 days, weekly data points
            start_date = now - datetime.timedelta(days=365)
            interval = datetime.timedelta(weeks=1)
            format_string = '%d %b'  # Day Month
        elif period == '5y':
            # Last 5 years, monthly data points
            start_date = now - datetime.timedelta(days=365*5)
            interval = datetime.timedelta(days=30)
            format_string = '%b %Y'  # Month Year
        else:
            # Default to 1 month
            start_date = now - datetime.timedelta(days=30)
            interval = datetime.timedelta(days=1)
            format_string = '%d %b'  # Day Month
        
        # Try to get current portfolio value from Redis for reference
        r = settings.get_redis_connection()
        
        # Default value if Redis is not available
        current_value = 50000
        
        if r:
            redis_value = r.get('portfolio:current_value')
            if redis_value:
                current_value = float(redis_value)
        
        # Generate data points from start_date to now
        data_points = []
        labels = []
        current_date = start_date
        
        # Start with a base value (60% of current value as a starting point)
        base_value = current_value * 0.6 if current_value > 0 else 50000
        
        # Generate an upward trend with some volatility
        while current_date <= now:
            # Format the date for the label
            label = current_date.strftime(format_string)
            labels.append(label)
            
            # Calculate a value with some randomness but general upward trend
            # The closer to current date, the closer to current_value
            progress = (current_date - start_date).total_seconds() / (now - start_date).total_seconds()
            target_value = base_value + (current_value - base_value) * progress
            
            # Add some volatility (±5%)
            volatility = random.uniform(-0.05, 0.05)
            value = target_value * (1 + volatility)
            
            data_points.append(round(value, 2))
            current_date += interval
        
        # Return the data
        return JsonResponse({
            'labels': labels,
            'values': data_points,
            'period': period
        })
    
    except Exception as e:
        print(f"Error in portfolio_history_api: {str(e)}")
        return JsonResponse({
            'error': str(e),
            'message': 'Failed to retrieve portfolio history data'
        }, status=500)

def run_migrations(request):
    """Temporary view to run migrations."""
    out = io.StringIO()
    call_command('migrate', stdout=out)
    return HttpResponse(f"Migrations applied:<br><pre>{out.getvalue()}</pre>")