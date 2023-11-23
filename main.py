from lss_sdk.client import Client

from utils.stat_writer import StatWriter

from tabulate import tabulate
import builtins
import json
import time
import math
import argparse
from datetime import datetime
from yachalk import chalk
import functools
import operator
import random
from collections.abc import Iterable
from _thread import start_new_thread
import traceback
import config.config as config


parser = argparse.ArgumentParser()
parser.add_argument('--dry', dest='dry', action='store_const', const=True, default=False)
parser.add_argument('--silent', dest='silent', action='store_const', const=True, default=False)
parser.add_argument('--reset-only', dest='rst', action='store_const', const=True, default=False)
args = parser.parse_args()

dry_run = args.dry
silent = args.silent
rst = args.rst
minimum_time_per_mission = .3 # 1.3
miminum_sleep_time = 30 # 60
disable_summary = False
results_only = False
performance_logging = False
high_performance_mode = True
simplify_summary = True
run_renewer = False

ignore_vehicles = [] # disabled vehicles, e.g. Bereitstellungsraum
unuav_v = [] # disabled vehicle types e.g. not owned / no drivers

min_probability_for_direct_required = -1.00

parallel_mission_count_limit = 10000
parallel_mission_count_limit_by_fire_stations_percentage = 2000
always_send_vehicles_to = [147]

max_dist_time = 100000000 # 30 * 60 * 3 # ca. 30 Minutes
max_preparation_time = 120 # 0

closest_vehicle_by_type_consider_only_first_num_vehicles_based_on_rough = 20

headers = config.headers

my_user_id = config.my_user_id

v_translation = {
    # Feuerwehr
    "Feuerlöschpumpe": ["LF 10", "LF 20", "HLF 20"],
    "Feuerlöschpumpen (z. B. LF)": ["LF 10", "LF 20", "HLF 20"],
    "Feuerlöschpumpe (z. B. LF)": ["LF 10", "LF 20", "HLF 20"],
    "Löschfahrzeuge": ["LF 10", "LF 20", "HLF 20"],
    "Löschfahrzeuge (LF)": ["LF 10", "LF 20", "HLF 20"],
    "Löschfahrzeug": ["LF 10", "LF 20", "HLF 20"],
    "Löschfahrzeug (LF)": ["LF 10", "LF 20", "HLF 20"],
    "Tragehilfe (z.B. durch ein LF)": ["LF 10", "LF 20", "HLF 20"],
    "Tragehilfe": ["LF 10", "LF 20", "HLF 20"],
    "LF": [],

    "Drehleitern": ["DLK 23"],
    "Drehleiter": ["DLK 23"],
    "DLK 23": ["DLK 23"],
    "Drehleiter (DLK 23)": ["DLK 23"],
    "Drehleitern (DLK 23)": ["DLK 23"],

    "Außenlastbehälter (allgemein)": [],

    "Rüstwagen": ["HLF 20", "RW"],
    "Rüstwagen oder HLF": ["HLF 20", "RW"],

    "ELW 1": ["ELW 2"],
    "ELW 2": ["ELW 2"],
    "Einsatzleitwagen 1": ["ELW 2"],
    "Einsatzleitwagen 2": ["ELW 2"],

    "SW 2000": ["SW 2000"],
    "GW L 2 Wasser": ["SW 2000"],
    "GW-L2 Wasser, SW 1000, SW 2000 oder Ähnliches": ["SW 2000"],
    "Schlauchwagen (GW-L2 Wasser, SW 1000, SW 2000 oder Ähnliches)": ["SW 2000"],
    "Schlauchwagen (GW-L2 Wasser": ["SW 2000"], # split result
    "SW 1000": [], # split result
    "SW 2000 oder Ähnliches)": [], # split result
    "SW 2000 oder Ähnliches).": [], # split result
    "Feuerlöschpumpen": ["SW 2000"],

    "GW-A": ["GW-A"],
    "GW-Atemschutz": ["GW-A"],

    "GW-Mess": ["GW-Mess", "GW-Messtechnik"],
    "GW-Messtechnik": ["GW-Mess", "GW-Messtechnik"],

    "GW-Gefahrgut": ["GW-Gefahrgut"],

    "GW-Höhenrettung": ["GW-Höhenrettung"],

    "GW-Öl": ["GW-Öl"],

    "Dekon-P": ["Dekon-P"],
    "Wir benötigen noch min. 4 Personen mit Dekon-P Ausbildung.": ["Dekon-P"],
    "Wir benötigen noch min. 3 Personen mit Dekon-P Ausbildung.": ["Dekon-P"],
    "Wir benötigen noch min. 2 Personen mit Dekon-P Ausbildung.": ["Dekon-P"],
    "Wir benötigen noch min. 1 Person mit Dekon-P Ausbildung.": ["Dekon-P"],

    "FwK": ["FwK"],
    "Feuerwehrkran": ["FwK"],
    "Feuerwehrkräne (FwK)": ["FwK"],

    # Werkfeuerwehr
    "GW-Werkfeuerwehr": ["GW-Werkfeuerwehr"],

    "Turbolöscher": ["Turbolöscher"],

    "ULF mit Löscharm": ["ULF mit Löscharm"],
    
    "Teleskopmast": ["TM 50"],
    "Teleskopmasten": ["TM 50"],
    "TM 50": ["TM 50"],

    # Flughafen
    "Flugfeldlöschfahrzeuge": ["FLF"],
    "Flugfeldlöschfahrzeug": ["FLF"],
    "FLF": ["FLF"],
    
    "Rettungstreppe": ["Rettungstreppe"],
    "Rettungstreppen": ["Rettungstreppe"],

    # Rettungsdienst    
    "RTW": ["RTW"],

    "NEF": ["NEF", "NAW"],

    "KTW": ["KTW"],
    
    "LNA": ["KdoW-LNA"],
    
    "KdoW-OrgL": ["KdoW-OrgL"],
    "OrgL": ["KdoW-OrgL"],

    "RTH": ["RTH"],

    "ITW": ["ITW"],

    # Wasserrettung
    "Boot": ["MZB", "Anh MzB"],
    "Boote": ["MZB", "Anh MzB"],
    "Wir benötigen noch min. 1 Person mit GW-Wasserrettung Ausbildung.": ["GW-Wasserrettung"],
    "Wir benötigen noch min. 2 Personen mit GW-Wasserrettung Ausbildung.": ["GW-Wasserrettung"],
    "Wir benötigen noch min. 3 Personen mit GW-Wasserrettung Ausbildung.": ["GW-Wasserrettung"],
    "Wir benötigen noch min. 4 Personen mit GW-Wasserrettung Ausbildung.": ["GW-Wasserrettung"],
    "Wir benötigen noch min. 5 Personen mit GW-Wasserrettung Ausbildung.": ["GW-Wasserrettung"],
    "Wir benötigen noch min. 6 Personen mit GW-Wasserrettung Ausbildung.": ["GW-Wasserrettung"],
    "GW-Taucher": ["GW-Taucher", "Tauchkraftwagen"],
    "GW-Wasserrettung": ["GW-Wasserrettung"],

    # Rettungshunde
    "Rettungshundestaffel/n": ["Rettungshundefahrzeug"],
    "Rettungshundestaffel": ["Rettungshundefahrzeug"],
    "Rettungshundestaffeln": ["Rettungshundefahrzeug"],
    "Rettungshundefahrzeug": ["Rettungshundefahrzeug"],

    # Polizei
    "Streifenwagen": ["FuStW"],
    "FuStW": ["FuStW"],
    "Funkstreifenwagen (Dienstgruppenleitung)": ["FuStW (DGL)"],
    "FuStW (DGL)": ["FuStW (DGL)"],

    "Zivilstreifenwagen": ["Zivilstreifenwagen"],

    "Polizeihubschrauber": ["Polizeihubschrauber"], # ["Außenlastbehälter (allgemein)"]
    "Außenlastbehälter (allgemein)": ["Außenlastbehälter (allgemein)"],

    "DHuFüKw": ["Diensthundeführerkraftwagen", "DHuFüKw"],
    "Diensthundeführerkraftwagen": ["Diensthundeführerkraftwagen", "DHuFüKw"],

    # BePo
    "GruKw": ["GruKw"],
    "leBefKw": ["leBefKw"],
    "GefKw": ["GefKw"],
    "Wasserwerfer": ["WaWe 10"],

    # SEK / MEK
    "SEK-Fahrzeuge": ["SEK - ZF", "SEK - MTF"],
    "SEK-Fahrzeug": ["SEK - ZF", "SEK - MTF"],
    "MEK-Fahrzeuge": ["MEK - ZF", "MEK - MTF"],
    "MEK-Fahrzeug": ["MEK - ZF", "MEK - MTF"],
    "FüKw": ["FüKw"],

    # THW
    "Gerätekraftwagen (GKW)": ["GKW"],
    "GKW": ["GKW"],

    "THW-Einsatzleitung (MTW TZ)": ["MTW-TZ"],
    "MTW-TZ": ["MTW-TZ"],
    
    "THW-Mehrzweckkraftwagen (MzKW)": ["MzKW"],
    "MzKW": ["MzKW"],

    "Radlader (BRmG R)": ["BRmG R"],
    "BRmG R,": ["BRmG R"],
    
    "LKW Kipper (LKW K 9)": ["LKW K 9"],
    "LKW K 9": ["LKW K 9"],

    "Anhänger Drucklufterzeugung": ["Anh DLE"],

    "Schmutzwasserpumpe": ["Anh SwPu", "Anh 7"],
    "Schmutzwasserpumpen": ["Anh SwPu", "Anh 7"],
    "Anh SwPu": ["Anh SwPu", "Anh 7"],
    "27.000 l/min": [("Anh SwPu", "Anh 7"), ("Anh SwPu", "Anh SwPu"), ("Anh 7", "Anh 7")]
    
}

vehicle_limits = {
    "KdoW-LNA": 1,
    "LNA": 1,
    "KdoW-OrgL": 1,
    "OrgL": 1,
}

vehicle_companions = {
    # Trailers (THW)
    "BRmG R": "LKW K 9",
    "Anh DLE": "MLW 5",
    "Anh SwPu": "MLW 4",
    "Anh 7": "LKW 7 Lbw",
}

vehicle_replacements = {
    "ELW 1": "ELW 2",
    "RW": "HLF 20",
}

# generate translation key permutations
for k in list(v_translation.keys()):
    # ff
    v_translation[k + "." + f" Wir benötigen noch min. 1 Feuerwehrmann."] = v_translation[k]
    for f in range(1, 170):
        v_translation[k + "." + f" Wir benötigen noch min. {f} Feuerwehrleute."] = v_translation[k]
    
    # numbers
    for i in [str(x) for x in range(1, 35)]:
        original_value = v_translation[k]
        value_x = []
        for itm in original_value:
            xed = tuple([itm for x in range(1, int(i)+1)])
            value_x.append(xed)

        # > without dot
        v_translation[i + " " + k] = value_x
        
        # > with dot
        v_translation[i + " " + k + "."] = value_x

        # > with Wir benötigen noch min.
        v_translation[i + " " + k + "." + f" Wir benötigen noch min. 1 Feuerwehrmann."] = value_x
        for f in range(1, 120):
            v_translation[i + " " + k + "." + f" Wir benötigen noch min. {f} Feuerwehrleute."] = value_x

for w in range(0, 90000 + 100, 50):
    # 3000 l. Wasser. Wir benötigen noch min. 27 Feuerwehrleute.
    # "Wir benötigen noch min. 8 Feuerwehrleute."
    for f in range(0, 150 + 1):
        if w == 0 and f == 0:
            continue

        if w == 0:
            if f == 1:
                result_string = f"Wir benötigen noch min. {f} Feuerwehrmann."
            else:
                result_string = f"Wir benötigen noch min. {f} Feuerwehrleute."
        elif f == 0:
            result_string = f"{w} l. Wasser."
        else:
            if f == 1:
                result_string = f"{w} l. Wasser. Wir benötigen noch min. {f} Feuerwehrmann."
            else:
                result_string = f"{w} l. Wasser. Wir benötigen noch min. {f} Feuerwehrleute."

        count_lf_w_lf = math.ceil(w / 2000)
        count_lf_w_hlf = math.ceil(w / 1600)
        count_lf_w_tlf = math.ceil(w / 4000)

        count_lf_f_lf = math.ceil(f / 5)
        count_lf_f_hlf = math.ceil(f / 5)
        count_lf_f_tlf = math.ceil(f / 3)

        count_lf  = max([count_lf_f_lf, count_lf_w_lf])
        count_hlf = max([count_lf_f_hlf, count_lf_w_hlf])
        count_tlf = max([count_lf_f_tlf, count_lf_w_tlf])

        # todo: permutations
        v_translation[result_string] = [
            tuple(["LF 20" for _ in range(0, count_lf)]),
            tuple(["HLF 20" for _ in range(0, count_hlf)]),
            # tuple(["TLF 4000" for _ in range(0, count_tlf)]),
        ]
        v_translation[result_string[:-1]] = v_translation[result_string]

c = Client(headers)

stats = StatWriter()

def mission_requester():
    global c, dry_run
    while True:
        try:
            c.mission_generate()
        except:
            print("Mission Requester: Generate failed")
        time.sleep(18)

start_new_thread(mission_requester, ())

def daily_and_task_checker():
    global c
    while True:
        print("Checker: Running")
        try:
            daily_options = c.get_daily_options()
            if len(daily_options) > 0:
                print("Checker: Submitting Daily")
                c.submit_daily(*daily_options[0])

            claimable_tasks = c.get_claimable_tasks()
            for t in claimable_tasks:
                print("Checker: Claiming Task")
                c.claim_task(*t)

        except:
            print("Checker: Failed")

        sleep_time = 60 * 60 + (10-int(random.random()*20)*60)  # every hour +- 10 min
        time.sleep(sleep_time)

start_new_thread(daily_and_task_checker, ())

def renewer():
    global c

    vehicle_room_ids = []

    while True:
        print("renewer: running")
        try:
            for v_r_id in vehicle_room_ids:
                c.renew_vehicle_room(v_r_id)
        except:
            print("renewer failed")

        sleep_time = 60 * 60 + (10-int(random.random()*20)*60)  # every hour +- 10 min
        print("renewer: sleeping", sleep_time/60)
        time.sleep(sleep_time)

if run_renewer:
    start_new_thread(renewer, ())

_print = builtins.print
def print(*args, force=False, no_time=False, color=None, file=None, end="\n"):
    global silent, performance_logging, _print
    
    if silent and not force:
        return

    print_string = " ".join(map(str, args)).replace("\n", "")
    if color is not None:
        print_string = color(print_string)

    if no_time:
        pre_string = ""
    else:
        if not performance_logging:
            pre_string = "[" + datetime.now().strftime('%H:%M:%S') + "] "
        else:
            pre_string = "[" + datetime.now().strftime('%H:%M:%S.%f')[:-3] + "] "
    _print(pre_string + print_string)

builtins.print = print
v_trans_get_func_reduced_cached_cache = {}

def v_trans_get_func_reduced_cached(v_key):
    if not v_key in v_trans_get_func_reduced_cached_cache:
        v_trans_get_func_reduced_cached_cache[v_key] = functools.reduce(operator.iconcat, v_translation[v_key], [])
    return v_trans_get_func_reduced_cached_cache[v_key]

def reset_stuck(missions):
    global c, dry_run
    print(c)
    for m in missions:
        c.reset_mission(m.id)

exact_route_cache = {}
def get_closest_vehicle_by_type(vehicles_by_type, vehicle_info_by_id, v_type, mission, mission_state):
    global c, dry_run, performance_logging
    if performance_logging: print(" > > > get closest_vehicle_by_type", v_type, mission)

    vehicle_distances = {}
    m_loc = mission.location
    vehicles_to_consider = []
    for v in vehicles_by_type[v_type]:
        vehicles_to_consider.append(v)
        if len(vehicles_to_consider) > closest_vehicle_by_type_consider_only_first_num_vehicles_based_on_rough+1:
            break

    v_locs = {v_id: c.get_vehicle_location(vehicle_info_by_id[v_id], mission_state) for v_id in vehicles_to_consider}

    for vxa in mission_state.vehicles_available_for_mission:
        if vxa[0] == v_type and int(vxa[1]) in vehicles_by_type[v_type]:
            v_locs[int(vxa[1])] = f"{vxa[2][0]},{vxa[2][1]}"

    if performance_logging: print(" > > > get closest_vehicle_by_type", "got v_locs")

    v_r_dist = {}
    for v_id in v_locs:
        (vX, vY), (mX, mY) = [float(x) for x in v_locs[v_id].split(",")], [float(x) for x in m_loc.split(",")]
        v_r_dist[v_id] = ((mX - vX)**2 + (mY - vY)**2)**0.5

    itr = 0
    for vbt_id in sorted(v_r_dist, key=v_r_dist.get):
        v_loc = v_locs[vbt_id]
        rough_distance = v_r_dist[vbt_id]

        if m_loc in exact_route_cache.keys() and v_loc in exact_route_cache[m_loc].keys():
            v_m_route = exact_route_cache[m_loc][v_loc]
        else:
            v_m_route = c.get_vehicle_route_info(v_loc, m_loc)
            if not m_loc in exact_route_cache.keys():
                exact_route_cache[m_loc] = {}
            exact_route_cache[m_loc][v_loc] = v_m_route


        v_m_route_time = v_m_route["route_summary"]["total_time"]
        vehicle_distances[vbt_id] = v_m_route_time

        if performance_logging: print(" > > > get closest_vehicle_by_type iterating", itr, vbt_id, v_loc, "rough vs actual", rough_distance, v_m_route_time)

        itr += 1
        if itr > closest_vehicle_by_type_consider_only_first_num_vehicles_based_on_rough:
            if performance_logging: print(" > > > get closest_vehicle_by_type", "===> RETURNING FROM TOP")
            break

    selected_v_id = min(vehicle_distances, key=vehicle_distances.get)

    if performance_logging: print(" > > > get_closest_vehicle_by_type: selected_v_id", selected_v_id, "==>", vehicle_distances[selected_v_id])

    if vehicle_distances[selected_v_id] > max_dist_time:
        return None
    
    if performance_logging: print(" > > > got closest_vehicle_by_type")
    return selected_v_id

if rst:
	reset_stuck(c.get_missions())
	exit()

def check_and_react():
    global c, dry_run
    t0 = time.time()

    next_change_in = 60 # default wait time: 1min

    ### GET VEHICLES
    # print("Getting vehicles")
    # print(" > translations:", len(v_translation))
    available_vehicles = {}
    for k in v_translation.keys():
        available_vehicles[k] = []

    vehicles_by_type = {}
    vehicle_info_by_id = {}
    for v in c.get_vehicles():
        if v.id in ignore_vehicles:
            # print("> ignoring", v)
            continue

        if v.state in [1, 2]:
            if not v.name in vehicles_by_type:
                vehicles_by_type[v.name] = []
            vehicles_by_type[v.name].append(v.id)
            vehicle_info_by_id[v.id] = v

            # for v_key in v_translation:
            #     if v.name in v_translation[v_key] or v.name in v_trans_get_func_reduced_cached(v_key):
            #         available_vehicles[v_key].append(v.id)

    # print("Available:", available_vehicles)
    # print("\n========\n")

    ### GET BUILDINGS & MANAGE HIRING
    buildings = c.get_buildings()
    for b in buildings:
        if b['building_type'] not in [1, 3, 4, 7, 8, 10, 14]:
            if int(b['hiring_phase']) != 3:
                print(b['id'], 'of type', b['building_type'], "> hire")
                c.hire_people(b['id'])

    fire_stations_ct = len([x for x in buildings if x['building_type'] in [0]])
    parallel_mission_count_limit = fire_stations_ct * parallel_mission_count_limit_by_fire_stations_percentage

    ### GET CREDITS
    # print("Getting credits")
    current_credits = c.get_credits()
    stats.report_current_credits(current_credits)
    # print("Available:", current_credits)
    # print("\n========\n")

    ### GET MISSIONS
    # print("Getting missions")
    missions = c.get_missions()
    # print("Available:", [x.name for x in missions])
    # print("\n========\n")

    ### HANDLE MISSIONS
    summary = {
        'Mission': [],
        'MissionID': [],
        'Status': [],
        'Completion': [],
        'Credits': [],
        'Requirements': [],
        'Vehicles': [],
        'MissingVehicles': [],
        'ColorBefore': [],
        'ColorAfter': [],
        'TimeUntilDone': [],
        'TimeVehicelsArrive': [],
    }
    handled_mission_count = 0
    for mission in missions:
        print("HANDLE", mission)
        mt0 = time.time()

        # check if mission should be handled
        if mission.user_id != my_user_id:
            print(" > IGNORE MISSION: NOT FROM ME", mission.user_id, mission, "!=", my_user_id, color=chalk.grey)
            print("", no_time=True)
            continue

        if mission.start_in > max_preparation_time:
            print(" > IGNORE MISSION: TOO FAR IN THE FUTURE", color=chalk.grey)
            print("", no_time=True)
            continue

        # get info
        if performance_logging: print(" > get mission info")
        type_info = c.get_mission_type_info(mission.mission_type_id, mission.id)
        mission_state = c.get_mission_state(mission.id)

        if not results_only:
            print(" > info:", type_info.generator, "|", type_info.credits, "Credits")
            print(" > state:")
            print(" > > vehicles_on_way:", mission_state.vehicles_on_way)
            print(" > > vehicles_at_mission:", mission_state.vehicles_at_mission)
            print(" > > vehicles_missing:", mission_state.vehicles_missing)
            print(" > > speak_urls:", len(mission_state.speak_urls))
            print(" > ")

        summary['Mission'].append(mission.caption)
        summary['MissionID'].append(mission.id)
        summary['Completion'].append(str(mission.completion) + "%")
        summary['Credits'].append(type_info.credits)
        summary['Requirements'].append(str(type_info.requirements))
        summary['ColorBefore'].append(mission.color)
        summary['TimeUntilDone'].append(mission.time_until_end if mission.time_until_end >= 0 else "-")

        stats.report_mission(mission.id, mission.mission_type_id, [v_translation[rv.name] if rv.name in v_translation else "unknown" for rv in type_info.requirements])
        if performance_logging: print(" > got mission info")

        # send patients to hospital or deny transport
        if performance_logging: print(" > handle patients")
        for itm in mission_state.speak_urls:
            none_found = True
            hospital_ids = [str(x['id']) for x in buildings if x['building_type'] in [4]]
            # TODO: choose closest hospital
            random.shuffle(hospital_ids)
            for h_id in hospital_ids:
                if c.get_hospital_free_beds(h_id) > 0:
                    c.set_patient_transport(itm, '/patient/' + h_id, dry_run)
                    none_found = False
                    break

            if none_found:
                c.set_patient_transport(itm, '/patient/-1', dry_run)
        if performance_logging: print(" > handled patients")

        # get all required & involved vehicles
        if performance_logging: print(" > calculate needed vehicles")
        involved_vehicles = [*mission_state.vehicles_on_way, *mission_state.vehicles_at_mission]
        required_vehicles = [x for x in type_info.requirements if float(x.probability) >= min_probability_for_direct_required]
        if len(required_vehicles) == 0:
            required_vehicles = type_info.requirements

        # print(" > vehicles -- ", involved_vehicles, "vs", [x.name for x in required_vehicles])
        summary['Vehicles'].append(str(involved_vehicles))

        # calculate needed vehicles
        needed_vehicles = []

        # calculate additionally needed vehicles
        if len(mission_state.vehicles_missing) > 0:
            if not results_only:
                print(" > vehicle info (additional):")

            additional_required_vehicles = {}
            for missing_vehicle_type in mission_state.vehicles_missing:
                additional_required_vehicles[missing_vehicle_type] = additional_required_vehicles.get(missing_vehicle_type, 0) + 1
            for rv, amount in additional_required_vehicles.items():
                if not rv in v_translation:
                    print(" > > unknown vehicle: " + rv, force=True, color=chalk.red)
                    continue
                v_options = v_translation[rv]
                rv_driving_count = 0

                for vo in v_options:
                    if not type(vo) == str and isinstance(vo, Iterable):
                        for voo in vo:
                            rv_driving_count += mission_state.vehicles_on_way.count(voo)
                    else:
                        rv_driving_count += mission_state.vehicles_on_way.count(vo)

                dif = -(rv_driving_count - amount)

                if not results_only:
                    print(" > >", rv.ljust(16), "=>", str(rv_driving_count).rjust(2), "|", str(amount).ljust(2), "( => " + str(dif) + ")")

                if dif > 0:
                    for i in range(0, dif):
                        needed_vehicles.append(rv)
            
            if not results_only:
                print(" > ")
        else:
            # calculate regularly needed vehicles
            if not results_only:
                print(" > vehicle info: involved | required")
            for rv in required_vehicles:
                if not rv.name in v_translation:
                    print(" > > unknown vehicle:", rv.name, force=True, color=chalk.red)
                    continue
                v_options = v_translation[rv.name]
                rv_involved_count = 0

                for vo in v_options:
                    if not type(vo) == str and isinstance(vo, Iterable):
                        for voo in vo:
                            rv_involved_count += involved_vehicles.count(voo)
                    else:
                        rv_involved_count += involved_vehicles.count(vo)

                dif = -(rv_involved_count - rv.amount)

                if not results_only:
                    print(" > >", rv.name.ljust(16), "=>", str(rv_involved_count).rjust(2), "|", str(rv.amount).ljust(2), "( => " + str(dif) + ")")

                if dif > 0:
                    for i in range(0, dif):
                        needed_vehicles.append(rv.name)

        # set RTW/KTW as needed if no vehicle info is given
        if len(involved_vehicles) == 0 and len(required_vehicles) == 0 and len(needed_vehicles) == 0:
            # Krankentransport
            if int(mission.mission_type_id) == 147:
                print(" > > Krankentransport: no vehicles specified or involved - sending KTW")
                needed_vehicles = ['KTW']
            else:
                if not results_only:
                    print(" > > no vehicles specified or involved - sending RTW")
                needed_vehicles = ['RTW']

        if performance_logging: print(" > calculated needed vehicles")

        # limit to max per vehicle type
        if performance_logging: print(" > check special vehicle conditions")
        if len(needed_vehicles) > 0:
            needed_vehicles_counts = {}
            new_needed_vehicles = []
            for itm in needed_vehicles[::]:
                if itm not in needed_vehicles_counts:
                    needed_vehicles_counts[itm] = 0

                if itm not in vehicle_limits or needed_vehicles_counts[itm] < vehicle_limits[itm]:
                    new_needed_vehicles.append(itm)
                    needed_vehicles_counts[itm] += 1
                else:
                    pass
                    # print(" > > removed one", itm)
            needed_vehicles = new_needed_vehicles

            # check for duplicates through vehicle companionship e.g. Boats or Trailers (e.g. THW)
            translated_needed_vehicles = functools.reduce(operator.iconcat, [v_trans_get_func_reduced_cached(x) for x in needed_vehicles], [])
            for companionship_trailer in vehicle_companions:
                # print(" > looking for", companionship_trailer, "in", translated_needed_vehicles)
                if companionship_trailer in translated_needed_vehicles:
                    companionship_driver = vehicle_companions[companionship_trailer]
                    # print(" > > found", companionship_trailer, "in translated_needed_vehicles, looking for", companionship_driver)
                    if companionship_driver in translated_needed_vehicles:
                        # print(" > > already have", companionship_trailer, "driven by", companionship_driver, "-> removing extra driver")
                        for nv in needed_vehicles[::]:
                            nv_pos_tr = v_trans_get_func_reduced_cached(nv)
                            # print(" > > > checking", nv, "as", nv_pos_tr, "against", companionship_driver)
                            if companionship_driver in nv_pos_tr:
                                # print(" > > > > removing", nv, "as driver", companionship_driver)
                                needed_vehicles.remove(nv)
                                break

            # check for duplicates through vehicle replacements
            for replacement in vehicle_replacements:
                if replacement in translated_needed_vehicles:
                    # TODO: Check for replacement for ${replacement}
                    pass 


        if performance_logging: print(" > checked special vehicle conditions")

        # check for unavailable vehicles
        break_exec = False
        for u_v in unuav_v:
            if u_v in needed_vehicles:
                print(" > > UNAVAILABLE - SKIPPING", u_v, force=True)
                status = "SKIPPED: VEHICLES UNAVAILABLE"
                break_exec = True
                break

        # check if max parallel mission count reached (if mission is not already started)
        if mission.completion == 0 and len(involved_vehicles) == 0:
            if handled_mission_count >= parallel_mission_count_limit:
                if not mission.mission_type_id in always_send_vehicles_to:
                    print(" > max parallel missions reached! CANCELLING")
                    status = "SKIPPED: MAX MISSIONS"
                    break_exec = True

        # send vehicles if not cancelled above
        if performance_logging: print(" > actually send vehicles")
        missing_vehilces = []
        if not break_exec:
            handled_mission_count += 1

            status = ""
            if len(needed_vehicles) != 0:
                if not results_only:
                    print(" > send vehicles:", needed_vehicles)
                for needed_v in needed_vehicles:
                    # print(f" > > Looking for \"{needed_v}\"")
                    if not needed_v in available_vehicles:
                        print(" > > UNKNOWN VEHICLE", needed_v, force=True, color=chalk.red)
                        status = "UNKNOWN"
                        continue

                    found_option = False
                    
                    if len(v_translation[needed_v]) == 0: # dummy option
                        found_option = True

                    for t_option in v_translation[needed_v]:
                        if found_option:
                            break

                        # multiple vehicles option
                        if not type(t_option) == str and isinstance(t_option, Iterable):
                            # print("multiple vehicles option", t_option)
                            v_type_counts = {}
                            for v_type in t_option:
                                if not v_type in v_type_counts:
                                    v_type_counts[v_type] = 0
                                v_type_counts[v_type] += 1
                            
                            v_available = True
                            for v_type in v_type_counts:
                                if not v_type in vehicles_by_type or len(vehicles_by_type[v_type]) < v_type_counts[v_type]:
                                    v_available = False
                                    break

                            if v_available:
                                print(" > > SELECTED OPTION (LIST)", t_option, color=chalk.blue)
                                found_option = True
                                for v_type in t_option:
                                    selected_v_id = get_closest_vehicle_by_type(vehicles_by_type, vehicle_info_by_id, v_type, mission, mission_state) # used to be vehicles_by_type[v_type][0]
                                    if selected_v_id is None:
                                        print(" > > > NOBODY CLOSE ENOUGH", v_type, color=chalk.red)
                                        status = "TOO FAR"
                                        continue

                                    success = c.add_vehicles_to_mission(mission.id, [selected_v_id], dry_run)

                                    if not success:
                                        print(" > > > SEND FAILED", v_type, force=True, color=chalk.red)
                                        status = "SEND FAILED"
                                        continue

                                    for a_key in vehicles_by_type:
                                        if selected_v_id in vehicles_by_type[a_key]:
                                            vehicles_by_type[a_key].remove(selected_v_id)

                                    print(" > > > SENDING", v_type, "=> ID:", selected_v_id, color=chalk.blue)

                        # single vehicle option
                        else:
                            # print("single vehicle option", t_option)
                            if t_option in vehicles_by_type and len(vehicles_by_type[t_option]) > 0:
                                selected_v_id = get_closest_vehicle_by_type(vehicles_by_type, vehicle_info_by_id, t_option, mission, mission_state) # used to be selected_v_id = vehicles_by_type[t_option][0]
                                if selected_v_id is None:
                                    print(" > > > NOBODY CLOSE ENOUGH", t_option, color=chalk.red)
                                    status = "TOO FAR"
                                    continue

                                success = c.add_vehicles_to_mission(mission.id, [selected_v_id], dry_run)

                                found_option = True
                                
                                if not success:
                                    print(" > > SEND FAILED", needed_v, force=True, color=chalk.red)
                                    status = "SEND FAILED"
                                    continue

                                if selected_v_id in vehicles_by_type[t_option]:
                                    vehicles_by_type[t_option].remove(selected_v_id)

                                print(" > > SENDING", needed_v, "=> ID:", selected_v_id, color=chalk.blue)
                            
                    if found_option:
                        status = "VEHICLES SENT"
                    else:
                        print(" > > NOT AVAILABLE", needed_v, "from", available_vehicles[needed_v], color=chalk.yellow)
                        missing_vehilces.append(needed_v)
                        stats.report_missing_vehicle(v_translation[needed_v], mission.id)
                        status = "VEHICLES NOT AVAILABLE"
            else:
                print(" > > ALL DONE", color=chalk.green)
                status = "DONE"
        else:
            print(" > break_exec: NO VEHICLES SENT")

        if time.time() - mt0 < minimum_time_per_mission:
            if performance_logging: print("Handling only took", round(time.time() - mt0, 2), "sleeping", minimum_time_per_mission - (time.time() - mt0))
            time.sleep(minimum_time_per_mission - (time.time() - mt0))
        summary['Status'].append(status)
        summary['MissingVehicles'].append(missing_vehilces)

        if not high_performance_mode:
            if performance_logging: print(" > get checkup mission state")
            new_mission_state = c.get_mission_state(mission.id)
            if performance_logging: print(" > got checkup mission state")
        else: # less accurate but saves another request
            new_mission_state = mission_state
        summary['TimeVehicelsArrive'].append(max(new_mission_state.vehicles_on_way_arrivals) if len(new_mission_state.vehicles_on_way_arrivals) > 0 else "-")

        print("HANDLED in", round(time.time() - mt0, 2), "s")
        print("", no_time=True)

    # flush batch
    c.flush_vehicle_batch(dry_run=dry_run)

    updated_missions = c.get_missions()
    for i in range(len(summary[list(summary.keys())[0]])):
        mission_id = summary['MissionID'][i]
        found = False
        for itm in updated_missions:
            if itm.id == mission_id:
                found = True
                new_color = itm.color
                new_time_until_done = itm.time_until_end if itm.time_until_end >= 0 else "-"
                break

        if not found:
            summary['ColorAfter'].append("done")
            summary['TimeUntilDone'][i] = "0"
            next_change_in = 0
        else:
            summary['ColorAfter'].append(new_color)
            summary['TimeUntilDone'][i] = new_time_until_done
            if new_color == "done":
                next_change_in = 30
            if new_time_until_done != "-" and int(new_time_until_done) < next_change_in:
                next_change_in = int(new_time_until_done)

    stuck = True
    itr = 0
    stuck_check_until = 10 # report as "stuck" once first 10 missions are red
    for col in summary['ColorAfter']:
        if itr == stuck_check_until:
            break

        if col != "rot":
            # print("NOT STUCK", col)
            stuck = False
            break
        
        itr += 1

    if stuck:
        print(" > STUCK: EMERGENCY RESET", force=True, color=chalk.red)
        reset_stuck(updated_missions)
        print(" > STUCK: EMERGENCY RESET DONE", force=True, color=chalk.red)

    print("ALL MISSIONS HANDLED IN", str(round(time.time() - t0, 2)) + "s")
    next_change_in = max(next_change_in, miminum_sleep_time)
    return summary, next_change_in

def colorcode_summary(summary):
    for i in range(len(summary[list(summary.keys())[0]])):
        mc = summary['ColorAfter'][i]
        status = summary['Status'][i]

        color_function = chalk.blue
        if status.startswith("SKIPPED: "):
            color_function = chalk.grey
        else:
            if mc == "rot":
                color_function = chalk.red

            elif mc == "gelb":
                color_function = chalk.yellow

            elif mc == "gruen":
                color_function = chalk.green

        for k in summary:
            summary[k][i] = color_function(summary[k][i])

    return summary


if __name__ == '__main__':
    while True:
        print("CHECK", force=True)

        try:
            summary, next_change_in = check_and_react()

            if not disable_summary:
                if simplify_summary: summary['MissingVehicles'] = [len(x) for x in summary['MissingVehicles']]

                summary = colorcode_summary(summary)

                del summary['MissionID']
                del summary['Requirements']
                del summary['Vehicles']
                del summary['Completion']
                del summary['Credits']
                del summary['ColorBefore']
                del summary['ColorAfter']

                summary['T-'] = [summary['TimeUntilDone'][i] if not "-" in summary['TimeUntilDone'][i] else summary['TimeVehicelsArrive'][i] for i in range(len(summary['TimeVehicelsArrive']))]
                del summary['TimeUntilDone']
                del summary['TimeVehicelsArrive']
                

                _print(tabulate(summary, headers='keys'))

            if dry_run:
                break

            print("SLEEP", next_change_in, force=True)
            time.sleep(next_change_in)
        except json.decoder.JSONDecodeError:
            print("JSON Decode Error", force=True)
            time.sleep(5)
        except Exception as ex:
            print("MAIN LOOP EXCEPTION", ex, force=True)
            traceback.print_exc()
            time.sleep(120)

        print("REPEAT", force=True)
        print("", force=True)
