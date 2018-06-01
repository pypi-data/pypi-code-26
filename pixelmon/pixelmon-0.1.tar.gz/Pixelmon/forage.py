import json

forage = {}
TtoD = {}

with open('forage.json') as f:
	forage = json.load(f)

# print(forage[0])

for entry in forage:
	if entry['item'] == 'minecraft:air':
		continue
	try:
		for _type in entry.get('types', ["ALL"]):
			for block in entry.get('blocks', [entry.get('material')]):
				# print(block)
				TtoD[_type] = TtoD.get(_type, {})
				TtoD[_type][block] = TtoD[_type].get(block, []) + [(entry['item'], entry['itemWeight'])]
				# print(TtoD.get('A'))
				# print(TtoD[_type][block])
	except:
		print(entry)
		break

with open("Type_to_Drop.json", 'w') as f:
	json.dump(TtoD, f, indent = 4)

def probabilities(type):
	ret = {}
	for block in TtoD[_type].keys():
		probs = {}
		items = TtoD[_type][block]
		total = sum([weight for name, weight in items]) + 300
		berry_count = 0
		for name, weight in items:
			prob = weight/total * 100
			if "_berry" in name:
				name = "Pixelmon:random_berry"
				berry_count += 1
				prob = prob * berry_count

			probs[name.split(":")[1]] =  round(prob, 1)
		probs["air"] = round(300/total * 100, 1)
		ret[block] = probs
	return ret

print("Please input a Type")

while 1:
	_type = input(">")
	if _type.lower() == 'exit':
		break
	elif _type in TtoD.keys():
		print(_type, probabilities(_type))