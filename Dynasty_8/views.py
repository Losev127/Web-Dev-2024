from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Adver, Apartment, District, Profile
from .serializers import AdverSerializer, ApartmentSerializer, DistrictSerializer, ProfileSerializer
from django.db.models import Q
from django.core.paginator import Paginator
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404


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

    # Фильтрация по типу
    if filter_type == 'below_2000000':
        filter_conditions &= Q(price__lt=2000000)
    elif filter_type == 'mortgage':
        filter_conditions &= Q(mortgage=True)

    # Фильтр: "Выгодные предложения"
    elif filter_type == 'good_deals':
        filter_conditions &= (Q(price__lt=2000000) | Q(mortgage=True)) & ~Q(score__lt=5)

    # Получаем объявления с применёнными фильтрами
    adverts = Adver.objects.filter(filter_conditions)

    # Пагинация: 5 объявлений на страницу
    paginator = Paginator(adverts, 5)
    page_number = request.GET.get('page')  # Получение текущей страницы
    page_obj = paginator.get_page(page_number)  # Получение объектов для текущей страницы

    # Передача данных в шаблон
    return render(request, 'index.html', {
        'page_obj': page_obj,
        'current_filter': filter_type,  # Для отображения текущего фильтра
        'price_min': price_min,  # Для сохранения значения фильтра в форме
        'price_max': price_max,
        'mortgage': mortgage
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
    

class AdverGoodDealsAPIView(APIView):
    def get(self, request):
        # Сложный Q-запрос для фильтрации выгодных предложений
        good_deals_query = (Q(price__lt=2000000) | Q(mortgage=True)) & ~Q(score__lt=5)
        adverts = Adver.objects.filter(good_deals_query)

        # Пагинация
        page = request.GET.get('page', 1)
        paginator = Paginator(adverts, 5)  # 5 объявлений на страницу
        try:
            adverts = paginator.page(page)
        except:
            return Response({"error": "Неверный номер страницы"}, status=status.HTTP_400_BAD_REQUEST)

        # Сериализация данных
        serializer = AdverSerializer(adverts, many=True)
        return Response({
            "page": page,
            "total_pages": paginator.num_pages,
            "total_count": paginator.count,
            "adverts": serializer.data,
        })


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

class AdverViewSet(ModelViewSet):
    queryset = Adver.objects.all()
    serializer_class = AdverSerializer

    # Кастомный метод: возвращает объявления с ипотекой
    @action(methods=['GET'], detail=False, url_path='mortgage-available')
    def mortgage_available(self, request):
        adverts = Adver.objects.filter(mortgage=True)
        serializer = self.get_serializer(adverts, many=True)
        return Response(serializer.data)

    # Кастомный метод: добавляет заметку к объявлению
    @action(methods=['POST'], detail=True, url_path='add-note')
    def add_note(self, request, pk=None):
        adver = self.get_object()  # Получение объекта объявления по pk
        note = request.data.get('note', '')
        if note:
            # Здесь вы можете добавить логику сохранения заметки
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
    
class ApartmentViewSet(ModelViewSet):
    queryset = Apartment.objects.all()
    serializer_class = ApartmentSerializer

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
