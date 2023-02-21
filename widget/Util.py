import requests


def send_coordinate(x, y):
    url = "http://127.0.0.1:5500/index.html"
    response = requests.get(url, params={"x": x, "y": y})
    if response.status_code == 200:
        print(response.text)