# Modelo Matemático - Problema Fake News

## Variáveis

- $x_{i,u} \in \{0,1\}$: vale 1 se o recurso $i$ foi alocado ao servidor $u$; 0 caso contrário;
- $y_{u,f} \in \{0,1\}$: vale 1 se o servidor $u$ foi atingido pela fake news em tempo menor ou igual a T, no contexto em que a fake news partiu do servidor $f$; 0 caso contrário;
- $t_{v,f} \in \mathbb{Z}$: tempo mínimo para o servidor $v$ ser atingido pela fake news, no contexto em que essa fake news partiu do servidor $f$;
- $S$: a maior quantidade de servidores atingidos pela fake news olhando o contexto geral em que ela partiu de qualquer vértice

## Função Objetivo

A fake news pode partir de qualquer vértice pertencente ao conjunto de vértices $V$ da instância. Desse modo, ao analisar o cenário, podemos obter alcancabilidades de servidores diferentes a depender da fonte $s$ a partir da qual partiu a fake news. Para podermos distribuir os recursos, temos que analisar o pior caso, ou seja, o vértice $s$ (fonte da fake news) que provoca maior alcançabilidade de vértices e, com isso, nosso objetivo é minimizar essa alcançabilidade do pior caso. Portanto, a função objetivo é minimizar a maior quantidade de servidores atingidos pela fake news, considerando o pior caso de $s$:

$$
\min S
$$

## Restrições

- Determinar o valor de S para cada fonte $s$ possível como a quantidade de servidores atingidos pela fake news no contexto em que ela partiu de $s$:
  
$$
S \geq \sum_{u \in V}y_{u,s} \space \forall s \in V
$$    
    
- O tempo em que um vértice $v$ é alcançado pela fake news é menor ou igual a $T$. Essa restrição força $y_{v,s} = 1$ se o tempo $t_{v,s} \lt T$. Vale ressaltar que é uma restrição "perigosa", pois ela não garante $y_{v,s} = 1$ quando $t_{v,s} = T$ nem $y_{v,s} = 0$ quando $t_{v,s} \gt T$:
  
$$
t_{v,s} \geq (T+1)(1-y_{v,s}) \space \forall v,s \in V
$$

- O tempo em que um vértice $v$ é alcançado pela fake news é calculado pelo tempo em que seu predecessor $u$ é alcançado somado ao tempo gasto no enlance, bem como a um valor de $\delta$ se algum dos recursos foi alocado no vértice $u$:
  
$$
t_{v,s} \leq t_{u,s} + t_{uv} + \delta*\sum_{i=1}^{\alpha}x_{i,u}, \space \forall (u,v) \in E
$$

- Para cada vértice, só pode ter no máximo um dos recursos alocados nele:
  
$$
\sum_{i=1}^{\alpha}x_{i,u} \leq 1, \space \forall u \in V
$$

- Para cada recurso, só pode ter no máximo um dos vértices com ele alocado:
  
$$
\sum_{u \in V}x_{i,u} \leq 1, \space \forall i=1,..,\alpha
$$

- Um recurso $i$ só pode ser alocado a um servidor $u$ se o tempo em que esse servidor $u$ foi alcançado for superior ao instante $\beta_{i}$ em que o recurso $i$ fica disponível:
  
$$
t_{u,s} \geq \sum_{i=1}^{\alpha}x_{i,u}*\beta_{i}, \space \forall u,s \in V
$$

- No contexto em que a fake news parte do servidor $s$, o valor de $y$ para o vértice $s$ é igual a 1 e o tempo em que o vértice $s$ é alcançado é 0
  
$$
y_{s,s} = 1
$$

$$
t_{s,s} = 0
$$

$$
\forall s \in V
$$
