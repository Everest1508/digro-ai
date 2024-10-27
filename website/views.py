from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request=request,template_name='home/index.html')

def about(request):
    return render(request=request,template_name='about/index.html')

def feature(request):
    return render(request=request,template_name='feature/index.html')

def pricing(request):
    return render(request=request,template_name='pricing/index.html')
