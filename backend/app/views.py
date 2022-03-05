from django.shortcuts import render

# Create your views here.
def register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
        
    if request.method == "POST":	
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        password = request.POST['password']
        user_type = request.POST['user_type']

        if form.is_valid():
            instance = User.objects.create_user(**form.cleaned_data)
            return HttpResponseRedirect(reverse('login')) #HttpResponse("<b>User Created Successfully</b>")

        else:
            print(form.errors)
            context = {
                "error" : "Email alreday exists.",
            }
            return render(request, 'backend/register.html', context=context)
            # return render(request, 'General/amj_register.html', context)
    else:
        return render(request, 'backend/register.html')