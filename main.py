import random

from collections import deque
from viewer import MazeViewer
from math import inf, sqrt
from results import Results


def gera_labirinto(n_linhas, n_colunas, inicio, goal):
    # cria labirinto vazio
    labirinto = [[0] * n_colunas for _ in range(n_linhas)]

    # adiciona celulas ocupadas em locais aleatorios de
    # forma que 25% do labirinto esteja ocupado
    numero_de_obstaculos = int(0.50 * n_linhas * n_colunas)
    for _ in range(numero_de_obstaculos):
        linha = random.randint(0, n_linhas - 1)
        coluna = random.randint(0, n_colunas - 1)
        labirinto[linha][coluna] = 1

    # remove eventuais obstaculos adicionados na posicao
    # inicial e no goal
    labirinto[inicio.y][inicio.x] = 0
    labirinto[goal.y][goal.x] = 0

    return labirinto


class Celula:
    def __init__(self, y, x, anterior):
        self.y = y
        self.x = x
        self.anterior = anterior
        self.custo = 0

    def __eq__(self, other):
        if not isinstance(other, Celula):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        # necessary for instances to behave sanely in dicts and sets.
        return hash((self.x, self.y))


def distancia(celula_1, celula_2):
    dx = celula_1.x - celula_2.x
    dy = celula_1.y - celula_2.y
    return sqrt(dx**2 + dy**2)


def esta_contido(lista, celula):
    return True if (celula in lista) else False


def get_index(lista, celula):
    if esta_contido(lista, celula):
        for elemento in lista:
            if (elemento.y == celula.y) and (elemento.x == celula.x):
                return lista.index(elemento)
    return -1


def custo_caminho(caminho):
    if len(caminho) == 0:
        return inf

    custo_total = 0
    for i in range(1, len(caminho)):
        custo_total += distancia(caminho[i].anterior, caminho[i])

    return custo_total


def obtem_caminho(goal):
    caminho = []

    celula_atual = goal
    while celula_atual is not None:
        caminho.append(celula_atual)
        celula_atual = celula_atual.anterior

    # o caminho foi gerado do final para o
    # comeco, entao precisamos inverter.
    caminho.reverse()

    return caminho


def celulas_vizinhas_livres(celula_atual, labirinto):
    # generate neighbors of the current state
    vizinhos = [
        Celula(y=celula_atual.y - 1, x=celula_atual.x - 1, anterior=celula_atual),
        Celula(y=celula_atual.y + 0, x=celula_atual.x - 1, anterior=celula_atual),
        Celula(y=celula_atual.y + 1, x=celula_atual.x - 1, anterior=celula_atual),
        Celula(y=celula_atual.y - 1, x=celula_atual.x + 0, anterior=celula_atual),
        Celula(y=celula_atual.y + 1, x=celula_atual.x + 0, anterior=celula_atual),
        Celula(y=celula_atual.y + 1, x=celula_atual.x + 1, anterior=celula_atual),
        Celula(y=celula_atual.y + 0, x=celula_atual.x + 1, anterior=celula_atual),
        Celula(y=celula_atual.y - 1, x=celula_atual.x + 1, anterior=celula_atual),
    ]

    # seleciona as celulas livres
    vizinhos_livres = []
    for v in vizinhos:
        # verifica se a celula esta dentro dos limites do labirinto
        if (
            (v.y < 0)
            or (v.x < 0)
            or (v.y >= len(labirinto))
            or (v.x >= len(labirinto[0]))
        ):
            continue
        # verifica se a celula esta livre de obstaculos.
        if labirinto[v.y][v.x] == 0:
            vizinhos_livres.append(v)

    return vizinhos_livres


def print_result(nome, caminho, custo_total, expandidos):
    if len(caminho) == 0:
        print("Goal é inalcançavel neste labirinto.")

    print(
        f"{nome}:"
        f"\tCusto total do caminho: {custo_total}.\n"
        f"\tNumero de passos: {len(caminho)-1}.\n"
        f"\tNumero total de nos expandidos: {len(expandidos)}.\n\n"
    )


def breadth_first_search(labirinto, inicio, goal, viewer=None):
    # nos gerados e que podem ser expandidos (vermelhos)
    fronteira = deque()
    # nos ja expandidos (amarelos)
    expandidos = set()

    # adiciona o no inicial na fronteira
    fronteira.append(inicio)

    # variavel para armazenar o goal quando ele for encontrado.
    goal_encontrado = None

    # Repete enquanto nos nao encontramos o goal e ainda
    # existem para serem expandidos na fronteira. Se
    # acabarem os nos da fronteira antes do goal ser encontrado,
    # entao ele nao eh alcancavel.
    while (len(fronteira) > 0) and (goal_encontrado is None):
        # seleciona o no mais antigo para ser expandido
        no_atual = fronteira.popleft()

        # busca os vizinhos do no
        vizinhos = celulas_vizinhas_livres(no_atual, labirinto)

        # para cada vizinho verifica se eh o goal e adiciona na
        # fronteira se ainda nao foi expandido e nao esta na fronteira
        for v in vizinhos:
            if v.y == goal.y and v.x == goal.x:
                goal_encontrado = v
                # encerra o loop interno
                break
            else:
                if (not esta_contido(expandidos, v)) and (
                    not esta_contido(fronteira, v)
                ):
                    fronteira.append(v)

        expandidos.add(no_atual)

        if viewer is not None:
            viewer.update(generated=fronteira, expanded=expandidos)
            # viewer.pause()

    caminho = obtem_caminho(goal_encontrado)
    custo = custo_caminho(caminho)

    if viewer is not None:
        viewer.update(path=caminho)

    return caminho, custo, expandidos


def depth_first_search(labirinto, inicio, goal, viewer=None):
    # nos gerados e que podem ser expandidos (vermelhos)
    fronteira = deque()
    # nos ja expandidos (amarelos)
    expandidos = set()

    # adiciona o no inicial na fronteira
    fronteira.append(inicio)

    # variavel para armazenar o goal quando ele for encontrado.
    goal_encontrado = None

    # Repete enquanto nos nao encontramos o goal e ainda
    # existem para serem expandidos na fronteira. Se
    # acabarem os nos da fronteira antes do goal ser encontrado,
    # entao ele nao eh alcancavel.
    while (len(fronteira) > 0) and (goal_encontrado is None):
        # seleciona o no mais antigo para ser expandido
        no_atual = fronteira.pop()

        # busca os vizinhos do no
        vizinhos = celulas_vizinhas_livres(no_atual, labirinto)

        # para cada vizinho verifica se eh o goal e adiciona na
        # fronteira se ainda nao foi expandido e nao esta na fronteira
        for v in vizinhos:
            if v.y == goal.y and v.x == goal.x:
                goal_encontrado = v
                # encerra o loop interno
                break
            else:
                if (not esta_contido(expandidos, v)) and (
                    not esta_contido(fronteira, v)
                ):
                    fronteira.append(v)

        expandidos.add(no_atual)

        if viewer is not None:
            viewer.update(generated=fronteira, expanded=expandidos)
            # viewer.pause()

    caminho = obtem_caminho(goal_encontrado)
    custo = custo_caminho(caminho)

    if viewer is not None:
        viewer.update(path=caminho)

    return caminho, custo, expandidos


def uniform_cost_search(labirinto, inicio, goal, viewer=None):
    # nos gerados e que podem ser expandidos (vermelhos)
    fronteira = []
    # nos ja expandidos (amarelos)
    expandidos = set()

    # adiciona o no inicial na fronteira
    fronteira.append(inicio)

    # variavel para armazenar o goal quando ele for encontrado.
    goal_encontrado = None

    # Repete enquanto nos nao encontramos o goal e ainda
    # existem nos para serem expandidos na fronteira. Se
    # acabarem os nos da fronteira antes do goal ser encontrado,
    # entao ele nao eh alcancavel.
    while (len(fronteira) > 0) and (goal_encontrado is None):
        # ordena a fronteira pelo custo do caminho
        fronteira.sort(key=lambda x: x.custo, reverse=True)

        # seleciona o no de menor custo para ser expandido
        no_atual = fronteira.pop()

        # testa objetivo:
        if no_atual.y == goal.y and no_atual.x == goal.x:
            # encerra loop interno
            goal_encontrado = no_atual
            break

        # adiciona no para explorados
        expandidos.add(no_atual)

        # busca os vizinhos do no
        vizinhos = celulas_vizinhas_livres(no_atual, labirinto)

        for v in vizinhos:
            # calcula o custo
            v.custo = custo_caminho(obtem_caminho(v))

            if (not esta_contido(expandidos, v)) and (not esta_contido(fronteira, v)):
                fronteira.append(v)
            elif esta_contido(fronteira, v):
                # encontra no na fronteira
                index = get_index(fronteira, v)

                if index > -1:
                    # atualiza o custo se o novo caminho tiver um custo menor
                    if v.custo < fronteira[index].custo:
                        fronteira[index] = v

        if viewer is not None:
            viewer.update(generated=fronteira, expanded=expandidos)
            # viewer.pause()

    caminho = obtem_caminho(goal_encontrado)
    custo = custo_caminho(caminho)

    if viewer is not None:
        viewer.update(path=caminho)

    return caminho, custo, expandidos


def a_star_search(labirinto, inicio, goal, viewer=None):
    # remova o comando abaixo e coloque o codigo A-star aqui
    pass


def cal_media(res_list):
    ret = Results(name=f"{res_list[0].name}_media")
    counter = 0
    tempo = 0
    numExpandidos = 0
    numGerados = 0
    custo_total = 0
    tamCaminho = 0
    for res in res_list:
        if res.alcancado:
            counter += 1
            tempo += res.tempo
            numExpandidos += res.numExpandidos
            numGerados += res.numGerados
            custo_total += res.custo_total
            tamCaminho += res.tamCaminho

    ret.tempo = tempo
    ret.numExpandidos = numExpandidos
    ret.numGerados = numGerados
    ret.custo_total = custo_total
    ret.tamCaminho = tamCaminho

    return ret


# -------------------------------


def main():
    print("Starting")
    REPETICOES = 10
    res_BFS = []
    res_DFS = []
    res_UCS = []

    SHOW_GRAPH = False
    # SHOW_GRAPH = False
    ZOOM = 30

    # SEED = 42  # coloque None no lugar do 42 para deixar aleatorio
    # random.seed(SEED)
    N_LINHAS = 100
    N_COLUNAS = 100
    INICIO = Celula(y=0, x=0, anterior=None)
    GOAL = Celula(y=N_LINHAS - 1, x=N_COLUNAS - 1, anterior=None)

    """
    O labirinto sera representado por uma matriz (lista de listas)
    em que uma posicao tem 0 se ela eh livre e 1 se ela esta ocupada.
    """
    print(f"Tamanho do labirinto: {N_LINHAS}x{N_COLUNAS}")

    for _ in range(REPETICOES):
        print("-------------------------")

        labirinto = gera_labirinto(N_LINHAS, N_COLUNAS, INICIO, GOAL)

        viewer_BFS = None
        viewer_DFS = None
        viewer_UCS = None
        if SHOW_GRAPH:
            viewer_BFS = MazeViewer(
                labirinto, INICIO, GOAL, step_time_miliseconds=20, zoom=ZOOM, name="BFS"
            )
            viewer_DFS = MazeViewer(
                labirinto, INICIO, GOAL, step_time_miliseconds=20, zoom=ZOOM, name="DFS"
            )
            viewer_UCS = MazeViewer(
                labirinto, INICIO, GOAL, step_time_miliseconds=20, zoom=ZOOM, name="UCS"
            )

        result_BFS = Results(
            "BFS", breadth_first_search, labirinto, INICIO, GOAL, viewer_BFS
        )
        result_DFS = Results(
            "DFS", depth_first_search, labirinto, INICIO, GOAL, viewer_DFS
        )
        result_UCS = Results(
            "UCS", uniform_cost_search, labirinto, INICIO, GOAL, viewer_UCS
        )

        # ----------------------------------------
        # BFS Search
        # ----------------------------------------
        result_BFS.run()
        result_BFS.printResults()
        res_BFS.append(result_BFS)

        # ----------------------------------------
        # DFS Search
        # ----------------------------------------
        result_DFS.run()
        result_DFS.printResults()
        res_DFS.append(result_DFS)

        # ----------------------------------------
        # Uniform Cost Search
        # ----------------------------------------
        result_UCS.run()
        result_UCS.printResults()
        res_UCS.append(result_UCS)

        print("+++++++++++++++++++++++++")

        if SHOW_GRAPH:
            print("OK! Pressione Enter pra finalizar...")
            input()

    print("=========================")

    res_media_BFS = cal_media(res_BFS)
    res_media_BFS.alcancado = True
    res_media_DFS = cal_media(res_DFS)
    res_media_DFS.alcancado = True
    res_media_UCS = cal_media(res_UCS)
    res_media_UCS.alcancado = True

    print("Resultado Final:")
    res_media_BFS.printResults()
    res_media_DFS.printResults()
    res_media_UCS.printResults()


if __name__ == "__main__":
    main()
