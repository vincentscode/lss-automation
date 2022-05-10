from pymongo import MongoClient
import datetime

class StatWriter:
    def __init__(self):
        self.client = MongoClient("localhost:27017")
        self.db = self.client.lss_stats

        self.missions_db = self.db.missions
        self.missing_vehicle_db = self.db.missing_vehicles
        self.current_credits = self.db.current_credits

    def report_mission(self, mission_id, mission_type_id, mission_required_vehicles):
        # check for duplicates
        if (self.missions_db.find({'mission_id': mission_id}).count() > 0):
            return

        report = {
            "date": datetime.datetime.utcnow(),
            "mission_id": mission_id,
            "mission_type_id": mission_type_id,
            "mission_required_vehicles": mission_required_vehicles,
        }

        self.missions_db.insert_one(report)

    def report_missing_vehicle(self, possible_vehicles, mission_id):
        report = {
            "date": datetime.datetime.utcnow(),
            "possible_vehicles": possible_vehicles,
            "mission_id": mission_id,
        }

        self.missing_vehicle_db.insert_one(report)

    def report_current_credits(self, credits):
        report = {
            "date": datetime.datetime.utcnow(),
            "credits": credits,
        }

        self.current_credits.insert_one(report)
