import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from game import Game
from graph import Graph # fix import error
import graphics.colors as colors

def reset_graph(graph: Graph):
    Game.window.fill(colors.BACKGROUND)
    graph.graph_init()
    graph.n = 1


def reset_graphs(graphs: list[Graph]):
    graphs[0].refresh()
    for graph in graphs:
        graph.n = 1