from pathlib import Path

import pandas as pd


full = pd.read_csv("output-full.csv")
simp = pd.read_csv("output-full-simple.csv")

mapping = dict()

for x in p:
	x_name = x.name.replace("._", "")
	x_path = str(x).replace("._", "")

	if x.is_file():
		if x_name in mapping:
			mapping[x_name].append(x_path)
		else:
			mapping[x_name] = [x_path]

print(mapping)