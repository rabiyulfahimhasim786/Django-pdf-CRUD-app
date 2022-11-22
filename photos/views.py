from django.shortcuts import render, redirect
from .models import Category, Photo, Csv
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
import requests
# Create your views here.
from django.http import HttpResponse, JsonResponse
import pandas as pd
import json
import time
#AWS s3
import boto3
import os
from functools import reduce
#import boto3
ACCESS_KEY = "Accesskey"
SECRET_KEY = "secretkey"
from botocore.exceptions import ClientError
import datetime
#create your views here

def loginUser(request):
    page = 'login'
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('gallery')

    return render(request, 'photos/login_register.html', {'page': page})


def logoutUser(request):
    logout(request)
    return redirect('login')


def registerUser(request):
    page = 'register'
    form = CustomUserCreationForm()

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()

            if user is not None:
                login(request, user)
                return redirect('gallery')

    context = {'form': form, 'page': page}
    return render(request, 'photos/login_register.html', context)


@login_required(login_url='login')
def gallery(request):
    user = request.user
    category = request.GET.get('category')
    if category == None:
        photos = Photo.objects.filter(category__user=user)
    else:
        photos = Photo.objects.filter(
            category__name=category, category__user=user)

    categories = Category.objects.filter(user=user)
    context = {'categories': categories, 'photos': photos}
    return render(request, 'photos/gallery.html', context)


@login_required(login_url='login')
def viewPhoto(request, pk):
    photo = Photo.objects.get(id=pk)
    csv = Csv.objects.get(id=pk)
    print(csv.csvfile)
    df = pd.read_csv(csv.csvfile)
    # parsing the DataFrame in json format.
    json_records = df.reset_index().to_json(orient ='records')
    data = []
    data = json.loads(json_records)
    print(data)
	#context = {'d': data}
	#return render(request, 'table.html', context)
    text = {'photo': photo, 'd': data}
    return render(request, 'photos/photo.html', text)#{'photo': photo})


@login_required(login_url='login')
def addPhoto(request):
    user = request.user

    categories = user.category_set.all()

    if request.method == 'POST':
        data = request.POST
        images = request.FILES.getlist('images')

        if data['category'] != 'none':
            category = Category.objects.get(id=data['category'])
        elif data['category_new'] != '':
            category, created = Category.objects.get_or_create(
                user=user,
                name=data['category_new'])
        else:
            category = None

        for image in images:
            photo = Photo.objects.create(
                category=category,
                description=data['description'],
                image=image,
            )
        time.sleep(18)
        #x = requests.get('http://127.0.0.1:8000/text/')
        #AWS s3 file post
        ACCESS_KEY = "Accesskey"
        SECRET_KEY = "secretkey"
        s3_client = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
        response = s3_client.list_objects_v2(Bucket='bucketname', Prefix='foldername')
        all = response['Contents']        
        latest = max(all, key=lambda x: x['LastModified'])
        print(latest)
        #print(latest.values())
        list(reduce(lambda x, y: x + y, latest.items()))
        a = list(reduce(lambda x, y: x + y, latest.items()))
        print(a[1])

        #file downloading 
        #print(latest.values())
        list(reduce(lambda x, y: x + y, latest.items()))
        a = list(reduce(lambda x, y: x + y, latest.items()))
        #print(a[1])
        urllink = a[1]
        url = f"https://bucketname.s3.amazonaws.com/{urllink}"
        print(url)
        datas = {"key": url}
        member = Csv(csvfile=url)
        member.save()
        return redirect('gallery')
    context = {'categories': categories}
    return render(request, 'photos/add.html', context)


  
def index(request):
    return HttpResponse("Hello, world.")


def text_views(request):
    #ACCESS_KEY = "Accesskey"
    #SECRET_KEY = "secretkey"
    
    ACCESS_KEY = "Accesskey"
    SECRET_KEY = "secretkey"
    s3_client = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
    response = s3_client.list_objects_v2(Bucket='bucketname', Prefix='foldername')
    all = response['Contents']        
    latest = max(all, key=lambda x: x['LastModified'])
    print(latest)
    #print(latest.values())
    list(reduce(lambda x, y: x + y, latest.items()))
    a = list(reduce(lambda x, y: x + y, latest.items()))
    print(a[1])

    #file downloading 
    #print(latest.values())
    list(reduce(lambda x, y: x + y, latest.items()))
    a = list(reduce(lambda x, y: x + y, latest.items()))
    #print(a[1])
    urllink = a[1]
    url = f"https://bucketname.s3.amazonaws.com/{urllink}"
    print(url)
    datas = {"key": url}
    #member = Csv(csvfile=url)
    #member.save()
    return JsonResponse({"code": "1", "status": "200", "data": [datas]})