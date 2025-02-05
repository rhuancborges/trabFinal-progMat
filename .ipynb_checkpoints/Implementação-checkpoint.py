from collections import defaultdict, deque
from gurobipy import GRB, Model
import random, time, argparse

# FUNÇÃO PARA LEITURA DE ARQUIVO DE INSTÂNCIA
# Lê o arquivo e coleta dele os dados dispostos conforme estrutura do arquivo de instância
# Retorna um dicionário com dados importantes da instância
def lerArquivoDat(nomeArquivo):
    with open(nomeArquivo, "r") as file:
        
        linha1 = file.readline().strip().split() # Lê a primeira linha
        n = int(linha1[0])        # Tamanho da grade n x n
        delta = int(linha1[1])    # Tempo adicional δ
        T = int(linha1[2])        # Tempo limite T
        
        # Lê a segunda linha
        m = int(file.readline().strip())  # Número de grupos de recursos
        
        # Ler as próximas m linhas (recursos disponíveis)
        betas = {}
        for i in range(m):
            t, k = map(int, file.readline().strip().split())
            for j in range(1, k+1):
                betas[j+k*i] = t
        alfa = len(betas)
        
        # Ler os arcos e armazena:
        # - arcos numa lista
        # - grafo num dicionário de listas (adjacências)
        # - vértices num set (para evitar repetições)
        grafo = defaultdict(list)
        arcos = []
        vertices = set({})
        for linha in file:
            u, v, t = linha.strip().split()
            arcos.append((u,v, int(t)))
            grafo[u].append((v,int(t)))
            vertices.add(u)
            vertices.add(v)
        vertices = list(sorted(vertices)) # Converte o set em lista, para retornar

    return {
        "n": n,
        "delta": delta,
        "T": T,
        "alfa": alfa,
        "betas": betas,
        "arcos": arcos,
        "vertices": vertices,
        "grafo": grafo
    }

# FUNÇÃO PARA IMPLEMENTAR O MODELO MATEMÁTICO E RESOLVÊ-LO VIA SOLVER GUROBI
# Implementa o modelo utilizando Gurobi e resvolve-o
def otimizacaoGurobi(dados):
    modelo = Model("fake_news")
    modelo.setParam('OutputFlag', 0) # Desativa o "log" do solver
    
    vertices = dados["vertices"]
    M = 1000 # Big-M para uma das restrições

    # Variávei x_{i,u} representando a alocação do recurso i no vértice u
    x = {}
    for i in range(1,dados["alfa"]+1):
      x[i] = {}
      for u in vertices:
          x[i][u] = modelo.addVar(vtype=GRB.BINARY, name=f"x_{i}_{u}")

    # Variável y_{u,f} representando a alcancabilidade do vértice u quando a fake news parte do vértice f
    y = {}
    for u in vertices:
      y[u] = {}
      for f in vertices:  
          y[u][f] = modelo.addVar(vtype=GRB.BINARY, name=f"y_{u}_{f}")

    # Variável t_{v,f} representando o tempo de alcance do vértice v quando a fake news parte do vértice f
    t = {}
    for v in vertices:
      t[v] = {}
      for f in vertices:  
          t[v][f] = modelo.addVar(vtype=GRB.INTEGER, name=f"t_{v}_{f}")

    # Variável S representando a maior quantidade de servidores atingidos, considerando o cenário geral de qualquer fonte de fake news
    S = modelo.addVar(vtype=GRB.INTEGER, name=f"S")
    
    # Função Objetivo - Minimizar o valor de S
    modelo.setObjective(S, GRB.MINIMIZE)

    # Para cada fonte s, a variável S vale no mínimo o número de vértices alcançados quando a fake news parte de s
    # No fim, o valor de S fica limitado inferiormente pela maior alcancabilidade
    for s in vertices:
        modelo.addConstr(S >= sum(y[u][s] for u in vertices))
    
    # Para cada fonte s e para cada vértice v, o vértice v é alcançado y_{v,s} = 1 se o tempo t_{v,s} <= T
    for s in vertices:
        for v in vertices:
            modelo.addConstr((dados["T"]+1)*(1-y[v][s]) <= t[v][s])
            modelo.addConstr(t[v][s] <= dados["T"]*y[v][s] + M*(1-y[v][s]))

    # Para cada fonte s e para cada arco (u,v,tuv), o tempo de alcance do vértice v (t_{v,s}) é o tempo de alcance do seu antecessor u (t_{u,s})
    # somado ao tempo de propagação no enlace (tuv) e um possível valor de delta caso o vértice u tenha um recurso alocado (x_{i,u} = 1)
    for s in vertices:
        for (u,v,tuv) in dados["arcos"]:
               modelo.addConstr(t[v][s] <= t[u][s] + tuv + dados["delta"]*sum(x[i][u] for i in range(1, dados["alfa"]+1)), name=f"cálculo de t_{v}")

    # Para cada vértice u, no máximo um recurso i pode ser alocado a ele
    for u in vertices:
            modelo.addConstr(sum(x[i][u] for i in range(1,dados["alfa"]+1)) <= 1)

    # Para cada recurso i, no máximo em um vértice u ele pode ser alocado
    for i in range(1,dados["alfa"]+1):
            modelo.addConstr(sum(x[i][u] for u in vertices) <= 1)

    # Para cada fonte s e para cada vértice u, um recurso i só pode ser alocado a u se o tempo de alcance de u (t_{u,s}) for maior ou igual ao 
    # instante em que o recurso i fica disponível
    for s in vertices:
        for u in vertices:
                modelo.addConstr(t[u][s] >= sum(x[i][u]*dados["betas"][i] for i in range(1,dados["alfa"]+1)))

    # Para cada fonte s, a alcancabilidade de s é 1 e o tempo de alcance é 0
    for s in vertices:
        modelo.addConstr(y[s][s] == 1)
        modelo.addConstr(t[s][s] == 0)
    
    # Otimiza o modelo
    modelo.optimize()

    # Retorna o valor do ótimo ou -1
    if(modelo.status==GRB.OPTIMAL):
      return modelo.objVal
    else:
      return -1 

# FUNÇÃO QUE CALCULA A ALCANCABILIDADE DE VÉRTICES A PARTIR DE UMA FONTE
# Utiliza BFS para varrer o grafo
def calcularAlcance(fonte, individuo, dados):
    T = dados["T"]
    delta = dados["delta"]
    grafo = dados["grafo"]
    alcancados = []
    fila = deque([(0, fonte)])  # (tempo, vertice)
   
    quantAlcancados = 1
    
    while fila:
        tempo_u, u = fila.popleft()
        for v, tuv in grafo[u]:
            tempo_v = tempo_u + tuv + (delta if individuo[u] == 1 else 0) # Calcula o tempo do vizinho

            # O vértice v só é considerado alcancado se seu tempo de alcance não ultrapassar T
            if tempo_v <= T and v not in alcancados:
                quantAlcancados += 1
                alcancados.append(v)
                fila.append((tempo_v, v))
                
    return quantAlcancados

# FUNÇÃO DO ALGORITMO GENÉTICO PARA CALCULAR APTIDÃO DO INDIVÍDUO
# Dado um indivíduo (alocação de recursos), para todos os possíveis vértices como fontes, essa função 
# chama a função calcularAlcance() e retorna o maior valor de alcancabilidade obtido (ou seja, o pior caso)
def aptidao(individuo, dados):
    resultado = []
    for verticeFonte in dados["vertices"]:
        resultado.append(calcularAlcance(verticeFonte, individuo, dados))
    return max(resultado)

# FUNCAO DO ALGORITMO GENÉTICO QUE INICIALIZA ALEATORIAMENTE UMA POPULAÇÃO DE k INDIVÍDUOS
# Ela gera um número aleatório no intervalo [0,alfa] para alocar os recursos randomicamente e em quantidade factível 
def inicializarPopulacao(k, dados):
    populacao = []
    
    for _ in range(k):  
        
        # Número aleatório de bits 1 entre 0 e alfa (número total de recursos)
        numBits1 = random.randint(0, dados["alfa"])
        
        # Cria um indivíduo com "numBits1" bits iguais a 1, e o restante 0
        individuo = {f"{chave}": 0 for chave in dados["vertices"]}
        indices1 = random.sample(dados["vertices"], numBits1)  # Seleciona aleatoriamente as posições para 1
        
        for i in indices1:
            individuo[i] = 1
        
        populacao.append(individuo)
    
    return populacao
    
# FUNÇÃO DO ALGORITMO GENÉTICO QUE REALIZA A SELEÇÃO DOS INDIVÍDUOS MAIS APTOS DA POPULACAO
# É feita a seleção por torneio, escolhendo dois aleatórios e comparando-os quanto à aptidão, retornando o de menor aptidão (ou seja, menor S)
def selecao(populacao,dados):
  indices = random.sample(range(len(populacao)), 2)  
  individuosTorneio = [populacao[indices[0]], populacao[indices[1]]]
  aptidoes = [aptidao(individuo, dados) for individuo in individuosTorneio]
  return individuosTorneio[aptidoes.index(min(aptidoes))]

# FUNÇÃO DO ALGORITMO GENÉTICO QUE APLICA A MUTAÇÃO NOS INDIVÍDUOS A UMA TAXA taxaMutacao
# É realizada a Mutação SWAP, a fim de manter a quantidade de recursos alocados inalterada
def mutacao(individuo, taxaMutacao):
    if random.random() < taxaMutacao:
        indicesTroca = random.sample(list(individuo.keys()), 2) 
        aux = individuo[indicesTroca[0]]
        individuo[indicesTroca[0]] = individuo[indicesTroca[1]] 
        individuo[indicesTroca[1]] = aux  
    return individuo

# FUNÇÃO DO ALGORITMO GENÉTICO QUE APLICA O CRUZAMENTO/CROSSOVER EM DOIS INDIVIDUOS A UMA TAXA taxaCrossover
# É realizado o Crossover de 2 pontos
def cruzamento(individuo1, individuo2, taxaCrossOver):
    if random.random() < taxaCrossOver:
        # Converte o dicionário para uma lista de chaves
        chaves = list(individuo1.keys())
        
        # Sorteia dois pontos para o crossover
        ponto1, ponto2 = sorted(random.sample(range(len(chaves)), 2
                                             
        # Cria os filhos trocando os valores entre os dois pontos
        filho1 = {}
        filho2 = {}
        
        for i, chave in enumerate(chaves):
            # Troca os genes compreendidos entre os dois pontos sorteados e mantém iguais os fora do limite
            if ponto1 <= i < ponto2:
                filho1[chave] = individuo2[chave]
                filho2[chave] = individuo1[chave]
            else:
                filho1[chave] = individuo1[chave]
                filho2[chave] = individuo2[chave]
        
        return filho1, filho2
    return individuo1, individuo2

# FUNÇÃO PRINCIPAL DO ALGORITMO GENÉTICO, QUE CHAMA AS OUTRAS FUNÇÕES
# Critério de parada: número de iterações/gerações = 10
# Seleciona 4 indivíduos mais aptos e realiza 8 cruzamentos, a fim de manter um padrão de tamanho de população igual a 16
def otimizacaoAG(dados, tamanhoPopulacao, taxaCrossover, taxaMutacao):
    it = 1
    maxIt = 10
    populacao = inicializarPopulacao(tamanhoPopulacao, dados)
    SI = [aptidao(individuo, dados) for individuo in populacao] # Solução inicial (indivíduos da população inicial)
    while it <= maxIt:
        pais = {}
        for i in range(4):
            pais[i] = selecao(populacao, dados)
        novaPopulacao = []
        novaPopulacao += cruzamento(pais[0], pais[1], taxaCrossover)
        novaPopulacao += cruzamento(pais[0], pais[2], taxaCrossover)
        novaPopulacao += cruzamento(pais[0], pais[3], taxaCrossover)
        novaPopulacao += cruzamento(pais[1], pais[2], taxaCrossover)
        novaPopulacao += cruzamento(pais[1], pais[3], taxaCrossover)
        novaPopulacao += cruzamento(pais[2], pais[3], taxaCrossover)
        novaPopulacao += cruzamento(pais[3], pais[2], taxaCrossover)
        novaPopulacao += cruzamento(pais[3], pais[1], taxaCrossover)
        novaPopulacao = [mutacao(individuo, taxaMutacao) for individuo in novaPopulacao]
        populacao = novaPopulacao
        it+=1
    SF = [aptidao(individuo, dados) for individuo in populacao] # Solução final (indivíduos após a 10º geração)
    return min(SI), min(SF)
        
# FUNÇÃO PRINCIPAL DO PROGRAMA, QUE REÚNE A LEITURA DE ARQUIVO, A EXECUÇÃO VIA SOLVER E EXECUÇÃO DO ALGORITMO GENÉTICO
# Essa função recebe alguns parâmetros via linha de comando:
# - nomeArquivoSolucao: o nome do arquivo para gravar as melhores soluções
# - tamanhoPopulacao: tamanho da população inicial a ser gerada para o Algoritmo Genético
# - taxaCrossover: valor decimal que representa a taxa de aplicação do crossover
# - taxaMutacao: valor decimal que representa a taxa de aplicação da mutação
# Essa função realiza a contagem do tempo de execução das funções otimizacaoGurobi() e otimizacaoAG()
# e também gera 5 sementes randômicas para executar o Algoritmo Genético 5 vezes, cada uma numa semente diferente
# Assim, os resultados retornados pelo Algoritmo Genético são médias de 5 execuções (e o tempo contado é a soma dos tempos de cada uma das 5 execuções)
# Além disso, essa função gera saídas na saída padrão e no arquivo passado como parâmetro
def main(nomeArquivoInstancia, num, nomeArquivoSolucao, tamanhoPopulacao, taxaCrossover, taxaMutacao):
    with open(nomeArquivoSolucao, "a") as f:
        f.write(f"INSTANCIA {num}.\n")
    
    dados = lerArquivoDat(nomeArquivoInstancia)
    inicioSolver = time.time()
    solver = otimizacaoGurobi(dados)
    fimSolver = time.time()
    if solver != -1:
        print(f"Solução via solver: {solver} em {fimSolver - inicioSolver} segundos")
        with open(nomeArquivoSolucao, "a") as f:
            f.write(f"Solução via solver: {solver} em {fimSolver - inicioSolver} segundos\n")
    else:
        print("Não há solução ótima via solver")
      
    seeds = [random.randint(0, 999999) for _ in range(5)]    
    solucoesI = []
    solucoesF = []
 
    inicioAG = time.time()
    for i in range(5):       
        random.seed(seeds[i])
        SI, SF = otimizacaoAG(dados, tamanhoPopulacao, taxaCrossover, taxaMutacao)
        solucoesI.append(SI)
        solucoesF.append(SF)
    fimAG = time.time()
    mediaSI = sum(solucoesI)/5
    mediaSF = sum(solucoesF)/5
    print(f"Solução inicial via AG: {mediaSI}\nSolução final via AG: {mediaSF} em {fimAG-inicioAG} segundos (5 execuções)")
    with open(nomeArquivoSolucao, "a") as f:
        f.write(f"Solução inicial via AG: {mediaSI}\nSolução final via AG: {mediaSF} em {fimAG-inicioAG} segundos (5 execuções)\n\n")

# FUNÇÃO QUE IMPLEMENTA UM PARSER PARA CAPTURAR PARÂMETROS VIA LINHA DE COMANDO
# Essa função configura 4 argumentos a serem passados ao executar o código via linha de comando
def capturarParametros():
    parser = argparse.ArgumentParser()
    
    # Definindo os parâmetros
    parser.add_argument('--arq', type=str, help="Nome do arquivo para registrar melhor solução", required=True)
    parser.add_argument('--popInicial', type=int, help="Tamanho da população inicial", required=True)
    parser.add_argument('--taxaCross', type=float, help="Valor decimal para a taxa de crossover", required=True)
    parser.add_argument('--taxaMut', type=float, help="Valor decimal para a taxa de mutacao", required=True)
    
    return parser.parse_args()

# BLOCO DE CÓDIGO RAIZ, EXECUTADO AO EXECUTAR O PROGRAMA
# Primeiramente ele captura os argumentos via linha de comando e chama a função main() para cada instância do problema
if __name__=="__main__":
    args = capturarParametros()
    for num in range(1,11):
       main(f"fake_news_problem/instances/fn{num}.dat", num, args.arq, args.popInicial, args.taxaCross, args.taxaMut)

    
                  