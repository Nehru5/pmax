from django.shortcuts import render
from django.http import HttpResponse
from pmax.models import User

def home(request):
  return render(request,"./pmax/home.html")

def signup(request):
  if request.method=="POST":
    username = request.POST.get("username")
    email = request.POST.get("email")
    password = request.POST.get("password")
    
    if User.objects.filter(username = username).exists():
      return render(request, "./pmax/signup.html",{"error":"Username already exist"})
    User.objects.create(username = username,email = email, password = password)
    return HttpResponse("User saved")
  else:
    return render(request,"./pmax/signup.html")
    
  
  
  
    
