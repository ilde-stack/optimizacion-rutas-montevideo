import pandas as pd

# 1. Cargar los datos con detección de separador
try:
    df_contenedores = pd.read_csv('Contenedores_domiciliarios.csv', sep=';', encoding='utf-8', low_memory=False)
    if len(df_contenedores.columns) == 1:
        df_contenedores = pd.read_csv('Contenedores_domiciliarios.csv', sep=',', encoding='utf-8', low_memory=False)
        
    df_circuitos = pd.read_csv('Circuitos_recoleccion.csv', sep=';', encoding='utf-8', low_memory=False)
    if len(df_circuitos.columns) == 1:
        df_circuitos = pd.read_csv('Circuitos_recoleccion.csv', sep=',', encoding='utf-8', low_memory=False)

except FileNotFoundError:
    print("Error: Asegúrate de que los archivos CSV estén en la misma carpeta que este script.")
    exit()

# Limpieza estricta de nombres de columnas
df_contenedores.columns = df_contenedores.columns.str.strip().str.lower()
df_circuitos.columns = df_circuitos.columns.str.strip().str.lower()

# 2. Filtrar contenedores inactivos (Filtro Inteligente)
print("--- DIAGNÓSTICO DE DATOS ---")
if 'motivo' in df_contenedores.columns:
    # Mostramos los primeros 5 motivos para ver qué dice la IM realmente
    print("Muestra de datos en columna 'motivo':", df_contenedores['motivo'].unique()[:5])
    
    # Filtramos nulos o celdas que solo tengan espacios vacíos
    filtro_activos = df_contenedores['motivo'].isna() | df_contenedores['motivo'].astype(str).str.strip().eq('') | df_contenedores['motivo'].astype(str).str.lower().eq('nan')
    df_contenedores_activos = df_contenedores[filtro_activos].copy()
else:
    df_contenedores_activos = df_contenedores.copy()

# SALVAVIDAS: Si el filtro nos deja en 0, usamos todos para no romper el script
if len(df_contenedores_activos) == 0:
    print("\nAVISO: No se pudieron identificar los activos. Usando TODOS los contenedores temporalmente.")
    df_contenedores_activos = df_contenedores.copy()

print(f"\nTotal de contenedores a procesar: {len(df_contenedores_activos)}")
print("----------------------------\n")

# 3. Integración Total (Join)
df_completo = pd.merge(
    df_contenedores_activos, 
    df_circuitos[['cod_circuito', 'municipio']], 
    on='cod_circuito', 
    how='inner'
)

# Si después del cruce da 0, significa que los códigos de circuito no coinciden en los archivos
if len(df_completo) == 0:
    print("ERROR CRÍTICO: Ningún contenedor coincidió con los circuitos de recolección.")
    exit()

# 4. Asignación de la Demanda Real
df_completo['demanda_kg'] = 2.55

# 5. Partición Inteligente: Seleccionar el circuito de prueba
conteo_circuitos = df_completo['cod_circuito'].value_counts()
circuitos_viables = conteo_circuitos[(conteo_circuitos > 20) & (conteo_circuitos < 80)]

if not circuitos_viables.empty:
    circuito_elegido = circuitos_viables.index[0]
    cantidad_nodos = circuitos_viables.iloc[0]
else:
    circuito_elegido = conteo_circuitos.index[-1]
    cantidad_nodos = conteo_circuitos.iloc[-1]

print(f"Circuito seleccionado para el modelo base: '{circuito_elegido}' con {cantidad_nodos} contenedores.")

# Filtramos el dataset completo
df_toy_problem = df_completo[df_completo['cod_circuito'] == circuito_elegido]

# 6. Exportar los datos limpios para Gurobi
nombre_archivo_salida = f"Datos_Gurobi_Circuito_{circuito_elegido}.csv"
df_toy_problem.to_csv(nombre_archivo_salida, index=False, sep=';', encoding='utf-8-sig')

print(f"¡Éxito! Archivo exportado como: {nombre_archivo_salida}")