import sys
import os
from django.http import HttpResponse, JsonResponse
from django.urls import path
from django.apps import AppConfig
from requests import get

from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = "django-insecure-0wo^wrqiz46dg1c+ua_+dvhl%q42pftg^+idp2g8y%n7-&-ihh"
DEBUG = True
ALLOWED_HOSTS = []
INSTALLED_APPS = []
ROOT_URLCONF = "apps"
TEMPLATES = []
TEMPLATE_DIRS = []
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
MIDDLEWARE = []
HTML = """
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Weather</title>
        <meta name="description" content="天気予報確認アプリです、都道府県を選ぶだけで高速に天気を知ることができます" />

        <style>
            .page:not(.active) {
                display: none;
            }
        </style>
    </head>
    <body>
        <div class="page home active">
            <h1>Weather Information</h1>
            <h2>今日の天気を知りたい場所を選択してください</h2>
            <label for="select">prefecture:</label>
            <select id="select">
                <option value=""></option>
                <option value="大阪府">大阪</option>
                <option value="兵庫県">兵庫</option>
            </select>
            <button>確認する</button>
        </div>
        <div class="page details">
            <h1>Weather Information</h1>
            <h2>
                <span class="prefecture">now loading...</span>
                <span class="date"></span>
                の天気
            </h2>
            <img src="">
            <h3 class="weather"></h3>
            <p>
                最高気温 :
                <span class="max">now loading...</span>
            </p>
            <p>
                最低気温 :
                <span class="min">now loading...</span>
            </p>
            <div>
                <a href="/">トップページに戻る</a>
            </div>
        </div>
        <script>
            const cities = { "北海道": "016010", "青森県": "020010", "岩手県": "030010", "宮城県": "040010", "秋田県": "050010", "山形県": "060010", "福島県": "070010", "茨城県": "080010", "栃木県": "090010", "群馬県": "100010", "埼玉県": "110010", "千葉県": "120010", "東京都": "130010", "神奈川県": "1440010", "新潟県": "150010", "富山県": "160010", "石川県": "170010", "福井県": "180010", "山梨県": "190010", "長野県": "200010", "岐阜県": "210010", "静岡県": "220010", "愛知県": "230010", "三重県": "240010", "滋賀県": "250010", "京都府": "260010", "大阪府": "270000", "兵庫県": "280010", "奈良県": "290010", "和歌山県": "300010", "鳥取県": "310010", "島根県": "320010", "岡山県": "330010", "広島県": "340010", "山口県": "350010", "徳島県": "360010", "香川県": "370010", "愛媛県": "380010", "高知県": "390010", "福岡県": "400010", "佐賀県": "410010", "長崎県": "420010", "熊本県": "430010", "大分県": "440010", "宮崎県": "450010", "鹿児島県": "460010", "沖縄県": "470010", }
            const element = (query) => document.querySelector(query)
            const cL = (query) => element(query).classList
            const on = (element, event, handler) => element.addEventListener(event, handler)

            const historyPush = (href) => {
                history.pushState(href, href, href)
            }

            const backHome = () => {
                cL(".details").remove("active")
                cL(".home").add("active")
                historyPush("/")
            }

            const toDetails = (city) => {
                cL(".details").add("active")
                cL(".home").remove("active")
                historyPush(`/details?city=${city}`)
            }

            const renderDetails = (data) => {
                element(".prefecture").innerText = data.city
                element(".date").innerText = data.weather.date
                element("img").src = data.image.url
                element(".weather").src = data.weather.telop
                element(".max").innerText = data.weather.temperature.max || "情報がありませんでした"
                element(".min").innerText = data.weather.temperature.min || "情報がありませんでした"
            }

            on(element("button"), "click", async (e)=> {
                const value = element("select").value
                if(!value)
                    return
                toDetails(value)
                const res = await (await fetch(`/weather?city=${value}&id=${cities[value]}`)).json()
                renderDetails(res)
            })
            on(element("a"), "click", async (e)=> {
                backHome()
            })

            const inti = async () => {
                if (location.pathname == "/details") {
                    cL(".details").add("active")
                    cL(".home").remove("active")
                    const value = (new URL(location.href)).searchParams.get("city")
                    const res = await (await fetch(`/weather?city=${value}&id=${cities[value]}`)).json()
                    renderDetails(res)
                    toDetails(value)
                    return
                }
                backHome()
            }
            inti()
        </script>
    </body>
</html>
"""



def render(path: str, content_type: str = "text/html; charset=utf-8"):
    with open(path) as f:
        return HttpResponse(f.read(), content_type=content_type)

class RequestConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "request"

def index(request):
    return HttpResponse(HTML, content_type="text/html; charset=utf-8")


def get_weather(params: int):
    url = f"https://weather.tsukumijima.net/api/forecast?city={params}"
    return get(url, verify=False).json()


def q(r, n, d=None):
    return r.GET.get(n) or d

def qi(r, n, d=None):
    return int(q(r, n, d))

def get_wether(request):
    params = qi(request, "id")
    data = get_weather(params)["forecasts"][0]
    context = {
        "weather": {
            "date": data["date"],
            "telop": data["telop"],
            "temperature": {
                "max": data["temperature"]["max"]["celsius"],
                "min": data["temperature"]["min"]["celsius"],
            },
        },
        "weathers": data,
        "city": q(request, "city"),
        "image": {
            "tag": data["image"]["title"],
            "url": data["image"]["url"],
        },
    }
    return JsonResponse(context)

urlpatterns = [
    path("", index),
    path("details", index),
    path("weather", get_wether)
]


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "apps")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
