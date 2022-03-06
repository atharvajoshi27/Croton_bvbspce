import datetime
from django.db import connection
from django.shortcuts import HttpResponse, redirect, render, HttpResponseRedirect, reverse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from rest_framework import views
from rest_framework.response import Response
from .models import *
from .forms import CreateUser
import string
import random
# Create your views here.
@login_required
def index(request):
    user = request.user
    if user.user_type == 0: # patient
        return redirect('index-patient')
    else: # practioner
        return redirect('index-doctor')

@login_required
def index_doctor(request):
    user = request.user
    if user.user_type == "0":
        return redirect('index-patient')
    doctor = user.doctor
    if not doctor.verified:
        return redirect('upload-docs')
    
    return HttpResponse("Work in progress")

@login_required
def index_patient(request):
    user = request.user
    if user.user_type == "1":
        return redirect('index-doctor')

def register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))

    if request.method == "POST":	
        form = CreateUser(request.POST)
        if form.is_valid():
            instance = User.objects.create_user(**form.cleaned_data)
            if instance.user_type == "0":
                patient = Patient(user=instance, encryption_key="".join(random.choices(string.ascii_letters+string.digits, k=512)))
                patient.save()
            else:
                doctor = Doctor(user=instance)
                doctor.save()
            return HttpResponseRedirect(reverse('login')) #HttpResponse("<b>User Created Successfully</b>")

        else:
            print(form.errors)
            context = {
                "error" : "Email alreday exists.",
            }
            return render(request, 'app/register.html', context=context)
    else:
        return render(request, 'app/register.html')


def log_in(request):
    user = request.user
    if user.is_authenticated:
        return redirect('index')

    if request.method == "GET":
        return render(request, 'app/login.html')
    
    if request.method == "POST":
        print(f"post params: {request.POST}")
        user = authenticate(request, email=request.POST["email"], password=request.POST["password"])
        if not user is None:
            login(request, user)
            return redirect('index')
        context = {
            'error' : 'Please provide correct email and password'
        }
        return render(request, 'app/login.html', context)
    return redirect(request, 'index')


@login_required
def log_out(request):
    logout(request)
    return redirect('index')


@login_required
@require_http_methods(["GET", "POST"])
def upload_docs(request):
    if request.user.user_type == "0":
        return redirect(request, 'index')
    doctor = request.user.doctor
    if request.method == "GET":
        context = {"hospital": doctor.hospital, "degree": doctor.degree}
        return render(request, 'app/upload_docs.html', context=context)

    if request.method == "POST":
        d = Document()
        d.document = request.FILES["document"]
        d.doctor = doctor
        hospital = request.POST["hospital"]
        degree = request.POST["degree"]
        doctor.hospital = hospital
        doctor.degree = degree
        doctor.save()
        d.save()
    return redirect('index')
    