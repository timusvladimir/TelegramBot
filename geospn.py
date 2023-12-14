import math
import requests

from dotenv import load_dotenv
from os import environ

load_dotenv("env")  # берем свой файл
static_maps_SERVICE = 'https://static-maps.yandex.ru/1.x/'
search_api_server = f"https://search-maps.yandex.ru/v1/"
geocoder_SERVICE = f"http://geocode-maps.yandex.ru/1.x/"
API_KEY = environ["API_KEY"]
API_KEY_2 = environ["API_KEY_2"]


# Определяем функцию, считающую расстояние между двумя точками, заданными координатами
def lonlat_distance(a, b):
    degree_to_meters_factor = 111 * 1000  # 111 километров в метрах
    a_lon, a_lat = a
    b_lon, b_lat = b

    # Берем среднюю по широте точку и считаем коэффициент для нее.
    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)

    # Вычисляем смещения в метрах по вертикали и горизонтали.
    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor

    # Вычисляем расстояние между точками.
    distance = math.sqrt(dx * dx + dy * dy)

    return round(distance)


# Получаем параметры объекта для рисования карты вокруг него.
def llspan(address):
    # Собираем запрос для геокодера.
    geocoder_params = {
        "apikey": API_KEY,
        "geocode": address,
        "format": "json"}

    # Выполняем запрос.
    response = requests.get(geocoder_SERVICE, params=geocoder_params)

    if response:
        # Преобразуем ответ в json-объект
        json_response = response.json()
    else:
        print("Ошибка выполнения запроса:")
        print(geocoder_SERVICE)
        print("Http статус:", response.status_code, "(", response.reason, ")")

    # Получаем первый топоним из ответа геокодера.
    # Согласно описанию ответа он находится по следующему пути:
    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    toponym_adress = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]

    if not toponym:
        return None, None

    # Координаты центра топонима:
    toponym_coordinates = toponym["Point"]["pos"]
    # Долгота и Широта :
    toponym_lon, toponym_lat = toponym_coordinates.split(" ")
    ll = ",".join([toponym_lon, toponym_lat])

    envelope = toponym["boundedBy"]["Envelope"]
    lowerCorner, left = envelope["lowerCorner"].split(" ")
    upperCorner, right = envelope["upperCorner"].split(" ")
    delta_x = abs(float(right) - float(left)) / 0.5
    delta_y = abs(float(upperCorner) - float(lowerCorner)) / 0.5

    spn = f"{delta_x},{delta_y}"

    #return float(toponym_lon), float(toponym_lat), spn
    return ll, spn


def find_org(coords):
    search_params = {
        "apikey": API_KEY_2,
        "lang": "ru_RU",
        "ll": coords,
        "spn": "0.001,0.001",
        "type": "biz",
        "text": "компьютерный магазин"
    }

    response = requests.get(search_api_server, params=search_params)

    if response:
        # Преобразуем ответ в json-объект
        json_response = response.json()
    else:
        print("Ошибка выполнения запроса:")
        print(search_api_server)
        print("Http статус:", response.status_code, "(", response.reason, ")")

    # Получаем первую найденную организацию.
    organizations = json_response["features"]
    return organizations[0] if organizations else None


def adres(address):
    # Собираем запрос для геокодера.
    geocoder_params = {
        "apikey": API_KEY,
        "geocode": address,
        "format": "json"}

    # Выполняем запрос.
    response = requests.get(geocoder_SERVICE, params=geocoder_params)

    if response:
        # Преобразуем ответ в json-объект
        json_response = response.json()
    else:
        print("Ошибка выполнения запроса:")
        print(geocoder_SERVICE)
        print("Http статус:", response.status_code, "(", response.reason, ")")

    # Получаем первый топоним из ответа геокодера.
    # Согласно описанию ответа он находится по следующему пути:
    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    toponym_adress = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]

    if not toponym:
        return None

    return toponym_adress


def post(address):
    # Собираем запрос для геокодера.
    geocoder_params = {
        "apikey": API_KEY,
        "geocode": address,
        "format": "json"}

    # Выполняем запрос.
    response = requests.get(geocoder_SERVICE, params=geocoder_params)

    if response:
        # Преобразуем ответ в json-объект
        json_response = response.json()
    else:
        print("Ошибка выполнения запроса:")
        print(geocoder_SERVICE)
        print("Http статус:", response.status_code, "(", response.reason, ")")

    # Получаем первый топоним из ответа геокодера.
    # Согласно описанию ответа он находится по следующему пути:
    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    toponym_adress = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]

    if not toponym:
        return None

    try:
        return toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]["postal_code"] + ", " + toponym_adress
    except KeyError:
        return toponym_adress
