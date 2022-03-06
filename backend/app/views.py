import numpy as np
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
from django.core.exceptions import ObjectDoesNotExist
from .emailer import mail
from django.http import FileResponse, Http404
# import magic
import mimetypes
from django.conf import settings
import os
import keras
from PIL import Image

# Create your views here.
@login_required
def index(request):
    print("Hello")
    user = request.user
    if user.user_type == "0": # patient
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
    # patients = doctor.access_list_set.all()
    return redirect(search_patient)
    # return HttpResponse("Work in progress of Doctor index")

@login_required
def index_patient(request):
    user = request.user
    if user.user_type == "1":
        return redirect('index-doctor')
    return redirect('view-documents', request.user.patient.id)
    # return HttpResponse("Work in progress of patient index")

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
        if doctor.verified:
            return redirect('index')
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

# need to give at max 3 trials : to be done
@login_required
@require_http_methods(["GET"])
def view_documents(request, patient_id):
    if request.user.user_type == "0" and request.user.patient.id != int(patient_id):
        return HttpResponse("<h2>Forbidden</h2>")
    
    try:
        patient = Patient.objects.get(id=patient_id)
    except ObjectDoesNotExist:
        return HttpResponse("No such patient exist")
    if request.user.user_type == "1" and (not request.user.doctor in patient.access_list.all()):
        return redirect('search-patient')

    # if request.method == "GET":
        
    reports = patient.report_set.all()
    mris = patient.mri_set.all()
    xrays = patient.xray_set.all()
    prescriptions = patient.prescription_set.all()
    something = (len(reports) or len(mris) or len(xrays) or len(prescriptions))
    context = {'reports': reports, 'mris': mris, 'xrays': xrays, 'prescriptions': prescriptions, 'patient_id': patient_id, 'something': something}
    return render(request, 'app/view_documents.html', context=context)
        
    # else:
    #     otp = request.POST['otp']
    #     actual_otp = request.session[f"{patient_id}_OTP"]
    #     print(f"Actual OTP = {actual_otp} and received otp = {otp}")
    #     if request.session.get(f'{patient_id}_OTP', 'NONE') == otp:
    #         patient.access_list.add(request.user.doctor)
    #         return redirect('view-documents', patient_id=patient_id)
    #     context = {'otp': True, 'patient_id': patient_id, 'error': "Incorrect OTP"}
    #     return render(request, 'app/view_documents.html', context=context)
        

@login_required
def search_patient(request):
    if request.user.user_type == "0":
        return HttpResponse("Forbidden")

    context = {"patients": request.user.doctor.patient_set.all(), "email": True}
    if request.method == "GET":
        context["email"] = True
        context["otp"] = False
        return render(request, 'app/search_patient.html', context=context)
    else:
        if request.POST["type_id"] == "0":
            doctor = request.user.doctor
            patient_id = request.POST["patient_id"]
            actual_otp = request.session.get(f'{patient_id}_OTP', "NONE")
            otp = request.POST["otp"]
            if actual_otp == otp:
                patient = Patient.objects.get(id=int(patient_id))
                patient.access_list.add(doctor)
                return redirect('view-documents', patient_id)
            else:
                # context = {'otp': True, 'error': "Incorrect otp entered", 'patient_id': patient_id}
                context["otp"] = True
                context["email"] = False
                context["error"] = "Incorrect otp entered"
                context["patient_id"] = patient_id

                return render(request, 'app/search_patient.html', context=context)
            # if not patient in doctor.patient_set.all():
                
            #     context = {'otp': True, 'patient_id': patient_id}
            #     return render(request, 'app/view_documents.html', context=context)

        if request.POST["type_id"] == "1":
            email = request.POST["email"]
            try:
                user = User.objects.get(email=email)
                if user.user_type == "1":
                    raise ObjectDoesNotExist
                patient = user.patient
                if request.user.doctor in patient.access_list.all():
                    return redirect('view-documents', patient.id)
            except ObjectDoesNotExist:
                context["email"] = True
                context["otp"] = False
                context["error"] = "Enter valid patient"
                return render(request, 'app/search_patient.html', context=context)

            otp = "".join(random.choices(string.digits, k=6))
            request.session[f"{patient.id}_OTP"] = otp
            mail(patient.user.email, "OTP for accessing documents", f"Your OTP is {otp}")
            context["otp"] = True
            context["email"] = False
            context["patient_id"] = patient.id
            return render(request, 'app/search_patient.html', context=context)
        else:
            return HttpResponse("Not found")


@login_required
@require_http_methods(["POST"])
def upload_patient_data(request, patient_id):
    if (request.user.user_type == "0" and request.user.patient.id != int(patient_id)):
        return HttpResponse("Forbidden")
    try:
        patient = Patient.objects.get(id=patient_id)
    except ObjectDoesNotExist:
        return HttpResponse("Patient not found.")
    if request.user.user_type == "1":
        doctor = request.user.doctor
        if doctor not in patient.access_list.all():
            return HttpResponse("Forbidden")
    print(f"Data = {request.POST}")
    print("HEY HERE id = ", request.POST["type_id"])
    if request.POST["type_id"] == "report":
        report_file = request.FILES["report_file"]
        report_title = request.POST["report_title"]
        report_date = request.POST["report_date"]
        new_report = Report(title=report_title, date=report_date, document=report_file, patient=patient)
        if request.user.user_type == "1":
            new_report.doctor = request.user.doctor
        new_report.save()

    elif request.POST["type_id"] == "mri":
        report_file = request.FILES["report_file"]
        report_title = request.POST["report_title"]
        report_date = request.POST["report_date"]
        new_report = Report(title=report_title, date=report_date, document=report_file, patient=patient)
        if request.user.user_type == "1":
            new_report.doctor = request.user.doctor
        new_report.save()

        mri_title = request.POST['mri_title']
        mri_file = request.FILES['mri_file']
        new_mri = Mri(title=mri_title, document=mri_file, report=new_report, patient=patient)
        new_mri.save()

    elif request.POST["type_id"] == "xray":
        report_file = request.FILES["report_file"]
        report_title = request.POST["report_title"]
        report_date = request.POST["report_date"]
        new_report = Report(title=report_title, date=report_date, document=report_file, patient=patient)
        if request.user.user_type == "1":
            new_report.doctor = request.user.doctor
        new_report.save()

        xray_title = request.POST['xray_title']
        xray_file = request.FILES['xray_file']
        new_xray = Xray(title=xray_title, document=xray_file, report=new_report, patient=patient)

        new_xray.save()

        pass
    elif request.POST["type_id"] == "prescription":
        p_title = request.POST["p_title"]
        p_date = request.POST["p_date"]
        p_file = request.FILES["p_file"]
        new_p = Prescription(title=p_title, date=p_date, document=p_file, patient=patient)
        if request.user.user_type == "1":
            new_p.doctor = request.user.doctor
        new_p.save()
        pass
    else:
        return HttpResponse("Not found")
    return redirect('index')
    # return redirect('view-documents', patient_id)

def validity_check(user, patient):
    if user.user_type == "0" and user.patient.id != patient.id:
        return False
    
    if user.user_type == "1" and (not user.doctor in patient.access_list.all()):
        return False

    return True

@login_required
def report_view(request, r_id):
    try:
        report = Report.objects.get(id=r_id)
    except ObjectDoesNotExist:
        return HttpResponse("Not found")

    if not validity_check(request.user, report.patient):
        return HttpResponse("Forbidden")

    try:
        # mime = magic.Magic(mime=True)
        # mimetype = mime.from_file(report.document.url) # 'application/pdf'
        print(f"BASE_DIR = {settings.BASE_DIR}")
        url = os.path.join(settings.BASE_DIR, report.document.url[1:])
        print("url = ", url)
        mimetype = mimetypes.guess_type(url)[0]
        return FileResponse(open(url, 'rb'), content_type=mimetype)
    except FileNotFoundError:
        raise Http404()

@login_required
def xray_view(request, r_id):
    try:
        report = Xray.objects.get(id=r_id)
    except ObjectDoesNotExist:
        return HttpResponse("Not found")

    if not validity_check(request.user, report.patient):
        return HttpResponse("Forbidden")

    try:
        # mime = magic.Magic(mime=True)
        # mimetype = mime.from_file(report.document.url) # 'application/pdf'
        print(f"BASE_DIR = {settings.BASE_DIR}")
        url = os.path.join(settings.BASE_DIR, report.document.url[1:])
        print("url = ", url)
        mimetype = mimetypes.guess_type(url)[0]
        return FileResponse(open(url, 'rb'), content_type=mimetype)
    except FileNotFoundError:
        raise Http404()

@login_required
def mri_view(request, r_id):

    try:
        report = Mri.objects.get(id=r_id)
    except ObjectDoesNotExist:
        return HttpResponse("Not found")

    if not validity_check(request.user, report.patient):
        return HttpResponse("Forbidden")

    try:
        # mime = magic.Magic(mime=True)
        # mimetype = mime.from_file(report.document.url) # 'application/pdf'
        print(f"BASE_DIR = {settings.BASE_DIR}")
        url = os.path.join(settings.BASE_DIR, report.document.url[1:])
        print("url = ", url)
        mimetype = mimetypes.guess_type(url)[0]
        return FileResponse(open(url, 'rb'), content_type=mimetype)
    except FileNotFoundError:
        raise Http404()

@login_required
def prescription_view(request, r_id):
    try:
        report = Prescription.objects.get(id=r_id)
    except ObjectDoesNotExist:
        return HttpResponse("Not found")

    if not validity_check(request.user, report.patient):
        return HttpResponse("Forbidden")
    try:
        # mime = magic.Magic(mime=True)
        # mimetype = mime.from_file(report.document.url) # 'application/pdf'
        print(f"BASE_DIR = {settings.BASE_DIR}")
        url = os.path.join(settings.BASE_DIR, report.document.url[1:])
        print("url = ", url)
        mimetype = mimetypes.guess_type(url)[0]
        return FileResponse(open(url, 'rb'), content_type=mimetype)
    except FileNotFoundError:
        raise Http404()

@login_required
def get_predictions(request):
    if request.user.user_type == "1":
        return HttpResponse("Forbidden")
    xrays = request.user.patient.xray_set.all()
    mris = request.user.patient.mri_set.all()
    d = {}
    XRAYS = {}
    MRIS = {}
    xray_model = keras.models.load_model('app/xray.h5')
    mri_model = keras.models.load_model('app/mri.h5')
    for xray in xrays:
        url = os.path.join(settings.BASE_DIR, xray.document.url[1:])
        image = Image.open(url).resize((150, 150))
        image = np.array(image).flatten()
        image = image.reshape(-1,150,150,3)
        prediction = xray_model.predict(image)[0][0]
        if prediction < 0.5:
            XRAYS[xray.title] = "No"
        else:
            XRAYS[xray.title] = "Yes"

    for mri in mris:
        url = os.path.join(settings.BASE_DIR, mri.document.url[1:])
        image = Image.open(url).resize((224, 224))
        image = np.array(image).flatten()
        image = image.reshape(-1,224,224,3)
        prediction = mri_model.predict(image)[0][0]
        prediction = mri_model.predict(image)[0][0]
        if prediction < 0.5:
            MRIS[xray.title] = "No"
        else:
            MRIS[xray.title] = "Yes"

    d['XRAYS'] = XRAYS
    d['MRIS'] = MRIS
    return render(request, 'app/predictions.html', context=d)

