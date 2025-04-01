import gurobipy as gp
import sys
from gurobipy import GRB


# restrição (2)
def restricao_custo_total(model, K, r1, r2, u1, u2, k):
    model.addConstr(K == gp.quicksum(k[0] * u1[j] for j in range(r1)) +
                        gp.quicksum(k[1] * u2[j] for j in range(r2)), name="Custo_Total")

# restrição (3)
def restricao_camisetas_frentes(model, W, r1, r2, x1, x2, p):
    model.addConstr(W <= gp.quicksum(p[0] * x1[j] for j in range(r1)) +
                        gp.quicksum(p[1] * x2[j] for j in range(r2)), name="Camisetas_Frentes")

# restrição (4)
def restricao_camisetas_costas(model, W, r1, r2, y1, y2, q):
    model.addConstr(W <= gp.quicksum(q[0] * y1[j] for j in range(r1)) +
                        gp.quicksum(q[1] * y2[j] for j in range(r2)), name="Camisetas_Costas")

# restrição (5)
def restricao_camisetas_mangas(model, W, r1, r2, z1, z2, s):
    model.addConstr(W <= gp.quicksum(s[0] * z1[j] for j in range(r1)) +
                        gp.quicksum(s[1] * z2[j] for j in range(r2)), name="Camisetas_Mangas")

# restrição (7) para rolo tipo 1
def restricao_blocos_rolo1(model, r1, x1, y1, z1, u1, M):
    for j in range(r1):
        model.addConstr(x1[j] + y1[j] + z1[j] <= M * u1[j], name=f"Blocos_Rolo1_{j}")

# restrição (7) para rolo tipo 2
def restricao_blocos_rolo2(model, r2, x2, y2, z2, u2, M):
    for j in range(r2):
        model.addConstr(x2[j] + y2[j] + z2[j] <= M * u2[j], name=f"Blocos_Rolo2_{j}")

# restrição (9) para rolo tipo 1
def restricao_comprimento_rolo1(model, r1, x1, y1, z1, a, b, c, l):
    for j in range(r1):
        model.addConstr(a[0] * x1[j] + b[0] * y1[j] + c[0] * z1[j] <= l[0], name=f"Comprimento_Rolo1_{j}")

# restrição (9) para rolo tipo 2
def restricao_comprimento_rolo2(model, r2, x2, y2, z2, a, b, c, l):
    for j in range(r2):
        model.addConstr(a[1] * x2[j] + b[1] * y2[j] + c[1] * z2[j] <= l[1], name=f"Comprimento_Rolo2_{j}")


def Cenario1(p,q,s,a,b,c,k,l):
    # Definição dos parâmetros
    r1 = 10              # Número de rolos do tipo 1
    r2 = 0               # Número de rolos do tipo 2
    r_total = r1 + r2    # Total de rolos
    alpha = 1000         # Peso para minimizar o custo
    beta = 1             # Peso para maximizar a quantidade de camisetas
    M = sys.maxsize      # Um valor suficientemente grande
    v = 20               # Quantidade mínima de camisetas a serem produzidas
    r = 10               # Quantidade total de rolos
    resultados=[]

    for v, r1 in zip(range(100, 1001, 100), range(1, 11)):
        model = gp.Model('Problema das Camisetas')

        u = model.addVars(2, r_total, vtype=GRB.BINARY, name='u')
        x = model.addVars(2, r_total, vtype=GRB.INTEGER, name='x')
        y = model.addVars(2, r_total, vtype=GRB.INTEGER, name='y')
        z = model.addVars(2, r_total, vtype=GRB.INTEGER, name='z')
        W = model.addVar(vtype=GRB.INTEGER, name='W')
        K = model.addVar(vtype=GRB.CONTINUOUS, name='K')

        model.setObjective(alpha * K - beta * W, GRB.MINIMIZE)
        model.addConstr(K == gp.quicksum(k[i] * u[i, j] for i in range(2) for j in range(r_total)))
        model.addConstr(W <= gp.quicksum(p[i] * x[i, j] for i in range(2) for j in range(r_total)))
        model.addConstr(W <= gp.quicksum(q[i] * y[i, j] for i in range(2) for j in range(r_total)))
        model.addConstr(W <= gp.quicksum(s[i] * z[i, j] for i in range(2) for j in range(r_total)))
        model.addConstr(W >= v)
        for i in range(2):
            for j in range(r_total):
                model.addConstr(x[i, j] + y[i, j] + z[i, j] <= M * u[i, j])
        model.addConstr(gp.quicksum(u[i, j] for i in range(2) for j in range(r_total)) <= r)   
        for i in range(2):
            for j in range(r_total):
                model.addConstr(a[i] * x[i, j] + b[i] * y[i, j] + c[i] * z[i, j] <= l[i])

        model.optimize()

        if model.status == GRB.OPTIMAL:
            W_val = W.X
            K_val = K.X
            resultados.append([v, W_val, r1,r2, K_val])

    with open('output.txt', 'w') as file:
        file.write("Tabela Cenario 1\n")
        file.write(f"{'Qtd mín de camisetas(v)':<25}{'Qtd possível de camisetas(W)':<30}{'Qtd rolos Tipo 1':<20}{'Qtd rolos Tipo 2':<20}{'Custo total (K)':<20}\n")
        for res in resultados:
            file.write(f"{res[0]:<25}{res[1]:<30}{res[2]:<20}{res[3]:<20}{res[4]:<20}\n")
                        
def Cenario2(p,q,s,a,b,c,k,l):
    r1_values = [1,2,1,1,1,2,2,3,2,2]
    r2_values = [0,0,2,3,4,4,5,5,7,8]
    beta = 1000
    alpha = 1
    M = sys.maxsize  # (7)
    resultados=[]

    for r1, r2 in zip(r1_values, r2_values):       
        model = gp.Model("otimizacao_camisas")

        u1 = model.addVars(r1, vtype=GRB.BINARY, name="u1")     # 0 ou 1 se o rolo tipo 1 é utilizado
        u2 = model.addVars(r2, vtype=GRB.BINARY, name="u2")     # 0 ou 1 se o rolo tipo 2 é utilizado
        x1 = model.addVars(r1, vtype=GRB.INTEGER, name="x1")    # quantidade de blocos de frentes tipo 1
        x2 = model.addVars(r2, vtype=GRB.INTEGER, name="x2")    # quantidade de blocos de frentes tipo 2
        y1 = model.addVars(r1, vtype=GRB.INTEGER, name="y1")    # quantidade de blocos de costas tipo 1
        y2 = model.addVars(r2, vtype=GRB.INTEGER, name="y2")    # quantidade de blocos de costas tipo 2
        z1 = model.addVars(r1, vtype=GRB.INTEGER, name="z1")    # quantidade de blocos de mangas tipo 1
        z2 = model.addVars(r2, vtype=GRB.INTEGER, name="z2")    # quantidade de blocos de mangas tipo 2
        W = model.addVar(vtype=GRB.INTEGER, name="W")           # quantidade total de camisetas
        K = model.addVar(vtype=GRB.CONTINUOUS, name="K")        # custo total dos rolos

        model.setObjective(beta * W - alpha * K, GRB.MAXIMIZE)

        restricao_custo_total(model, K, r1, r2, u1, u2, k)
        restricao_camisetas_frentes(model, W, r1, r2, x1, x2, p)
        restricao_camisetas_costas(model, W, r1, r2, y1, y2, q)
        restricao_camisetas_mangas(model, W, r1, r2, z1, z2, s)
        restricao_blocos_rolo1(model, r1, x1, y1, z1, u1, M)
        restricao_blocos_rolo2(model, r2, x2, y2, z2, u2, M)
        restricao_comprimento_rolo1(model, r1, x1, y1, z1, a, b, c, l)
        restricao_comprimento_rolo2(model, r2, x2, y2, z2, a, b, c, l)
        
        model.optimize()

        if model.status == GRB.OPTIMAL:
            W_val = W.X
            K_val = K.X
            resultados.append([r1 + r2, r1, r2, W_val, K_val])

    with open('output.txt', 'a') as file:
        file.write("\nTabela Cenario 2\n")
        file.write(f"{'Total de Rolos':<15}{'Tipo 1':<10}{'Tipo 2':<10}{'W (camisetas)':<20}{'K (custo)':<10}\n")
        for res in resultados:
            file.write(f"{res[0]:<15}{res[1]:<10}{res[2]:<10}{res[3]:<20}{res[4]:<10}\n")


def Cenario3(p,q,s,a,b,c,k,l):
    r1_values = [1,1,2,2,2,2,2,3]
    r2_values = [3,3,4,5,6,6,7,8]
    beta = 1
    alpha = 1000
    M = sys.maxsize  # (7)
    resultados=[]

    for r1, r2, v in zip(r1_values, r2_values,range(300,1001,100)):       
        model = gp.Model("otimizacao_camisas")

        u1 = model.addVars(r1, vtype=GRB.BINARY, name="u1")     
        u2 = model.addVars(r2, vtype=GRB.BINARY, name="u2")     
        x1 = model.addVars(r1, vtype=GRB.INTEGER, name="x1")    
        x2 = model.addVars(r2, vtype=GRB.INTEGER, name="x2")    
        y1 = model.addVars(r1, vtype=GRB.INTEGER, name="y1")    
        y2 = model.addVars(r2, vtype=GRB.INTEGER, name="y2")    
        z1 = model.addVars(r1, vtype=GRB.INTEGER, name="z1")    
        z2 = model.addVars(r2, vtype=GRB.INTEGER, name="z2")    
        W = model.addVar(vtype=GRB.INTEGER, name="W")           
        K = model.addVar(vtype=GRB.CONTINUOUS, name="K")        

        model.setObjective(alpha * K - beta * W, GRB.MINIMIZE)

        restricao_custo_total(model, K, r1, r2, u1, u2, k)
        restricao_camisetas_frentes(model, W, r1, r2, x1, x2, p)
        restricao_camisetas_costas(model, W, r1, r2, y1, y2, q)
        restricao_camisetas_mangas(model, W, r1, r2, z1, z2, s)
        restricao_blocos_rolo1(model, r1, x1, y1, z1, u1, M)
        model.addConstr(W >= v)
        restricao_blocos_rolo2(model, r2, x2, y2, z2, u2, M)
        restricao_comprimento_rolo1(model, r1, x1, y1, z1, a, b, c, l)
        restricao_comprimento_rolo2(model, r2, x2, y2, z2, a, b, c, l)
        model.optimize()

        if model.status == GRB.OPTIMAL:
            W_val = W.X
            K_val = K.X
            resultados.append([v, W_val, r1,r2, K_val])

    with open('output.txt', 'a') as file:
        file.write("\nTabela Cenario 3\n")
        file.write(f"{'Qtd mín de camisetas(v)':<25}{'Qtd possível de camisetas(W)':<30}{'Qtd rolos Tipo 1':<20}{'Qtd rolos Tipo 2':<20}{'Custo total (K)':<20}\n")
        for res in resultados:
            file.write(f"{res[0]:<25}{res[1]:<30}{res[2]:<20}{res[3]:<20}{res[4]:<20}\n")

def Cenario4(p,q,s,a,b,c,k,l):
    r1 = 0             
    r2 = 10             
    alpha = 1           
    beta = 1000         
    M = sys.maxsize     
    resultados=[]

    for r2 in range(1,11):        
        model = gp.Model("otimizacao_camisas")

        u1 = model.addVars(r1, vtype=GRB.BINARY, name="u1")     
        u2 = model.addVars(r2, vtype=GRB.BINARY, name="u2")     
        x1 = model.addVars(r1, vtype=GRB.INTEGER, name="x1")    
        x2 = model.addVars(r2, vtype=GRB.INTEGER, name="x2")    
        y1 = model.addVars(r1, vtype=GRB.INTEGER, name="y1")    
        y2 = model.addVars(r2, vtype=GRB.INTEGER, name="y2")    
        z1 = model.addVars(r1, vtype=GRB.INTEGER, name="z1")    
        z2 = model.addVars(r2, vtype=GRB.INTEGER, name="z2")    
        W = model.addVar(vtype=GRB.INTEGER, name="W")           
        K = model.addVar(vtype=GRB.CONTINUOUS, name="K")        

        model.setObjective(beta * W - alpha * K, GRB.MAXIMIZE)

        restricao_custo_total(model, K, r1, r2, u1, u2, k)
        restricao_camisetas_frentes(model, W, r1, r2, x1, x2, p)
        restricao_camisetas_costas(model, W, r1, r2, y1, y2, q)
        restricao_camisetas_mangas(model, W, r1, r2, z1, z2, s)
        restricao_blocos_rolo1(model, r1, x1, y1, z1, u1, M)
        restricao_blocos_rolo2(model, r2, x2, y2, z2, u2, M)
        restricao_comprimento_rolo1(model, r1, x1, y1, z1, a, b, c, l)
        restricao_comprimento_rolo2(model, r2, x2, y2, z2, a, b, c, l)
        model.optimize()

        if model.status == GRB.OPTIMAL:
            W_val = W.X
            K_val = K.X
            resultados.append([r1, r2, W_val, K_val])

    with open('output.txt', 'a') as file:
        file.write("\nTabela Cenario 4\n")
        file.write(f"{'Qtd rolos tipo 1':<20}{'Qtd rolos tipo 2':<25}{'Qtd camisetas(W)':<30}{'Custo total (K)':<35}\n")
        for res in resultados:
            file.write(f"{res[0]:<20}{res[1]:<25}{res[2]:<30}{res[3]:<35}\n")




if __name__ == "__main__":
    # Parâmetros comuns a todos os cenários
    p = [3, 4]           # Quantidade de frentes de cada bloco do rolo tipo i
    q = [3, 4]           # Quantidade de costas de cada bloco do rolo tipo i
    s = [2, 6]           # Quantidade de pares de mangas de cada bloco do rolo tipo i
    a = [0.76, 0.76]     # Comprimento de um bloco de frentes do rolo tipo i (em metros)
    b = [0.73, 0.73]     # Comprimento de um bloco de costas do rolo tipo i (em metros)
    c = [0.275, 0.6422]  # Comprimento de um bloco de mangas do rolo tipo i (em metros)
    k = [551, 556]       # Custo de um rolo do tipo i (em reais)
    l = [66.6, 50.4]     # Comprimento de um rolo do tipo i (em metros)
    Cenario1(p,q,s,a,b,c,k,l)
    Cenario2(p,q,s,a,b,c,k,l)
    Cenario3(p,q,s,a,b,c,k,l)
    Cenario4(p,q,s,a,b,c,k,l)
    print("DADOS FORAM REGISTRADO NO ARQUIVO 'output.txt' NESTE MESMO DIRETÓRIO")



'''
COMENTÁRIOS:
No artigo foram especificados dois modelos-:
MODELO 1 -> Formulação (1) até (11)                 MINIMIZAÇÃO DE CUSTO
MODELO 2 -> Formulação (2) até (5) e (7) até (12)   MAXIMIZAÇÃO DE PRODUÇÃO
Nos cenários 1 e 3 foi utilizado o MODELO 1.
Nos cenários 2 e 4 foi utilizado o MODELO 2.
As variaveis p,q,s,a,b,c,k,l presentes no "main" são comuns a todos os cenários.
No cenário 1 -> minimiza o custo na produção de uma demanda minima pre-estabelecida de camisetas, sendo essa demanda minima o 'v';
No cenário 2 -> maximiza  a  quantidade  decamisetas que podem ser produzidas com uma quantidade fixa de rolos;
No cenário 3 -> minimiza o custo na produção de uma demanda minima de camisetas considerando que determinadas partes das roupas 
(blocos) sejam associadas a determinados tamanhos de rolo, ou seja,fixa-se alguns xij,yij e zij iguais a zero, no caso x1j = y1j = 0 e z2j = 0 
( as mangas necessariamente são extraídas de rolos de 0, 9m e as frentes e costas são extraídas de rolos de 1, 2m );
No cenário 4 -> maximiza  a  quantidade  decamisetas considerando apenas rolos de largura 1,2m, ou seja, r1= 0 e r2>0.
'''
