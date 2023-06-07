from time import time
import networkx as nx


class Results:
    def __init__(
        self,
        name="Nome",
        method=None,
        G_inicial: nx.Graph = None,
        source=None,
        goal=None,
        estimation=[]
    ):
        self.name = name
        self.method = method
        self.G_inicial = G_inicial
        self.source = source
        self.goal = goal
        self.estimation = estimation

        self.t0 = 0
        self.tf = 0
        self.tempo = 0

        self.caminho = []
        self.custo_total = 0
        self.tamCaminho = 0

        self.numExpandidos = 0
        self.G: nx.Graph = None

    def getTime(self):
        self.tempo = self.tf - self.t0
        return self.tempo

    def run(self):
        if self.method is not None:
            self.t0 = time()
            self.G, self.caminho, self.custo_total, self.numExpandidos = self.method(
                self.G_inicial, self.source, self.goal, self.estimation
            )
            self.tf = time()
            self.getTime()

            if len(self.caminho) == 0:
                self.alcancado = False
                self.tamCaminho = 0
                self.numExpandidos = 0
            else:
                self.alcancado = True
                self.tamCaminho = len(self.caminho) - 1

    def printResults(self):
        if not self.alcancado:
            print("Goal é inalcançavel neste labirinto.")
        else:
            print(
                f"Método: {self.name}\n"
                f"\tTempo de execução: {round( self.tempo,4)} segundos\n"
                f"\tNúmero de nós expandidos: {self.numExpandidos}\n"
                f"\tCusto do caminho: {round(self.custo_total, 4)}\n"
                f"\tTamanho do caminho: {self.tamCaminho}\n"
            )
