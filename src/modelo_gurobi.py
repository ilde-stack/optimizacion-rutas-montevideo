import pandas as pd
import math
import gurobipy as gp
from gurobipy import GRB

# ==========================================
# 1. CARGA Y PREPARACIÓN DE DATOS (COMPLETOS)
# ==========================================
archivo_circuito = "Datos_Gurobi_Circuito_A_DU_RM_CL_110      .csv"

try:
    df_nodos = pd.read_csv(archivo_circuito, sep=';', encoding='utf-8-sig')
except FileNotFoundError:
    print(f"Error: No se encontró el archivo '{archivo_circuito}'. Revisa el nombre.")
    exit()

# Definir e insertar el Nodo 0 (Usina Felipe Cardoso)
X_USINA = 586233  
Y_USINA = 6141972

nodo_deposito = pd.DataFrame([{
    'gid': 0,
    'cod_circuito': 'DEPOSITO',
    'x': X_USINA,
    'y': Y_USINA,
    'demanda_kg': 0.0 
}])

# Unir el depósito con TODOS los contenedores del circuito
df_vrp = pd.concat([nodo_deposito, df_nodos], ignore_index=True)

# ==========================================
# 2. PARÁMETROS DEL MODELO MATEMÁTICO
# ==========================================
nodos = list(df_vrp.index)
clientes = nodos[1:] # Del 1 al 79 son los contenedores

coordenadas = {i: (df_vrp.loc[i, 'x'], df_vrp.loc[i, 'y']) for i in nodos}
demandas = {i: df_vrp.loc[i, 'demanda_kg'] for i in nodos}

# Capacidad del camión recolector
Q = 8000 

# Calcular matriz de distancias (Distancia Euclidiana)
distancias = {}
for i in nodos:
    for j in nodos:
        if i != j:
            dx = coordenadas[i][0] - coordenadas[j][0]
            dy = coordenadas[i][1] - coordenadas[j][1]
            distancias[i, j] = math.sqrt(dx**2 + dy**2)

# ==========================================
# 3. CREACIÓN DEL MODELO EN GUROBI
# ==========================================
modelo = gp.Model("Ruteo_Completo_Contenedores")

# Ocultar el texto excesivo de la consola de Gurobi (opcional)
modelo.setParam('OutputFlag', 1) 

# Variables de ruteo (x4): 1 si viaja de i a j, 0 en caso contrario
x4 = modelo.addVars(distancias.keys(), vtype=GRB.BINARY, name="x4")

# Variables de capacidad (x5): Carga acumulada al visitar el nodo i (MTZ)
x5 = modelo.addVars(clientes, vtype=GRB.CONTINUOUS, lb=0, name="x5")

# Función Objetivo: Minimizar la distancia total recorrida
modelo.setObjective(gp.quicksum(distancias[i, j] * x4[i, j] for i, j in distancias.keys()), GRB.MINIMIZE)

# Restricción 1: Entrar a cada contenedor exactamente 1 vez
modelo.addConstrs((gp.quicksum(x4[i, j] for i in nodos if i != j) == 1 for j in clientes), name="Entrada")

# Restricción 2: Salir de cada contenedor exactamente 1 vez
modelo.addConstrs((gp.quicksum(x4[i, j] for j in nodos if j != i) == 1 for i in clientes), name="Salida")

# Restricción 3: Eliminación de subtours y control de capacidad (MTZ)
for i in clientes:
    for j in clientes:
        if i != j:
            modelo.addConstr(
                x5[i] + demandas[j] <= x5[j] + Q * (1 - x4[i, j]),
                name=f"MTZ_{i}_{j}"
            )

# Límite de carga: x5 no puede exceder Q ni ser menor a su propia demanda
modelo.addConstrs((x5[i] >= demandas[i] for i in clientes), name="CargaMinima")
modelo.addConstrs((x5[i] <= Q for i in clientes), name="CargaMaxima")

# Configuración del solver: 10 MINUTOS EXACTOS
modelo.setParam('TimeLimit', 600) 

print(f"\nIniciando optimización con Gurobi para {len(nodos)} nodos totales...")
print("Esto tomará exactamente 10 minutos. Podés ir a prepararte un mate...\n")
modelo.optimize()

# ==========================================
# 4. EXTRACCIÓN Y VISUALIZACIÓN DE RESULTADOS
# ==========================================
if modelo.Status == GRB.OPTIMAL or modelo.Status == GRB.TIME_LIMIT:
    print("\n" + "="*50)
    print("¡Ruta Óptima (o mejor encontrada) finalizada!")
    print(f"Distancia Total Recorrida: {modelo.ObjVal:.2f} unidades")
    print("="*50)
    
    # Reconstruir la ruta siguiendo las variables x4 que tomaron valor 1
    ruta = [0]
    nodo_actual = 0
    while True:
        # Buscar el siguiente nodo donde x4_i_j sea > 0.5
        siguientes = [j for j in nodos if j != nodo_actual and x4[nodo_actual, j].x > 0.5]
        
        if not siguientes:
            break 
            
        siguiente = siguientes[0]
        ruta.append(siguiente)
        nodo_actual = siguiente
        if nodo_actual == 0:
            break
            
    print(f"\nSecuencia del Camión (Nodos):\n{ruta}")
    print(f"\nEl camión inicia en el Nodo 0 (Usina), visita {len(ruta)-2} contenedores y retorna a la Usina.")
else:
    print("\nEl modelo no pudo encontrar una solución factible.")