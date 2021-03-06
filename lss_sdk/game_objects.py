class Vehicle:
    def __init__(self, j):
        self.full_json = j

        self.id = j['id']
        self.type_id = j['vehicle_type']
        self.name = j['caption']
        self.state = j['fms_real']

    def __repr__(self):
        return f'ID: {self.id} | State: {self.state} | Type: {self.type_id} | Name: {self.name}'

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
    def __init__(self, vehicles_on_way, vehicles_at_mission, vehicles_missing, speak_urls, vehicles_on_way_arrivals):
        self.vehicles_on_way = vehicles_on_way
        self.vehicles_at_mission = vehicles_at_mission
        self.vehicles_missing = vehicles_missing
        self.speak_urls = speak_urls
        self.vehicles_on_way_arrivals = vehicles_on_way_arrivals

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
        "Ben??tigte Drehleitern": "Drehleiter Anforderungswahrscheinlichkeit",
        "Ben??tigte Feuerwehrkr??ne (FwK)": "FwK Anforderungswahrscheinlichkeit",
        "Ben??tigte R??stwagen": "R??stwagen Anforderungswahrscheinlichkeit",
        "Ben??tigte Streifenwagen": "Streifenwagen Anforderungswahrscheinlichkeit",
        "Ben??tigte ELW 1": "ELW 1 Anforderungswahrscheinlichkeit",
        "Ben??tigte ELW 2": "ELW 2 Anforderungswahrscheinlichkeit",
        "Ben??tigte L??schfahrzeuge": "L??schfahrzeuge Anforderungswahrscheinlichkeit",
        "Ben??tigte GW-??l": "GW-??l Anforderungswahrscheinlichkeit",
        "Ben??tigte GW-A": "GW-A Anforderungswahrscheinlichkeit",
        "Ben??tigte GW-H??henrettung": "GW-H??henrettung Anforderungswahrscheinlichkeit",
        "Ben??tigte DHuF??Kw": "DHuF??Kw Anforderungswahrscheinlichkeit",
        "Ben??tigte Feuerl??schpumpen": "Feuerl??schpumpen Anforderungswahrscheinlichkeit",
        "Ben??tigte GW L 2 Wasser": "GW L 2 Wasser Anforderungswahrscheinlichkeit",
        "Ben??tigte Au??enlastbeh??lter (allgemein)": "Au??enlastbeh??lter (allgemein) Anforderungswahrscheinlichkeit",
        "Ben??tigte GW-Mess": "GW-Mess Anforderungswahrscheinlichkeit",
        "Ben??tigte GW-Gefahrgut": "GW-Gefahrgut Anforderungswahrscheinlichkeit",
        "Ben??tigte Dekon-P": "Dekon-P Anforderungswahrscheinlichkeit",
        "Ben??tigte Turbol??scher": "Turbol??scher Anforderungswahrscheinlichkeit",
        "Ben??tigte Teleskopmasten": "Teleskopmasten Anforderungswahrscheinlichkeit",
        "Ben??tigte GW-Werkfeuerwehr": "GW-Werkfeuerwehr Anforderungswahrscheinlichkeit",
        "Ben??tigte ULF mit L??scharm": "ULF mit L??scharm Anforderungswahrscheinlichkeit",
    }

    def __init__(self, tables):
        self.generator = tables[0]['Generiert von']
        self.credits = tables[0]['Credits im Durchschnitt'] if 'Credits im Durchschnitt' in tables[0] else 0
        self.requirements = []
        for req in tables[1]:
            if req.startswith('Ben??tigte'):
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

                self.requirements.append(MissionRequirement(req[len('Ben??tigte '):], int(tables[1][req]), prob))

    def __repr__(self):
        return f'{self.generator} | {self.credits} Credits ==> [{", ".join([str(x) for x in self.requirements])}]'

    def __str__(self):
        return self.__repr__()
