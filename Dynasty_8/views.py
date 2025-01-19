from django.shortcuts import render, redirect, get_list_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Adver, Apartment, District, Profile, Review
from .serializers import AdverSerializer, ApartmentSerializer, DistrictSerializer, ProfileSerializer
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404
import django_filters
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail
from django.core.cache import cache
from django.http import JsonResponse
from .utils import get_adverts_by_apartment
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.db.models import Avg, Min, Max, Count
from django.contrib import messages
from .forms import AdverForm, ReviewForm, ApartmentFilterForm
from django.utils.timezone import now
from django.urls import reverse


def district_list(request):
    districts = District.objects.all()
    return render(request, 'districts.html', {'districts': districts})

def apartment_list(request):
    queryset = Apartment.objects.all()  # Изначально получаем все объекты
    form = ApartmentFilterForm(request.GET)

    if form.is_valid():
        district = form.cleaned_data.get('district')
        min_area = form.cleaned_data.get('min_area')
        max_area = form.cleaned_data.get('max_area')
        rooms = form.cleaned_data.get('rooms')
        min_floor = form.cleaned_data.get('min_floor')
        max_floor = form.cleaned_data.get('max_floor')
        address = form.cleaned_data.get('address')
        description = form.cleaned_data.get('description')

        # Применение фильтров
        if district:
            queryset = queryset.filter(district=district)
        if min_area is not None:
            queryset = queryset.filter(area__gte=min_area)
        if max_area is not None:
            queryset = queryset.filter(area__lte=max_area)
        if rooms:
            queryset = queryset.filter(room_quantity=rooms)
        if min_floor is not None:
            queryset = queryset.filter(floor_app__gte=min_floor)
        if max_floor is not None:
            queryset = queryset.filter(floor_app__lte=max_floor)
        if address:
            queryset = queryset.filter(address__icontains=address)
        if description:
            queryset = queryset.filter(description__contains=description)

    total_apartments = queryset.count()
    large_apartments_exist = queryset.filter(area__gt=150).exists()

    return render(request, 'apartment_list.html', {
        'form': form,
        'apartments': queryset,
        'total_apartments': total_apartments,
        'large_apartments_exist': large_apartments_exist
    })


def set_session_data(request):
    request.session['user_id'] = 42
    request.session['cart'] = {'item1': 3, 'item2': 5}  # Добавляем данные в сеанс
    return HttpResponse("Данные добавлены в сеанс")

def get_session_data(request):
    user_id = request.session.get('user_id', 'Не задано')
    cart = request.session.get('cart', {})
    return HttpResponse(f"ID пользователя: {user_id}, Корзина: {cart}")

def apartment_detail(request, pk):  
    apartment = get_object_or_404(Apartment, pk=pk)
    reviews = apartment.reviews.all()  # Получение всех отзывов для квартиры

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            # Использование form.cleaned_data для получения данных формы
            author = form.cleaned_data['author']
            text = form.cleaned_data['text']
            rating = form.cleaned_data['rating']

            # Создание объекта Review с использованием данных из cleaned_data
            review = Review(apartment=apartment, author=author, text=text, rating=rating)
            review.save()  # Сохранение отзыва в базу данных

            messages.success(request, "Ваш отзыв успешно добавлен.")
            # Использование HttpResponseRedirect для перенаправления
            return HttpResponseRedirect(reverse('apartment_detail', args=[pk]))
    else:
        form = ReviewForm()  # Создание новой формы, если метод GET или форма невалидна

    # Передача формы и отзывов в шаблон
    return render(request, 'apartment_detail.html', {
        'apartment': apartment,
        'reviews': reviews,
        'form': form
    })

def create_adver(request): 
    if request.method == "POST":
        form = AdverForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()  # Вызов переопределенного save с commit=True
            return redirect('index_page')
    else:
        form = AdverForm()
    
    return render(request, 'create_adver.html', {'form': form})

def update_adver(request, pk):
    """Редактирует объявление с указанным pk."""
    adver = get_object_or_404(Adver, pk=pk)
    
    if request.method == 'POST':
        form = AdverForm(request.POST, request.FILES, instance=adver)
        if form.is_valid():
            form.save()
            return redirect('index_page')
    else:
        form = AdverForm(instance=adver)

    return render(request, 'update_adver.html', {'form': form})

def delete_adver(request, pk):
    adver = get_object_or_404(Adver, pk=pk)
    adver.delete()
    messages.success(request, "Объявление успешно удалено.")
    return redirect('index_page')

class ApartmentDetailView(DetailView):
    model = Apartment
    template_name = 'apartment_detail.html'

def list_admins(request):
    admins = Profile.objects.admins()
    data = {"admins": list(admins.values("eEmail", "phoneNumber", "roleName"))}
    return JsonResponse(data)

class AdverFilter(FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    start_date = django_filters.DateFilter(field_name="date_created", lookup_expr="gte")
    end_date = django_filters.DateFilter(field_name="date_created", lookup_expr="lte")
    mortgage = django_filters.BooleanFilter(field_name="mortgage")
    min_score = django_filters.NumberFilter(field_name="score", lookup_expr="gte")
    max_score = django_filters.NumberFilter(field_name="score", lookup_expr="lte")

    class Meta:
        model = Adver
        fields = ["min_price", "max_price", "start_date", "end_date", "mortgage", "min_score", "max_score"]

class ApartmentFilter(FilterSet):
    min_area = django_filters.NumberFilter(field_name="area", lookup_expr="gte")
    max_area = django_filters.NumberFilter(field_name="area", lookup_expr="lte")
    min_floor = django_filters.NumberFilter(field_name="floor_app", lookup_expr="gte")
    max_floor = django_filters.NumberFilter(field_name="floor_app", lookup_expr="lte")
    min_rooms = django_filters.NumberFilter(field_name="room_quantity", lookup_expr="gte")
    max_rooms = django_filters.NumberFilter(field_name="room_quantity", lookup_expr="lte")

    class Meta:
        model = Apartment
        fields = ["min_area", "max_area", "min_floor", "max_floor", "min_rooms", "max_rooms", "district"]

class AdverViewSet(ModelViewSet):
    queryset = Adver.objects.all()
    # serializer_class = AdverSerializer
    # filter_backends = [DjangoFilterBackend, SearchFilter]
    # filterset_class = AdverFilter
    search_fields = ["own", "apartment__address"]

    # Кастомный метод: возвращает объявления с ипотекой
    @action(methods=['GET'], detail=False, url_path='mortgage-available')
    def mortgage_available(self, request):
        """
        Квартиры с ипотекой
        """
        adverts = Adver.objects.filter(mortgage=True)
        serializer = self.get_serializer(adverts, many=True)
        return Response(serializer.data)

    # Кастомный метод: добавляет заметку к объявлению
    @action(methods=['POST'], detail=True, url_path='add-note')
    def add_note(self, request, pk=None):
        adver = self.get_object()
        note = request.data.get('note', '')
        if note:
            # Логика сохранения заметки
            return Response({"message": f"Заметка добавлена к объявлению {adver.id}: {note}"})
        return Response({"error": "Заметка не предоставлена"}, status=400)
     
     # Получение одного объекта
    def retrieve(self, request, pk=None):
        adver = get_object_or_404(Adver, pk=pk)
        serializer = self.get_serializer(adver)
        return Response(serializer.data)

    # Удаление объекта
    def destroy(self, request, pk=None):
        adver = get_object_or_404(Adver, pk=pk)
        adver.delete()
        return Response({"message": "Объявление удалено"}, status=status.HTTP_204_NO_CONTENT)

    # Создание объекта
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['GET'], detail=False, url_path='good-deals')
    def good_deals(self, request):
        """
        Выгодные предложения:
        - Цена ниже 2,000,000 или доступна ипотека
        - Исключены объекты с рейтингом меньше 5
        """
        good_deals_query = (Q(price__lt=2000000) | Q(mortgage=True)) & ~Q(score__lt=5)
        adverts = self.queryset.filter(good_deals_query)

        serializer = self.get_serializer(adverts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
class ApartmentViewSet(ModelViewSet):
    queryset = Apartment.objects.all()
    serializer_class = ApartmentSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    filterset_class = ApartmentFilter
    search_fields = ["address", "description", "district__district_name"]

    # Получение одного объекта
    def retrieve(self, request, pk=None):
        apartment = get_object_or_404(Apartment, pk=pk)
        serializer = self.get_serializer(apartment)
        return Response(serializer.data)

    # Удаление объекта
    def destroy(self, request, pk=None):
        apartment = get_object_or_404(Apartment, pk=pk)
        apartment.delete()
        return Response({"message": "Квартира удалена"}, status=status.HTTP_204_NO_CONTENT)

    # Создание объекта
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Метод для получения квартир с площадью не менее 60 кв.м.
    @action(methods=['GET'], detail=False, url_path='area-60-plus')
    def area_60_plus(self, request):
        """
        Фильтрация квартир:
        - Площадь не менее 60 кв.м.
        """
        apartments = self.queryset.filter(area__gte=60)

        if not apartments.exists():
            return Response({"message": "Нет квартир с площадью не менее 60 кв.м."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(apartments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    @action(methods=['GET'], detail=False, url_path='max-appart')
    def max_appart(self, request):
        """
        Фильтрация квартир:
        - Этаж не ниже 2 или площадь не меньше 50 кв.м.
        - Исключены квартиры с количеством комнат меньше 3.
        """
        max_appart_query = Q(floor_app__gte=2) | Q(area__gte=50)
        exclude_query = Q(room_quantity__lt=3)
        apartments = self.queryset.filter(max_appart_query).exclude(exclude_query)

        if not apartments.exists():
            return Response({"message": "Нет подходящих квартир"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(apartments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
def search_results(request):
    search_query = request.GET.get('search_query', '')

    # Поиск по объявлениям
    adverts = Adver.objects.filter(
        Q(apartment__address__icontains=search_query) |
        Q(own__icontains=search_query)
    )

    # Поиск по районам
    districts = District.objects.filter(
        Q(district_name__icontains=search_query) |
        Q(city_name__icontains=search_query)
    )

    # Поиск по профилям
    profiles = Profile.objects.filter(
        Q(eEmail__icontains=search_query) |
        Q(phoneNumber__icontains=search_query)
    )

    return render(request, 'search_results.html', {
        'search_query': search_query,
        'adverts': adverts,
        'districts': districts,
        'profiles': profiles,
    })

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

def index_page(request): 
    # Получение выбранных фильтров из GET-запроса, по умолчанию "all"
    filter_type = request.GET.get('filter', 'all')
    price_min = request.GET.get('price_min', None)
    price_max = request.GET.get('price_max', None)
    mortgage = request.GET.get('mortgage', None)

    # Создание объекта Q для комбинирования фильтров
    filter_conditions = Q()

    # Фильтрация по цене
    if price_min:
        filter_conditions &= Q(price__gte=price_min)
    if price_max:
        filter_conditions &= Q(price__lte=price_max)
    
    # Фильтрация по ипотеке
    if mortgage == 'True':
        filter_conditions &= Q(mortgage=True)
    elif mortgage == 'False':
        filter_conditions &= Q(mortgage=False)

    # Объявления по умолчанию
    adverts = Adver.objects.filter(filter_conditions)

    # Фильтрация по типу
    if filter_type == 'below_2000000':
        adverts = adverts.filter(price__lt=2000000)
    elif filter_type == 'mortgage':
        adverts = adverts.filter(mortgage=True)
    elif filter_type == 'good_deals':
        adverts = adverts.filter((Q(price__lt=2000000) | Q(mortgage=True)) & ~Q(score__lt=5))
    elif filter_type == 'high_rating':
        adverts = adverts.exclude(score__lt=5)  # Исключаем объявления с низким рейтингом
    elif filter_type == 'order_price':
        adverts = adverts.order_by('price')  # Сортируем по цене

    # Агрегирование данных
    stats = adverts.aggregate(
        avg_price=Avg('price'),
        min_price=Min('price'),
        max_price=Max('price'),
        total_count=Count('id')
    )

    # Пагинация: 6 объявлений на страницу
    paginator = Paginator(adverts, 6)
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)

    # Получаем все районы с сортировкой по удаленности от центра
    all_districts = District.objects.order_by('distance_from_center')

    # Пагинация: 3 района на страницу
    district_paginator = Paginator(all_districts, 3)
    district_page_number = request.GET.get('district_page')

    try:
        district_page_obj = district_paginator.get_page(district_page_number)
    except PageNotAnInteger:
        district_page_obj = district_paginator.get_page(1)
    except EmptyPage:
        district_page_obj = district_paginator.get_page(district_paginator.num_pages)

    # Фильтрация профилей только для администраторов и модераторов
    profiles = Profile.objects.filter(roleName__in=['admin', 'moderator'])

    # Передача данных в шаблон
    return render(request, 'index.html', {
        'page_obj': page_obj,
        'current_filter': filter_type,
        'price_min': price_min,
        'price_max': price_max,
        'mortgage': mortgage,
        'stats': stats,
        'districts': district_page_obj,
        'profiles': profiles
    })

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
        image = request.FILES.get('image')

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

    # API для объявлений
class AdverListCreateAPIView(APIView):
    def get(self, request):
        adverts = Adver.objects.all()
        serializer = AdverSerializer(adverts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AdverSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# API для квартир
class ApartmentListCreateAPIView(APIView):
    def get(self, request):
        apartments = Apartment.objects.all()
        serializer = ApartmentSerializer(apartments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ApartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# API для районов
class DistrictListCreateAPIView(APIView):
    def get(self, request):
        districts = District.objects.all()
        serializer = DistrictSerializer(districts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DistrictSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# API для профилей
class ProfileListCreateAPIView(APIView):
    def get(self, request):
        profiles = Profile.objects.all()
        serializer = ProfileSerializer(profiles, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class AdverSearchAPIView(ListAPIView):
    queryset = Adver.objects.all()
    serializer_class = AdverSerializer
    filter_backends = [SearchFilter]
    search_fields = ['own', 'apartment__address', 'apartment__description']

@extend_schema(
    summary="Получить список объявлений",
    description="Эндпоинт возвращает список всех объявлений.",
    responses={200: AdverSerializer},
)
class AdverViewSet(ModelViewSet):
    queryset = Adver.objects.all()
    serializer_class = AdverSerializer

def test_email_view(request):
    send_mail(
        "Тестовое письмо от Django",
        "Это тестовое письмо, отправленное через MailHog.",
        "test@example.com",
        ["recipient@example.com"],
    )
    return HttpResponse("Тестовое письмо отправлено!")

def get_adverts_by_apartment(apartment_id):
    """
    Получает объявления по квартире. Сначала проверяет кэш, затем базу данных.
    """
    # Формируем ключ для кэша
    cache_key = f"adverts_apartment_{apartment_id}"
    
    # Проверяем наличие данных в кэше
    adverts = cache.get(cache_key)
    if adverts is None:
        # Если данных нет в кэше, извлекаем из базы
        adverts = list(Adver.objects.filter(apartment_id=apartment_id))
        
        # Сохраняем в кэш на 15 минут
        cache.set(cache_key, adverts, timeout=60 * 15)
    return adverts

def adverts_view(request, apartment_id):
    """
    Отображает список объявлений по конкретной квартире.
    """
    adverts = get_adverts_by_apartment(apartment_id)
    data = [
        {
            "id": adver.id,
            "price": adver.price,
            "date_created": adver.date_created.strftime("%Y-%m-%d"),
            "own": adver.own,
            "mortgage": adver.mortgage,
            "score": adver.score,
            "apartment": adver.apartment.id,
        }
        for adver in adverts
    ]
    return JsonResponse(data, safe=False)

class AdverCreateView(CreateView):
    model = Adver
    fields = ['price', 'own', 'date_created', 'apartment', 'score', 'image', 'mortgage']
    template_name = 'create_adv.html'
    success_url = reverse_lazy('index_page')
