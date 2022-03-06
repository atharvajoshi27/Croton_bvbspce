from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name='index'),
    path("register", views.register, name='register'),
    path("login", views.log_in, name='login'),
    path("logout", views.log_out, name='logout'),
    path("upload_docs", views.upload_docs, name='upload-docs'),
    path("index", views.index, name='index'),
    path("doctor/index", views.index_doctor, name='index-doctor'),
    path("doctor/search", views.search_patient, name='search-patient'),
    path("patient/index", views.index_patient, name='index-patient'),
    path("patient/<str:patient_id>/documents", views.view_documents, name='view-documents'),
    path("data/<str:patient_id>", views.upload_patient_data, name='upload-data'),
]