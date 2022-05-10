from lss_sdk.client import Client
from lss_sdk.manager import Manager

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
from collections.abc import Iterable
from _thread import start_new_thread

from config import headers, my_user_id, hospitals

parser = argparse.ArgumentParser()
parser.add_argument('--dry', dest='dry', action='store_const', const=True, default=False)
parser.add_argument('--silent', dest='silent', action='store_const', const=True, default=False)
args = parser.parse_args()

dry_run = args.dry
silent = args.silent
t_delay = 1
disable_summary = True
results_only = True

ignore_vehicles = [] # disabled vehicles, e.g. Bereitstellungsraum
unuav_v = [] # disabled vehicle types e.g. not owned / no drivers

min_probability_for_direct_required = 0.4

parallel_mission_count_limit = 12
max_preparation_time = 1200

v_translation = {
    # Feuerwehr
    "Feuerlöschpumpe": ["LF 10", "LF 20", "TLF 4000", "HLF 20"],
    "Löschfahrzeuge": ["LF 10", "LF 20", "TLF 4000", "HLF 20"],
    "Löschfahrzeuge (LF)": ["LF 10", "LF 20", "TLF 4000", "HLF 20"],
    "Löschfahrzeug": ["LF 10", "LF 20", "TLF 4000", "HLF 20"],
    "Löschfahrzeug (LF)": ["LF 10", "LF 20", "TLF 4000", "HLF 20"],
    "Tragehilfe (z.B. durch ein LF)": ["LF 10", "LF 20", "HLF 20"],
    "LF": [],

    "Drehleitern": ["DLK 23"],
    "Drehleiter": ["DLK 23"],
    "DLK 23": ["DLK 23"],
    "Drehleiter (DLK 23)": ["DLK 23"],

    "Außenlastbehälter (allgemein)": [],

    "Rüstwagen": ["RW", "HLF 20"],
    "Rüstwagen oder HLF": ["RW", "HLF 20"],

    "ELW 1": ["ELW 2"],
    "ELW 2": ["ELW 2"],
    "Einsatzleitwagen 1": ["ELW 2"],
    "Einsatzleitwagen 2": ["ELW 2"],

    "SW 2000": ["SW 2000"],
    "GW L 2 Wasser": ["SW 2000"],
    "GW-L2 Wasser, SW 1000, SW 2000 oder Ähnliches": ["SW 2000"],
    "1 Schlauchwagen (GW-L2 Wasser": ["SW 2000"], # split result
    "SW 1000": [], # split result
    "SW 2000 oder Ähnliches)": [], # split result
    "Feuerlöschpumpen": ["SW 2000"],

    "GW-A": ["GW-A"],
    "GW-Atemschutz": ["GW-A"],

    "GW-Mess": ["GW-Mess", "GW-Messtechnik"],
    "GW-Messtechnik": ["GW-Mess", "GW-Messtechnik"],

    "GW-Gefahrgut": ["GW-Gefahrgut"],

    "GW-Höhenrettung": ["GW-Höhenrettung"],

    "GW-Öl": ["GW-Öl"],

    "Dekon-P": ["Dekon-P"],

    # Werkfeuerwehr
    "GW-Werkfeuerwehr": ["GW-Werkfeuerwehr"],

    "Turbolöscher": ["Turbolöscher"],

    "ULF mit Löscharm": ["ULF mit Löscharm"],
    
    "Teleskopmast": ["TM 50"],
    "Teleskopmasten": ["TM 50"],
    "TM 50": ["TM 50"],

    # Rettungsdienst    
    "RTW": ["RTW"],

    "NEF": ["NEF"],

    # Polizei
    "Streifenwagen": ["FuStW"],
    "FuStW": ["FuStW"],

    # THW
    "Gerätekraftwagen (GKW)": ["GKW"],
    
}

# generate translation key permutations
for k in list(v_translation.keys()):
    # numbers
    for i in [str(x) for x in range(1, 25)]:
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
        for f in range(1, 100):
            v_translation[i + " " + k + "." + f" Wir benötigen noch min. {f} Feuerwehrleute."] = value_x

for w in range(0, 100000 + 100, 100):
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
            tuple(["TLF 4000" for _ in range(0, count_tlf)]),
        ]
        v_translation[result_string[:-1]] = v_translation[result_string]

c = Client(headers)
stats = StatWriter()

def mission_requester():
    while True:
        c.mission_generate()
        time.sleep(30)

start_new_thread(mission_requester, ())

def print(*args, force=False, no_time=False, color=None):
    global silent
    
    if silent and not force:
        return

    print_string = " ".join(map(str, args)).replace("\n", "")
    if color is not None:
        print_string = color(print_string)

    if no_time:
        pre_string = ""
    else:
        pre_string = "[" + datetime.now().strftime('%H:%M:%S') + "] "
    
    builtins.print(pre_string + print_string)


def check_and_react():
    global c, dry_run
    next_change_in = 4 * 60 # default wait time: 4 Minutes

    ### GET VEHICLES
    # print("Getting vehicles")
    available_vehicles = {}
    for k in v_translation.keys():
        available_vehicles[k] = []

    vehicle_locations = {}
    vehicles_by_type = {}
    for v in c.get_vehicles():
        if v.id in ignore_vehicles:
            # print("ignoring", v)
            continue

        if v.state in [1, 2]:
            if not v.name in vehicles_by_type:
                vehicles_by_type[v.name] = []
            vehicles_by_type[v.name].append(v.id)

            for v_key in v_translation:
                if v.name in v_translation[v_key] or v.name in functools.reduce(operator.iconcat, v_translation[v_key], []):
                    available_vehicles[v_key].append(v.id)

    # print("Available:", available_vehicles)
    # print("\n========\n")

    ### GET BUILDINGS & MANAGE HIRING
    buildings = c.get_buildings()
    for b in buildings:
        if b['building_type'] not in [1, 4, 7]:
            if int(b['hiring_phase']) != 3:
                print(b['id'], "> hire")
                c.hire_people(b['id'])

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

        # TODO: prioritize missions with a lot of vehicles already involved
        # TODO: get num humans on vehicle vs. num humans required
        # TODO: get water on vehicle

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
        type_info = c.get_mission_type_info(mission.mission_type_id)
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
        
        # send patients to hospital or deny transport
        for itm in mission_state.speak_urls:
            none_found = True
            for h_id in hospitals:
                if c.get_hospital_free_beds(h_id) > 0:
                    # TODO: Check if full
                    c.set_patient_transport(itm, '/patient/' + h_id, dry_run)
                    none_found = False
                    break

            if none_found:
                c.set_patient_transport(itm, '/patient/-1', dry_run)

        # get all required & involved vehicles
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

            additional_reuired_vehicles = mission_state.vehicles_missing
            for rv in additional_reuired_vehicles:
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

                amount = 1
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

        # set RTW as needed if no vehicle info is given
        if len(involved_vehicles) == 0 and len(required_vehicles) == 0 and len(needed_vehicles) == 0:
            if not results_only:
                print(" > > no vehicles specified or involved - sending RTW")
            needed_vehicles = ['RTW']

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
                print(" > max parallel missions reached! CANCELLING")
                status = "SKIPPED: MAX MISSIONS"
                break_exec = True

        # send vehicles if not cancelled above
        missing_vehilces = []
        if not break_exec:
            handled_mission_count += 1

            status = ""
            if len(needed_vehicles) != 0:
                if not results_only:
                    print(" > send vehicles:", needed_vehicles)
                for needed_v in needed_vehicles:
                    if not needed_v in available_vehicles:
                        print(" > > UNKNOWN VEHICLE", needed_v, force=True, color=chalk.red)
                        status = "UNKNOWN"
                        continue

                    if len(available_vehicles[needed_v]) > 0:
                        found_option = False
                        
                        if len(v_translation[needed_v]) == 0: # dummy option
                            found_option = True

                        for t_option in v_translation[needed_v]:
                            if found_option:
                                break
                            # multiple vehicles option
                            if not type(t_option) == str and isinstance(t_option, Iterable):
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
                                        selected_v_id = vehicles_by_type[v_type][0]
                                        success = c.add_vehicles_to_mission(mission.id, [selected_v_id], dry_run)

                                        if not success:
                                            print(" > > > SEND FAILED", v_type, force=True, color=chalk.red)
                                            status = "SEND FAILED"
                                            continue

                                        for a_key in available_vehicles:
                                            if selected_v_id in available_vehicles[a_key]:
                                                available_vehicles[a_key].remove(selected_v_id)

                                        for a_key in vehicles_by_type:
                                            if selected_v_id in vehicles_by_type[a_key]:
                                                vehicles_by_type[a_key].remove(selected_v_id)

                                        print(" > > > SENT", v_type, "=> ID:", selected_v_id, color=chalk.blue)

                            # single vehicle option
                            else:
                                selected_v_id = available_vehicles[needed_v][0]
                                success = c.add_vehicles_to_mission(mission.id, [selected_v_id], dry_run)

                                if not success:
                                    print(" > > SEND FAILED", needed_v, force=True, color=chalk.red)
                                    status = "SEND FAILED"
                                    continue

                                found_option = True

                                for a_key in available_vehicles:
                                    if selected_v_id in available_vehicles[a_key]:
                                        available_vehicles[a_key].remove(selected_v_id)

                                print(" > > SENT", needed_v, "=> ID:", selected_v_id, color=chalk.blue)
                        
                        if found_option:
                            status = "VEHICLES SENT"
                        else:
                            print(" > > NOT AVAILABLE", needed_v, "from", available_vehicles[needed_v], color=chalk.yellow)
                            missing_vehilces.append(needed_v)
                            stats.report_missing_vehicle(v_translation[needed_v], mission.id)
                            status = "VEHICLES NOT AVAILABLE"
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

        time.sleep(t_delay)
        summary['Status'].append(status)
        summary['MissingVehicles'].append(missing_vehilces)

        new_mission_state = c.get_mission_state(mission.id)
        summary['TimeVehicelsArrive'].append(max(new_mission_state.vehicles_on_way_arrivals) if len(new_mission_state.vehicles_on_way_arrivals) > 0 else "-")

        print("", no_time=True)

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
        else:
            summary['ColorAfter'].append(new_color)
            summary['TimeUntilDone'][i] = new_time_until_done
            if new_color == "done":
                next_change_in = 30
            if new_time_until_done != "-" and int(new_time_until_done) < next_change_in:
                next_change_in = int(new_time_until_done)

    next_change_in = max(next_change_in, 30) # wait at least 30s
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


while True:
    print("CHECK", force=True)

    try:
        summary, next_change_in = check_and_react()

        if not disable_summary:
            # summary['MissingVehicles'] = [len(x) for x in summary['MissingVehicles']]

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
            

            builtins.print(tabulate(summary, headers='keys'))

        if dry_run:
            break

        print("SLEEP", next_change_in, force=True)
        time.sleep(next_change_in)
    except Exception as ex:
        print("MAIN LOOP EXCEPTION", ex, force=True)
        time.sleep(120)

    print("REPEAT", force=True)
    print("", force=True)
