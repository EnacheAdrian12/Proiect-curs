from django.shortcuts import render, redirect
from django.db.models import Q
from .models import Message, Room, Topic
from .forms import RoomForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.forms import  UserCreationForm




def loginPage(request):

    page ='login'

    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        
        user = authenticate(request, username = username, password = password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or Password does not exist')
    context={'page': page}
    return render(request, 'playground/login_register.html', context)



def logoutUser(request):
    logout(request)
    return redirect('home')




def registerPage(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occured during registration')
    return render(request,'playground/login_register.html', {'form': form})




def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(Q(topic__name__icontains=q) |
        Q(name__icontains = q)  |
        Q(description__icontains = q)
    )
    topic = Topic.objects.all()
    room_count = rooms.count()
    context = {'rooms': rooms, 'topics': topic, 'room_count': room_count}
    return render(request, 'playground/home.html', context)




def room (request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()
    if request.method =='POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room',pk=room.id)

    context ={'room': room, 'room_messages': room_messages, 'participants': participants}
    return render(request, 'playground/room.html', context)




@login_required(login_url="login")
def createRoom(request):
    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room=form.save(commit=False)
            room.host = request.user
            room.save()
            return redirect('home')
    
    context={'form': form}
    return render(request, 'playground/room_form.html', context)




@login_required(login_url="login")
def deleteRoom(request,pk):
    room = Room.objects.get(id=pk)

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request,'playground/delete.html',{'obj':room})




@login_required(login_url="login")
def deleteMessage(request,pk):
    message = Message.objects.get(id=pk)

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request,'playground/delete.html',{'obj':message})




