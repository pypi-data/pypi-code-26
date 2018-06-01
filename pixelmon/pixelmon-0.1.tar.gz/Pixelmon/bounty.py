import json


BtoP = {}

Pokemon_set = {}

with open("Biomes_to_Pokemon.json") as f:
	BtoP = json.load(f)

for Biome_name, Biome_set in BtoP.items():
	for Time_name, Time_set in Biome_set.items():
		for Location_name, Pokemon_spawns in Time_set.items():
			if Location_name not in ['Land', 'Water', 'Air']:
				pass
				#continue
			Pokemon_spawns = Pokemon_spawns[1:]
			for Pokemon, Spawn_Rate in Pokemon_spawns:
				Pokemon_set[Pokemon] = Pokemon_set.get(Pokemon, 0) + int(Spawn_Rate*100)

print(Pokemon_set)

items_set = sorted(Pokemon_set.items(), reverse = True, key = lambda x: x[1])
print(items_set)

total_per = 65
skip_start = 0

print(len(items_set))
Easy = items_set[skip_start:total_per+skip_start]
Medium = items_set[skip_start+total_per:skip_start+total_per+total_per]
Hard = items_set[skip_start+total_per+total_per:skip_start+total_per+total_per+total_per]

print("Easy")
print(", ".join([x for x, y in Easy]))
print("Medium")
print(", ".join([x for x, y in Medium]))
print("Hard")
print(", ".join([x for x, y in Hard]))