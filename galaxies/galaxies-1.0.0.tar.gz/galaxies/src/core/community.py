import networkx as nx
import community
import matplotlib.pyplot as plt


# Recuperation du graphe de Zachary du Karate-Club
G = nx.karate_club_graph()

# l'algorithme de Louvain cherche les communautÃ©s
part = community.best_partition(G)
values = [part.get(node) for node in G.nodes()]
# networkx propose une visualisation (reposant sur une disposition "spring")
# des noeuds, avec des couleurs correspondants aux groupes obtenus
nx.draw_spring(G, cmap=plt.get_cmap('jet'), node_color=values,
               node_size=120, with_labels=True)
plt.show()

# valeur de la modularité
mod = community.modularity(part, G)
print("modularity: %0.5f" % mod)


if __name__ == '__main__':
    pass
