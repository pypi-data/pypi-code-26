import json

better_drops = {}
with open('pokedrops.json') as f:
	Drops = json.load(f)

for drop in Drops:
	new_drop = {}
	main_drop = [drop['maindropdata'], drop.get('maindropmin', 0), drop.get('maindropmax', 1)]
	optional_drops = []
	for x in range(5):
		if "optdrop{}data".format(x) in drop.keys():
			optional_drops += [ [drop["optdrop{}data".format(x)], drop.get("optdrop{}min".format(x), 0), drop.get("optdrop{}max".format(x), 1)] ]
	if 'raredropdata' in drop.keys():
		rare_drop = [drop['raredropdata'], drop.get('raredropmin', 0), drop.get('raredropmax', 1)]
	else:
		rare_drop = [None, 0, 0]
	better_drops[drop['pokemon'].lower()] = {
		'pokemon' : drop['pokemon'].lower(),
		"main_drop" : main_drop,
		'optional_drops' : optional_drops,
		"rare_drop" : rare_drop
	}

with open("better_drops.json", 'w') as f:
	json.dump(better_drops, f, indent = 4)

def search_for_drop(drop):
	dropping_pokemon = {
	"main" : [],
	"optional" : [],
	'rare' : []
	}
	for pokemon in better_drops.keys():
		main = better_drops[pokemon]['main_drop']
		# print(main[0])
		if main[0] == drop:
			dropping_pokemon['main'] = dropping_pokemon['main'] + [[pokemon, main[1], main[2]]]
		optional = better_drops[pokemon]['optional_drops']
		for option in optional:
			if option[0] == drop:
				dropping_pokemon['optional'] = dropping_pokemon['optional'] + [[pokemon, option[1], option[2]]]

		rare = better_drops[pokemon]['rare_drop']
		if rare[0] == drop:
			dropping_pokemon['rare'] = dropping_pokemon['rare'] + [[pokemon, rare[1], rare[2]]]
	return {drop : dropping_pokemon}

# print(search_for_drop('minecraft:dragon_breath'))
