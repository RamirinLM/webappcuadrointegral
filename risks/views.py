from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Risk
from .forms import RiskForm

@login_required
def risk_list(request):
    risks = Risk.objects.all()
    return render(request, 'risks/risk_list.html', {'risks': risks})

@login_required
def risk_create(request):
    if request.method == 'POST':
        form = RiskForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Risk created successfully.')
            return redirect('risks:risk_list')
    else:
        form = RiskForm()
    return render(request, 'risks/risk_form.html', {'form': form})
