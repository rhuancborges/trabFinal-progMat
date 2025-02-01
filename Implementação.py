from collections import defaultdict
from gurobipy import GRB, Model

def mapearU(x,y,n):
    return (x-1)*n + y
    
def ler_arquivo_dat(nome_arquivo):
    with open(nome_arquivo, "r") as file:
        # Ler a primeira linha
        linha1 = file.readline().strip().split()
        n = int(linha1[0])        # Tamanho da grade n x n
        delta = int(linha1[1])    # Tempo adicional δ
        T = int(linha1[2])        # Tempo limite T
        
        # Ler a segunda linha
        m = int(file.readline().strip())  # Número de grupos de recursos

        # Ler as próximas m linhas (recursos disponíveis)
        betas = {}
        for i in range(m):
            t, k = map(int, file.readline().strip().split())
            for j in range(1, k+1):
                betas[j+3*i] = t
        alfa = len(betas)

        # Ler os arcos
        arcos = []
        vertices = set({})
        for linha in file:
            parte1, parte2, t = linha.strip().split()
            x1, y1 = map(int, parte1.split('-'))
            x2, y2 = map(int, parte2.split('-'))
            u = mapearU(x1,y1,n)
            v = mapearU(x2,y2,n)
            arcos.append((u,v, int(t)))
            vertices.add(u)
            vertices.add(v)
       

    return {
        "n": n,
        "delta": delta,
        "T": T,
        "alfa": alfa,
        "betas": betas,
        "arcos": arcos,
        "vertices": vertices
    }


# Exemplo de uso:
dados = ler_arquivo_dat("fake_news_problem/instances/fn1.dat")
"""dados = {
    "n": 4,
    "delta": 2,
    "T": 1,
    "alfa": 1,
    "betas": {1: 0},
    "arcos": [(1,2,2), (1,4,1), (4,3,3)],
    "vertices": {1,2,3,4}
}"""
# Exibir os dados lidos
print("Tamanho da grade:", dados["n"])
print("Tempo adicional δ:", dados["delta"])
print("Tempo limite T:", dados["T"])
print("Número de recursos:", dados["alfa"])
print("Recursos disponíveis:", dados["betas"])

modelo = Model("fake_news")

vertices = dados["vertices"]

x = {}
for i in range(1,dados["alfa"]+1):
  x[i] = {}
  for u in vertices:
      x[i][u] = modelo.addVar(vtype=GRB.BINARY, name=f"x_{i}_{u}")

y = {}
for u in vertices:
  y[u] = modelo.addVar(vtype=GRB.BINARY, name=f"y_{u}")

t = {}
for v in vertices:
  t[v] = modelo.addVar(vtype=GRB.INTEGER, name=f"t_{v}")


modelo.setObjective(sum(y[u] for u in vertices), GRB.MINIMIZE)

for v in vertices:
  modelo.addConstr(t[v] <= dados["T"] + 100*(1-y[v]))
  #modelo.addConstr(t[v] >= dados["T"]*(1-y[v]))

for (u,v,tuv) in dados["arcos"]:
       modelo.addConstr(t[v] >= t[u] + tuv + sum(x[i][u]*dados["delta"] for i in range(1, dados["alfa"]+1)))
       #modelo.addConstr(sum(x[i][u]*dados["delta"] for i in range (1, dados["alfa"]+1)) <= t[v] - t[u] - tuv)

for u in vertices:
        modelo.addConstr(sum(x[i][u] for i in range(1,dados["alfa"]+1)) <= 1)

for i in range(1,dados["alfa"]+1):
        modelo.addConstr(sum(x[i][u] for u in vertices) <= 1)

for u in vertices:
    for i in range(1,dados["alfa"]+1):
        modelo.addConstr(t[u] >= dados["betas"][i]*x[i][u])

modelo.addConstr(t[list(vertices)[0]] == 0)
modelo.addConstr(y[list(vertices)[0]] == 1)

modelo.optimize()

if(modelo.status==GRB.OPTIMAL):
  print(f"\n\nFunção Objetivo: {modelo.objVal}")
  for i in vertices:
      print(f"Vertice {i}: {y[i].X}")
      #if(y[i].X==1):
      print(f"\tTempo: {t[i].X}")
  for i in range(1,dados["alfa"]+1):
      for u in vertices:
          print(f"Recurso {i} aplicado no vertice {u}? {x[i][u].X}")
else:
  print("Não foi possível encontrar uma solução")