
# OSMEnv BEST RESULTS Parameters
max_steps_per_episode = 100
num_episodes = 750
agent_start_refresh_rate = 50
max_number_stations=25
minimum_agent_amount = 4
maximum_agent_amount = 12
video_filename = "osm_env_training.mp4"

# Reward Weights

Weights = {
    "Success": 1.0,
    "Fail": -1.0,
    "DistanceTimeAvg": 0.3,
    "TravelTime": 0.6,
    "TravelLength": 0.7,
    "Cycle": -1.0,
    "DeadEnd": -0.8,
    "Coverage": 0.9,
    "Exploration": 0.6,
    "Overlap": -0.1,
    "POI": 0.6,
    "Crossing": 0.9,
    "StationProximityPOI": 0.7,
    "StationMultiRouteUse": 0.9,
    "StationDensityPenalty": -0.3,
    "StationCost": -0.4
}

# Training Consts

PLOT_EPISODE_INTERVAL = 300
LOAD_PRETRAINED_MODELS = False
EXPLORATION_DECAY_RATE = 0.01

# Experiments

experiments = {
    "ramat_aviv": {
        "num_agents": 3,
        "location": "Ramat Aviv, Tel Aviv, Israel",
        "central_stations": [8557525209, 440061820, 11498283530],
        "interest_points": {
                    1104534232: {'type': 'mall', 'grade': 1},
                    440062888: {'type': 'school', 'grade': 0.6},
                    440062013: {'type': 'park', 'grade': 0.8},
                    440062762: {'type': 'restaurant', 'grade': 0.7},
                    290507602: {'type': 'hospital', 'grade': 0.9},
                    1135283061: {'type': 'cafe', 'grade': 0.5}
      },
    },
    "bat_yam": {
        "num_agents": 10,
        "location": "Bat Yam, Tel Aviv Subdistrict, Tel-Aviv District, Israel",
        "central_stations": [367010181, 10285992984, 318177548, 566747901, 566749403, 2320421889, 566948027, 1880782316, 319076297, 5067373990,],
        "interest_points": {
                            566751227: {'type': 'mall', 'grade': 1},
                            1240318661: {'type': 'school', 'grade': 0.6},
                            1295251398: {'type': 'park', 'grade': 0.8},
                            5265723735: {'type': 'restaurant', 'grade': 0.7},
                            11230870752: {'type': 'hospital', 'grade': 0.9},
                            318178073: {'type': 'cafe', 'grade': 0.5},
                            734894851: {'type': 'mall', 'grade': 1},
                            566751244: {'type': 'school', 'grade': 0.6},
                            1731446290: {'type': 'park', 'grade': 0.8},
                            1295251423: {'type': 'restaurant', 'grade': 0.7},
        },
    },
    "beer_sheva": {
        "num_agents": 6,
        "location": "Old City, Beersheba, Israel",
        "central_stations": [3684782944, 3761306917, 3715859182, 306543884, 3761279370, 306543861],
        "interest_points": {
                            305928367: {'type': 'mall', 'grade': 1},
                            286303784: {'type': 'school', 'grade': 0.6},
                            281397946: {'type': 'park', 'grade': 0.8},
                            309076045: {'type': 'restaurant', 'grade': 0.7},
                            281391220: {'type': 'hospital', 'grade': 0.9},
                            3758979801: {'type': 'cafe', 'grade': 0.5},
                            286303775: {'type': 'mall', 'grade': 1},
                            306583303: {'type': 'school', 'grade': 0.6},
                            281391326: {'type': 'park', 'grade': 0.8}
        },
    }
}
