from django.shortcuts import render, redirect
from .models import Adver, Apartment, District

def index_page(request):
    return render(request, 'index.html')

def create_adv(request):
    return render(request, 'create_adv.html')

def create_adv(request):
    if request.method == "POST":
        price = request.POST.get('price')
        date_created = request.POST.get('date_created')
        own = request.POST.get('own')
        mortgage = request.POST.get('mortgage') == 'True'
        score = request.POST.get('score')
        apartment_id = request.POST.get('apartment')
        apartment = Apartment.objects.get(id=apartment_id)
        image = request.POST.get('image')

        # Создание нового объявления
        Adver.objects.create(
            price=price,
            date_created=date_created,
            own=own,
            mortgage=mortgage,
            score=score,
            apartment=apartment,
            image=image
        )
        return redirect('/')  # Редирект на главную страницу после успешного создания объявления

    apartments = Apartment.objects.all()  # Получение всех квартир для выбора в форме
    return render(request, 'create_adv.html', {'apartments': apartments})

def create_app(request):
    if request.method == "POST":
        floor_app = request.POST.get('floor_app')
        district_id = request.POST.get('district')
        district = District.objects.get(id=district_id)
        area = request.POST.get('area')
        room_quantity = request.POST.get('room_quantity')
        address = request.POST.get('address')
        description = request.POST.get('description')

        # Создание новой квартиры
        Apartment.objects.create(
            floor_app=floor_app,
            district=district,
            area=area,
            room_quantity=room_quantity,
            address=address,
            description=description
        )
        return redirect('/')  # Редирект на главную страницу после успешного создания квартиры

    districts = District.objects.all()  # Получение всех районов для выбора в форме
    return render(request, 'create_app.html', {'districts': districts})
