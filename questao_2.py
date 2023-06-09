import numpy as np
from numpy import random
import networkx as nx
import matplotlib.pyplot as plt

from collections import deque
from queue import PriorityQueue
from results2 import Results

""" CONSTANTES: """

# SHOW_GRAPH = True
SHOW_GRAPH = False


def calcula_custo_caminho(G, caminho):
    """Calcula custo total de um caminho"""

    custo = 0.0
    for i in range(len(caminho) - 1):
        u, v = caminho[i], caminho[i + 1]
        custo += G[u][v]["weight"]
    return custo


# calcula custo do caminho da cidade origem até a cidade atual
def calcula_custo_g(G, caminho_origem_atual):
    """Cálculo custo do nó origem até o nó atual: custo g(n)"""
    return calcula_custo_caminho(G, caminho_origem_atual)


# No futuro, a funcao abaixo será substituída apropriadamente
# para os cálculos das estimativas euclidianas
def estima_custo_h(cidade_atual, Estimation):
    """Estimativa do custo do nó atual para o destino: custo h(n)"""
    # destino == 'Bucharest':
    return Estimation[cidade_atual]


def obtem_caminho(G, s, t):
    L = [t]
    u = t
    while u != s:
        u = G.nodes[u]["pre"]
        L.append(u)

    L.reverse()

    return L


def plot_grafo(G, u, my_pos, fig):
    if isinstance(u, tuple):
        u = u[0]

    print(
        f"no atual: {u}, {{\n\t"
        f"dis: {G.nodes[u]['dis']}, "
        f"cor: {G.nodes[u]['cor']}, "
        f"f_n: {G.nodes[u]['f']}, "
        f"pre: {G.nodes[u]['pre']}"
        f"}}"
    )
    color_map = []
    for x in G.nodes():
        color_map.append(G.nodes[x]["cor"])
    nx.draw(
        G,
        pos=my_pos,
        node_color=color_map,
        with_labels=True,
        edge_color="white",
        font_color="red",
        node_size=500,
    )
    labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(G, my_pos, edge_labels=labels, font_size=10)
    fig.set_facecolor("#4b70ab")
    plt.waitforbuttonpress()
    # plt.show()


"""## Algoritmo BFS (Busca em Largura)"""


# Implementação do algoritmo BFS
def BFS(G_inicial, source, goal, Estimation):
    # Faz uma copia do grafo
    G = G_inicial.copy()

    # Contador de nós expandidos
    numExpandidos = 0

    # Inicia todos os nós com cor branca e distância infinita
    for v in G.nodes() - {source}:
        G.nodes[v]["cor"] = "white"
        G.nodes[v]["dis"] = np.inf
        G.nodes[v]["f"] = 0
        G.nodes[v]["pre"] = ""

    # Inicia o nó origem com cor cinza e distância zero
    G.nodes[source]["cor"] = "grey"
    G.nodes[source]["dis"] = 0
    G.nodes[source]["f"] = 0
    G.nodes[source]["pre"] = ""

    # Implementação de Fila FIFO (append (right), popleft)
    Q = deque()
    Q.append(source)

    # configuração para printar o grafo no mesmo formato sempre
    my_pos = nx.spring_layout(G, seed=3113794652)
    fig = plt.figure("BFS", figsize=(8, 8))

    while len(Q) != 0:
        u = Q.popleft()

        G.nodes[u]["cor"] = "blue"

        # Define os vizinhos para cinza
        for v in G.neighbors(u):
            if G.nodes[v]["cor"] == "white":
                G.nodes[v]["cor"] = "grey"

                G.nodes[v]["dis"] = G.nodes[u]["dis"] + 1
                G.nodes[v]["pre"] = u

                Q.append(v)

        numExpandidos += 1

        if SHOW_GRAPH:
            plot_grafo(G, u, my_pos, fig)

        # marca o nó vizitado para cor preta
        G.nodes[u]["cor"] = "black"

    # Grafo G retornado contem as informações de distância
    # e cores desde o nó origem a todos os demais nós
    caminho = obtem_caminho(G, source, goal)
    custo_total = calcula_custo_caminho(G, caminho)
    return G, caminho, custo_total, numExpandidos


# ----------------------------------------------------------------


"""## Algoritmo UCS (Custo Uniforme)"""


# Implementação do algoritmo UCS
# f(n) = g(n)
def UCS(G_inicial, source, goal, Estimation):
    # Faz uma copia do grafo
    G = G_inicial.copy()

    # Contador de nós expandidos
    numExpandidos = 1

    # Inicia todos os nós com cor branca, distância infinita e custo zero
    for v in G.nodes() - {source}:
        G.nodes[v]["cor"] = "white"
        G.nodes[v]["dis"] = np.inf
        G.nodes[v]["f"] = 0
        G.nodes[v]["pre"] = ""

    # Inicia o nó origem com cor cinza, distância infinita e custo zero
    G.nodes[source]["cor"] = "grey"
    G.nodes[source]["dis"] = 0
    G.nodes[source]["f"] = 0
    G.nodes[source]["pre"] = ""

    # Implementação de Fila ordenada
    Q = PriorityQueue()
    Q.put((G.nodes[source]["f"], source))

    # configuração para printar o grafo no mesmo formato sempre
    my_pos = nx.spring_layout(G, seed=3113794652)
    fig = plt.figure("UCS", figsize=(8, 8))

    while len(Q.queue) != 0:
        # seleciona o no de menor custo para ser expandido
        u = Q.get()[1]

        G.nodes[u]["cor"] = "blue"

        # testa objetivo
        if u == goal:
            G.nodes[goal]["cor"] = "black"
            G.nodes[goal]["dis"] = G.nodes[u]["dis"] + 1
            caminho = obtem_caminho(G, source, goal)
            G.nodes[v]["f"] = calcula_custo_g(G, caminho)

            if SHOW_GRAPH:
                plot_grafo(G, u, my_pos, fig)
            break

        numExpandidos += 1

        # calcula funcao custo f(u) = g(u)
        f_u = calcula_custo_g(G, obtem_caminho(G, source, u))

        for v in G.neighbors(u):
            # verifica se v não foi visitado e não está na fronteira
            if G.nodes[v]["cor"] == "white":
                G.nodes[v]["dis"] = G.nodes[u]["dis"] + 1
                # define no atual como anterior ao no v
                G.nodes[v]["pre"] = u

                # calcula função custo f(v)
                G.nodes[v]["f"] = f_u + G[u][v]["weight"]

                # adiciona no à fronteira
                G.nodes[v]["cor"] = "grey"
                Q.put((G.nodes[v]["f"], v))

            # verifica se o nó está na fronteira
            elif G.nodes[v]["cor"] == "grey":
                # calcula função custo f(v)
                f_v = f_u + G[u][v]["weight"]

                # atualiza o no na fronteira se o novo custo for menor
                if G.nodes[v]["f"] > f_v:
                    G.nodes[v]["f"] = f_v
                    G.nodes[v]["pre"] = u
                    G.nodes[v]["dis"] = G.nodes[u]["dis"] + 1

        if SHOW_GRAPH:
            plot_grafo(G, u, my_pos, fig)

        # marca o nó vizitado para cor preta
        G.nodes[u]["cor"] = "black"

        # if SHOW_GRAPH:
        #     plot_grafo(G, u, my_pos, fig)

    # Grafo G retornado contem as informações de distância
    # e cores desde o nó origem a todos os demais nós
    caminho = obtem_caminho(G, source, goal)
    custo_total = calcula_custo_caminho(G, caminho)
    return G, caminho, custo_total, numExpandidos


"""## Algoritmo A-star"""


# Implementação do algoritmo A-star
# f(n) = g(n) + h(n)
def AStar(G_inicial, source, goal, Estimation):
    # Faz uma copia do grafo
    G = G_inicial.copy()

    # Contador de nós expandidos
    numExpandidos = 1

    # Inicia todos os nós com cor branca, distância infinita e custo zero
    for v in G.nodes() - {source}:
        G.nodes[v]["cor"] = "white"
        G.nodes[v]["dis"] = np.inf
        G.nodes[v]["f"] = 0
        G.nodes[v]["pre"] = ""

    # Inicia o nó origem com cor cinza, distância infinita e custo zero
    G.nodes[source]["cor"] = "grey"
    G.nodes[source]["dis"] = 0
    G.nodes[source]["f"] = 0
    G.nodes[source]["pre"] = ""

    # Implementação de Fila ordenada
    Q = PriorityQueue()
    Q.put((G.nodes[source]["f"], source))

    # configuração para printar o grafo no mesmo formato sempre
    my_pos = nx.spring_layout(G, seed=3113794652)
    fig = plt.figure("A-Star", figsize=(8, 8))

    while len(Q.queue) != 0:
        # seleciona o no de menor custo para ser expandido
        u = Q.get()[1]

        G.nodes[u]["cor"] = "blue"

        # testa objetivo
        if u == goal:
            G.nodes[goal]["cor"] = "black"
            G.nodes[goal]["dis"] = G.nodes[u]["dis"] + 1
            caminho = obtem_caminho(G, source, goal)
            G.nodes[v]["f"] = calcula_custo_g(G, caminho)

            if SHOW_GRAPH:
                plot_grafo(G, u, my_pos, fig)
            break

        numExpandidos += 1

        # calcula funcao custo f(u) = g(u) + h(u)
        f_u = calcula_custo_g(G, obtem_caminho(G, source, u)) + estima_custo_h(
            u, Estimation
        )

        for v in G.neighbors(u):
            # verifica se v não foi visitado e não está na fronteira
            if G.nodes[v]["cor"] == "white":
                G.nodes[v]["dis"] = G.nodes[u]["dis"] + 1
                # define no atual como anterior ao no v
                G.nodes[v]["pre"] = u

                # calcula função custo f(v)
                G.nodes[v]["f"] = (
                    f_u + G[u][v]["weight"] + estima_custo_h(v, Estimation)
                )

                # adiciona no à fronteira
                G.nodes[v]["cor"] = "grey"
                Q.put((G.nodes[v]["f"], v))

            # verifica se o nó está na fronteira
            elif G.nodes[v]["cor"] == "grey":
                # calcula função custo f(v)
                f_v = f_u + G[u][v]["weight"] + estima_custo_h(v, Estimation)

                # atualiza o no na fronteira se o novo custo for menor
                if G.nodes[v]["f"] > f_v:
                    G.nodes[v]["f"] = f_v
                    G.nodes[v]["pre"] = u
                    G.nodes[v]["dis"] = G.nodes[u]["dis"] + 1

        if SHOW_GRAPH:
            plot_grafo(G, u, my_pos, fig)

        # marca o nó vizitado para cor preta
        G.nodes[u]["cor"] = "black"

        # if SHOW_GRAPH:
        #     plot_grafo(G, u, my_pos, fig)

    # Grafo G retornado contem as informações de distância
    # e cores desde o nó origem a todos os demais nós
    caminho = obtem_caminho(G, source, goal)
    custo_total = calcula_custo_caminho(G, caminho)
    return G, caminho, custo_total, numExpandidos


def main():
    print("Starting")

    G_inicial = nx.Graph()

    # inicializando manualmente as cidades (vérticies) e
    # os respectivos custos g(n) entre elas (arestas).
    G_inicial.add_weighted_edges_from(
        [
            ("Arad", "Sibiu", 140),
            ("Arad", "Timisoara", 118),
            ("Arad", "Zerind", 75),
            ("Bucharest", "Fagaras", 211),
            ("Bucharest", "Giurgiu", 90),
            ("Bucharest", "Pitesti", 101),
            ("Bucharest", "Urziceni", 85),
            ("Craiova", "Dobreta", 120),
            ("Craiova", "Pitesti", 138),
            ("Craiova", "Rimnicu_Vilcea", 146),
            ("Dobreta", "Mehadia", 75),
            ("Eforie", "Hirsova", 86),
            ("Fagaras", "Sibiu", 99),
            ("Hirsova", "Urziceni", 98),
            ("Iasi", "Neamt", 87),
            ("Iasi", "Vaslui", 92),
            ("Lugoj", "Mehadia", 70),
            ("Lugoj", "Timisoara", 111),
            ("Oradea", "Zerind", 71),
            ("Oradea", "Sibiu", 151),
            ("Pitesti", "Rimnicu_Vilcea", 97),
            ("Rimnicu_Vilcea", "Sibiu", 80),
            ("Urziceni", "Vaslui", 142),
        ]
    )

    # if SHOW_GRAPH:
    #     # Plotando para conferir
    # my_pos = nx.spring_layout(G_inicial, seed=3113794652)
    # fig = plt.figure(figsize=(8, 8))
    # nx.draw(
    #     G_inicial,
    #     pos=my_pos,
    #     with_labels=True,
    #     node_size=500,
    # )
    # # plt.show()
    # labels = nx.get_edge_attributes(G_inicial, "weight")
    # nx.draw_networkx_edge_labels(G_inicial, my_pos, edge_labels=labels, font_size=10)
    # plt.waitforbuttonpress()

    # Estimativa das distâncias de todas as cidades com destino
    # para Bucharest, heurísticas h(n)
    Estimation = {
        "Arad": 366,
        "Bucharest": 0,
        "Craiova": 160,
        "Dobreta": 242,
        "Eforie": 161,
        "Fagaras": 178,
        "Giurgiu": 77,
        "Hirsova": 151,
        "Iasi": 226,
        "Lugoj": 244,
        "Mehadia": 241,
        "Neamt": 234,
        "Oradea": 380,
        "Pitesti": 98,
        "Rimnicu_Vilcea": 193,
        "Sibiu": 253,
        "Timisoara": 329,
        "Urziceni": 80,
        "Vaslui": 199,
        "Zerind": 374,
    }
    # Definições de origem e destino
    origem = "Arad"
    # destino = "Bucharest"
    destino = "Craiova"

    result_BFS = Results("BFS", BFS, G_inicial, origem, destino)
    result_UCS = Results("UCS", UCS, G_inicial, origem, destino)
    result_AStar = Results("A-Star", AStar, G_inicial, origem, destino, Estimation)

    """
    # ----------------------------------------
    # BFS
    # ----------------------------------------
    """
    result_BFS.run()
    result_BFS.printResults()
    """
    # ----------------------------------------
    # UCS
    # ----------------------------------------
    """
    result_UCS.run()
    result_UCS.printResults()
    """
    # ----------------------------------------
    # A-star
    # ----------------------------------------
    """
    result_AStar.run()
    result_AStar.printResults()
    if SHOW_GRAPH:
        print("OK! Pressione Enter pra finalizar...")
        input()


if __name__ == "__main__":
    main()
