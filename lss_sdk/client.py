import requests
import json
import re
import time
from bs4 import BeautifulSoup
import lxml
import lxml.html
from lxml.cssselect import CSSSelector
from lxml.etree import tostring
import cchardet
from yachalk import chalk
from .helpers import *
from .game_objects import *
import logging
import random

class SessionCloak:
    def __init__(self, session):
        self.session = session
        self.logging_enabled = False
        self.debug_logging_enabled = False
        if self.debug_logging_enabled:
            logging.basicConfig(level=logging.DEBUG)

        self.last_lss_response = None

        self.url_logging_filter = [
            "https://www.leitstellenspiel.de/osrmroute/viaroute",
            "https://osrm.missionchief.com/viaroute"
        ]

        self.permanent_url_caches = {
            "https://www.leitstellenspiel.de/einsaetze/": {}
        }

    def random_delay(self, avg_seconds = 0.1):
        time.sleep(random.random()*2*avg_seconds)

    def get(self, url, params=None, allow_redirects=True):
        save_cache = False
        for url_category in self.permanent_url_caches:
            if url.startswith(url_category) and params is None:
                if url in self.permanent_url_caches[url_category]:
                    if self.logging_enabled and url not in self.url_logging_filter:
                        print(chalk.grey(f"SC> GET {url} (!!CACHED!!)"))
                    return self.permanent_url_caches[url_category][url]
                else:
                    save_cache = True

        if self.logging_enabled and url not in self.url_logging_filter:
            print(chalk.grey(f"SC> GET {url} ({params})"))

        
        # if url not in self.url_logging_filter:
        #     self.random_delay()

        r = self.session.get(url, params=params, allow_redirects=allow_redirects)

        if save_cache:
            self.permanent_url_caches[url_category][url] = r

        if url.startswith("https://www.leitstellenspiel.de/"):
            self.last_lss_response = r

        return r


    def post(self, url, data, params=None, allow_redirects=True):
        if self.logging_enabled and url not in self.url_logging_filter:
            print(chalk.grey(f"SC> POST {url} [{data}] ({params})"))

        self.random_delay()

        return self.session.post(url, data=data, params=params, allow_redirects=allow_redirects)

class Client:
    def __init__(self, headers):
        self._session = requests.Session()
        self._session.headers.update(headers)

        self.session = SessionCloak(self._session)

        self.vehicle_batch = []
        self.vehicle_batch_mission_id = 0

        self.building_cache_time = 0
        self.building_cache = []

        self.driving_vehicle_marker_cache_time = 0
        self.driving_vehicle_marker_cache = []

    def _get(self, url):
        return self.session.get(url)

    def _soup(self, response):
        return BeautifulSoup(response.content, 'lxml')

    def _soup_string(self, html_string):
        return BeautifulSoup(html_string, 'lxml')

    def _lxml(self, response):
        return lxml.html.fromstring(response.content)

    def get_vehicle_states(self):
        return self._get('https://www.leitstellenspiel.de/api/vehicle_states').json()

    def get_vehicles(self):
        res = self._get('https://www.leitstellenspiel.de/api/vehicles')
        if res.status_code != 200:
            print("get_vehicles failed:")
            print(res)
            print(res.headers)
            print(res.text)
        res_j = res.json()
        return [Vehicle(j) for j in res_j]

    def get_buildings(self):
        if time.time() - self.building_cache_time > 5 * 60: # cache lasts 5 minutes
            self.building_cache_time = time.time()
            self.building_cache = self._get('https://www.leitstellenspiel.de/api/buildings').json()
        return self.building_cache

    def get_credits(self):
        return self._get('https://www.leitstellenspiel.de/api/credits').json()['credits_user_current']

    def get_allianceinfo(self):
        return self._get('https://www.leitstellenspiel.de/api/allianceinfo').json()

    def get_missions(self):
        c = self._get('https://www.leitstellenspiel.de/').text
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

    def get_building_abuse_detected(self):
        return "anti-abuse-warning" in self._get('https://www.leitstellenspiel.de/').text

    def get_mission_type_info(self, mission_type_id, mission_id):
        # r = self._get(f'https://www.leitstellenspiel.de/einsaetze/{mission_type_id}?mission_id={mission_id}')
        r = self._get(f'https://www.leitstellenspiel.de/einsaetze/{mission_type_id}')
        s = self._soup(r)
        tables = s.find_all('table', { 'class' : 'table table-striped' })
        table_data = [extract_table_data(x) for x in tables]
        return MissionTypeInfo(table_data)

    def get_mission_state(self, mission_id):
        # print("get_mission_state > req")
        r = self._get(f'https://www.leitstellenspiel.de/missions/{mission_id}')
        # print("get_mission_state < req")
        # s = self._soup(r)
        l = self._lxml(r)


        try:
            x_tables = l.cssselect("#vehicle_show_table_all")
            x_table = self._soup_string(lxml.etree.tostring(x_tables[0]))
            trs = x_table.select(".vehicle_select_table_tr")

            vehicles_available_for_mission = []
            for x in trs:
                name = x.attrs["vehicle_caption"]
                v_id = x.attrs["id"].replace("vehicle_element_content_", "")

                coords = x.select(f'#vehicle_sort_{v_id}')[0].attrs["class"][0]
                # -> 'alarm_distance_49_968233678966726_7_911357629532857_1'
                coords = coords.replace("alarm_distance_", "")
                # -> '49_968233678966726_7_911357629532857_1'
                lat_a, lat_b, lon_a, lon_b, _ = coords.split("_")
                lat = float(f"{lat_a}.{lat_b}")
                lon = float(f"{lon_a}.{lon_b}")
                coords = (lat, lon)

                vehicles_available_for_mission.append((name, v_id, coords))
        except Exception as ex:
            print(chalk.red("Fallback: vehicles_available_for_mission = []"), ex)
            vehicles_available_for_mission = []
        
        try:
            # s_tables = s.select("#mission_vehicle_driving")
            l_tables = l.cssselect("#mission_vehicle_driving")
            if len(l_tables) > 0:
                # s_table = s_tables[0]
                s_table = self._soup_string(lxml.etree.tostring(l_tables[0]))
                
                # basic data
                table_data = extract_table_text(s_table)
                raw_vehicle_names = [x[1] for x in table_data if len(x) >= 2]
                
                vehicles_on_way = [v[v.index("(")+1:v.index(")")] for v in raw_vehicle_names[1:]]

                # advanced data
                table_html = extract_table_html(s_table)
                table_html_r1 = [str(x[1]).replace("\n", "").replace("\r", "") for x in table_html if len(x) >= 2]
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
            # vehicle_tables = s.select("#mission_vehicle_at_mission")
            vehicle_tables = l.cssselect("#mission_vehicle_at_mission")
            if len(vehicle_tables) > 0:
                # vehicle_table = extract_table_text(vehicle_tables[0])
                vehicle_table = extract_table_text(self._soup_string(lxml.etree.tostring(vehicle_tables[0])).select("#mission_vehicle_at_mission")[0])
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
        # alerts = s.select("div.alert.alert-danger")
        alerts = l.cssselect("div.alert.alert-danger")
        if len(alerts) > 0:
            for alert in alerts:
                alert = self._soup_string(lxml.html.tostring(alert))
                # print("a>", alert)
                txt = alert.get_text(strip=True)
                if "Benötigtes Wasser:" in txt:
                    txt_split = txt.split("Benötigtes Wasser:")
                    if len(txt_split) == 1:
                        txt = ""
                    else:
                        txt = txt_split[0]
                if len(txt) != 0:
                    if "Sprechwunsch" in txt or "Gefangene" in txt:
                        if "Wirklich alle entlassen?" in r.text:
                            self.release_captives(mission_id)
                        else:
                            try:
                                speak_url = [x.get('href') for x in alert.find_all('a')]
                                for speak_url_u in speak_url:
                                    speak_urls.append(speak_url_u)
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
                    

        return MissionState(vehicles_on_way, vehicles_at_mission, vehicles_missing, speak_urls, vehicles_on_way_arrivals, vehicles_available_for_mission)

    def _get_authenticity_token(self, mission_id=None):
        token = None
        if not mission_id:
            if self.session.last_lss_response:
                s = self._soup(self.session.last_lss_response)
                self.session.last_lss_response = None
            else:
                # print("_get_authenticity_token: csrf fallback")
                s = self._soup(self._get(f'https://www.leitstellenspiel.de/'))

            token = s.find('meta', {'name': 'csrf-token'}).get('content')
        else:
            s = self._soup(self._get(f'https://www.leitstellenspiel.de/missions/{mission_id}'))
            token = s.find('input', {'name': 'authenticity_token'}).get('value')

        return token

    def flush_vehicle_batch(self, dry_run=False):
        mission_id = self.vehicle_batch_mission_id
        # print(" > > > Flushing", len(self.vehicle_batch), "vehicle(s) for", mission_id)

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

        for v_id in self.vehicle_batch:
            data.append(('vehicle_ids[]', v_id))

        if not dry_run:
            r = self.session.post(f'https://www.leitstellenspiel.de/missions/{mission_id}/alarm', data=data, allow_redirects=False)
            if r.status_code != 302:
                print("STATUS NOT 302")
                print(r)
                print(r.text)
        else:
            print("DRY RUN", mission_id, vehicle_ids)

        self.vehicle_batch = []
        self.vehicle_batch_mission_id = 0

        return True


    def add_vehicles_to_mission(self, mission_id, vehicle_ids, dry_run=True, max_batch_size=2500):
        debug_print = False

        if debug_print: print("[CLIENT] > add_vehicles_to_mission", mission_id, vehicle_ids)
        if mission_id != self.vehicle_batch_mission_id:
            if debug_print: print("[CLIENT] | add_vehicles_to_mission: flush old batch")
            if len(self.vehicle_batch) != 0:
                self.flush_vehicle_batch(dry_run=dry_run)
            self.vehicle_batch_mission_id = mission_id
            if debug_print: print("[CLIENT] | add_vehicles_to_mission: flushed old batch")

        if debug_print: print("[CLIENT] | add_vehicles_to_mission: add to new batch")
        for vid in vehicle_ids:
            self.vehicle_batch.append(vid)

        if len(self.vehicle_batch) >= max_batch_size:
            if debug_print: print("[CLIENT] | add_vehicles_to_mission: flush full batch")
            self.flush_vehicle_batch(dry_run=dry_run)
            if debug_print: print("[CLIENT] | add_vehicles_to_mission: flushed full batch")

        if debug_print: print("[CLIENT] < add_vehicles_to_mission")
        return True

    def set_patient_transport(self, url, url_extension, dry_run=True):
        if not dry_run:
            self.session.get(f'https://www.leitstellenspiel.de{url}{url_extension}')
        else:
            print("DRY RUN", f'https://www.leitstellenspiel.de{url}{url_extension}')

    def get_hospital_free_beds(self, hospital_id):
        r = self.session.get(f"https://www.leitstellenspiel.de/buildings/{hospital_id}")
        regex = r"Derzeit liegen [0-9]+ Patienten in der Notaufnahme oder werden transportiert\. Deine Notaufnahme kann maximal [0-9]+ Patienten aufnehmen\."
        res = re.findall(regex, r.text)[0]
        res = ''.join(c for c in res if c in "0123456789 ")
        res = [x for x in res.split(" ") if len(x) > 0]
        return int(res[1]) - int(res[0]) 

    def get_building_info(self, building_id):
        r = self.session.get(f"https://www.leitstellenspiel.de/api/buildings/{building_id}")
        return r.json()

    def get_building_personnel(self, building_id):
        r = self._get(f"https://www.leitstellenspiel.de/buildings/{building_id}/personals")
        s = self._soup(r)
        table = s.find_all('table', { 'class' : 'table table-striped' })[0]
        table_data = extract_table_text(table)
        table_html = extract_table_html(table)
        table_header = [
            "name", "schooling", "bound", "status", "options"
        ]
        table_content = table_data[1:]
        table_content_html = table_html[1:]

        personnel = []
        for l in table_content:
            l_data = {}
            for i in range(len(table_header)):
                l_data[table_header[i]] = l[i]
            l_html = str(table_content_html[table_content.index(l)])
            l_data["id"] = int(re.findall(r'href="/personals/[0-9]{1,}"', l_html)[0].replace('href="/personals/', '').replace('"', ''))

            personnel.append(Person(l_data))


        return personnel

    def add_building_extension(self, building_id, extension_id):
        try:
            token = self._get_authenticity_token()
        except:
            return False
        
        data = {
            'authenticity_token': token,
            '_method': 'post',
        }

        r = self.session.post(f"https://www.leitstellenspiel.de/buildings/{building_id}/extension/credits/{extension_id}", data=data)

    def bind_person_to_vehicle(self, vehicle_id, person_id):
        try:
            token = self._get_authenticity_token()
        except:
            return False
        
        additional_headers = {
            'Referer': f'https://www.leitstellenspiel.de/vehicles/{vehicle_id}/zuweisung',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'accept': '*/*',
            'x-csrf-token': token,
            'x-requested-with': 'XMLHttpRequest',
        }
        res = self.session.session.post(f'https://www.leitstellenspiel.de/vehicles/{vehicle_id}/zuweisungDo/{person_id}', headers=additional_headers)
        if not '"label label-success"' in res.text:
            print(res.text)
            raise Exception("Binding person to vehicle failed. See above for res.text.")

    def get_free_schools_for_schooling_type(self, schooling_type):
        school_type_to_building_type = {
            "Feuerwehr": 1,
            "Rettungsdienst": 3,
            "Polizei": 8,
            "THW": 10,
        }
        building_type = school_type_to_building_type[schooling_type]
        schools_of_type = [Building(x) for x in self.get_buildings() if x["building_type"] == building_type]
        free_schools = [x for x in schools_of_type if len(x.schoolings) < len([e for e in x.extensions if e["caption"] == "Weiterer Klassenraum"])]
        return free_schools

    def school_persons(self, building_id, schooling_type, schooling, personal_ids):
        try:
            token = self._get_authenticity_token()
        except:
            return False
        
        assert len(personal_ids) <= 10

        education_id_lookup = {
            "Feuerwehr": [
                "GW-Messtechnik",
                "GW-Gefahrgut",
                "GW-Höhenrettung",
                "ELW 2",
                "Wechsellader Lehrgang",
                "Dekon-P",
                "Feuerwehrkran",
                "GW-Wasserrettung",
                "GW-Taucher",
                "Notarzt",
                "Flugfeldlöschfahrzeug",
                "Rettungstreppe",
                "Werkfeuerwehr",
                "Intensivpflege",
            ],
            "Polizei": [
                "Zugführer (leBefKw)",
                "Hundertschaftsführer (FüKw)",
                "Polizeihubschrauber",
                "Wasserwerfer",
                "SEK",
                "MEK",
                "Hundeführer (Schutzhund)",
                "Motorradstaffel",
                "Brandbekämpfung",
                "Kriminalpolizei",
                "Dienstgruppenleitung",
            ],
            "Rettungsdienst": [
                "Notarzt",
                "LNA",
                "OrgL",
                "SEG - Einsatzleitung",
                "SEG - GW-San",
                "GW-Wasserrettung",
                "GW-Taucher",
                "Rettungshundeführer (SEG)",
                "Intensivpflege",
            ],
            "THW": [
                "Zugtrupp",
                "Fachgruppe Räumen",
                "Fachgruppe Wassergefahren",
                "Fachgruppe Bergungstaucher",
                "Rettungshundeführer (THW)",
                "Fachgruppe Wasserschaden/Pumpen",
            ]
        }

        education_id = education_id_lookup[schooling_type].index(schooling)

        data = {
            'authenticity_token': token,
            'education': str(education_id),
            'personal_ids[]': [str(x) for x in personal_ids],
            'building_rooms_use': '1',
            'alliance[duration]': '0',
            'alliance[cost]': '0',
            'commit': 'Ausbilden',
            'utf8': '✓',
        }

        res = self.session.post(f'https://www.leitstellenspiel.de/buildings/{building_id}/education', data=data, allow_redirects=False)

        return "https://www.leitstellenspiel.de/schoolings/" in res.text

    def purchase_building(self, building_type_id, lat_long, name):
        try:
            token = self._get_authenticity_token()
        except:
            return False

        address_text = self.session.get('https://www.leitstellenspiel.de/reverse_address', params={
            'latitude': lat_long[0],
            'longitude': lat_long[1],
        }).text

        data = {
            'utf8': '✓',
            'authenticity_token': token,
            'building[building_type]': str(building_type_id),
            'building[name]': name,
            'building[latitude]': lat_long[0],
            'building[longitude]': lat_long[1],
            'build_with_coins': '',
            'build_as_alliance': '',
            'building[address]': address_text,
        }

        extra_data_for_building_type_id = {
            0: {
                'building[start_vehicle_feuerwache]': '30',
                'building[start_vehicle_feuerwache_kleinwache]': ''
            }
        }

        if building_type_id in list(extra_data_for_building_type_id.keys()):
            extra_data = extra_data_for_building_type_id[building_type_id]
            for k in list(extra_data.keys()):
                data[k] = extra_data[k]

        r = self.session.post('https://www.leitstellenspiel.de/buildings', data=data, allow_redirects=False)
        if not 'href="https://www.leitstellenspiel.de/buildings">redirected</a>.</body></html>' in r.text:
            raise Exception()

    def set_leitstelle(self, building_id, leitstelle_id):
        r = self.session.get(f'https://www.leitstellenspiel.de/buildings/{building_id}/leitstelle-set/{leitstelle_id}')

    def purchase_vehicle(self, building_id, vehicle_id):
        r = self.session.get(f'https://www.leitstellenspiel.de/buildings/{building_id}/vehicle/{building_id}/{vehicle_id}/credits?building={building_id}')

    def set_vehicle_fms(self, vehicle_id, fms):
        if not fms in [2, 6]:
            raise Exception()
        r = self.session.get(f'https://www.leitstellenspiel.de/vehicles/{vehicle_id}/set_fms/{fms}')

    def upgrade_building(self, building_id, level):
        params = {
            'level': str(level-1),
        }

        r = self.session.get(f'https://www.leitstellenspiel.de/buildings/{building_id}/expand_do/credits', params=params)

    def release_captives(self, mission_id):
        try:
            token = self._get_authenticity_token(mission_id)
        except:
            return False

        data = [
          ('_method', 'post'),
          ('authenticity_token', token),
        ]

        r = self.session.post(f"https://www.leitstellenspiel.de/missions/{mission_id}/gefangene/entlassen", data=data, allow_redirects=False)

    def hire_people(self, building_id):
        self.session.get(f"https://www.leitstellenspiel.de/buildings/{building_id}/hire_do/3")

    def mission_generate(self):
        r = self.session.get('https://www.leitstellenspiel.de/mission-generate?_=' + str(time.time()))
        # print("mission_generate", r)

    def reset_mission(self, mission_id):
        r = self.session.get(f"https://www.leitstellenspiel.de/missions/{mission_id}/backalarmAll", allow_redirects=False)
        print("reset_mission:", r)
        return r

    def get_vehicle_route(self, vehicle_id):
        r = self._get(f"https://www.leitstellenspiel.de/vehicles/{vehicle_id}/routing")
        vm = VehicleMarker(json.loads((re.findall(r"vehicleDrive.+", r.text)[0]).replace("vehicleDrive(", "").replace(");", "")))
        return vm

    def _get_driving_vehicle_markers(self):
        if time.time() - self.driving_vehicle_marker_cache_time < 1 * 60: # cache lasts 1 Minute
            return self.driving_vehicle_marker_cache

        self.driving_vehicle_marker_cache_time = time.time()
        c = self._get('https://www.leitstellenspiel.de/').text
        self.driving_vehicle_marker_cache = [VehicleMarker(json.loads(x.replace("vehicleDrive(", "").replace(");", ""))) for x in re.findall(r"vehicleDrive.+", c)]
        return self.driving_vehicle_marker_cache

    def get_vehicle_location(self, vehicle, mission_state = None):
        if vehicle.state not in [1, 2]:
            raise Exception("get_vehicle_location: invalid vehicle state", vehicle)

        if mission_state != None:
            # vxa = (name, v_id, (lat, lon))
            for vxa in mission_state.vehicles_available_for_mission:
                if vxa[1] == vehicle.id:
                    print("[!] Using Mission State Location for vehicle")
                    return f"{vxa[2][0]},{vxa[2][1]}"

        if vehicle.state == 1:
            vehicle_markers = [x for x in self._get_driving_vehicle_markers() if x.id == vehicle.id]
            if len(vehicle_markers) == 1:
                vehicle_marker = vehicle_markers[0]
                return vehicle_marker.location
            else:
                # vehicle_marker = self.get_vehicle_route(vehicle.id)
                # return vehicle_marker.location

                return "0,0"

        elif vehicle.state == 2:
            buildings = self.get_buildings()
            vehicle_building = [b for b in buildings if b["id"] == vehicle.building_id][0]
            return f"{vehicle_building['latitude']},{vehicle_building['longitude']}"
        
    def get_vehicle_route_info(self, vehicle_location, mission_location): # e.g '49.98967,7.885277'
        params = (
            ('loc', [vehicle_location, mission_location]),
        )

        r = self.session.get('https://osrm.missionchief.com/viaroute', params=params)
        j = r.json()
        return j

    def renew_vehicle_room(self, building_id):
        r = self.session.get(f'https://www.leitstellenspiel.de/buildings/{building_id}/bereitstellung-verlaengern', allow_redirects=False)
        return r

    def get_daily_options(self):
        r = self._get(f"https://www.leitstellenspiel.de/daily_bonuses")
        s = self._soup(r)
        
        options = []
        for h in s.select('#iframe-inside-container > div > div > form'):
            if 'disabled="disabled"' in str(h):
                continue

            action = h.attrs["action"]
            token = h.find("input", {"name": "authenticity_token"}).attrs["value"]
            options.append((action, token))

        return options

    def submit_daily(self, url_path, token):
        data = {
            'utf8': '✓',
            'authenticity_token': token,
        }

        r = self.session.post(f'https://www.leitstellenspiel.de{url_path}', data=data)
        return r

    def get_claimable_tasks(self):
        r = self._get(f"https://www.leitstellenspiel.de/tasks/index")
        s = self._soup(r)
        button_forms = s.select('#iframe-inside-container > div > div.panel-heading > div:nth-child(1) > span.reward_button > form')

        claimable_tasks = []
        for b in button_forms:
            if 'disabled="disabled"' in str(b):
                continue

            action = b.attrs["action"]
            token = b.find("input", {"name": "authenticity_token"}).attrs["value"]
            claimable_tasks.append((action, token))

        return claimable_tasks

    def claim_task(self, url_path, token):
        data = {
            'authenticity_token': token,
        }

        r = self.session.post(f'https://www.leitstellenspiel.de{url_path}', data=data)
        return r
