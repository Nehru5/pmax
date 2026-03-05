from django.shortcuts import render,redirect
from django.http import HttpResponse
from pmax.models import User,Movie
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
    return redirect("login")
  else:
    return render(request,"./pmax/signup.html")
    
  
def login(request):
  if request.method == "POST":
    username = request.POST.get("username")
    password = request.POST.get("password")
    
    try:
      user = User.objects.get(username=username,password=password)
      request.session["user-id"] = user.id
      request.session["user-name"] = user.username
      return redirect("dashboard")
    except:
      return render(request,"./pmax/login.html",{"error":"Invalid credentials"})
  else:
    return render(request,"./pmax/login.html")
      
  
    
def dashboard(request):
  user_id = request.session.get("user-id")
  if not user_id:
    return redirect("login")
  
  movies = Movie.objects.all()
  return render(request, "./pmax/dashboard.html",{"movies":movies})