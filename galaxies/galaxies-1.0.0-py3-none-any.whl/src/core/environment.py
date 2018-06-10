# -*- coding: utf-8 -*-
""" Contient les différents arguments passés en entrée et utilisés par les
modules `main.py` et `galaxie_creation.py`.
Une valeur assignée directement dans ce code correspond à une valeur par défaut.
"""

import os.path


######################
## Needed arguments ##
######################
# Path of the source database, containing all reuses.
# The database must be in the TSV, TAB or CSV format.
path_database_source = None


#########################
## Optional parameters ##
#########################
# Max book to read from the source file and to add in the database.
# Set to -1 for all books available
max_book_to_add = -1

# Filenames created by the software
file_name_galaxies = "galaxies.db"
file_name_list_galaxies = "list_galaxies"  # Shelve object
file_name_adjacency_graph = "ajacency_graph"  # Shelve object
file_name_adjacency_graph_transposed = "ajacency_graph_transposed"  # Shelve object
file_name_graphe_galaxie = "graphe_galaxie_{}.gml"
file_name_graphe_galaxie_amas = "graphe_galaxie_{}_amas_{}.gml"

# Path for directories and files
path_dir_dest = "results"  # Directory containing all created files
path_dir_galaxies = os.path.join(path_dir_dest, "galaxies")  # Directory containing all galaxies
path_dir_amas = os.path.join(path_dir_dest, "amas")  # Directory containing all amas
path_file_galaxies = os.path.join(path_dir_dest, file_name_galaxies)
path_file_list_galaxies = os.path.join(path_dir_dest, file_name_list_galaxies)
path_file_adjacency_graph = os.path.join(path_dir_dest, file_name_adjacency_graph)
path_file_adjacency_graph_transposed = os.path.join(path_dir_dest, file_name_adjacency_graph_transposed)
path_file_graphe_galaxie = os.path.join(path_dir_galaxies, file_name_graphe_galaxie)
path_file_graphe_galaxie_amas = os.path.join(path_dir_amas, file_name_graphe_galaxie_amas)

# Delimiter used to pass the reuses' file
delimiter = "\t"

# Encoding of the reuses' file
encoding_src = "utf8"

# Remove the header present in the reuses' file
remove_header = True

# Indexes of the data which is gonna ba extracted from the reuses' file
index_src_author = 2
index_src_title = 2
index_src_date = 12
index_src_text_matched = 6
index_src_start_byte = 3
index_src_end_byte = 4

index_dest_author = 15
index_dest_title = 16
index_dest_date = 12
index_dest_text_matched = 20
index_dest_start_byte = 17
index_dest_end_byte = 18

# Format du graphe créé lors de l'extraction des galaxies
format_graph = "gml"

# Affiche le temps de construction tous les `step_nodes_time` noeuds effectués
step_nodes_time = 10000
step_galaxies_time = 10000
step_number_of_nodes_galaxie = 10000


if __name__ == '__main__':
    pass
