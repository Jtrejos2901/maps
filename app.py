import dash
from dash import dcc, html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN

from adjustText import adjust_text

# Lectura de la información.
principal_data = pd.read_excel(r'C:\Users\svm12\Desktop\CAS\MyDashApp\src\casDataPais.xlsx', sheet_name=0)
location_data = pd.read_excel(r'C:\Users\svm12\Desktop\CAS\MyDashApp\src\casDataPais.xlsx', sheet_name=1)

# Kilometros por randiante.
kms_per_radian = 6371.0088

# Distancia máxima a considerar de 1000km convertida a radianes.
epsilon = 1000 / kms_per_radian

# Se extraen las coordenadas del dataframe inicial.
coords = location_data.iloc[:,[1,2]].values

# Se ejecuta el algoritmo DBSCAN.
db = DBSCAN(eps=epsilon, min_samples=1, algorithm='ball_tree', metric='haversine').fit(np.radians(coords))
cluster_labels = db.labels_
num_clusters = len(set(cluster_labels))

location_data['cluster'] = cluster_labels

# Se genera el nuevo DataFrame.
df_totales = principal_data.groupby('Loc ID', as_index=False)[['Suma Asegurada', 'Prima', 'Monto de siniestro']].sum()
df_medias = principal_data.groupby('Loc ID', as_index=False)[['Suma Asegurada', 'Prima', 'Monto de siniestro']].mean()

# Se agrega la información al DataFrame ya existente.
location_data_t = location_data.merge(df_totales[['Loc ID', 'Suma Asegurada', 
                                                'Prima', 'Monto de siniestro']], on='Loc ID', how='left')
location_data_m = location_data.merge(df_medias[['Loc ID', 'Suma Asegurada', 
                                                'Prima', 'Monto de siniestro']], on='Loc ID', how='left')

location_data_t = location_data_t.replace(np.nan, 0)
location_data_m = location_data_m.replace(np.nan, 0)


color_palette = [
    "#e41a1c",  # Rojo
    "#ff7f00",  # Naranja
    "#377eb8",  # Azul
    "#4daf4a",  # Verde
    "#984ea3",  # Púrpura
    "#a65628",  # Marrón
    "#f781bf",  # Rosa
    "#999999",  # Gris
    "#66c2a5",  # Verde claro
    "#fc8d62",  # Naranja claro
    "#8da0cb",  # Azul claro
    "#e78ac3",  # Rosa claro
    "#a6d854",  # Verde brillante
    "#ffd92f",  # Amarillo
    "#e5c494",  # Beige
    "#b3b3b3",  # Gris claro
    "#b2df8a",  # Verde menta
    "#33a02c",  # Verde esmeralda
    "#fb9a99",  # Rojo claro
    "#fdbf6f",  # Amarillo mostaza
    "#ff9999",  # Rosa suave
    "#cab2d6",  # Lavanda
    "#6a3d9a",  # Púrpura oscuro
    "#dfb635",  # Amarillo pálido
    "#ffcc99",  # Naranja pálido
    "#ffb3e6",  # Rosa pálido
    "#ffb3b3",  # Rojo claro
    "#c2c2f0"   # Azul pálido
]

# Inicializar la aplicación Dash
app = dash.Dash(__name__)

# Declare server for Heroku deployment. Needed for Procfile.
server = app.server
# Código de tus tres gráficos
# Gráfico 1
fig1 = px.scatter_mapbox(location_data_m,
                          lat="Latitud",
                          lon="Longitud",
                          hover_name="Pais",
                          hover_data={
                              'Loc ID': True,
                              'Ciudad': True,
                              'cluster': True,
                              'Suma Asegurada': True,
                              'Prima': True,
                              'Monto de siniestro': True
                          },
                          zoom=0)
cluster_colors1 = location_data['cluster'].map(dict(enumerate(color_palette)))
fig1.update_traces(marker=dict(color=cluster_colors1, size=8))
fig1.update_layout(mapbox_style="carto-positron")

for cluster_id in location_data_m['cluster'].unique():
    fig1.add_trace(go.Scattergeo(
        lat=[None],
        lon=[None],
        marker=dict(color=color_palette[cluster_id], size=10),
        name=f'Cluster {cluster_id}',
        showlegend=True
    ))
    
# Gráfico 3
fig3 = px.scatter_geo(location_data_m,
                       lat='Latitud',
                       lon='Longitud',
                       projection='orthographic',
                       opacity=0.8,
                       hover_name='Pais',
                       hover_data={
                           'Loc ID': True,
                           'Ciudad': True,
                           'cluster': True,
                           'Suma Asegurada': True,
                           'Prima': True,
                           'Monto de siniestro': True
                       })
cluster_colors3 = location_data['cluster'].map(dict(enumerate(color_palette)))
fig3.update_traces(marker=dict(color=cluster_colors3, size=10))

# Gráfico 2
fig2 = px.density_mapbox(location_data_m,
                          lat="Latitud",
                          lon="Longitud",
                          z='Suma Asegurada',
                          hover_name="Pais",
                          radius=40,
                          hover_data={
                              'Loc ID': True,
                              'Ciudad': True,
                              'cluster': True,
                              'Suma Asegurada': True,
                              'Prima': True,
                              'Monto de siniestro': True
                          },
                          zoom=0)
fig2.update_layout(mapbox_style="carto-positron")

for cluster_id in location_data['cluster'].unique():
    fig3.add_trace(go.Scattergeo(
        lat=[None],
        lon=[None],
        marker=dict(color=color_palette[cluster_id], size=10),
        name=f'Cluster {cluster_id}',
        showlegend=True
    ))

# Diseño de la aplicación
app.layout = html.Div(children=[
    html.H1(children='Dashboard de Mapas'),

    # Contenedor para los dos gráficos en la misma fila
    html.Div(className='row', children=[
        html.Div(children=[
            html.Div(children=''''''),
            dcc.Graph(id='map1', figure=fig1, style={'height': '500px'})  # Aumentar altura aquí
        ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'}),  # Alineación superior

        html.Div(children=[
            html.Div(children=''''''),
            dcc.Graph(id='map2', figure=fig2, style={'height': '500px'})  # Aumentar altura aquí
        ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'}),  # Alineación superior
    ], style={'display': 'flex', 'flex-direction': 'row'}),  # Flexbox para fila

    # Contenedor para el tercer gráfico
    html.Div(children=[
        html.Div(children=''''''),
        dcc.Graph(id='map3', figure=fig3, style={'height': '600px'})  # Aumentar altura aquí
    ], style={'width': '100%', 'display': 'block'}),
])

if __name__ == '__main__':
    app.run_server(debug=True)