import requests
import json
from bs4 import BeautifulSoup

class Manager:
    def __init__(self):
        self.session = requests.Session()

    def _request(self, url):
        return self.session.get(url)

    def list_cars(self):
        return self._request('https://lss-manager.de/api/cars.php')