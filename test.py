import sys
from io import BytesIO  # Этот класс поможет нам сделать картинку из потока байт

import requests
from geocoder_find_map_params import (get_map_params)
from PIL import Image

toponym_to_find = " ".join(sys.argv[1:])
map_params = get_map_params(toponym_to_find)
map_params["apikey"] = "5815d7d2-6bbe-424d-a32d-028b8c596fa2"
map_params["pt"] = map_params["ll"]

map_api_server = "https://static-maps.yandex.ru/v1"
response = requests.get(map_api_server, params=map_params)
im = BytesIO(response.content)
opened_image = Image.open(im)
opened_image.show()