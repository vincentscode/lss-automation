from .game_objects import Building, BuildingTypeInfo, VehicleType

import time

building_type_info = {k: BuildingTypeInfo(x) for (k,x) in {
	0: {
		"caption": "Feuerwache",
		"coins": 30,
		"credits": 100000,
		"extensions": [{
			"caption": "Rettungsdienst-Erweiterung",
			"credits": 100000,
			"coins": 20,
			"duration": "7 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 0,
			"unlocksVehicleTypes": [28, 29, 38, 73, 74]
		}, {
			"caption": "Abrollbehälter-Stellplatz",
			"credits": 100000,
			"coins": 20,
			"duration": "7 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 1,
			"unlocksVehicleTypes": [47, 48, 49, 54, 62, 71, 77, 78],
			"parkingLotReservations": [
				[47, 48, 49, 54, 62, 71, 77, 78]
			],
			"cannotDisable": True
		}, {
			"caption": "Wasserrettungs-Erweiterung",
			"credits": 400000,
			"coins": 25,
			"duration": "7 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 0,
			"unlocksVehicleTypes": [64, 63, 70]
		}, {
			"caption": "Abrollbehälter-Stellplatz",
			"credits": 100000,
			"coins": 20,
			"duration": "7 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 1,
			"unlocksVehicleTypes": [47, 48, 49, 54, 62, 71, 77, 78],
			"parkingLotReservations": [
				[47, 48, 49, 54, 62, 71, 77, 78]
			],
			"cannotDisable": True
		}, {
			"caption": "Flughafen-Erweiterung",
			"credits": 300000,
			"coins": 25,
			"duration": "7 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 0,
			"unlocksVehicleTypes": [75, 76]
		}, {
			"caption": "Großwache",
			"credits": 1000000,
			"coins": 50,
			"duration": "7 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 10,
			"cannotDisable": True
		}, {
			"caption": "Abrollbehälter-Stellplatz",
			"credits": 100000,
			"coins": 20,
			"duration": "7 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 1,
			"unlocksVehicleTypes": [47, 48, 49, 54, 62, 71, 77, 78],
			"parkingLotReservations": [
				[47, 48, 49, 54, 62, 71, 77, 78]
			],
			"cannotDisable": True
		}, {
			"caption": "Werkfeuerwehr",
			"credits": 100000,
			"coins": 20,
			"duration": "7 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 0,
			"unlocksVehicleTypes": [83, 84, 85, 86]
		}],
		"maxLevel": 16,
		"startPersonnel": 10,
		"startParkingLots": 1,
		"startVehicles": ["LF 20", "LF 10", "LF 8/6", "LF 20/16", "LF 10/6", "LF 16-TS", "KLF", "MLF", "TSF-W", "HLF 20", "HLF 10"],
		"schoolingTypes": ["Feuerwehr"]
	},
	1: {
		"caption": "Feuerwehrschule",
		"coins": 50,
		"credits": 500000,
		"extensions": [{
			"caption": "Weiterer Klassenraum",
			"credits": 400000,
			"coins": 40,
			"duration": "7 Tage",
			"newClassrooms": 1,
			"requiredExtensions": [],
			"cannotDisable": True
		}],
		"maxLevel": 0,
		"startClassrooms": 1
	},
	2: {
		"caption": "Rettungswache",
		"coins": 35,
		"credits": 200000,
		"extensions": [],
		"maxLevel": 14,
		"startPersonnel": 3,
		"startParkingLots": 1,
		"startVehicles": ["RTW"],
		"schoolingTypes": ["Rettungsdienst"]
	},
	3: {
		"caption": "Rettungsschule",
		"coins": 50,
		"credits": 500000,
		"extensions": [{
			"caption": "Weiterer Klassenraum",
			"credits": 400000,
			"coins": 40,
			"duration": "7 Tage",
			"newClassrooms": 1,
			"requiredExtensions": [],
			"cannotDisable": True
		}],
		"maxLevel": 0,
		"startClassrooms": 1
	},
	4: {
		"caption": "Krankenhaus",
		"coins": 25,
		"credits": 200000,
		"extensions": [{
			"caption": "Allgemeine Innere",
			"credits": 10000,
			"coins": 10,
			"duration": "7 Tage",
			"cannotDisable": True
		}, {
			"caption": "Allgemeine Chirurgie",
			"credits": 10000,
			"coins": 10,
			"duration": "7 Tage",
			"cannotDisable": True
		}, {
			"caption": "Gynäkologie",
			"credits": 70000,
			"coins": 15,
			"duration": "7 Tage",
			"requiredExtensions": [1],
			"cannotDisable": True
		}, {
			"caption": "Urologie",
			"credits": 70000,
			"coins": 15,
			"duration": "7 Tage",
			"requiredExtensions": [1],
			"cannotDisable": True
		}, {
			"caption": "Unfallchirurgie",
			"credits": 70000,
			"coins": 15,
			"duration": "7 Tage",
			"requiredExtensions": [1],
			"cannotDisable": True
		}, {
			"caption": "Neurologie",
			"credits": 70000,
			"coins": 15,
			"duration": "7 Tage",
			"requiredExtensions": [0],
			"cannotDisable": True
		}, {
			"caption": "Neurochirurgie",
			"credits": 70000,
			"coins": 15,
			"duration": "7 Tage",
			"requiredExtensions": [1],
			"cannotDisable": True
		}, {
			"caption": "Kardiologie",
			"credits": 70000,
			"coins": 15,
			"duration": "7 Tage",
			"requiredExtensions": [0],
			"cannotDisable": True
		}, {
			"caption": "Kardiochirurgie",
			"credits": 70000,
			"coins": 15,
			"duration": "7 Tage",
			"requiredExtensions": [1],
			"cannotDisable": True
		}],
		"maxLevel": 20,
		"startBeds": 10
	},
	5: {
		"caption": "Rettungshubschrauber-Station",
		"coins": 50,
		"credits": 1000000,
		"extensions": [],
		"maxLevel": 6,
		"startPersonnel": 0,
		"startParkingLots": 1,
		"startVehicles": [],
		"schoolingTypes": ["Rettungsdienst"]
	},
	6: {
		"caption": "Polizeiwache",
		"coins": 35,
		"credits": 100000,
		"extensions": [{
			"caption": "Zelle",
			"credits": 25000,
			"coins": 5,
			"duration": "7 Tage",
			"newCells": 1,
			"cannotDisable": True
		}, {
			"caption": "Zelle",
			"credits": 25000,
			"coins": 5,
			"duration": "7 Tage",
			"newCells": 1,
			"requiredExtensions": [0],
			"cannotDisable": True
		}, {
			"caption": "Diensthundestaffel",
			"credits": 100000,
			"coins": 10,
			"duration": "5 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 1,
			"unlocksVehicleTypes": [94],
			"parkingLotReservations": [
				[94]
			]
		}, {
			"caption": "Kriminalpolizei-Erweiterung",
			"credits": 100000,
			"coins": 20,
			"duration": "7 Tage",
			"givesParkingLots": 0,
			"unlocksVehicleTypes": [98]
		}, {
			"caption": "Dienstgruppenleitung-Erweiterung",
			"credits": 200000,
			"coins": 25,
			"duration": "7 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 1,
			"unlocksVehicleTypes": [103],
			"parkingLotReservations": [
				[103]
			]
		}],
		"maxLevel": 14,
		"startPersonnel": 2,
		"startParkingLots": 1,
		"startCells": 0,
		"startVehicles": ["FuStW"],
		"schoolingTypes": ["Polizei"]
	},
	7: {
		"caption": "Leitstelle",
		"coins": 0,
		"credits": 0,
		"extensions": [],
		"maxLevel": 0,
		"isDispatchCenter": True
	},
	8: {
		"caption": "Polizeischule",
		"coins": 50,
		"credits": 500000,
		"extensions": [{
			"caption": "Weiterer Klassenraum",
			"credits": 400000,
			"coins": 40,
			"duration": "7 Tage",
			"newClassrooms": 1,
			"requiredExtensions": [],
			"cannotDisable": True
		}],
		"maxLevel": 0,
		"startClassrooms": 1
	},
	9: {
		"caption": "THW-Ortsverband",
		"coins": 35,
		"credits": 200000,
		"extensions": [{
			"caption": "1. Technischer Zug: Bergungsgruppe 2",
			"credits": 25000,
			"coins": 5,
			"duration": "7 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 1,
			"unlocksVehicleTypes": [41],
			"parkingLotReservations": [
				[41]
			]
		}, {
			"caption": "1. Technischer Zug: Zugtrupp",
			"credits": 25000,
			"coins": 5,
			"duration": "7 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 1,
			"unlocksVehicleTypes": [40],
			"parkingLotReservations": [
				[40]
			]
		}, {
			"caption": "Fachgruppe Räumen",
			"credits": 25000,
			"coins": 5,
			"duration": "7 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 4,
			"unlocksVehicleTypes": [42, 43, 44, 45],
			"parkingLotReservations": [
				[42],
				[43],
				[44],
				[45]
			],
			"requiredExtensions": [0, 1]
		}, {
			"caption": "Fachgruppe Wassergefahren",
			"credits": 500000,
			"coins": 25,
			"duration": "7 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 5,
			"unlocksVehicleTypes": [65, 66, 67, 68, 69],
			"parkingLotReservations": [
				[65],
				[66],
				[67],
				[68],
				[69]
			],
			"requiredExtensions": [0, 1]
		}, {
			"caption": "2. Technischer Zug - Grundvoraussetzungen",
			"credits": 25000,
			"coins": 5,
			"duration": "7 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 1,
			"unlocksVehicleTypes": [39],
			"parkingLotReservations": [
				[39]
			],
			"requiredExtensions": [0, 1]
		}, {
			"caption": "2. Technischer Zug: Bergungsgruppe 2",
			"credits": 25000,
			"coins": 5,
			"duration": "7 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 1,
			"unlocksVehicleTypes": [41],
			"parkingLotReservations": [
				[41]
			],
			"requiredExtensions": [4]
		}, {
			"caption": "2. Technischer Zug: Zugtrupp",
			"credits": 25000,
			"coins": 5,
			"duration": "7 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 1,
			"unlocksVehicleTypes": [40],
			"parkingLotReservations": [
				[40]
			],
			"requiredExtensions": [4]
		}, {
			"caption": "Fachgruppe Ortung",
			"credits": 450000,
			"coins": 25,
			"duration": "7 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 2,
			"unlocksVehicleTypes": [92, 93],
			"parkingLotReservations": [
				[92],
				[93]
			],
			"giftsVehicles": [92, 93],
			"requiredExtensions": [0, 1]
		}, {
			"caption": "Fachgruppe Wasserschaden/Pumpen",
			"credits": 200000,
			"coins": 25,
			"duration": "7 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 4,
			"unlocksVehicleTypes": [99, 100, 101, 102],
			"parkingLotReservations": [
				[99],
				[100],
				[101],
				[102]
			],
			"requiredExtensions": [0, 1]
		}],
		"maxLevel": 0,
		"startPersonnel": 9,
		"startParkingLots": 1,
		"startVehicles": ["GKW"],
		"schoolingTypes": ["THW"]
	},
	10: {
		"caption": "THW Bundesschule",
		"coins": 50,
		"credits": 500000,
		"extensions": [{
			"caption": "Weiterer Klassenraum",
			"credits": 400000,
			"coins": 40,
			"duration": "7 Tage",
			"newClassrooms": 1,
			"requiredExtensions": [],
			"cannotDisable": True
		}],
		"maxLevel": 0,
		"startClassrooms": 1
	},
	11: {
		"caption": "Bereitschaftspolizei",
		"coins": 50,
		"credits": 500000,
		"extensions": [{
			"caption": "2. Zug der 1. Hundertschaft",
			"coins": 5,
			"credits": 25000,
			"duration": "3 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 4,
			"unlocksVehicleTypes": [35, 50],
			"parkingLotReservations": [
				[35],
				[50],
				[50],
				[50]
			]
		}, {
			"caption": "3. Zug der 1. Hundertschaft",
			"coins": 5,
			"credits": 25000,
			"duration": "3 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 5,
			"unlocksVehicleTypes": [35, 50, 51],
			"parkingLotReservations": [
				[35],
				[50],
				[50],
				[50],
				[51]
			],
			"requiredExtensions": [0]
		}, {
			"caption": "Sonderfahrzeug: Gefangenenkraftwagen",
			"coins": 5,
			"credits": 25000,
			"duration": "3 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 1,
			"unlocksVehicleTypes": [52],
			"parkingLotReservations": [
				[52]
			],
			"requiredExtensions": [1]
		}, {
			"caption": "Technischer Zug: Wasserwerfer",
			"coins": 5,
			"credits": 25000,
			"duration": "3 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 4,
			"unlocksVehicleTypes": [35, 72],
			"parkingLotReservations": [
				[35],
				[72],
				[72],
				[72]
			]
		}, {
			"caption": "SEK: 1. Zug",
			"coins": 10,
			"credits": 100000,
			"duration": "7 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 5,
			"unlocksVehicleTypes": [51, 79, 80],
			"parkingLotReservations": [
				[51],
				[79],
				[79],
				[79],
				[80]
			]
		}, {
			"caption": "SEK: 2. Zug",
			"coins": 10,
			"credits": 100000,
			"duration": "7 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 5,
			"unlocksVehicleTypes": [51, 79, 80],
			"parkingLotReservations": [
				[51],
				[79],
				[79],
				[79],
				[80]
			],
			"requiredExtensions": [4]
		}, {
			"caption": "MEK: 1. Zug",
			"coins": 10,
			"credits": 100000,
			"duration": "7 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 5,
			"unlocksVehicleTypes": [51, 81, 82],
			"parkingLotReservations": [
				[51],
				[81],
				[81],
				[81],
				[82]
			]
		}, {
			"caption": "MEK: 2. Zug",
			"coins": 10,
			"credits": 100000,
			"duration": "7 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 5,
			"unlocksVehicleTypes": [51, 81, 82],
			"parkingLotReservations": [
				[51],
				[81],
				[81],
				[81],
				[82]
			],
			"requiredExtensions": [6]
		}, {
			"caption": "Diensthundestaffel",
			"credits": 100000,
			"coins": 10,
			"duration": "5 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 3,
			"unlocksVehicleTypes": [94],
			"parkingLotReservations": [
				[94],
				[94],
				[94]
			]
		}],
		"maxLevel": 0,
		"startPersonnel": 0,
		"startParkingLots": 4,
		"startParkingLotReservations": [
			[35],
			[50],
			[50],
			[50]
		],
		"startVehicles": [],
		"schoolingTypes": ["Polizei"]
	},
	12: {
		"caption": "Schnelleinsatzgruppe (SEG)",
		"coins": 30,
		"credits": 100000,
		"extensions": [{
			"caption": "Führung",
			"coins": 5,
			"credits": 25000,
			"duration": "3 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 1,
			"unlocksVehicleTypes": [59],
			"parkingLotReservations": [
				[59]
			]
		}, {
			"caption": "Sanitätsdienst",
			"coins": 5,
			"credits": 25500,
			"duration": "3 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 4,
			"unlocksVehicleTypes": [28, 58, 60],
			"parkingLotReservations": [
				[28],
				[58],
				[58],
				[60]
			]
		}, {
			"caption": "Wasserrettungs-Erweiterung",
			"coins": 25,
			"credits": 500000,
			"duration": "7 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 3,
			"unlocksVehicleTypes": [63, 64, 70],
			"parkingLotReservations": [
				[63, 64, 70],
				[63, 64, 70],
				[63, 64, 70]
			]
		}, {
			"caption": "Rettungshundestaffel",
			"coins": 25,
			"credits": 350000,
			"duration": "7 tage",
			"isVehicleExtension": True,
			"givesParkingLots": 2,
			"unlocksVehicleTypes": [91],
			"parkingLotReservations": [
				[91],
				[91]
			]
		}],
		"maxLevel": 0,
		"startPersonnel": 0,
		"startParkingLots": 1,
		"startVehicles": ["KTW Typ B"],
		"schoolingTypes": ["Rettungsdienst"]
	},
	13: {
		"caption": "Polizeihubschrauberstation",
		"coins": 50,
		"credits": 1000000,
		"extensions": [{
			"caption": "Außenlastbehälter-Erweiterung",
			"credits": 200000,
			"coins": 15,
			"duration": "3 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 1,
			"givesParkingLotsPerLevel": 1,
			"unlocksVehicleTypes": [96],
			"parkingLotReservations": [
				[96]
			]
		}],
		"maxLevel": 6,
		"startPersonnel": 0,
		"startParkingLots": 1,
		"startVehicles": [],
		"schoolingTypes": ["Polizei"]
	},
	14: {
		"caption": "Bereitstellungsraum",
		"coins": 0,
		"credits": 0,
		"extensions": [],
		"maxLevel": 0,
		"isStagingArea": True
	},
	15: {
		"caption": "Wasserrettung",
		"coins": 50,
		"credits": 500000,
		"extensions": [],
		"maxLevel": 5,
		"startPersonnel": 6,
		"startParkingLots": 1,
		"startVehicles": ["GW-Wasserrettung"],
		"schoolingTypes": ["Rettungsdienst"]
	},
	16: {
		"caption": "Verbandszellen",
		"coins": -1,
		"credits": 100000,
		"extensions": [{
			"caption": "Zelle",
			"credits": 25000,
			"coins": 5,
			"duration": "7 Tage",
			"newCells": 1,
			"cannotDisable": True
		}, {
			"caption": "Zelle",
			"credits": 25000,
			"coins": 5,
			"duration": "7 Tage",
			"newCells": 1,
			"requiredExtensions": [0],
			"cannotDisable": True
		}],
		"maxLevel": 0,
		"startCells": 1
	},
	17: {
		"caption": "Polizei-Sondereinheiten",
		"coins": 40,
		"credits": 400000,
		"extensions": [{
			"caption": "SEK: 1. Zug",
			"coins": 10,
			"credits": 100000,
			"duration": "7 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 5,
			"unlocksVehicleTypes": [51, 79, 80],
			"parkingLotReservations": [
				[51],
				[79],
				[79],
				[79],
				[80]
			]
		}, {
			"caption": "SEK: 2. Zug",
			"coins": 10,
			"credits": 100000,
			"duration": "7 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 5,
			"unlocksVehicleTypes": [51, 79, 80],
			"parkingLotReservations": [
				[51],
				[79],
				[79],
				[79],
				[80]
			],
			"requiredExtensions": [0]
		}, {
			"caption": "MEK: 1. Zug",
			"coins": 10,
			"credits": 100000,
			"duration": "7 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 5,
			"unlocksVehicleTypes": [51, 81, 82],
			"parkingLotReservations": [
				[51],
				[81],
				[81],
				[81],
				[82]
			]
		}, {
			"caption": "MEK: 2. Zug",
			"coins": 10,
			"credits": 100000,
			"duration": "7 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 5,
			"unlocksVehicleTypes": [51, 81, 82],
			"parkingLotReservations": [
				[51],
				[81],
				[81],
				[81],
				[82]
			],
			"requiredExtensions": [2]
		}, {
			"caption": "Diensthundestaffel",
			"credits": 100000,
			"coins": 10,
			"duration": "5 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 3,
			"unlocksVehicleTypes": [94],
			"parkingLotReservations": [
				[94],
				[94],
				[94]
			]
		}],
		"maxLevel": 0,
		"startPersonnel": 0,
		"startParkingLots": 0,
		"startVehicles": [],
		"schoolingTypes": ["Polizei"]
	},
	18: {
		"caption": "Feuerwache (Kleinwache)",
		"coins": 25,
		"credits": 50000,
		"extensions": [{
			"caption": "Rettungsdienst-Erweiterung",
			"credits": 100000,
			"coins": 20,
			"duration": "7 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 0,
			"unlocksVehicleTypes": [28, 29, 38, 73, 74]
		}, {
			"caption": "Abrollbehälter-Stellplatz",
			"credits": 100000,
			"coins": 20,
			"duration": "7 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 1,
			"unlocksVehicleTypes": [47, 48, 49, 54, 62, 71, 77, 78],
			"parkingLotReservations": [
				[47, 48, 49, 54, 62, 71, 77, 78]
			],
			"cannotDisable": True
		}, {
			"caption": "Wasserrettungs-Erweiterung",
			"credits": 400000,
			"coins": 25,
			"duration": "7 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 0,
			"unlocksVehicleTypes": [64, 63, 70]
		}, {
			"caption": "Flughafen-Erweiterung",
			"credits": 300000,
			"coins": 25,
			"duration": "7 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 0,
			"unlocksVehicleTypes": [75, 76]
		}, {
			"caption": "Werkfeuerwehr",
			"credits": 100000,
			"coins": 20,
			"duration": "7 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 0,
			"unlocksVehicleTypes": [83, 84, 85, 86]
		}],
		"maxLevel": 5,
		"startPersonnel": 10,
		"startParkingLots": 1,
		"startVehicles": ["LF 20", "LF 10", "LF 8/6", "LF 20/16", "LF 10/6", "LF 16-TS", "KLF", "MLF", "TSF-W", "HLF 20", "HLF 10"],
		"schoolingTypes": ["Feuerwehr"]
	},
	19: {
		"caption": "Polizeiwache (Kleinwache)",
		"coins": 25,
		"credits": 50000,
		"extensions": [{
			"caption": "Zelle",
			"credits": 25000,
			"coins": 5,
			"duration": "7 Tage",
			"newCells": 1,
			"cannotDisable": True
		}, {
			"caption": "Zelle",
			"credits": 25000,
			"coins": 5,
			"duration": "7 Tage",
			"newCells": 1,
			"requiredExtensions": [0],
			"cannotDisable": True
		}, {
			"caption": "Diensthundestaffel",
			"credits": 100000,
			"coins": 10,
			"duration": "5 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 1,
			"unlocksVehicleTypes": [94],
			"parkingLotReservations": [
				[94]
			]
		}, {
			"caption": "Kriminalpolizei-Erweiterung",
			"credits": 100000,
			"coins": 20,
			"duration": "7 Tage",
			"givesParkingLots": 0,
			"unlocksVehicleTypes": [98]
		}, {
			"caption": "Dienstgruppenleitung-Erweiterung",
			"credits": 200000,
			"coins": 25,
			"duration": "7 Tage",
			"isVehicleExtension": True,
			"givesParkingLots": 1,
			"unlocksVehicleTypes": [103],
			"parkingLotReservations": [
				[103]
			]
		}],
		"maxLevel": 4,
		"startPersonnel": 2,
		"startParkingLots": 1,
		"startCells": 0,
		"startVehicles": ["FuStW"],
		"schoolingTypes": ["Polizei"]
	},
	20: {
		"caption": "Rettungswache (Kleinwache)",
		"coins": 25,
		"credits": 100000,
		"extensions": [],
		"maxLevel": 5,
		"startPersonnel": 3,
		"startParkingLots": 1,
		"startVehicles": ["RTW"],
		"schoolingTypes": ["Rettungsdienst"]
	},
	21: {
		"caption": "Rettungshundestaffel",
		"coins": 50,
		"credits": 450000,
		"extensions": [],
		"maxLevel": 5,
		"startPersonnel": 10,
		"startParkingLots": 2,
		"startVehicles": ["Rettungshundefahrzeug"],
		"schoolingTypes": ["Rettungsdienst"]
	},
	22: {
		"caption": "Großer Komplex",
		"coins": -1,
		"credits": -1,
		"extensions": [],
		"maxLevel": 5,
		"startPersonnel": -1,
		"startParkingLots": 0,
		"startVehicles": [""],
		"schoolingTypes": []
	},
	23: {
		"caption": "Kleiner Komplex",
		"coins": -1,
		"credits": -1,
		"extensions": [],
		"maxLevel": 5,
		"startPersonnel": -1,
		"startParkingLots": 0,
		"startVehicles": [""],
		"schoolingTypes": []
	}
}.items()}

vehicle_type_info = {k: VehicleType(x) for (k,x) in {
    0: {
        "caption": "LF 20",
        "coins": 25,
        "credits": 5000,
        "minPersonnel": 1,
        "maxPersonnel": 9,
        "wtank": 2000,
        "pumpcap": 2000,
        "possibleBuildings": [0, 18]
    },
    1: {
        "caption": "LF 10",
        "coins": 25,
        "credits": 5000,
        "minPersonnel": 1,
        "maxPersonnel": 9,
        "wtank": 1200,
        "pumpcap": 1000,
        "possibleBuildings": [0, 18]
    },
    2: {
        "caption": "DLK 23",
        "coins": 30,
        "credits": 10000,
        "minPersonnel": 1,
        "maxPersonnel": 3,
        "possibleBuildings": [0, 18]
    },
    3: {
        "caption": "ELW 1",
        "coins": 25,
        "credits": 10000,
        "minPersonnel": 1,
        "maxPersonnel": 3,
        "possibleBuildings": [0, 18]
    },
    4: {
        "caption": "RW",
        "coins": 25,
        "credits": 12180,
        "minPersonnel": 1,
        "maxPersonnel": 3,
        "possibleBuildings": [0, 18]
    },
    5: {
        "caption": "GW-A",
        "coins": 25,
        "credits": 11680,
        "minPersonnel": 1,
        "maxPersonnel": 3,
        "possibleBuildings": [0, 18]
    },
    6: {
        "caption": "LF 8/6",
        "coins": 25,
        "credits": 5000,
        "minPersonnel": 1,
        "maxPersonnel": 9,
        "wtank": 600,
        "pumpcap": 800,
        "possibleBuildings": [0, 18]
    },
    7: {
        "caption": "LF 20/16",
        "coins": 25,
        "credits": 5000,
        "minPersonnel": 1,
        "maxPersonnel": 9,
        "wtank": 1600,
        "pumpcap": 2000,
        "possibleBuildings": [0, 18]
    },
    8: {
        "caption": "LF 10/6",
        "coins": 25,
        "credits": 5000,
        "minPersonnel": 1,
        "maxPersonnel": 9,
        "wtank": 600,
        "pumpcap": 1000,
        "possibleBuildings": [0, 18]
    },
    9: {
        "caption": "LF 16-TS",
        "coins": 25,
        "credits": 5000,
        "minPersonnel": 1,
        "maxPersonnel": 9,
        "pumpcap": 1600,
        "possibleBuildings": [0, 18]
    },
    10: {
        "caption": "GW-Öl",
        "coins": 25,
        "credits": 12000,
        "minPersonnel": 1,
        "maxPersonnel": 3,
        "possibleBuildings": [0, 18]
    },
    11: {
        "caption": "GW-L2-Wasser",
        "coins": 25,
        "credits": 17300,
        "minPersonnel": 1,
        "maxPersonnel": 3,
        "possibleBuildings": [0, 18]
    },
    12: {
        "caption": "GW-Messtechnik",
        "coins": 25,
        "credits": 18300,
        "minPersonnel": 1,
        "maxPersonnel": 3,
        "schooling": {
            "Feuerwehr": {
                "GW-Messtechnik": {
                    "all": True
                }
            }
        },
        "possibleBuildings": [0, 18]
    },
    13: {
        "caption": "SW 1000",
        "coins": 25,
        "credits": 17300,
        "minPersonnel": 1,
        "maxPersonnel": 3,
        "possibleBuildings": [0, 18]
    },
    14: {
        "caption": "SW 2000",
        "coins": 25,
        "credits": 17300,
        "minPersonnel": 1,
        "maxPersonnel": 6,
        "possibleBuildings": [0, 18]
    },
    15: {
        "caption": "SW 2000-Tr",
        "coins": 25,
        "credits": 17300,
        "minPersonnel": 1,
        "maxPersonnel": 3,
        "possibleBuildings": [0, 18]
    },
    16: {
        "caption": "SW Kats",
        "coins": 25,
        "credits": 17300,
        "minPersonnel": 1,
        "maxPersonnel": 3,
        "possibleBuildings": [0, 18]
    },
    17: {
        "caption": "TLF 2000",
        "coins": 25,
        "credits": 5000,
        "minPersonnel": 1,
        "maxPersonnel": 3,
        "wtank": 2000,
        "pumpcap": 1000,
        "possibleBuildings": [0, 18]
    },
    18: {
        "caption": "TLF 3000",
        "coins": 25,
        "credits": 5000,
        "minPersonnel": 1,
        "maxPersonnel": 3,
        "wtank": 3000,
        "pumpcap": 2000,
        "possibleBuildings": [0, 18]
    },
    19: {
        "caption": "TLF 8/8",
        "coins": 25,
        "credits": 5000,
        "minPersonnel": 1,
        "maxPersonnel": 3,
        "wtank": 800,
        "pumpcap": 800,
        "possibleBuildings": [0, 18]
    },
    20: {
        "caption": "TLF 8/18",
        "coins": 25,
        "credits": 5000,
        "minPersonnel": 1,
        "maxPersonnel": 3,
        "wtank": 1800,
        "pumpcap": 800,
        "possibleBuildings": [0, 18]
    },
    21: {
        "caption": "TLF 16/24-Tr",
        "coins": 25,
        "credits": 5000,
        "minPersonnel": 1,
        "maxPersonnel": 3,
        "wtank": 2400,
        "pumpcap": 1600,
        "possibleBuildings": [0, 18]
    },
    22: {
        "caption": "TLF 16/25",
        "coins": 25,
        "credits": 5000,
        "minPersonnel": 1,
        "maxPersonnel": 6,
        "wtank": 2400,
        "pumpcap": 1600,
        "possibleBuildings": [0, 18]
    },
    23: {
        "caption": "TLF 16/45",
        "coins": 25,
        "credits": 5000,
        "minPersonnel": 1,
        "maxPersonnel": 3,
        "wtank": 4500,
        "pumpcap": 1600,
        "possibleBuildings": [0, 18]
    },
    24: {
        "caption": "TLF 20/40",
        "coins": 25,
        "credits": 5000,
        "minPersonnel": 1,
        "maxPersonnel": 3,
        "wtank": 4000,
        "pumpcap": 2000,
        "possibleBuildings": [0, 18]
    },
    25: {
        "caption": "TLF 20/40-SL",
        "coins": 25,
        "credits": 5000,
        "minPersonnel": 1,
        "maxPersonnel": 3,
        "wtank": 4000,
        "pumpcap": 2000,
        "possibleBuildings": [0, 18]
    },
    26: {
        "caption": "TLF 16",
        "coins": 25,
        "credits": 5000,
        "minPersonnel": 1,
        "maxPersonnel": 3,
        "wtank": 1800,
        "pumpcap": 1600,
        "possibleBuildings": [0, 18]
    },
    27: {
        "caption": "GW-Gefahrgut",
        "coins": 25,
        "credits": 19200,
        "minPersonnel": 1,
        "maxPersonnel": 3,
        "schooling": {
            "Feuerwehr": {
                "GW-Gefahrgut": {
                    "all": True
                }
            }
        },
        "possibleBuildings": [0, 18]
    },
    28: {
        "caption": "RTW",
        "coins": 25,
        "credits": 5000,
        "minPersonnel": 1,
        "maxPersonnel": 2,
        "possibleBuildings": [0, 18, 2, 12, 20]
    },
    29: {
        "caption": "NEF",
        "coins": 25,
        "credits": 20000,
        "minPersonnel": 1,
        "maxPersonnel": 2,
        "schooling": {
            "Feuerwehr": {
                "Notarzt": {
                    "all": True
                }
            },
            "Rettungsdienst": {
                "Notarzt": {
                    "all": True
                }
            }
        },
        "possibleBuildings": [0, 18, 2, 20]
    },
    30: {
        "caption": "HLF 20",
        "coins": 25,
        "credits": 20000,
        "minPersonnel": 1,
        "maxPersonnel": 9,
        "wtank": 1600,
        "pumpcap": 2000,
        "possibleBuildings": [0, 18]
    },
    31: {
        "caption": "RTH",
        "coins": 30,
        "credits": 300000,
        "minPersonnel": 1,
        "maxPersonnel": 1,
        "schooling": {
            "Rettungsdienst": {
                "Notarzt": {
                    "all": True
                }
            }
        },
        "possibleBuildings": [5]
    },
    32: {
        "caption": "FuStW",
        "coins": 25,
        "credits": 5000,
        "minPersonnel": 1,
        "maxPersonnel": 2,
        "possibleBuildings": [6, 19]
    },
    33: {
        "caption": "GW-Höhenrettung",
        "coins": 25,
        "credits": 19500,
        "minPersonnel": 1,
        "maxPersonnel": 9,
        "schooling": {
            "Feuerwehr": {
                "GW-Höhenrettung": {
                    "all": True
                }
            }
        },
        "possibleBuildings": [0, 18]
    },
    34: {
        "caption": "ELW 2",
        "coins": 25,
        "credits": 25500,
        "minPersonnel": 1,
        "maxPersonnel": 6,
        "schooling": {
            "Feuerwehr": {
                "ELW 2": {
                    "all": True
                }
            }
        },
        "possibleBuildings": [0, 18]
    },
    35: {
        "caption": "leBefKw",
        "coins": 25,
        "credits": 10000,
        "minPersonnel": 1,
        "maxPersonnel": 3,
        "schooling": {
            "Polizei": {
                "Zugführer (leBefKw)": {
                    "all": True
                }
            }
        },
        "possibleBuildings": [11]
    },
    36: {
        "caption": "MTW",
        "coins": 12,
        "credits": 2500,
        "minPersonnel": 1,
        "maxPersonnel": 9,
        "possibleBuildings": [0, 18]
    },
    37: {
        "caption": "TSF-W",
        "coins": 25,
        "credits": 5000,
        "minPersonnel": 1,
        "maxPersonnel": 6,
        "wtank": 500,
        "pumpcap": 1000,
        "possibleBuildings": [0, 18]
    },
    38: {
        "caption": "KTW",
        "coins": 25,
        "credits": 5000,
        "minPersonnel": 1,
        "maxPersonnel": 2,
        "possibleBuildings": [0, 2, 18, 20]
    },
    39: {
        "caption": "GKW",
        "coins": 25,
        "credits": 13000,
        "minPersonnel": 1,
        "maxPersonnel": 9,
        "possibleBuildings": [9]
    },
    40: {
        "caption": "MTW-TZ",
        "coins": 12,
        "credits": 2500,
        "minPersonnel": 1,
        "maxPersonnel": 4,
        "schooling": {
            "THW": {
                "Zugtrupp": {
                    "all": True
                }
            }
        },
        "possibleBuildings": [9]
    },
    41: {
        "caption": "MzKW",
        "coins": 25,
        "credits": 15000,
        "minPersonnel": 1,
        "maxPersonnel": 9,
        "possibleBuildings": [9]
    },
    42: {
        "caption": "LKW K 9",
        "coins": 25,
        "credits": 15000,
        "minPersonnel": 1,
        "maxPersonnel": 3,
        "schooling": {
            "THW": {
                "Fachgruppe Räumen": {
                    "all": True
                }
            }
        },
        "possibleBuildings": [9]
    },
    43: {
        "caption": "BRmG R",
        "coins": 25,
        "credits": 15000,
        "minPersonnel": 0,
        "maxPersonnel": 0,
        "possibleBuildings": [9]
    },
    44: {
        "caption": "Anh DLE",
        "coins": 25,
        "credits": 15000,
        "minPersonnel": 0,
        "maxPersonnel": 0,
        "possibleBuildings": [9]
    },
    45: {
        "caption": "MLW 5",
        "coins": 12,
        "credits": 2500,
        "minPersonnel": 1,
        "maxPersonnel": 6,
        "schooling": {
            "THW": {
                "Fachgruppe Räumen": {
                    "all": True
                }
            }
        },
        "possibleBuildings": [9]
    },
    46: {
        "caption": "WLF",
        "coins": 12,
        "credits": 5000,
        "minPersonnel": 1,
        "maxPersonnel": 3,
        "schooling": {
            "Feuerwehr": {
                "Wechsellader Lehrgang": {
                    "all": True
                }
            }
        },
        "truck": "truck-pickup",
        "possibleBuildings": [0, 18]
    },
    47: {
        "caption": "AB-Rüst",
        "coins": 12,
        "credits": 6000,
        "minPersonnel": 0,
        "maxPersonnel": 0,
        "possibleBuildings": [0, 18]
    },
    48: {
        "caption": "AB-Atemschutz",
        "coins": 12,
        "credits": 6000,
        "minPersonnel": 0,
        "maxPersonnel": 0,
        "possibleBuildings": [0, 18]
    },
    49: {
        "caption": "AB-Öl",
        "coins": 12,
        "credits": 6000,
        "minPersonnel": 0,
        "maxPersonnel": 0,
        "possibleBuildings": [0, 18]
    },
    50: {
        "caption": "GruKw",
        "coins": 25,
        "credits": 10000,
        "minPersonnel": 1,
        "maxPersonnel": 9,
        "possibleBuildings": [11]
    },
    51: {
        "caption": "FüKw",
        "coins": 25,
        "credits": 17500,
        "minPersonnel": 1,
        "maxPersonnel": 3,
        "schooling": {
            "Polizei": {
                "Hundertschaftsführer (FüKw)": {
                    "all": True
                }
            }
        },
        "possibleBuildings": [11]
    },
    52: {
        "caption": "GefKw",
        "coins": 25,
        "credits": 13000,
        "minPersonnel": 1,
        "maxPersonnel": 2,
        "possibleBuildings": [11]
    },
    53: {
        "caption": "Dekon-P",
        "coins": 25,
        "credits": 23100,
        "minPersonnel": 3,
        "maxPersonnel": 6,
        "schooling": {
            "Feuerwehr": {
                "Dekon-P": {
                    "all": True
                }
            }
        },
        "possibleBuildings": [0, 18]
    },
    54: {
        "caption": "AB-Dekon-P",
        "coins": 12,
        "credits": 6000,
        "minPersonnel": 0,
        "maxPersonnel": 0,
        "possibleBuildings": [0, 18]
    },
    55: {
        "caption": "KdoW-LNA",
        "coins": 25,
        "credits": 20000,
        "minPersonnel": 1,
        "maxPersonnel": 1,
        "schooling": {
            "Rettungsdienst": {
                "LNA": {
                    "all": True
                }
            }
        },
        "possibleBuildings": [2, 20]
    },
    56: {
        "caption": "KdoW-OrgL",
        "coins": 25,
        "credits": 20000,
        "minPersonnel": 1,
        "maxPersonnel": 1,
        "schooling": {
            "Rettungsdienst": {
                "OrgL": {
                    "all": True
                }
            }
        },
        "possibleBuildings": [2, 20]
    },
    57: {
        "caption": "FwK",
        "coins": 25,
        "credits": 30000,
        "minPersonnel": 1,
        "maxPersonnel": 2,
        "schooling": {
            "Feuerwehr": {
                "Feuerwehrkran": {
                    "all": True
                }
            }
        },
        "possibleBuildings": [0, 18]
    },
    58: {
        "caption": "KTW Typ B",
        "coins": 25,
        "credits": 5000,
        "minPersonnel": 1,
        "maxPersonnel": 2,
        "possibleBuildings": [12]
    },
    59: {
        "caption": "ELW 1 (SEG)",
        "coins": 25,
        "credits": 25500,
        "minPersonnel": 1,
        "maxPersonnel": 2,
        "schooling": {
            "Rettungsdienst": {
                "SEG - Einsatzleitung": {
                    "all": True
                }
            }
        },
        "possibleBuildings": [12]
    },
    60: {
        "caption": "GW-San",
        "coins": 25,
        "credits": 10000,
        "minPersonnel": 6,
        "maxPersonnel": 6,
        "schooling": {
            "Rettungsdienst": {
                "SEG - GW-San": {
                    "all": True
                }
            }
        },
        "possibleBuildings": [12]
    },
    61: {
        "caption": "Polizeihubschrauber",
        "coins": 30,
        "credits": 300000,
        "minPersonnel": 1,
        "maxPersonnel": 3,
        "schooling": {
            "Polizei": {
                "Polizeihubschrauber": {
                    "all": True
                }
            }
        },
        "possibleBuildings": [13]
    },
    62: {
        "caption": "AB-Schlauch",
        "coins": 12,
        "credits": 6000,
        "minPersonnel": 0,
        "maxPersonnel": 0,
        "possibleBuildings": [0, 18]
    },
    63: {
        "caption": "GW-Taucher",
        "coins": 25,
        "credits": 10000,
        "minPersonnel": 2,
        "maxPersonnel": 2,
        "schooling": {
            "Feuerwehr": {
                "GW-Taucher": {
                    "all": True
                }
            },
            "Rettungsdienst": {
                "GW-Taucher": {
                    "all": True
                }
            }
        },
        "possibleBuildings": [0, 12, 15, 18, 22]
    },
    64: {
        "caption": "GW-Wasserrettung",
        "coins": 25,
        "credits": 10000,
        "minPersonnel": 1,
        "maxPersonnel": 6,
        "schooling": {
            "Feuerwehr": {
                "GW-Wasserrettung": {
                    "all": True
                }
            },
            "Rettungsdienst": {
                "GW-Wasserrettung": {
                    "all": True
                }
            }
        },
        "possibleBuildings": [0, 12, 15, 18, 22]
    },
    65: {
        "caption": "LKW 7 Lkr 19 tm",
        "coins": 25,
        "credits": 10000,
        "minPersonnel": 1,
        "maxPersonnel": 2,
        "possibleBuildings": [9]
    },
    66: {
        "caption": "Anh MzB",
        "coins": 12,
        "credits": 6000,
        "minPersonnel": 0,
        "maxPersonnel": 0,
        "possibleBuildings": [9]
    },
    67: {
        "caption": "Anh SchlB",
        "coins": 12,
        "credits": 6000,
        "minPersonnel": 0,
        "maxPersonnel": 0,
        "possibleBuildings": [9]
    },
    68: {
        "caption": "Anh MzAB",
        "coins": 12,
        "credits": 6000,
        "minPersonnel": 0,
        "maxPersonnel": 0,
        "possibleBuildings": [9]
    },
    69: {
        "caption": "Tauchkraftwagen",
        "coins": 25,
        "credits": 10000,
        "minPersonnel": 1,
        "maxPersonnel": 2,
        "schooling": {
            "THW": {
                "Fachgruppe Bergungstaucher": {
                    "all": True
                }
            }
        },
        "possibleBuildings": [9]
    },
    70: {
        "caption": "MZB",
        "coins": 12,
        "credits": 6000,
        "minPersonnel": 0,
        "maxPersonnel": 0,
        "possibleBuildings": [0, 12, 15, 18, 22]
    },
    71: {
        "caption": "AB-MZB",
        "coins": 12,
        "credits": 6000,
        "minPersonnel": 0,
        "maxPersonnel": 0,
        "possibleBuildings": [0, 18]
    },
    72: {
        "caption": "WaWe 10",
        "coins": 25,
        "credits": 13000,
        "minPersonnel": 5,
        "maxPersonnel": 5,
        "schooling": {
            "Polizei": {
                "Wasserwerfer": {
                    "all": True
                }
            }
        },
        "possibleBuildings": [11]
    },
    73: {
        "caption": "GRTW",
        "coins": 25,
        "credits": 25000,
        "minPersonnel": 6,
        "maxPersonnel": 6,
        "schooling": {
            "Feuerwehr": {
                "Notarzt": {
                    "all": True
                }
            },
            "Rettungsdienst": {
                "Notarzt": {
                    "all": True
                }
            }
        },
        "possibleBuildings": [0, 2, 18, 20]
    },
    74: {
        "caption": "NAW",
        "coins": 25,
        "credits": 25000,
        "minPersonnel": 3,
        "maxPersonnel": 3,
        "schooling": {
            "Feuerwehr": {
                "Notarzt": {
                    "all": True
                }
            },
            "Rettungsdienst": {
                "Notarzt": {
                    "all": True
                }
            }
        },
        "possibleBuildings": [0, 2, 18, 20]
    },
    75: {
        "caption": "FLF",
        "coins": 25,
        "credits": 80000,
        "minPersonnel": 2,
        "maxPersonnel": 3,
        "wtank": 12000,
        "schooling": {
            "Feuerwehr": {
                "Flugfeldlöschfahrzeug": {
                    "all": True
                }
            }
        },
        "possibleBuildings": [0, 18]
    },
    76: {
        "caption": "Rettungstreppe",
        "coins": 25,
        "credits": 20000,
        "minPersonnel": 2,
        "maxPersonnel": 2,
        "schooling": {
            "Feuerwehr": {
                "Rettungstreppe": {
                    "all": True
                }
            }
        },
        "possibleBuildings": [0, 18]
    },
    77: {
        "caption": "AB-Gefahrgut",
        "coins": 12,
        "credits": 6000,
        "minPersonnel": 0,
        "maxPersonnel": 0,
        "possibleBuildings": [0, 18]
    },
    78: {
        "caption": "AB-Einsatzleitung",
        "coins": 12,
        "credits": 6000,
        "minPersonnel": 0,
        "maxPersonnel": 0,
        "possibleBuildings": [0, 18]
    },
    79: {
        "caption": "SEK - ZF",
        "coins": 25,
        "credits": 10000,
        "minPersonnel": 3,
        "maxPersonnel": 4,
        "schooling": {
            "Polizei": {
                "SEK": {
                    "all": True
                }
            }
        },
        "possibleBuildings": [11, 17]
    },
    80: {
        "caption": "SEK - MTF",
        "coins": 25,
        "credits": 10000,
        "minPersonnel": 9,
        "maxPersonnel": 9,
        "schooling": {
            "Polizei": {
                "SEK": {
                    "all": True
                }
            }
        },
        "possibleBuildings": [11, 17]
    },
    81: {
        "caption": "MEK - ZF",
        "coins": 25,
        "credits": 10000,
        "minPersonnel": 3,
        "maxPersonnel": 4,
        "schooling": {
            "Polizei": {
                "MEK": {
                    "all": True
                }
            }
        },
        "possibleBuildings": [11, 17]
    },
    82: {
        "caption": "MEK - MTF",
        "coins": 25,
        "credits": 10000,
        "minPersonnel": 9,
        "maxPersonnel": 9,
        "schooling": {
            "Polizei": {
                "MEK": {
                    "all": True
                }
            }
        },
        "possibleBuildings": [11, 17]
    },
    83: {
        "caption": "GW-Werkfeuerwehr",
        "coins": 30,
        "credits": 15000,
        "minPersonnel": 1,
        "maxPersonnel": 9,
        "schooling": {
            "Feuerwehr": {
                "Werkfeuerwehr": {
                    "all": True
                }
            }
        },
        "possibleBuildings": [0, 18]
    },
    84: {
        "caption": "ULF mit Löscharm",
        "coins": 25,
        "credits": 20000,
        "minPersonnel": 1,
        "maxPersonnel": 3,
        "wtank": 5000,
        "schooling": {
            "Feuerwehr": {
                "Werkfeuerwehr": {
                    "all": True
                }
            }
        },
        "possibleBuildings": [0, 18]
    },
    85: {
        "caption": "TM 50",
        "coins": 30,
        "credits": 20000,
        "minPersonnel": 1,
        "maxPersonnel": 3,
        "schooling": {
            "Feuerwehr": {
                "Werkfeuerwehr": {
                    "all": True
                }
            }
        },
        "possibleBuildings": [0, 18]
    },
    86: {
        "caption": "Turbolöscher",
        "coins": 30,
        "credits": 12500,
        "minPersonnel": 1,
        "maxPersonnel": 3,
        "schooling": {
            "Feuerwehr": {
                "Werkfeuerwehr": {
                    "all": True
                }
            }
        },
        "possibleBuildings": [0, 18]
    },
    87: {
        "caption": "TLF 4000",
        "coins": 25,
        "credits": 5000,
        "minPersonnel": 1,
        "maxPersonnel": 3,
        "wtank": 4000,
        "pumpcap": 2000,
        "possibleBuildings": [0, 18]
    },
    88: {
        "caption": "KLF",
        "coins": 25,
        "credits": 5000,
        "minPersonnel": 1,
        "maxPersonnel": 6,
        "wtank": 500,
        "pumpcap": 1000,
        "possibleBuildings": [0, 18]
    },
    89: {
        "caption": "MLF",
        "coins": 25,
        "credits": 5000,
        "minPersonnel": 1,
        "maxPersonnel": 6,
        "wtank": 1000,
        "pumpcap": 1000,
        "possibleBuildings": [0, 18]
    },
    90: {
        "caption": "HLF 10",
        "coins": 25,
        "credits": 20000,
        "minPersonnel": 1,
        "maxPersonnel": 9,
        "wtank": 1000,
        "pumpcap": 1000,
        "possibleBuildings": [0, 18]
    },
    91: {
        "caption": "Rettungshundefahrzeug",
        "coins": 25,
        "credits": 25000,
        "minPersonnel": 4,
        "maxPersonnel": 5,
        "schooling": {
            "Rettungsdienst": {
                "Rettungshundeführer (SEG)": {
                    "all": True
                }
            }
        },
        "possibleBuildings": [12, 21]
    },
    92: {
        "caption": "Anh Hund",
        "coins": 0,
        "credits": 6000,
        "minPersonnel": 0,
        "maxPersonnel": 0,
        "possibleBuildings": [9]
    },
    93: {
        "caption": "MTW-OV",
        "coins": 0,
        "credits": 19000,
        "minPersonnel": 4,
        "maxPersonnel": 5,
        "schooling": {
            "THW": {
                "Rettungshundeführer (THW)": {
                    "all": True
                }
            }
        },
        "possibleBuildings": [9]
    },
    94: {
        "caption": "DHuFüKw",
        "coins": 10,
        "credits": 15000,
        "minPersonnel": 1,
        "maxPersonnel": 2,
        "schooling": {
            "Polizei": {
                "Hundeführer (Schutzhund)": {
                    "all": True
                }
            }
        },
        "possibleBuildings": [6, 11, 17, 19, 22]
    },
    95: {
        "caption": "Polizeimotorrad",
        "coins": 10,
        "credits": 3000,
        "minPersonnel": 1,
        "maxPersonnel": 1,
        "schooling": {
            "Polizei": {
                "Motorradstaffel": {
                    "all": True
                }
            }
        },
        "possibleBuildings": [6, 19]
    },
    96: {
        "caption": "Außenlastbehälter (allgemein)",
        "coins": 10,
        "credits": 50000,
        "minPersonnel": 0,
        "maxPersonnel": 0,
        "possibleBuildings": [13]
    },
    97: {
        "caption": "ITW",
        "coins": 25,
        "credits": 30000,
        "minPersonnel": 3,
        "maxPersonnel": 3,
        "schooling": {
            "Feuerwehr": {
                "Intensivpflege": {
                    "min": 2
                },
                "Notarzt": {
                    "min": 1
                }
            },
            "Rettungsdienst": {
                "Intensivpflege": {
                    "min": 2
                },
                "Notarzt": {
                    "min": 1
                }
            }
        },
        "possibleBuildings": [0, 2, 18, 20]
    },
    98: {
        "caption": "Zivilstreifenwagen",
        "coins": 25,
        "credits": 5000,
        "minPersonnel": 1,
        "maxPersonnel": 2,
        "schooling": {
            "Polizei": {
                "Kriminalpolizei": {
                    "all": True
                }
            }
        },
        "possibleBuildings": [6, 19]
    },
    99: {
        "caption": "LKW 7 Lbw",
        "coins": 25,
        "credits": 15000,
        "minPersonnel": 1,
        "maxPersonnel": 3,
        "schooling": {
            "THW": {
                "Fachgruppe Wasserschaden/Pumpen": {
                    "all": True
                }
            }
        },
        "possibleBuildings": [9]
    },
    100: {
        "caption": "MLW 4",
        "coins": 25,
        "credits": 15000,
        "minPersonnel": 1,
        "maxPersonnel": 7,
        "schooling": {
            "THW": {
                "Fachgruppe Wasserschaden/Pumpen": {
                    "all": True
                }
            }
        },
        "possibleBuildings": [9]
    },
    101: {
        "caption": "Anh SwPu",
        "coins": 25,
        "credits": 15000,
        "minPersonnel": 0,
        "maxPersonnel": 0,
        "pumpcap": 15000,
        "possibleBuildings": [9]
    },
    102: {
        "caption": "Anh 7",
        "coins": 25,
        "credits": 15000,
        "minPersonnel": 0,
        "maxPersonnel": 0,
        "pumpcap": 12400,
        "possibleBuildings": [9]
    },
    103: {
        "caption": "FuStW (DGL)",
        "coins": 25,
        "credits": 25000,
        "minPersonnel": 1,
        "maxPersonnel": 2,
        "schooling": {
            "Polizei": {
                "Dienstgruppenleitung": {
                    "all": True
                }
            }
        },
        "possibleBuildings": [6, 19]
    }
}.items()}

# adds additional info to buildings
def add_additional_building_info(c, buildings, vehicles, first_n_only=-1):
	buildings = sorted([Building(b) for b in buildings], key=lambda e: e.name)

	mod_b = []
	for b in buildings:
		print(f"Loading Building Info {buildings.index(b)+1} / {len(buildings)}...", end="\r")

		b.type_info = building_type_info[b.building_type]
		b.personnel = c.get_building_personnel(b.id)

		# add extension info
		enriched_extensions = []
		for ex in b.extensions:
			extension_info = [x for x in building_type_info[b.building_type].extensions if x.name == ex["caption"]][0]
			extension_info.building_in_progress = "available_at" in ex.keys()
			enriched_extensions.append(extension_info)

		b.extensions = enriched_extensions

		# add vehicle type infos
		b.vehicles = []
		for v in vehicles:
			if v.building_id != b.id:
				continue
			v.type_info = vehicle_type_info[v.type_id]
			b.vehicles.append(v)

		# calculate total vehicle slots
		if b.type_info.start_parking_lots is not None:
			b.total_parking = b.type_info.start_parking_lots + b.level + sum([x.gives_parking_lots for x in b.extensions if x.gives_parking_lots is not None])
		else:
			b.total_parking = None

		# add personnel per schooling
		b.personnel_count_by_schooling = {}
		for p in b.personnel:
			if p.schooling not in b.personnel_count_by_schooling:
				b.personnel_count_by_schooling[p.schooling] = 0

			b.personnel_count_by_schooling[p.schooling] += 1

		# add required personnel per schooling
		b.min_personnel_with_schooling_required = {}
		b.max_personnel_with_schooling_required = {}
		for v in b.vehicles:
			if len(list(v.type_info.schooling.keys())) == 0:
				b.min_personnel_with_schooling_required[None] = b.min_personnel_with_schooling_required[None] + v.type_info.min_personnel if None in b.min_personnel_with_schooling_required else v.type_info.min_personnel
				b.max_personnel_with_schooling_required[None] = b.max_personnel_with_schooling_required[None] + v.type_info.max_personnel if None in b.max_personnel_with_schooling_required else v.type_info.max_personnel
			else:
				for k in v.type_info.schooling:
					if v.type_info.schooling[k] is True:
						b.min_personnel_with_schooling_required[k] = b.min_personnel_with_schooling_required[k] + v.type_info.min_personnel if k in b.min_personnel_with_schooling_required else v.type_info.min_personnel
						b.max_personnel_with_schooling_required[k] = b.max_personnel_with_schooling_required[k] + v.type_info.max_personnel if k in b.max_personnel_with_schooling_required else v.type_info.max_personnel
					else:
						b.min_personnel_with_schooling_required[k] = b.min_personnel_with_schooling_required[k] + v.type_info.schooling[k] if k in b.min_personnel_with_schooling_required else v.type_info.schooling[k]
						b.max_personnel_with_schooling_required[k] = b.max_personnel_with_schooling_required[k] + v.type_info.schooling[k] if k in b.max_personnel_with_schooling_required else v.type_info.schooling[k]

		# save updated version
		mod_b.append(b)

		if first_n_only > 0 and buildings.index(b)+1 == first_n_only:
			break

		time.sleep(0.1)
	
	print(" "*(len(f"Loading Building Info {len(buildings)} / {len(buildings)}...")+2), end="\r")

	return mod_b
