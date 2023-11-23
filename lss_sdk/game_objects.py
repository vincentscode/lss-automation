import json

class Person:
    def __init__(self, j):
        self.full_json = j

        self.id = j['id']
        self.name = j['name'] if len(j["name"]) > 0 else None
        self.schooling = j["schooling"] if len(j["schooling"]) > 0 else None
        self.bound_to_vehicle = j["bound"] if len(j["bound"]) > 0 else None
        self.status = j["status"] if len(j["status"]) > 0 else None
        self.options = j["options"] if len(j["options"]) > 0 else None

    def __repr__(self):
        return f'ID: {self.id} | Schooling: {self.schooling} | Bound: {self.bound_to_vehicle}'

    def __str__(self):
        return self.__repr__()


class Vehicle:
    def __init__(self, j):
        self.full_json = j

        self.id = j['id']
        self.type_id = j['vehicle_type']
        self.name = j['caption']
        self.state = j['fms_real']

        self.building_id = j['building_id']
        
        self.assigned_personnel_count = j['assigned_personnel_count'] if j['assigned_personnel_count'] is not None else 0

    def __repr__(self):
        return f'ID: {self.id} | State: {self.state} | Type: {self.type_id} | Name: {self.name}'

    def __str__(self):
        return self.__repr__()

class VehicleType:
    def __init__(self, t):
        self.full_json = t

        self.name = t['caption']
        self.cost_coins = t["coins"]
        self.cost_credits = t["credits"]

        self.min_personnel = t["minPersonnel"]
        self.max_personnel = t["maxPersonnel"]

        self.wtank = t["wtank"] if "wtank" in t else None
        self.pumpcap = t["pumpcap"] if "pumpcap" in t else None

        self.possible_buildings = t["possibleBuildings"]

        schooling_info = t["schooling"] if "schooling" in t else None
        if schooling_info is not None:
            all_schooling_types_count = {}
            for school_type in schooling_info.keys():
                for schooling_type in schooling_info[school_type].keys():
                    k = list(schooling_info[school_type][schooling_type].keys())[0]
                    if k == "all":
                        all_schooling_types_count[schooling_type] = True
                    elif k == "min":
                        all_schooling_types_count[schooling_type] = schooling_info[school_type][schooling_type][k]
                    else:
                        raise Exception("Unknown Schooling Count Type " + k)
            self.schooling = all_schooling_types_count
        else:
            self.schooling = {}


    def __repr__(self):
        return f'ID: {self.id} | State: {self.state} | Type: {self.type_id} | Name: {self.name}'

    def __str__(self):
        return self.__repr__()

class VehicleMarker:
    def __init__(self, j):
        self.full_json = j

        self.id = j['id']
        self.name = j['caption']
        self.route = [f"{x[0]},{x[1]}" for x in json.loads(j['s'])]
        self.location = self.route[0]
        self.target_location = self.route[-1]
        self.state = j['fms_real']

    def __repr__(self):
        return f'ID: {self.id} | Location {self.location}'

    def __str__(self):
        return self.__repr__()

class Mission:
    def __init__(self, t):
        self.full_json = t

        self.caption = t['caption']

        self.id = t['id']
        self.mission_type_id = t['mtid']
        self.alliance_id = t['alliance_id']
        self.user_id = t['user_id']

        self.current_value = t['live_current_value']
        self.completion = int((1.0 - (float(self.current_value) / 100.0))*100)
        self.location = f"{t['latitude']},{t['longitude']}"

        self.start_in = t['sw_start_in']

        self.icon = t['icon']
        self.color = self.icon.split("_")[-1]
        if int(t['date_end']) - int(t['date_now']) > 0 and self.color == "gruen":
            self.time_until_end = int(t['date_end']) - int(t['date_now'])
        else:
            self.time_until_end = -1

        self.patients_count = t['patients_count']
        self.prisoners_count = t['prisoners_count']

    def __repr__(self):
        return ' '.join([str(x) for x in [self.caption, '| ID:', self.id, "|", 'Lookup-ID:', self.mission_type_id, "|", 'C:', str(self.completion) + "%", 'Start in:', self.start_in]])

    def __str__(self):
        return self.__repr__()

class MissionState:
    def __init__(self, vehicles_on_way, vehicles_at_mission, vehicles_missing, speak_urls, vehicles_on_way_arrivals, vehicles_available_for_mission):
        self.vehicles_on_way = vehicles_on_way
        self.vehicles_at_mission = vehicles_at_mission
        self.vehicles_missing = vehicles_missing
        self.speak_urls = speak_urls
        self.vehicles_on_way_arrivals = vehicles_on_way_arrivals
        self.vehicles_available_for_mission = vehicles_available_for_mission

class MissionRequirement:
    def __init__(self, name, amount, probability=1.0):
        self.name = name
        self.amount = amount
        self.probability = probability

    def __repr__(self):
        if self.probability != 1:
            return f'<{self.name} x {self.amount} @ {str(int(float(self.probability)))}%>'
        else:
            return f'<{self.name} x {self.amount}>'

    def __str__(self):
        return self.__repr__()

class MissionTypeInfo:
    req_prob_dict = {
        "Benötigte Drehleitern": "Drehleiter Anforderungswahrscheinlichkeit",
        "Benötigte Feuerwehrkräne (FwK)": "FwK Anforderungswahrscheinlichkeit",
        "Benötigte Rüstwagen": "Rüstwagen Anforderungswahrscheinlichkeit",
        "Benötigte Streifenwagen": "Streifenwagen Anforderungswahrscheinlichkeit",
        "Benötigte ELW 1": "ELW 1 Anforderungswahrscheinlichkeit",
        "Benötigte ELW 2": "ELW 2 Anforderungswahrscheinlichkeit",
        "Benötigte Löschfahrzeuge": "Löschfahrzeuge Anforderungswahrscheinlichkeit",
        "Benötigte GW-Öl": "GW-Öl Anforderungswahrscheinlichkeit",
        "Benötigte GW-A": "GW-A Anforderungswahrscheinlichkeit",
        "Benötigte GW-Höhenrettung": "GW-Höhenrettung Anforderungswahrscheinlichkeit",
        "Benötigte DHuFüKw": "DHuFüKw Anforderungswahrscheinlichkeit",
        "Benötigte Feuerlöschpumpen": "Feuerlöschpumpen Anforderungswahrscheinlichkeit",
        "Benötigte GW L 2 Wasser": "GW L 2 Wasser Anforderungswahrscheinlichkeit",
        "Benötigte Außenlastbehälter (allgemein)": "Außenlastbehälter (allgemein) Anforderungswahrscheinlichkeit",
        "Benötigte GW-Mess": "GW-Mess Anforderungswahrscheinlichkeit",
        "Benötigte GW-Gefahrgut": "GW-Gefahrgut Anforderungswahrscheinlichkeit",
        "Benötigte Dekon-P": "Dekon-P Anforderungswahrscheinlichkeit",
        "Benötigte Turbolöscher": "Turbolöscher Anforderungswahrscheinlichkeit",
        "Benötigte Teleskopmasten": "Teleskopmasten Anforderungswahrscheinlichkeit",
        "Benötigte GW-Werkfeuerwehr": "GW-Werkfeuerwehr Anforderungswahrscheinlichkeit",
        "Benötigte ULF mit Löscharm": "ULF mit Löscharm Anforderungswahrscheinlichkeit",
        "Benötigte GKW": "GKW Anforderungswahrscheinlichkeit",
        "Benötigte MTW-TZ": "MTW-TZ Anforderungswahrscheinlichkeit",
        "Benötigte MzKW": "MzKW Anforderungswahrscheinlichkeit",
        "Benötigte leBefKw": "leBefKw Anforderungswahrscheinlichkeit",
        "Benötigte GruKw": "GruKw Anforderungswahrscheinlichkeit",
        "Benötigte FüKw": "FüKw Anforderungswahrscheinlichkeit",
        "Benötigte Rettungshundestaffeln": "Rettungshundestaffeln Anforderungswahrscheinlichkeit",
        "Benötigte GefKw": "GefKw Anforderungswahrscheinlichkeit",
        "Benötigte Polizeihubschrauber": "Polizeihubschrauber Anforderungswahrscheinlichkeit",
    }

    def __init__(self, tables):
        # metadata table
        try:
            self.generator = tables[0]['Generiert von']
        except:
            self.generator = "Unknown"
        try:
            self.credits = tables[0]['Credits im Durchschnitt']
        except:
            self.credits = 0
        try:
            self.kind = tables[0]['Einsatzart']
        except:
            self.kind = "Unknown"
        
        # requirement table
        self.requirements = []
        try:
            for req in tables[1]:
                if req.startswith('Benötigte'):
                    if req in self.req_prob_dict:
                        prob_key = self.req_prob_dict[req]
                        # print(req, "=>", prob_key)
                    else:
                        print("UNKNOWN", req, "=> req_prob")
                        prob_key = "unknown"

                    if prob_key in tables[1]:
                        prob = tables[1][prob_key]
                    else:
                        prob = 1.0

                    self.requirements.append(MissionRequirement(req[len('Benötigte '):], int(tables[1][req]), prob))
        except:
            pass


        # additional info table
        # patients
        self.min_patients = int(tables[2].get('Mindest Patientenanzahl', 0))
        self.max_patients = int(tables[2].get('Maximale Patientenanzahl', 0))
        self.patient_transport_probability = int(tables[2].get('Wahrscheinlichkeit, dass ein Patient transportiert werden muss', 100))
        vehicle_probilities = {}
        for entry in tables[2]:
            if entry.endswith(' Anforderungswahrscheinlichkeit'):
                vehicle_probilities[entry.replace(' Anforderungswahrscheinlichkeit', '').strip()] = tables[2][entry]

        for v, p in vehicle_probilities.items():
            self.requirements.append(MissionRequirement(v, 1, 1.0))
            # print("Patients additional req ", self.requirements[-1])
        if self.min_patients > 0 and self.max_patients >= self.min_patients:
            num_rtw = round(sum([self.min_patients, self.max_patients])/2)
            # print("Patients: ", self.min_patients, self.max_patients, "=>", num_rtw, "RTW")
            self.requirements.append(MissionRequirement("RTW", num_rtw, 1.0))


    def __repr__(self):
        return f'{self.generator} | {self.credits} Credits ==> [{", ".join([str(x) for x in self.requirements])}]'

    def __str__(self):
        return self.__repr__()

class Building:
    building_type_names_by_id = {
        0: "firehouse",
        1: "fire_school",
        2: "ambulance_station",
        3: "rescue_school",
        4: "hospital",
        5: "rescue_copter_station",
        6: "police_station",
        7: "dispatch_center",
        8: "police_school",
        9: "technical_aid_organization",
        10: "technical_aid_organization_school",
        11: "riot_police",
        12: "rapid_deployment_group",
        13: "police_copter_station",
        14: "staging_area",
        15: "water_watch",
        17: "police_special_forces",
        21: "rescue_dog_unit",
        22: "complex",
        23: "complex"
    }
    building_name_translations = [
        "Feuerwache",
        "Feuerwehrschule",
        "Rettungswache",
        "Rettungsschule",
        "Krankenhaus",
        "Rettungshubschrauber-Station",
        "Polizeiwache",
        "Leitstelle",
        "Polizeischule",
        "THW-Ortsverband",
        "THW Bundesschule",
        "Bereitschaftspolizei",
        "Schnelleinsatzgruppe (SEG)",
        "Polizeihubschrauberstation",
        "Bereitstellungsraum",
        "Wasserrettung",
        "Verbandszellen",
        "Polizei-Sondereinheiten",
        "Feuerwache (Kleinwache)",
        "Polizeiwache (Kleinwache)",
        "Rettungswache (Kleinwache)",
        "Rettungshundestaffel",
        "Großer Komplex",
        "Kleiner Komplex"
    ]

    def __init__(self, t):
        self.full_json = t

        self.id = t['id']
        self.name = t['caption']
        self.location = [t['latitude'], t['longitude']]
        self.personal_count = t['personal_count']
        self.level = t['level']
        self.building_type = t['building_type']
        self.building_type_name = Building.building_type_names_by_id[self.building_type]
        self.extensions = t['extensions']
        self.leitstelle_building_id = t['leitstelle_building_id']
        self.small_building = t['small_building']
        self.enabled = t['enabled']
        self.personal_count_target = t['personal_count_target']
        self.hiring_phase = t['hiring_phase']

        if self.building_type_name == "hospital":
            self.patient_count = t['patient_count']
            self.complex_type = t['complex_type']


        if 'schoolings' in t:
            self.schoolings = t['schoolings']

    def __repr__(self):
        return f'ID: {self.id} | Name: {self.name} | Type: {self.building_type_name} ({self.building_type}) [L: {self.level}] | Location: {self.location}'

    def __str__(self):
        return self.__repr__()

class BuildingExtensionTypeInfo:
    def __init__(self, t):
        self.full_json = t

        self.name = t["caption"]
        self.cost_coins = t["coins"]
        self.cost_credits = t["credits"]
        self.build_duration = t["duration"]

        self.gives_parking_lots = t["givesParkingLots"] if "givesParkingLots" in t else 0

        self.is_vehicle_extension = t["isVehicleExtension"] if "isVehicleExtension" in t else False
        
        self.unlocks_vehicle_types = t["unlocksVehicleTypes"] if "unlocksVehicleTypes" in t else []

        self.parking_lot_reservations = t["parkingLotReservations"] if "parkingLotReservations" in t else None

        self.available = t["available"] if "available" in t else None

        self.building_in_progress = False

    def __repr__(self):
        return f'Name: {self.name} | Build Duration: {self.build_duration} | Parking: +{self.gives_parking_lots} | Unlocks: {self.unlocks_vehicle_types}'

    def __str__(self):
        return self.__repr__()

class BuildingTypeInfo:
    def __init__(self, t):
        self.full_json = t

        self.name = t["caption"]
        self.cost_coins = t["coins"]
        self.cost_credits = t["credits"]
        self.max_level = t["maxLevel"]

        if "extensions" in t:
            self.extensions = [BuildingExtensionTypeInfo(x) for x in t["extensions"]]
        else:
            self.extensions = []

        if "startParkingLots" in t:
            self.start_parking_lots = t["startParkingLots"]
        else:
            self.start_parking_lots = None
        
        if "startVehicles" in t:
            self.start_vehicle_options = t["startVehicles"]

        if "schoolingTypes" in t:
            self.schooling_types = t["schoolingTypes"]
        else:
            self.schooling_types = []

        if "startPersonnel" in t:
            self.start_personnel = t["startPersonnel"]

        if "startClassrooms" in t:
            self.start_classrooms = t["startClassrooms"]

    def __repr__(self):
        return f'Name: {self.name} | Extensions: {len(self.extensions)} | MaxLevel: {self.max_level}'

    def __str__(self):
        return self.__repr__()
