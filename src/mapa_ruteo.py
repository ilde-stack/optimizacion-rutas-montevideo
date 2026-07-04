import pandas as pd
import folium
from pyproj import Transformer
import requests

# 1. Recrear el DataFrame de 15 nodos
archivo_circuito = "Datos_Gurobi_Circuito_A_DU_RM_CL_110      .csv"
df_nodos = pd.read_csv(archivo_circuito, sep=';', encoding='utf-8-sig')

X_USINA = 586233  
Y_USINA = 6141972

nodo_deposito = pd.DataFrame([{'gid': 0, 'cod_circuito': 'DEPOSITO', 'x': X_USINA, 'y': Y_USINA, 'demanda_kg': 0.0}])
df_vrp = pd.concat([nodo_deposito, df_nodos], ignore_index=True).head(15)

# 2. La ruta exacta de Gurobi
ruta_optima = [0, 7, 12, 9, 14, 4, 3, 1, 6, 8, 10, 13, 2, 11, 5, 0]

# 3. Conversión de coordenadas (UTM 21S a Lat/Lon)
transformer = Transformer.from_crs("epsg:32721", "epsg:4326")

coordenadas_ruta = []
for nodo in ruta_optima:
    x_utm = df_vrp.loc[nodo, 'x']
    y_utm = df_vrp.loc[nodo, 'y']
    lat, lon = transformer.transform(x_utm, y_utm)
    coordenadas_ruta.append((lat, lon))

# ==========================================
# 4. CONEXIÓN CON OSRM PARA RUTEO POR CALLES
# ==========================================
# OSRM pide las coordenadas en formato "longitud,latitud" separadas por punto y coma
coordenadas_osrm = ";".join([f"{lon},{lat}" for lat, lon in coordenadas_ruta])

# Armamos la URL de la API pidiendo la geometría completa (overview=full)
url_osrm = f"http://router.project-osrm.org/route/v1/driving/{coordenadas_osrm}?overview=full&geometries=geojson"

print("Calculando el trazado por las calles de Montevideo...")
respuesta = requests.get(url_osrm).json()

# Extraemos la lista de puntos que forman la ruta por las calles
# OSRM devuelve [lon, lat], pero Folium usa [lat, lon], así que los invertimos
geometria_calles = respuesta['routes'][0]['geometry']['coordinates']
ruta_folium = [[lat, lon] for lon, lat in geometria_calles]

# ==========================================
# 5. DIBUJAR EL MAPA
# ==========================================
mapa = folium.Map(location=coordenadas_ruta[0], zoom_start=14, tiles="CartoDB positron")

# Dibujamos la línea siguiendo exactamente las calles
folium.PolyLine(
    locations=ruta_folium,
    color='#0078D7', # Un azul más profesional
    weight=5,
    opacity=0.8,
    tooltip="Ruta óptima del Camión"
).add_to(mapa)

# Agregar marcadores para los contenedores y la Usina
for i, (lat, lon) in enumerate(coordenadas_ruta[:-1]):
    if ruta_optima[i] == 0:
        folium.Marker(
            [lat, lon], popup="<b>USINA FELIPE CARDOSO</b><br>Inicio y Fin de Ruta", 
            icon=folium.Icon(color="red", icon="home")
        ).add_to(mapa)
    else:
        # Mostramos qué número de contenedor es y en qué orden se visita
        folium.Marker(
            [lat, lon], 
            popup=f"<b>Contenedor N° {ruta_optima[i]}</b><br>Orden de visita: {i}",
            icon=folium.Icon(color="green", icon="trash", prefix='fa')
        ).add_to(mapa)

# 6. Guardar el mapa
archivo_mapa = "mapa_ruta_montevideo_calles.html"
mapa.save(archivo_mapa)
print(f"¡Mapa listo! Abrí '{archivo_mapa}' para ver el resultado.")