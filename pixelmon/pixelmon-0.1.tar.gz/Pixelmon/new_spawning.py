import json
import glob
import os

class SpawnInfo:
	def __init__(self, spawninfo):
		self.raw_info = spawninfo

		self.name = self.raw_info['spec']['name']

		if "level" in self.raw_info['spec'].keys():
			self.level = self.raw_info['spec']['level']
		else:
			self.level = (self.raw_info['minLevel'], self.raw_info['maxLevel'])

		self.form = self.raw_info['spec'].get('form')
		# self.level = self.raw_info[]

		self.times = self.raw_info.get('condition', {}).get('times', ["ALL"]) # , {"times" : "ALL"}

		if "DAWN" in self.times and "DUSK" in self.times:
			self.times.remove("DAWN")
			self.times.remove("DUSK")
			self.times.append("DAWN/DUSK")

		self.max_light =  self.raw_info.get('condition', {}).get('maxLightLevel')

		self.locations = self.raw_info.get('stringLocationTypes')
		if self.locations == None:
			self.bad_location = True
			self.locations = self.raw_info['condition', {}].get('stringLocationTypes')

		self.weather = self.raw_info.get('condition', {}).get('weathers') # , {"weathers" : "ALL"}

		self.rarity = self.raw_info['rarity']

		self.spawn_block = self.raw_info.get('condition', {}).get('baseBlocks')

		self.near_blocks = self.raw_info.get('condition', {}).get('neededNearbyBlocks')

		self.moon_phase = self.raw_info.get('condition', {}).get('moonPhase')

		self.biomes = self.raw_info.get('condition', {}).get('stringBiomes', ["ALL"]) # , {"stringBiomes" : "ALL"}

		self.legendary = self.raw_info.get('interval') == "legendary"

	def clean_biome(self, biome, group = True):
		global biome_mapper
		# If biome group
		if biome in biome_mapper.keys() and group:
			# print("Group")
			return [self.clean_biome(x.replace("minecraft:", "").replace("Minecraft:", ""), group = False) for x in biome_mapper[biome]]
		else:
			biome = biome.replace("_", " ").replace("minecraft:", "")

			biome = Biome_Dict.get(biome.lower(), biome)

			if biome.split(" ")[0] == 'mutated':
				biome = " ".join(biome.split(" ")[1:]) + " M"

			return biome.replace("minecraft:", "").capitalize()

	def contains(self, biome, location, time):
		biome_check, location_check, time_check = False, False, False
		# print(biome, self.out_biomes)

		if biome == None:
			biome_check = True

		elif self.biomes == ['ALL']:
			# print("ALL")
			biome_check = True

		elif biome in self.out_biomes:
			biome_check = True



		if location in self.locations:
			location_check = True

		elif location == None:
			location_check = True



		if self.times == ['ALL']:
			time_check = True

		elif time == None:
			time_check = True

		elif time in self.times:
			time_check = True

		elif time == "MIDNIGHT" and "NIGHT" in self.times:
			time_check = True

		return biome_check and location_check and time_check

	# max_light, weather, spawn_block, near_blocks, moon_phase
	@property
	def side_conditions(self):
		return {
			"max_light" : self.max_light,
			"weather": self.weather,
			"spawn_block" : self.spawn_block,
			"near_blocks" : self.near_blocks,
			"moon_phase" : self.moon_phase
		}

	@property
	def out_biomes(self):
		if self.biomes == ["ALL"]:
			return ["All"]
		biomes = []
		for biome in self.biomes:
			out = self.clean_biome(biome)
			if type(out) == list:
				biomes += out
			else:
				biomes.append(out)
		return biomes

	def __str__(self):
		return str(self.out())

	def out(self):
		out = self.__dict__
		del out['raw_info']
		out['biomes'] = self.out_biomes
		return out
		return {
			"name" : self.name,
			"form" : self.form,
			"biomes" : self.out_biomes,
			"weather" : self.weather,
			"times" : self.times,
			"rarity" : self.rarity,
			"locations" : self.locations,
			"other_conditions" : {
			"max_light" : self.max_light
			}
		}

class PokemonSpawn:
	def __init__(self,id, SpawnInfos):
		self.name = id
		self.Spawns = []
		for spawninfo in SpawnInfos:
			self.add_spawn(spawninfo)

	def add_spawn(self,spawninfo):
		self.Spawns.append(SpawnInfo(spawninfo))

	def out(self):
		return [spawn.out() for spawn in self.Spawns]

	def contains(self, biome = None, location = None, time = None):
		for spawn in self.Spawns:
			found = spawn.contains(biome, location, time)
			if found:
				#print(spawn.out())
				# print("{} Nope".format(self.name))
				return spawn
		return None

	def rarity_for(self, biome = None, location = None, time = None):
		spawn = self.contains(biome, location, time)
		#print(biome, location, time)
		if spawn == None:
			#print("bad")
			return 0
		return spawn.rarity

	@property
	def biomes(self):
		b = []
		for spawn in self.Spawns:
			o_biomes = spawn.out_biomes
			# print(o_biomes)
			if o_biomes == ['All']:
				return ALL_BIOMES
			# print(o_biomes)
			b += o_biomes
		return b

	@property
	def locations(self):
		l = []
		for spawn in self.Spawns:
			l += spawn.locations
		return l

	@property
	def times(self):
		t = []
		for spawn in self.Spawns:
			time = spawn.times
			if time == ["ALL"]:
				return ALL_TIMES
			t += time
		return t

	@property
	def spawn_combos(self):
		combos = []
		for biome in self.biomes:
			for location in self.locations:
				for time in self.times:
					rarity = self.rarity_for(biome, location, time)
					if rarity == 0:
						continue
					combos.append(((biome, location, time), rarity))
		return combos


	@property
	def spawn_rates(self):
		combos = self.spawn_combos
		spawnrates = []
		for combo in combos:
			conditions, rarity = combo
			biome, location, time = conditions
			if location == "Headbutt":
				continue
			total_rarity = sum([x.rarity_for(biome, location, time) for x in Database.values()])
			# spawn_obj = self.contains(biome, location, time)



			spawnrates.append((conditions, rarity / total_rarity))
			# print(total_rarity, conditions)
		return spawnrates

	@property
	def extra_conditions(self):
		conditions = []
		for spawn in self.Spawns:
			conditions.append(spawn.side_conditions)
		return conditions

def clean(biome):
	biome = biome.replace("_", " ").replace("minecraft:", "")

	biome = Biome_Dict.get(biome.lower(), biome)

	if biome.split(" ")[0] == 'mutated':
		biome = " ".join(biome.split(" ")[1:]) + " M"

	return biome.replace("minecraft:", "").capitalize()

def set_parts(biome_name):
	_sets = []
	for item in biome_mapper.items():
		# print(item[1])
		biomes = [clean(biome) for biome in item[1]]
		# print(biomes)
		if biome_name in biomes:
			_sets.append(item[0])
	return _sets

def complete(set_info, biomes):
	found_biomes = biome_mapper[set_info[0]]
	found_biomes = [clean(biome) for biome in found_biomes]
	# print(biomes, found_biomes)
	if set(found_biomes) == set(biomes):
		# print("Found")
		return True
	return False

def merge_spawns(spawns):
	ret = []
	_sets = {}
	grouped_biomes = []
	for spawn in spawns:
		# print(spawn[0][0])
		biome, location, time = spawn[0]
		found_sets = set_parts(biome)
		for _set in found_sets:
			_sets[(_set, location, time)] = _sets.get((_set, location, time), []) + [biome]

	print(_sets)
	for _set_name, _set_entries in _sets.items():
		if complete(_set_name, _set_entries):
			# print("Complete")
			ret.append((_set_name))
			for biome in _set_entries:
				grouped_biomes.append(biome)
		else:
			for biome in [x for x in _set_entries if x not in grouped_biomes]:
				group, location, time = _set_name
				ret.append((biome, location, time))

	return ret

this_dir, this_filename = os.path.split(__file__)
files = [os.path.join(this_dir, "spawning", x) for x in glob.glob(os.path.join(this_dir, "spawning/*"))]

Database = {}

Biome_Dict = {
	"ice flats" : "ice plains",
	"smaller extreme hills" : "extreme hills edge",
	"taiga cold" : "cold taiga",
	"taiga cold hills" : "cold taiga hills",
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

with open(os.path.join(this_dir, "biome_config.json")) as f:
	biome_mapper = json.load(f)['biomeCategories']

for file in files:
	try:
		J = json.load(open(file))
	except Exception as e:
		continue
		# print(e)
		# print(open(file).read())
		# break
	# print(J['id'])
	output = PokemonSpawn(J['id'], J['spawnInfos'])
	Database[output.name] = output

# print(Database['Pikachu'].contains(biome = "Forest"))
# print([x.contains(biome = "Taiga hills", time = "DAWN/DUSK").name for x in Database.values() if x.contains(biome = 'Taiga hills', time = "DAWN/DUSK") != None])

#print(Database['Abomasnow'].out())

ALL_BIOMES = set()
ALL_TIMES = set()

for spawn_big in Database.values():
	for spawn in spawn_big.Spawns:
		ALL_BIOMES = ALL_BIOMES.union(set(spawn.out_biomes))
		ALL_TIMES = ALL_TIMES.union(set(spawn.times))
ALL_BIOMES.remove("All")
ALL_TIMES.remove("ALL")

# print(ALL_TIMES)

#print(Database['Zubat'].biomes)
#print(Database['Zubat'].locations)
#print(Database['Celebi'].spawn_combos)
#print()


#Database['Dugtrio'].spawn_rates
# while 1:
# 	in_ = input(">")
#
# 	pokemon = in_.capitalize()
#
# 	print("Top 10 spawns for {}".format(pokemon.capitalize()))
#
# 	print("\n".join(["{}% in {} at {} on {}".format(round(y[1]*100, 2), y[0][0], y[0][2], y[0][1]) for y in sorted(Database[pokemon].spawn_rates, key = lambda x: x[1], reverse = True)[:10]]))
#
# 	print("Spawn Biomes:\n{}".format(Database[pokemon].biomes))
# 	print("Spawn Times:\n{}".format(Database[pokemon].times if len(Database[pokemon].times) != 4 else ['ALL']))
# 	print("Spawn Location:\n{}".format(Database[pokemon].locations))
#
# 	print("Spawn extra conditions:\n{}".format(Database[pokemon].extra_conditions))
