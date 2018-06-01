import json
import os
files = ["spawning/" + x for x in os.listdir("spawning")]

BtoP = {}
PtoB = {}

TIMES = ["DAY", "DAWN", 'DUSK', 'NIGHT']
WEATHERS = ['STORM', 'CLEAR', 'RAIN']
LOCATIONS = ['Land', 'Headbutt', 'Air', 'Underground', 'Water']
# LEGENDS = ["Arceus","Entei","Kyogre","Mew","Articuno","Genesect","Landorus","Mewtwo","Azelf","Giratina","Latias","Moltres","Celebi","Groudon","Latios","Palkia","Cresselia","Heatran","Lugia","Raikou","Darkrai","Ho-Oh","Manaphy","Rayquaza","Deoxys","Jirachi","Meloetta","Regice","Dialga","Keldeo","Mespirit","Regirock","Shaymin","Tornadus","Zapdos","Registeel","Suicune","Uxie","Zekrom","Reshiram","Terrakion","Victini","Kyurem","Thunderus","Virizion"]

Biome_Dict = {
	"ice flats" : "ice plains",
	"smaller extreme hills" : "extreme hills edge",
	"taiga cold" : "cold taiga",
	"taiga cold hils" : "cold taiga hills",
	"redwood taiga" : "mega taiga",
	"redwood taiga hills" : "mega taiga hills",
	"extreme hills with trees" : "extreme hills +",
	"savanna rock" : "savana plateau",
	"mesa rock" : "mesa plateau F",
	"mesa clear rock" : "mesa plateau",
	"mutated plains" : "sunflower plains",
	"mutated forest" : "flower forest",
	"mutated ice flats" : "ice plains spikes",
	"mutated taiga cold" : "cold taiga M",
	"mutated redwood taiga" : "mega spruce taiga",
	"mutated extreme hills with trees" : "extreme hills M+",
	"mutated savanna rock" : "savanna plateau M",
	"mutated mesa" : "mesa bryce",
	"mutated mesa rock" : "mesa plateau F M",
	"mutated mesa clear rock" : "mesa plateau M"
}


class SpawnInfo:
	def __init__(spawninfo):
		self.raw_info = spawninfo

		Times = spawnInfo['condition'].get('times', TIMES)
		Locations = spawnInfo['condition']['stringLocationTypes']
		Weather = spawnInfo['condition'].get('weathers')
		Rarity = spawnInfo['rarity']



class PokemonSpawn:
	def __init__(self,id, SpawnInfos):
		self.name = id
		self.Spawns = []
		for spawninfo in SpawnInfos:
			self.add_spawn(spawninfo)

	def add_spawn(self,spawninfo):
		self.Spawns.append(SpawnInfo(spawninfo))

	def __str__(self):
		return "\n".join([str(spawn) for spawn in self.Spawns])

def BiomeCleaner(Biome):
	Biome = Biome.replace("_", " ")

	Biome = Biome_Dict.get(Biome, Biome)

	if Biome.split(" ")[0] == 'mutated':
		Biome = " ".join(Biome.split(" ")[1:]) + " M"

	return Biome.capitalize()

Legend_Spawns = {}
# print(JSON)
for file in files:
	try:
		J = json.load(open(file))
	except Exception as e:
		print(e)
		print(open(file).read())
		break
	# print(J['id'])
	Name = J['id']
	# The Amount of different ways it can spawn
	count = 0
	for spawnInfo in J['spawnInfos']:
		count+=1
		# The Biomes the Pokemon can spawn in
		Biomes = spawnInfo['condition'].get('stringBiomes', list(BtoP.keys()))

		# Biomes = [BiomeCleaner(Biome) for Biome in Biomes]

		# The Times that certain pokemon spawn  (like Day or stuff)
		Times = spawnInfo['condition'].get('times', TIMES)
		Locations = spawnInfo['condition']['stringLocationTypes']
		Weather = spawnInfo['condition'].get('weathers')
		Rarity = spawnInfo['rarity']
		legend_toggle = spawnInfo.get('interval')

		if 'ANY' in Times:
			Times = TIMES
		if legend_toggle:
			# print(Name)
			for Biome in Biomes:
				Legend_Spawns[Biome] = Legend_Spawns.get(Biome, []) + [" {}\n  {}\n  {}\n  {}".format(Name, ", ".join(Times), ", ".join(Locations), ", ".join(Weather))]
			print(Name, Biomes)

		# print(J['spawnInfos'][0].keys())
		# print(rarity)
		# print("{}: {}, {}".format(Name, Biomes, Rarity))
		for Biome in Biomes:
			for Time in Times:
				for Location in Locations:
					BtoP[Biome] = BtoP.get(Biome, {})
					BtoP[Biome][Time] = BtoP[Biome].get(Time, {})
					BtoP[Biome][Time][Location] = BtoP[Biome][Time].get(Location, []) + [(Name, Rarity)]
					if Location not in LOCATIONS:
						pass 
						#print(Name, Location)

		PtoB["{}{}".format(Name, count)] = Biomes

	# print("{} {} {}".format(J['id'], J['spawnInfos']['stringBiomes'], J['rarity']))

for Biome in Legend_Spawns.keys():
	print("{}:\n{}\n".format(Biome, "\n".join(Legend_Spawns[Biome])))
# print(Legend_Spawns)

for Biome in BtoP.keys():
	for Time in BtoP[Biome].keys():
		for Location in BtoP[Biome][Time].keys():
			cur = BtoP[Biome][Time][Location]
			# print(cur, Biome, Time, Location)
			total = sum([x[1] for x in cur])
			for x in range(len(cur)):
				cur[x] = [cur[x][0], round(cur[x][1]/total * 100, 3)]
			BtoP[Biome][Time][Location] = sorted(cur, key = lambda x: x[1], reverse = True)


with open("Biomes_to_Pokemon.json", 'w') as f:
	json.dump(BtoP, f)
with open("Pokemon_to_Biomes.json", 'w') as f:
	json.dump(PtoB, f)

def find_spawn_rate(pokemon, Spawns):
	#print(Spawns)
	ret = []
	# print(Times, Locations)
	for Time in TIMES:
		for Location in LOCATIONS:
			#print(Spawns[Time][Location])
			for entry in Spawns.get(Time, {}).get(Location, []):
				#print(entry)
				if pokemon == entry[0]:
					ret += [Time, Location, entry[1]]
	return ret

# print(BtoP)
print("Biomes: {}".format(list(BtoP.keys())))

print("Please input either a pokemon Name or Biome Name")
while 1:
	In = input(">")
	if In.lower() == 'exit':
		break
	if In in BtoP.keys():
		for time in BtoP[In]:
			if time == 'DUSK':
				continue
			if time == "DAWN":
				print("***DAWN/DUSK***")
			else:
				print("***{}***".format(time))
			for Location in BtoP[In][time].keys():
				pokes = BtoP[In][time][Location]
				nice_print = ["{0} *{1}%*".format(poke[0], poke[1]) for poke in pokes]
				print("**{}**\n{}".format(Location, ", ".join(nice_print)))
			print("\n")
		# print(BtoP[In])
	elif In in PtoB.keys():
		for biome in PtoB[In]:
			print(biome, "\n", find_spawn_rate(In, BtoP[biome]))
		# print(PtoB[In])
