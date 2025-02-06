#  Problema da Fake News com Algoritmo Genético
<p align="left"> 
<a href="https://www.python.org" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" alt="python" width="40" height="40"/> </a> 
<a href="https://www.gurobi.com/" target="_blank" rel="noreferrer"> <img src="https://avatars.githubusercontent.com/u/15114496?s=200&v=4" alt="gurobi" width="37" height="37"/> </a>
</p>  
<p align="right"> 
<i>Desenvolvido por Rhuan Campideli Borges</i>
</p> 

<p>Esse repositório armazena o que foi desenvolvido no trabalho final da disciplina GCC118 - Programação Matemática do curso de Ciência da Computação da Universidade Federal de Lavras (UFLA)</p>

## Modelo
A primeira etapa do desenvolvimento do trabalho foi a elaboração de um modelo matemático que pudesse ser executado e otimizado pelo solver Gurobi. O arquivo Markdown em que consta o modelo matemático para o Problema da Fake News está presente neste repositório e pode ser acessado abaixo:

[`modelo.md`](https://github.com/rhuancborges/trabFinal-progMat/blob/main/modelo.md)

## Objetivo
O objetivo principal do desenvolvimento de um profundo conhecimento de uma metaheurística, assunto selecionado para ser aprendido ativamente (através deste trabalho) no contexto da disciplina. Com isso, a metaheurística selecionada neste trabalho foi a metaheurística evolutiva populacional Algoritmo Genético.

### Implementação do Algoritmo Genético
O Algoritmo Genético consiste em uma sequência de passos que imitam a evolução das espécies da natureza: dada uma **população inicial**, os indivíduos mais *aptos* são **selecionados** e são submetidos a **cruzamentos** entre si e **mutações** em seus genes ao longo das *gerações*. 
Inspirado nesse processo, o Algoritmo Genético atua da seguinte maneira:
- Inicializa uma população de indivíduos;
- Seleciona (por um mecanismo) os mais aptos;
- Sujeita-os a cruzamentos, podendo trocar genes (*crossover*) a uma dada probabilidade;
- Sujeita os indivíduos gerados a mutações em seus genes a uma dada probabilidade;
- Atualiza a população atual (*nova geração*).

O código da implementação, juntamente com todas as funções pode ser visto em [`Implementação.py`](https://github.com/rhuancborges/trabFinal-progMat/blob/main/Implementação.py)

Alguns detalhes importantes:

- O mecanismo de *crossover* escolhido foi o **Crossover de 2 pontos**;
- O mecanismo de mutação escolhido foi a **Mutação Swap**;
- O mecanismo de seleção escolhido foi a **Seleção por Torneio**;
- O critério de parada escolhido foi o de **número máximo de gerações**;
- As soluções retornadas pelo Algoritmo Genético são uma média de 5 execuções do método, como sementes randômicas diferentes.

## Protocolos de Execução
Para executar o código e testar a implementação, é importante ter o gurobi instalando na sua máquina. Tendo-o instalado, no prompt de comando dentro do diretório em que os arquivos deste repositório estão armazenados, digite o seguinte comando:

`python Implementação.py --arq NOMEDOARQUIVO --popInicial TAMANHOPOPULACAO --taxaCross TAXACROSSOVER --taxaMut TAXAMUTACAO` (em sistemas Linux, é `python3`)

- O parâmetro `NOMEDOARQUIVO` representa o nome do arquivo em que serão registradas as soluções encontradas pelo algoritmo para cada uma das instâncias;
- O parâmetro `TAMANHOPOPULACAO` representa o número de indivíduos a serem gerados para compor a população inicial;
- O parâmetro `TAXACROSSOVER` é o valor decimal que representa a porcentagem/taxa de *crossover* do Algoritmo Genético;
- O parâmetro `TAXAMUTACAO` é o valor decimal que representa a porcentagem/taxa de mutação do Algoritmo Genético.
  
## Outros arquivos do repositório

- [`fake_news_problem/instances`](https://github.com/rhuancborges/trabFinal-progMat/tree/main/fake_news_problem/instances) é um subdiretório que contém as instâncias de teste do Problema da Fake News. Dentro desse subdiretório, encontra-se um `Readme.md` que mostra o formato em que essas instâncias estão estruturadas;
- [`melhorSolução.txt`](https://github.com/rhuancborges/trabFinal-progMat/blob/main/melhorSolu%C3%A7%C3%A3o.txt) é o arquivo `.txt` gerado durante a fase de testes da implementação, sendo este arquivo que foi passado como parâmetro em `--arq NOMEDOARQUIVO` na linha de comando. Em seus testes, você deve, de preferências, passar outros nomes de arquivos para gerar outros arquivos para registro das soluções, a fim de que os registros em `melhorSolução.txt`não se alterem;
- [`teste.dat`](https://github.com/rhuancborges/trabFinal-progMat/blob/main/teste.dat) e [`teste2.dat`](https://github.com/rhuancborges/trabFinal-progMat/blob/main/teste2.dat) são dois arquivos de instâncias simples criados no início da implementação para testar os códigos desenvolvidos;
- [`Problema da Fake News com Algoritmo Genético.pdf`](https://github.com/rhuancborges/trabFinal-progMat/blob/main/Problema%20da%20Fake%20News%20com%20Algoritmo%20Gen%C3%A9tico.pdf) é um relatório de todo o processo de desenvolvimento e implementação do projeto.

