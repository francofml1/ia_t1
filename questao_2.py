import numpy as np
from numpy import random
import networkx as nx
import matplotlib.pyplot as plt

from collections import deque
from queue import PriorityQueue

""" CONSTANTES: """

SHOW_GRAPH = True
# SHOW_GRAPH = False


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
        f"no atual: {u}, "
        f"dis: {G.nodes[u]['dis']}, "
        f"cor: {G.nodes[u]['cor']}, "
        f"f_n: {G.nodes[u]['f']}"
    )
    print(
        f"no atual: {u}, \n"
        f"\tdis: {G.nodes[u]['dis']}, \n"
        f"\tcor: {G.nodes[u]['cor']}, \n"
        f"\tf_n: {G.nodes[u]['f']}\n"
        f"\tpre: {G.nodes[u]['pre']}, \n"
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
def BFS(G_inicial, source):
    # Faz uma copia do grafo
    G = G_inicial.copy()

    color_map = []

    # Inicia todos os nós com cor branca e distância infinita
    for v in G.nodes() - {source}:
        G.nodes[v]["cor"] = "white"
        G.nodes[v]["dis"] = np.inf
        G.nodes[v]["f"] = 0
        G.nodes[v]["pre"] = ''

    # Inicia o nó origem com cor cinza e distância zero
    G.nodes[source]["cor"] = "grey"
    G.nodes[source]["dis"] = 0
    G.nodes[source]["f"] = 0
    G.nodes[source]["pre"] = ''

    # Implementação de Fila FIFO (append (right), popleft)
    Q = deque()
    Q.append(source)

    # configuração para printar o grafo no mesmo formato sempre
    my_pos = nx.spring_layout(G, seed=3113794652)
    fig = plt.figure(figsize=(8, 8))

    while len(Q) != 0:
        u = Q.popleft()

        # Define os vizinhos para cinza
        for v in G.neighbors(u):
            if G.nodes[v]["cor"] == "white":
                G.nodes[v]["cor"] = "grey"

                G.nodes[v]["dis"] = G.nodes[u]["dis"] + 1
                G.nodes[v]["pre"] = u

                Q.append(v)

        # marca o nó vizitado para cor preta
        G.nodes[u]["cor"] = "black"

        if SHOW_GRAPH:
            plot_grafo(G, u, my_pos, fig)

    # Grafo G retornado contem as informações de distância
    # e cores desde o nó origem a todos os demais nós
    return G


# ----------------------------------------------------------------


"""## Algoritmo UCS (Custo Uniforme)"""


# Implementação do algoritmo UCS
# f(n) = g(n)
def UCS(G_inicial, source, goal):
    # Faz uma copia do grafo
    G = G_inicial.copy()

    # Inicia todos os nós com cor branca, distância infinita e custo zero
    for v in G.nodes() - {source}:
        G.nodes[v]["cor"] = "white"
        G.nodes[v]["dis"] = np.inf
        G.nodes[v]["f"] = 0
        G.nodes[v]["pre"] = ''

    # Inicia o nó origem com cor cinza, distância infinita e custo zero
    G.nodes[source]["cor"] = "grey"
    G.nodes[source]["dis"] = 0
    G.nodes[source]["f"] = 0
    G.nodes[source]["pre"] = ''

    # Implementação de Fila ordenada
    Q = PriorityQueue()
    Q.put((G.nodes[source]["f"], source))

    # configuração para printar o grafo no mesmo formato sempre
    my_pos = nx.spring_layout(G, seed=3113794652)
    fig = plt.figure(figsize=(8, 8))

    while len(Q.queue) != 0:
        # seleciona o no de menor custo para ser expandido
        u = Q.get()[1]
        
        G.nodes[u]["cor"] = "#0000FF"

        # testa objetivo
        if u == goal:
            G.nodes[goal]["cor"] = "black"
            G.nodes[goal]["dis"] = G.nodes[u]["dis"] + 1
            caminho = obtem_caminho(G, source, goal)
            G.nodes[v]["f"] = calcula_custo_g(G, caminho)

            if SHOW_GRAPH:
                plot_grafo(G, u, my_pos, fig)
            break


        if SHOW_GRAPH:
            plot_grafo(G, u, my_pos, fig)
            
        # calcula funcao custo f(u) = g(u)
        f_u = calcula_custo_g(G, obtem_caminho(G, source, u))

        # Define os vizinhos para cinza
        for v in G.neighbors(u):
            # verifica se o nó não foi visitado ou já está na fronteira
            if G.nodes[v]["cor"] == "white":
                # adiciona no à fronteira
                G.nodes[v]["cor"] = "grey"

                G.nodes[v]["dis"] = G.nodes[u]["dis"] + 1
                G.nodes[v]["pre"] = u

                # calcula função custo f(v)
                G.nodes[v]["f"] = f_u + G[u][v]["weight"]

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

        # marca o nó vizitado para cor preta
        G.nodes[u]["cor"] = "black"

        # if SHOW_GRAPH:
        #     plot_grafo(G, u, my_pos, fig)

    # Grafo G retornado contem as informações de distância
    # e cores desde o nó origem a todos os demais nós
    return G


"""## Algoritmo A-star"""


# Implementação do algoritmo A-star
# f(n) = g(n) + h(n)
def AStar(G_inicial, source, goal, Estimation):
    # Faz uma copia do grafo
    G = G_inicial.copy()

    # Inicia todos os nós com cor branca, distância infinita e custo zero
    for v in G.nodes() - {source}:
        G.nodes[v]["cor"] = "white"
        G.nodes[v]["dis"] = np.inf
        G.nodes[v]["f"] = 0
        G.nodes[v]["pre"] = ''

    # Inicia o nó origem com cor cinza, distância infinita e custo zero
    G.nodes[source]["cor"] = "grey"
    G.nodes[source]["dis"] = 0
    G.nodes[source]["f"] = 0
    G.nodes[source]["pre"] = ''

    # Implementação de Fila FIFO (append (right), popleft)
    Q = []
    Q.append((source, G.nodes[source]["f"]))

    # configuração para printar o grafo no mesmo formato sempre
    my_pos = nx.spring_layout(G, seed=3113794652)
    fig = plt.figure(figsize=(8, 8))

    while len(Q) != 0:
        # ordena a fronteira pelo custo do caminho
        Q.sort(key=lambda x: x[1], reverse=True)

        # seleciona o no de menor custo para ser expandido
        u = Q.pop()

        # testa objetivo
        if u[0] == goal:
            G.nodes[goal]["cor"] = "black"
            G.nodes[goal]["dis"] = G.nodes[u[0]]["dis"] + 1
            caminho = obtem_caminho(G, source, goal)
            G.nodes[v]["f"] = calcula_custo_g(G, caminho)

            if SHOW_GRAPH:
                plot_grafo(G, u, my_pos, fig)
            break

        f_u = calcula_custo_g(G, obtem_caminho(G, source, u[0])) + estima_custo_h(
            u[0], Estimation
        )

        # Define os vizinhos para cinza
        for v in G.neighbors(u[0]):
            if G.nodes[v]["cor"] == "white":
                G.nodes[v]["cor"] = "grey"

                G.nodes[v]["dis"] = G.nodes[u[0]]["dis"] + 1
                G.nodes[v]["pre"] = u[0]
                caminho = obtem_caminho(G, source, v)
                G.nodes[v]["f"] = calcula_custo_g(G, caminho) + estima_custo_h(
                    v, Estimation
                )

                Q.append((v, G.nodes[v]["f"]))
            elif G.nodes[v]["cor"] == "grey":
                # caminho = obtem_caminho(G, source, v)
                f_v = (
                    calcula_custo_g(G, obtem_caminho(G, source, u[0]))
                    + G[u[0]][v]["weight"]
                    + estima_custo_h(v, Estimation)
                )
                if G.nodes[v]["f"] > f_v:
                    G.nodes[v]["f"] = f_v
                    G.nodes[v]["dis"] = G.nodes[u[0]]["dis"] + 1
                    G.nodes[v]["pre"] = u[0]

        # marca o nó vizitado para cor preta
        G.nodes[u[0]]["cor"] = "black"

        if SHOW_GRAPH:
            plot_grafo(G, u, my_pos, fig)

    # Grafo G retornado contem as informações de distância
    # e cores desde o nó origem a todos os demais nós
    return G


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
    destino = "Bucharest"

    """
    # ----------------------------------------
    # BFS
    # ----------------------------------------
    """
    # G_BFS = BFS(G_inicial, origem)
    # caminho_BFS = obtem_caminho(G_BFS, origem, destino)

    # custo_BFS = calcula_custo_caminho(G_BFS, caminho_BFS)
    # dist_G_BFS = G_BFS.nodes[destino]["dis"]

    # print(
    #     f"BFS:\n"
    #     f"\tCusto: {custo_BFS}\n"
    #     f"\tCaminho: {caminho_BFS}\n"
    #     f"\tDistancia: {dist_G_BFS}"
    # )

    """
    # ----------------------------------------
    # UCS
    # ----------------------------------------
    """
    G_UCS = UCS(G_inicial, origem, destino)
    caminho_UCS = obtem_caminho(G_UCS, origem, destino)

    custo_UCS = calcula_custo_caminho(G_UCS, caminho_UCS)
    dist_G_UCS = G_UCS.nodes[destino]["dis"]

    print(
        f"UCS:\n"
        f"\tCusto: {custo_UCS}\n"
        f"\tCaminho: {caminho_UCS}\n"
        f"\tDistancia: {dist_G_UCS}"
    )

    """
    # ----------------------------------------
    # A-star
    # ----------------------------------------
    """
    G_AStar = AStar(G_inicial, origem, destino, Estimation)
    caminho_AStar = obtem_caminho(G_AStar, origem, destino)

    custo_AStar = calcula_custo_caminho(G_AStar, caminho_AStar)
    dist_G_AStar = G_AStar.nodes[destino]["dis"]

    print(
        f"A-star:\n"
        f"\tCusto: {custo_AStar}\n"
        f"\tCaminho: {caminho_AStar}\n"
        f"\tDistancia: {dist_G_AStar}"
    )

    if SHOW_GRAPH:
        print("OK! Pressione Enter pra finalizar...")
        input()


if __name__ == "__main__":
    main()
