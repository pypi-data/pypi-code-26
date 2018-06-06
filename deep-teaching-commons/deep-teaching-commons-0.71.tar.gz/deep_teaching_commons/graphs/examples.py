import networkx as nx
import pandas as pd


def student_bayes_net():
    I = pd.DataFrame(
        [
            ['high', 0.3],
            ['normal', 0.7]
        ],
        columns=['I', 'p']
    )

    D = pd.DataFrame(
        [
            ['hard', 0.4],
            ['easy', 0.6]
        ],
        columns=['D', 'p']
    )

    S_given_I = pd.DataFrame(
        [
            ['high', 'high', 0.8],
            ['high', 'low', 0.2],
            ['normal', 'high', 0.05],
            ['normal', 'low', 0.95]
        ],
        columns=['I', 'S', 'p']
    )

    G_given_I_D = pd.DataFrame(
        [
            ['high', 'hard', 'good', 0.5],
            ['high', 'hard', 'mediocre', 0.3],
            ['high', 'hard', 'bad', 0.2],
            ['high', 'easy', 'good', 0.9],
            ['high', 'easy', 'mediocre', 0.08],
            ['high', 'easy', 'bad', 0.02],
            ['normal', 'hard', 'good', 0.05],
            ['normal', 'hard', 'mediocre', 0.25],
            ['normal', 'hard', 'bad', 0.7],
            ['normal', 'easy', 'good', 0.3],
            ['normal', 'easy', 'mediocre', 0.4],
            ['normal', 'easy', 'bad', 0.3]
        ],
        columns=['I', 'D', 'G', 'p']
    )

    L_given_G = pd.DataFrame(
        [
            ['good', 'issued', 0.9],
            ['good', 'denied', 0.1],
            ['mediocre', 'issued', 0.6],
            ['mediocre', 'denied', 0.4],
            ['bad', 'issued', 0.01],
            ['bad', 'denied', 0.99]
        ],
        columns=['G', 'L', 'p']
    )

    g = nx.DiGraph()

    g.add_node('I', df=I, pos=(100, 0))
    g.add_node('D', df=D, pos=(0, 0))
    g.add_node('S', df=S_given_I, pos=(150, -70))
    g.add_node('G', df=G_given_I_D, pos=(50, -70))
    g.add_node('L', df=L_given_G, pos=(50, -140))

    g.add_edge('I', 'S')
    g.add_edge('I', 'G')
    g.add_edge('D', 'G')
    g.add_edge('G', 'L')

    return g
