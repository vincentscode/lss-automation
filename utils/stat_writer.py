import datetime

class StatWriter:
    def __init__(self):
        self.file_missing_vehicle = open("stats_missing_vehicle.tsv", "a")
        self.file_credits = open("stats_credits.tsv", "a")
    
    def report_mission(self, mission_id, mission_type_id, mission_required_vehicles):
        pass
    
    def report_missing_vehicle(self, possible_vehicles, mission_id):
        try:
            x = possible_vehicles[0][0][1]
            possible_vehicles = possible_vehicles[0]
        except:
            pass
        
        try:
            out = '|'.join(list(possible_vehicles))
            self.file_missing_vehicle.write('\t'.join([str(datetime.datetime.utcnow()), out, str(mission_id)]) + '\n')
            self.file_missing_vehicle.flush()
        except Exception as ex:
            print("Exception in report_missing_vehicle:", ex)
    
    def report_current_credits(self, credits):
        try:
            self.file_credits.write(str(datetime.datetime.utcnow()) + '\t' + str(credits) + '\n')
            self.file_credits.flush()
        except Exception as ex:
            print("Exception in report_missing_vehicle:", ex)
