from time import time


class Results:
    def __init__(
        self,
        name="Nome",
        method=None,
        labirinto=None,
        inicio=None,
        goal=None,
        viewer=None,
    ):
        self.name = name
        self.method = method
        self.labirinto = labirinto
        self.inicio = inicio
        self.goal = goal
        self.viewer = viewer

        self.t0 = 0
        self.tf = 0
        self.tempo = 0

        self.caminho = None
        self.custo_total = 0
        self.tamCaminho = 0

        self.expandidos = None
        self.numExpandidos = 0

        self.numGerados = 0

        self.alcancado = False

    def getTime(self):
        self.tempo = self.tf - self.t0
        return self.tempo

    def run(self):
        if self.method is not None:
            self.t0 = time()
            self.caminho, self.custo_total, self.expandidos = self.method(
                self.labirinto, self.inicio, self.goal, self.viewer
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
                self.numExpandidos = len(self.expandidos)

    def printResults(self):
        if not self.alcancado:
            print("Goal é inalcançavel neste labirinto.")
        else:
            print(
                f"Método: {self.name}\n"
                f"\tTempo de execução: {round( self.tempo,4)} segundos\n"
                f"\tNúmero de nós expandidos: {self.numExpandidos}\n"
                f"\tNúmero de nós gerados: {self.numGerados}\n"
                f"\tCusto do caminho: {round(self.custo_total, 4)}\n"
                f"\tTamanho do caminho: {self.tamCaminho}\n"
            )
