import requests
import json
import re
import time
from bs4 import BeautifulSoup
from yachalk import chalk
from .helpers import *
from .game_objects import *

class Client:
    def __init__(self, headers):
        self.session = requests.Session()
        self.session.headers.update(headers)

    def _request(self, url):
        return self.session.get(url)

    def _soup(self, response):
        return BeautifulSoup(response.content, 'html.parser')

    def get_vehicle_states(self):
        return self._request('https://www.leitstellenspiel.de/api/vehicle_states').json()

    def get_vehicles(self):
        res = self._request('https://www.leitstellenspiel.de/api/vehicles')
        if res.status_code != 200:
            print("get_vehicles failed:")
            print(res)
            print(res.headers)
            print(res.text)
        res_j = res.json()
        return [Vehicle(j) for j in res_j]

    def get_buildings(self):
        return self._request('https://www.leitstellenspiel.de/api/buildings').json()

    def get_credits(self):
        return self._request('https://www.leitstellenspiel.de/api/credits').json()['credits_user_current']

    def get_allianceinfo(self):
        return self._request('https://www.leitstellenspiel.de/api/allianceinfo').json()

    def get_missions(self):
        c = self._request('https://www.leitstellenspiel.de/').text
        c = c[c.index('missionMarkerAdd'):]
        c = c[:c.index('missionMarkerBulkAdd')].replace("\n", "").replace("\t", "").replace(" ", "")
        c = c.split('missionMarkerAdd(')[1:]

        result = []
        for t in c:
            try:
                # ignore missionInvolved
                if 'missionInvolved' in t:
                    t = t[:t.index('missionInvolved')]

                # process patient info
                if 'patientMarkerAdd' in t:
                    sp = t.split('patientMarkerAdd')
                    t = sp[0]
                    pt = sp[1][:-2]

                if 'prisonerMarkerAdd' in t:
                    sp = t.split('prisonerMarkerAdd')
                    t = sp[0]
                    pt = sp[1][:-2]
                    

                result.append(Mission(json.loads(t[:-2])))
            except Exception as ex:
                print("Parsing Mission JSON failed:", ex)
                print("JSON:", t)

        return result

    def get_mission_type_info(self, mission_type_id):
        s = self._soup(self._request(f'https://www.leitstellenspiel.de/einsaetze/{mission_type_id}'))
        table_data = [extract_table_data(x) for x in s.find_all('table', { 'class' : 'table table-striped' })]
        return MissionTypeInfo(table_data)

    def get_mission_state(self, mission_id):
        r = self._request(f'https://www.leitstellenspiel.de/missions/{mission_id}')
        s = self._soup(r)
        
        try:
            if len(s.select("#mission_vehicle_driving")) > 0:
                s_table = s.select("#mission_vehicle_driving")[0]
                
                # basic data
                table_data = extract_table_text(s_table)
                raw_vehicle_names = [x[1] for x in table_data]
                
                vehicles_on_way = [v[v.index("(")+1:v.index(")")] for v in raw_vehicle_names[1:]]

                # advanced data
                table_html = extract_table_html(s_table)
                table_html_r1 = [str(x[1]).replace("\n", "").replace("\r", "") for x in table_html]
                arrival_countdowns = {y[1]: y[0] for y in [x.split("(")[1].replace(")", "").split(", ") for x in re.findall(r"vehicleArrivalCountdown\([0-9]*, [0-9]*, [0-9]*\)", r.text)]}

                vehicle_ids = []
                vehicles_on_way_arrivals = []
                for r1 in table_html_r1[1:]:
                    vehicle_id_raw = r1[r1.index('vehicle_id="')+len('vehicle_id="'):]
                    vehicle_id = vehicle_id_raw[:vehicle_id_raw.index('"')]
                    vehicle_ids.append(vehicle_id)
                    vehicles_on_way_arrivals.append(int(arrival_countdowns[vehicle_id]))

                # print(vehicle_ids)
                # print(vehicles_on_way_arrivals)
                    
            else:
                vehicles_on_way = []
                vehicles_on_way_arrivals = []
        except Exception as ex:
            print(chalk.red("Fallback: vehicles_on_way = []"), ex)
            vehicles_on_way = []
            vehicles_on_way_arrivals = []

        try:
            if len(s.select("#mission_vehicle_at_mission")) > 0:
                vehicle_table = extract_table_text(s.select("#mission_vehicle_at_mission")[0])
                # print("vehicles_at_mission", vehicle_table)
                vehicles_at_mission = [x[1] for x in vehicle_table if len(x) > 1][1:]
                vehicles_at_mission = [v[v.index("(")+1:v.index(")")] for v in vehicles_at_mission]

            else:
                vehicles_at_mission = []
        except Exception as ex:
            print("Fallback: vehicles_at_mission = []", ex)
            vehicles_at_mission = []

        speak_urls = []
        vehicles_missing = []
        if len(s.select("div.alert.alert-danger")) > 0:
            for alert in s.select("div.alert.alert-danger"):
                txt = alert.get_text(strip=True)
                if len(txt) != 0:
                    if "Sprechwunsch" in txt or "Gefangene" in txt:
                        print(" > !!SPRECHWUNSCH!!")
                        if "Wirklich alle entlassen?" in r.text:
                            print(" > > Captives")
                            self.release_captives(mission_id)
                        else:
                            print(" > > RTW")
                            try:
                                speak_url = alert.find('a').get('href')
                                speak_urls.append(speak_url)
                            except Exception as ex:
                                print("Sprechwunsch - Error", ex)
                    elif ": " in txt:
                        if "," in txt:
                            for itm in txt[txt.index(": ")+2:].split(","):
                                vehicles_missing.append(itm.strip())
                        else:
                            vehicles_missing.append(txt[txt.index(": ")+2:].strip())
                    else:
                        vehicles_missing.append(txt)
                    

        return MissionState(vehicles_on_way, vehicles_at_mission, vehicles_missing, speak_urls, vehicles_on_way_arrivals)

    def _get_authenticity_token(self, mission_id):
        s = self._soup(self._request(f'https://www.leitstellenspiel.de/missions/{mission_id}'))
        token = s.find('input', {'name': 'authenticity_token'}).get('value')
        return token

    def add_vehicles_to_mission(self, mission_id, vehicle_ids, dry_run=True):
        try:
            token = self._get_authenticity_token(mission_id)
        except:
            return False

        data = [
            ('utf8', '\u2713'),
            ('authenticity_token', token),
            ('commit', 'Alarmieren'),
            ('next_mission', '0'),
            ('alliance_mission_publish', '0'),
        ]

        for v_id in vehicle_ids:
            data.append(('vehicle_ids[]', v_id))

        if not dry_run:
            r = self.session.post(f'https://www.leitstellenspiel.de/missions/{mission_id}/alarm', data=data, allow_redirects=False)
            if r.status_code != 302:
                print("STATUS NOT 302")
                print(r)
                print(r.text)
        else:
            print("DRY RUN", mission_id, vehicle_ids)

        return True

    def set_patient_transport(self, url, url_extension, dry_run=True):
        if not dry_run:
            self.session.get(f'https://www.leitstellenspiel.de{url}{url_extension}')
        else:
            print("DRY RUN", f'https://www.leitstellenspiel.de{url}{url_extension}')

    def get_hospital_free_beds(self, hospital_id):
        r = self.session.get(f"https://www.leitstellenspiel.de/buildings/{hospital_id}")
        res = re.findall(r"Derzeit liegen [0-9]+ Patienten in der Notaufnahme\. Deine Notaufnahme kann maximal [0-9]+ Patienten aufnehmen", r.text)[0]
        res = ''.join(c for c in res if c in "0123456789 ")
        res = [x for x in res.split(" ") if len(x) > 0]
        return int(res[1]) - int(res[0]) 

    def release_captives(self, mission_id):
        try:
            token = self._get_authenticity_token(mission_id)
        except:
            return False

        data = [
          ('_method', 'post'),
          ('authenticity_token', token),
        ]

        print("release_captives:", mission_id)
        r = self.session.post(f"https://www.leitstellenspiel.de/missions/{mission_id}/gefangene/entlassen", data=data, allow_redirects=False)
        print("release_captives:", r)

    def hire_people(self, building_id):
        self.session.get(f"https://www.leitstellenspiel.de/buildings/{building_id}/hire_do/3")

    def mission_generate(self):
        r = self.session.get('https://www.leitstellenspiel.de/mission-generate?_=' + str(time.time()))
