# Optimización del Sistema de Recolección de Residuos en Montevideo mediante CVRP (Gurobi & Python)

Este proyecto desarrolla e implementa un modelo de optimización a gran escala para el diseño de rutas eficientes de recolección de residuos domiciliarios en Montevideo, Uruguay, utilizando herramientas de Investigación Operativa. A partir de datos georreferenciados reales del Portal de Datos Abiertos de la Intendencia de Montevideo (IM), el problema se formuló como un Problema de Ruteo de Vehículos Capacitado (CVRP) con restricciones temporales de turno, resolviéndose de manera exacta mediante el optimizador matemático Gurobi y proyectándose sobre la infraestructura vial real mediante OSRM y Folium.

## Características Técnicas
* **Pipeline de Datos (ETL):** Procesamiento, diagnóstico y filtrado inteligente de contenedores activos e integración de geodatasets sectorizados por circuitos mediante Python (Pandas).
* **Modelado Matemático (Investigación Operativa):** Formulación de programación lineal entera mixta (MILP) incorporando restricciones de flujo, límites de capacidad física del vehículo ($Q = 8000\text{ kg}$) y eliminación de subtours mediante formulación de Miller-Tucker-Zemlin (MTZ).
* **Restricción Temporal Estricta:** Incorporación de tiempos fijos de servicio por contenedor y estimación precisa de tiempos de viaje basados en distancias de red real.
* **Integración de APIs y Sistemas Geográficos:** Uso de la API de OSRM (*Open Source Routing Machine*) para el cálculo de distancias por calles reales (respetando sentidos de circulación y giros permitidos) y proyección cartográfica interactiva mediante Folium.

## Resultados Computacionales Destacados
* **Convergencia Exacta:** El solver Gurobi resolvió el escenario base (circuito piloto de 79 contenedores y 1,109 restricciones) alcanzando un **Gap de optimización del 0.0000%** en solo 20.11 segundos, explorando más de 52,000 nodos de Branch-and-Bound.
* **Eficiencia Operativa:** La ruta óptima totalizó una distancia recorrida de **48.80 km** con una duración estimada de **235.63 minutos**, permitiendo completar el circuito utilizando únicamente el **49.1%** del turno de trabajo matutino disponible y validando la viabilidad operativa con un camión único.
* **Robustez del Modelo:** Los análisis de sensibilidad evidenciaron que el sistema mantiene la factibilidad operativa total ante caídas severas de velocidad por tráfico (hasta $15\text{ km/h}$) o incrementos críticos en los tiempos de servicio en contenedor (hasta 4.0 minutos).

## Requisitos y Ejecución

### Prerrequisitos
* Python 3.9 o superior.
* Licencia activa y software instalado de **Gurobi Optimizer**.
* Conectividad a internet para consultas externas de la API de OSRM.

### Pipeline de Ejecución
1. **Preparación e integración de datos base de la IM:**
   ```bash
   python src/gse.py
   ```
2. **Ejecución del modelo matemático de optimización con Gurobi:**
   ```bash
   python src/modelo_gurobi.py
   ```
3. **Generación del mapeo geográfico y trazado por calles:**
   ```bash
   python src/mapa_ruteo.py
   ```

## Estructura del Proyecto

```text
optimizacion-rutas-montevideo/
├── src/
│   ├── gse.py             # Script de parsing, limpieza y merge de datos de la IM
│   ├── modelo_gurobi.py   # Formulación del VRP, variables binarias y llamada al solver
│   └── mapa_ruteo.py      # Transformación UTM a Lat/Lon, consultas OSRM y renderizado Folium
├── docs/
│   └── Informe.pdf        # Documento académico con la formulación formal y análisis de sensibilidad
├── .gitignore             # Exclusión de archivos de soluciones locales y datasets masivos
└── README.md              # Portada técnica del repositorio
```
