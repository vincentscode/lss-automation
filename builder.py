from lss_sdk.client import Client
from lss_sdk.building_enricher import add_additional_building_info, building_type_info
from lss_sdk.game_objects import Building, BuildingTypeInfo, VehicleType

from utils.mission_requirements import mission_requirements

import config
import random
import time
from yachalk import chalk


people_logging = False

build_new = False
build_and_expand = False
build_only = False

c = Client(config.headers)
abuse = c.get_building_abuse_detected()
credits = c.get_credits()

buildings = c.get_buildings()
if not build_only:
	buildings = add_additional_building_info(c, buildings, c.get_vehicles(), first_n_only=-1)
else:
	buildings = sorted([Building(b) for b in buildings], key=lambda e: e.name)


print("Abuse:", abuse)
print("Credits:", credits)

def get_coords_for_new_building(buildings):
	all_coords = [b.location for b in buildings]
	lats = [c[0] for c in all_coords]
	lons = [c[1] for c in all_coords]

	min_lat, max_lat = min(lats), max(lats)
	min_lon, max_lon = min(lons), max(lons)

	latvar = abs(min_lat - max_lat)
	lonvar = abs(min_lon - max_lon)

	latavg = sum(lats) / len(lats)
	lonavg = sum(lons) / len(lons)

	dist_mult = 0.2
	latrand = random.uniform(latavg - dist_mult * latvar, latavg + dist_mult * latvar)
	lonrand = random.uniform(lonavg - dist_mult * lonvar, lonavg + dist_mult * lonvar)

	# f = 0.5
	# latrand = random.uniform(min_lat + f*latvar, max_lat-f*latvar)
	# lonrand = random.uniform(min_lon + f*lonvar, max_lon-f*lonvar)

	return [latrand, lonrand]

def build(c, building_type_id, noprompt=False):
	print("Building", building_type_id)
	if not noprompt:
		input("Do it? > ")
	lat_long = get_coords_for_new_building(buildings)
	name = f"Auto - {building_type_info[building_type_id].name}"
	c.purchase_building(building_type_id, lat_long, name)

if build_new and build_and_expand:
	for i in range(25):
		# build(c, 0) # Feuerwache
		# build(c, 1) # Feuerwehrschule

		# build(c, 2, True) # Rettungswache
		# build(c, 3) # Rettungsschule

		# build(c, 4) # Krankenhaus
		# build(c, 5) # Rettungshubschrauber-Station
		# build(c, 7) # Leitstelle
		# build(c, 11) # Bereitschaftspolizei
		# build(c, 12) # Schnelleinsatzgruppe (SEG)
		# build(c, 13) # Polizeihubschrauberstation
		# build(c, 14) # Bereitstellungsraum
		# build(c, 15) # Wasserrettung
		# build(c, 16) # Verbandszellen
		# build(c, 17) # Polizei-Sondereinheiten
		# build(c, 18) # Feuerwache (Kleinwache)
		# build(c, 19) # Polizeiwache (Kleinwache)
		# build(c, 20) # Rettungswache (Kleinwache)
		# build(c, 21) # Rettungshundestaffel
		# build(c, 22) # Großer Komplex
		# build(c, 23) # Kleiner Komplex

		# build(c, 6) # Polizeiwache
		# build(c, 8) # Polizeischule

		# build(c, 9) # THW-Ortsverband
		# build(c, 10) # THW Bundesschule

		pass

if build_only:
	exit()

buildings_by_type = {}
for b in buildings:
	b_type_name = b.type_info.name
	buildings_by_type[b_type_name] = buildings_by_type[b_type_name] + 1 if b_type_name in buildings_by_type else 1


vehicle_target_by_buildig_type = {
	# Feuerwache (16/17)
	0: [
		30, 30, 30, 30, 30, # 5 HLF 20
		2, # 1 DLK 23
		34, 34, # 2 ELW 2
		5, # 1 GW-A
		33, # 1 GW-Höhenrettung
		12, # 1 GW-Messtechnik
		10, # 1 GW-Öl
		14, # 1 SW 2000
		27, # 1 GW-Gefahrgut
		53, # 1 Dekon-P
		57, # 1 FwK
	],
	# Rettungswache (15/15)
	2: [
		28, 28, 28, 28, 28, 28, # 7 RTW
		29, 29, 29, 29, # 4 NEF
		38, 38, # 2 KTW
		55, # 1 LNA
		56, # 1 OrgL
	],
	# Polizeiwache (10/16)
	6: [
		32, 32, 32, 32, 32, 32, 32, 32, 32, 32, # 10 Fustw
	],
	# THW-Ortsverband (23)
	9: [

	],
}

building_upgrades_by_building_type = {
	# Krankenhaus
	4: {
		0: (1, "Allgemeine Innere"),
		1: (1, "Allgemeine Chirurgie"),
	},
	# Feuerwache
	0: {
		13: (0.1, "Werkfeuerwehr"), # 10 % Werkfeuerwehr
		9: (0.05, "Großwache"), # 5 % Großwache
		8: (0.05, "Flughafen-Erweiterung"), # 5 % Flughafen
	},
	# Rettungswache
	2: {},
	# Polizeiwache
	6: {
		0: (1, "Zelle"),
		1: (1, "Zelle"),
		2: (1, "Zelle"),
		3: (1, "Zelle"),
		4: (1, "Zelle"),
		5: (1, "Zelle"),
		6: (1, "Zelle"),
		7: (1, "Zelle"),
		8: (1, "Zelle"),
		9: (1, "Zelle"),
	},
	# THW-Ortsverband
	9: {
		0: (1, "1. Technischer Zug: Bergungsgruppe 2"),
		1: (1, "1. Technischer Zug: Zugtrupp"),
	},
	# Schools
	1: {
		0: (1, "Weiterer Klassenraum"),
		1: (1, "Weiterer Klassenraum"),
		2: (1, "Weiterer Klassenraum"),
	},
	3: {
		0: (1, "Weiterer Klassenraum"),
		1: (1, "Weiterer Klassenraum"),
		2: (1, "Weiterer Klassenraum"),
	},
	8: {
		0: (1, "Weiterer Klassenraum"),
		1: (1, "Weiterer Klassenraum"),
		2: (1, "Weiterer Klassenraum"),
	},
	10: {
		0: (1, "Weiterer Klassenraum"),
		1: (1, "Weiterer Klassenraum"),
		2: (1, "Weiterer Klassenraum"),
	},
}

# print("Building Summary:")
# for k in buildings_by_type:
#     print(f" > {k}: {buildings_by_type[k]}")

missing = {}
for req in mission_requirements:
	for r in req:
		num = int(''.join(c for c in r if c in "0123456789"))
		name = r.replace(str(num), "").strip()

		if not name in buildings_by_type:
			print("UNKNOWN Building", name)
			if not name in missing or missing[name] < num:
				missing[name] = num
			continue

		if buildings_by_type[name] < num:
			print("NOT ENOUGH", name)
			if not name in missing or missing[name] < num:
				missing[name] = num

			continue

# print("Missing Summary:")
# for k in missing:
#     print(f" > {k}: {buildings_by_type[k] if k in buildings_by_type else None} / {missing[k]}")

global_education_waitlist = {}

leitstelle_id = '12178022'

print("Buildings:")
for b in buildings:
	print(" >", b)

	if not b.leitstelle_building_id or str(b.leitstelle_building_id) != leitstelle_id:
		c.set_leitstelle(b.id, leitstelle_id)

	if b.level < b.type_info.max_level and build_and_expand:
		print(f" > > Upgrading", b.id, "to", b.type_info.max_level)
		c.upgrade_building(b.id, b.type_info.max_level)

	print(f" > > Extensions ({len(b.extensions)} / {len(b.type_info.extensions)}):")

	for ex in b.extensions:
		print(" > > >", ex)

	if b.building_type in building_upgrades_by_building_type:
		# seed for specific building
		random.seed(b.id)
		
		# check if any upgrades are in progress
		if any([x.building_in_progress for x in b.extensions]):
			print(" > > > Extension already being built.")
			continue

		# check for wanted upgrades
		wanted_upgrades = building_upgrades_by_building_type[b.building_type]
		for upgrade_id in wanted_upgrades.keys():
			# schoolrooms
			if b.building_type in [1, 3, 8, 10]:
				if len(b.extensions) == 3:
					continue

			# everything else
			else:
				if name in [x.name for x in b.extensions]:
					continue

			probability, name = wanted_upgrades[upgrade_id]
			if random.random() < probability and build_and_expand:
				print(" > > > Adding Extension:", name)
				c.add_building_extension(b.id, upgrade_id)
				break
		
		# reseed
		random.seed()

	if people_logging:
		print(f" > > Personnel ({b.personal_count}):")
		for k in b.personnel_count_by_schooling:
			print(" > > >", f"{k}: {b.personnel_count_by_schooling[k]}")

	# populate available_person_ids_by_schooling
	available_person_ids_by_schooling = {}
	for p in b.personnel:
		if p.bound_to_vehicle is not None or p.status != "Verfügbar":
			continue

		if p.schooling not in available_person_ids_by_schooling:
			available_person_ids_by_schooling[p.schooling] = []

		available_person_ids_by_schooling[p.schooling].append(p.id)

	# populate learning_person_ids_by_schooling
	learning_person_ids_by_schooling = {}
	for p in b.personnel:
		if p.bound_to_vehicle is not None:
			continue

		if not "Im Unterricht:" in p.status:
			continue

		learning_schooling = p.status.replace("Im Unterricht:", "").strip()

		if learning_schooling not in learning_person_ids_by_schooling:
			learning_person_ids_by_schooling[learning_schooling] = []

		learning_person_ids_by_schooling[learning_schooling].append(p.id)


	print(f" > > Vehicles ({len(b.vehicles)} / {b.total_parking}):")
	education_waitlist = {}
	all_have_at_least_minimum = True
	for v in b.vehicles[::]:
		person_counts = f"{v.assigned_personnel_count} / {v.type_info.max_personnel} (min: {v.type_info.min_personnel})"
		if v.assigned_personnel_count == v.type_info.max_personnel:
			person_counts = chalk.green(person_counts)
		elif v.assigned_personnel_count < v.type_info.min_personnel:
			person_counts = chalk.red(person_counts)
		else:
			person_counts = chalk.yellow(person_counts)

		if people_logging:
			print(" > > >", v)
			print(" > > > > Personnel:", person_counts, "Schooling:", v.type_info.schooling)
		else:
			print(" > > >", v, "P:", person_counts, "S:", v.type_info.schooling)

		while v.assigned_personnel_count < v.type_info.min_personnel:
			schoolings_required = list(v.type_info.schooling.keys())
			if len(schoolings_required) == 0:
				k = None
			elif len(schoolings_required) > 1:
				raise Exception("TODO: UNHANDLED - MULTIPLE SCHOOLINGS REQUIRED")
			else:
				k = schoolings_required[0]

			if k is None or v.type_info.schooling[k] is True:
				if k in available_person_ids_by_schooling and len(available_person_ids_by_schooling[k]) > 0:
					if v.state == 6:
						print(chalk.red(" > > > >", f"Activating {v.id}"))
						c.set_vehicle_fms(v.id, 2)

					p_id = random.choice(available_person_ids_by_schooling[k])
					if people_logging:
						print(f" > > > > > Binding {p_id} to {v.id} ({k})")
					c.bind_person_to_vehicle(v.id, p_id)
					available_person_ids_by_schooling[k].remove(p_id)
					v.assigned_personnel_count += 1
					b.vehicles[b.vehicles.index(v)] = v
				else:
					if v.state == 2:
						print(chalk.red(" > > > >", f"Deactivating {v.id} for lack of personnel."))
						c.set_vehicle_fms(v.id, 6)

					for i in range(v.type_info.min_personnel - v.assigned_personnel_count):
						if people_logging:
							print(" > > > > >", chalk.red(f"Missing people for {v.id} ({k})"))
						
						if k is not None:
							if k not in education_waitlist:
								education_waitlist[k] = []
							if not None in available_person_ids_by_schooling or len(available_person_ids_by_schooling[None]) == 0:
								continue
							p_id = random.choice(available_person_ids_by_schooling[None])
							if people_logging:
								print(" > > > > > >", chalk.blue(f"Educating {p_id} for {v.id} ({k})"))
							education_waitlist[k].append(p_id)
							available_person_ids_by_schooling[None].remove(p_id)

					all_have_at_least_minimum = False
					break
			else:
				if v.state == 2:
					c.set_vehicle_fms(v.id, 6)
					break
				else:
					raise Exception("TODO: UNHANDLED")

	if all_have_at_least_minimum:
		if b.building_type in vehicle_target_by_buildig_type:
			wanted_vehicles = vehicle_target_by_buildig_type[b.building_type][::]
			for v in b.vehicles:
				if v.type_id in wanted_vehicles:
					wanted_vehicles.remove(v.type_id)
			
			space_left = b.total_parking - len(b.vehicles)
			for v_id in wanted_vehicles:
				if space_left <= 0 or not build_and_expand:
					break

				print(" > > >", f"Purchasing Vehicle ({v_id}) for {b.name} ({b.id})")
				c.purchase_vehicle(b.id, v_id)
				time.sleep(0.5)
				all_have_at_least_minimum = False
				space_left -= 1

	if all_have_at_least_minimum:
		for v in b.vehicles:
			if people_logging:
				print(" > > >", v, "(second round)")
			while v.assigned_personnel_count < v.type_info.max_personnel:
				schoolings_required = list(v.type_info.schooling.keys())
				if len(schoolings_required) == 0:
					k = None
				elif len(schoolings_required) > 1:
					raise Exception("TODO: UNHANDLED - MULTIPLE SCHOOLINGS REQUIRED")
				else:
					k = schoolings_required[0]

				if k is None or v.type_info.schooling[k] is True:
					if k in available_person_ids_by_schooling and len(available_person_ids_by_schooling[k]) > 0:
						p_id = random.choice(available_person_ids_by_schooling[k])
						if people_logging:
							print(f" > > > > > Binding {p_id} to {v.name} ({v.id}) [{k}]")
						c.bind_person_to_vehicle(v.id, p_id)
						available_person_ids_by_schooling[k].remove(p_id)
						v.assigned_personnel_count += 1
						b.vehicles[b.vehicles.index(v)] = v
					else:
						for i in range(v.type_info.max_personnel - v.assigned_personnel_count):
							if people_logging:
								print(" > > > > >", chalk.yellow(f"Missing people for {v.name} ({v.id}) [{k}]"))

							if k is not None:
								if k not in education_waitlist:
									education_waitlist[k] = []
								if not None in available_person_ids_by_schooling or len(available_person_ids_by_schooling[None]) == 0:
									continue
								p_id = random.choice(available_person_ids_by_schooling[None])
								if people_logging:
									print(" > > > > > >", chalk.blue(f"Educating {p_id} for {v.name} ({v.id}) [{k}]"))
								education_waitlist[k].append(p_id)
								available_person_ids_by_schooling[None].remove(p_id)

						all_have_at_least_minimum = False
						break
				else:
					raise Exception("TODO: UNHANDLED - PARTIAL SCHOOLINGS REQUIRED")


	print(" > > Awaiting Education:")
	for k in education_waitlist:
		print(" > > >", k, "=>", len(education_waitlist[k]))
		already_running = len(learning_person_ids_by_schooling[k]) if k in learning_person_ids_by_schooling else 0
		print(" > > > >", "already running for", already_running)
		
		school_class = []
		for p_id in education_waitlist[k]:
			if already_running > 0:
				already_running -= 1
				continue
			school_class.append(p_id)

		if len(school_class) == 0:
			print(" > > > >", "nobody left to teach")
			continue

		school_type = b.type_info.schooling_types[0]
		if not school_type in global_education_waitlist:
			global_education_waitlist[school_type] = {}

		if not k in global_education_waitlist[school_type]:
			global_education_waitlist[school_type][k] = []


		for p_id in school_class:
			global_education_waitlist[school_type][k].append(p_id)

print("Global Education:")
for school_type in global_education_waitlist:
	schools_of_type = c.get_free_schools_for_schooling_type(school_type)
	for k in global_education_waitlist[school_type]:
		student_ids = global_education_waitlist[school_type][k]
		print(" >", school_type, k, "=>", len(student_ids))

		chunked_list = list()
		chunk_size = 10

		for i in range(0, len(student_ids), chunk_size):
			chunked_list.append(student_ids[i:i+chunk_size])

		for school_class in chunked_list:
			if len(schools_of_type) == 0:
				print(" > > > >", chalk.red("no school rooms available"))
				continue

			success = False
			while not success and len(schools_of_type) > 0:
				chosen = random.choice(schools_of_type)
				school_building_id = chosen.id
				success = c.school_persons(school_building_id, school_type, k, school_class)
				if not success:
					print(" > >", "teaching failed, retry", schools_of_type)
					schools_of_type.remove(chosen)
					time.sleep(1)

			print(" > >", "teaching initiated")

# Leitstellen
num_leitstellen_buildable = int(len(buildings) / 25)
num_leitstellen = buildings_by_type["Leitstelle"]

print("Leitstellen:", num_leitstellen, "/", num_leitstellen_buildable)
for _ in range(num_leitstellen_buildable - num_leitstellen):
	pass # build distributed

# assign buildings to closest
