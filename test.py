import requests
from pprint import pprint
url = "https://weatherapi-com.p.rapidapi.com/forecast.json"

querystring = {"q":"Kursk","days":"1"}

headers = {
	"X-RapidAPI-Key": "a15a7e959cmsh7fc7c4400cf946cp167646jsn7f3812b1db78",
	"X-RapidAPI-Host": "weatherapi-com.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)
x = response.json().get('current')
last_updated = x.get('last_updated')
temperature = x.get('temp_c')
wind_mph = x.get('wind_mph')
pressure_mb = x.get('pressure_mb')
feels_like_c = x.get('feelslike_c')
#print(f'Погода на:{last_updated}, температура{temperature}, ветер{wind_mph}, давление{pressure_mb}')
pprint(response.json())