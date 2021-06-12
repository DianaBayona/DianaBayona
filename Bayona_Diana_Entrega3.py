import numpy as np
import pandas as pd
import plotly.express as px
from dash import Dash
import json
from urllib.request import urlopen
import dash
import dash_core_components as dcc
import dash_html_components as html

with urlopen('https://gist.githubusercontent.com/john-guerra/43c7656821069d00dcbc/raw/be6a6e239cd5b5b803c6e7c2ec405b793a9064dd/Colombia.geo.json') as response: 
	departamentos = json.load(response)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df_colocaciones = pd.read_csv('Colocaciones_de_cr_dito_Sector_Agropecuario_2020.csv', 
                 sep = ',', thousands=',', decimal='.', dtype={"ID Depto": str})
df_colocaciones['ID Depto'] = df_colocaciones['ID Depto'] .replace(['5','8'],['05','08'])

lan_lon = pd.read_csv('col-adm1-departments.csv', 
                 sep = ',', thousands=',', decimal='.', dtype={"id": str})

df = df_colocaciones.merge(lan_lon, 
                             left_on='ID Depto', 
                             right_on='id', 
                             how = 'left')

lp=["ACTIVIDADES RURALES (CT)","ACTIVIDADES RURALES (I)",  "COMERCIALIZACION (CT)" ,      
  "COMERCIALIZACION (I)" ,    "COMPRA DE ANIMALES (I)" ,  "CONSOLIDACION DE PASIVOS (N)",   
  "INFRAEST Y ADECU DE TIERRAS (I)", "MAQUINARIA Y EQUIPO (I)", "MICROCREDITO (CT)",             
  "OTRAS ACTIVIDADES (I)", "PRODUCCIÓN (CT)", "SERVICIOS DE APOYO (CT)",        
  "SERVICIOS DE APOYO (I)", "SIEMBRAS (I)", "SOSTENIMIENTO (CT)"]
b=df[~df['Linea de Produccion'].isin(lp)]
b['Linea de Produccion']="SERVICIOS DE APOYO (I)"
c=df[df['Linea de Produccion'].isin(lp)]
df0=pd.concat([b, c])

columns = ["Año",
           "Mes",
           "fuente Colocacion",
           "Id Tipo Prod" ,
           "Tipo Productor" ,
           "Valor Inversion",
           "Colocacion" ,
           "ID Depto" ,
           "Departamento Inversion",
           "Id Munic" ,
           "Municipio Inversion",
           "Municipio de PostConflico?" ,
           "DEPCOL",
           "Departamento de Colocacion de Credito",
           "MUNCOL",
           "Municipio Colocacion de Credito",
           "Plazo",
           "Linea de Credito" ,
           "Linea de Produccion",
           "ID Rubro",
           "Destino de Credito" ,
           "Genero",
           "LATITUD",
           "LONGITUD",
           "CANTIDAD",
           "Coordenada",
           "lon",
           "lat"
          ]
df2 = df0.copy()
df2 = df0[columns]

df_dedupped = df2.drop_duplicates()

Amazonia=["AMAZONAS","CAQUETA",  "GUAVIARE","GUAINIA", "PUTUMAYO", "VAUPES"]
Andina= ["ANTIOQUIA", "BOYACA", "CALDAS", "CESAR", "CUNDINAMARCA", "HUILA", 
         "NORTE DE SANTANDER", "QUINDIO", "RISARALDA", "SANTANDER", "TOLIMA"]
Caribe=["SUCRE", "ATLANTICO", "BOLIVAR", "CESAR", "CORDOBA", "LA GUAJIRA", "MAGDALENA"]
Insular=["SAN ANDRES"]
Orinoquia=["ARAUCA", "CASANARE", "META", "VICHADA"]
Pacifico=["CHOCO", "CAUCA", "NARIÑO"]

df_dedupped['Region'] = np.where(df_dedupped['Departamento Inversion'].isin(Amazonia), 'Amazonia', 
                                np.where(df_dedupped['Departamento Inversion'].isin(Andina), 'Andina',
                                        np.where(df_dedupped['Departamento Inversion'].isin(Caribe), 'Caribe',
                                                np.where(df_dedupped['Departamento Inversion'].isin(Insular), 'Insular',
                                                        np.where(df_dedupped['Departamento Inversion'].isin(Orinoquia), 'Orinoquia', 'Pacifico')))))


available_lineacredito = df_dedupped['Linea de Credito'].unique()
available_tipo_productor = df_dedupped['Tipo Productor'].unique()
available_lineacredito2 = df_dedupped['Linea de Credito'].unique()


app.layout = html.Div(
    children=[
        html.H1(children="Proyecto final - Colocaciones de crédito sector agropecuario",
            style = {
                        'textAlign': 'center',
            }),
        html.H2(children="Extracción y limpieza de datos"),
        html.P(
            children="La base de datos fue descargada de Datos Abiertos y presenta las operaciones de crédito colocadas en el sector agropecuario colombiano 2020, los datos fueron siniestrados por el Fondo para el Financiamiento del Sector Agropecuario (FINAGRO) y estos fueron actualizados el 11 de febrero de 2021."
            "La base esta conformada por 513235 filas y 28 columnas."
            "Con respecto a la limpieza de datos, Se identifica que hay una categoría repetida SERVICIOS DE APOYO (I) y SERVICIOS DE APOYO (I), " 
            "por lo cual se busca dejar una sola categoría debido a que las dos se refieren a lo mismo y la diferencia consiste en un espacio adicional. "
            "Adicionalmente, las variables  FAG y Vlr Inic Garantia tienen un porcentaje de 46.07 de datos faltantes, esta variable representa el Fondo Agropecuario de Garantias la cual indica el valor del fondo con el que se busca respaldar los créditos concedidos por Finagro. Se decide eliminar estas variables debido a que son cuantitativas y no se puede clasificar en la categoría perdido, así mismo su alto porcentaje de datos faltantes hace que la imputación no sea una vía adecuada. Al igual se eliminan las variables id y name debido a que ya están replicadas como ID Depto y Departamento Inversion."
            "Finalmente se eliminan 24769 datos duplicados y se identifica que todos los registros correponden al año 2020, así mismo no hay valores de créditos ni de inversión negativos. No hay problemas de digitación con los departamentos, meses, tipo de productor y las líneas de crédito. Por lo cual a primera instancia los datos son consistentes, no se evidencian datos nulos y cada variable presenta items dentro de las categorías"
            ),

###Grafico 1

    html.Div([
        html.Div([
            html.H1(children='Gráfico 1'),
            html.P(children=" El siguiente gráfico tiene como objetivo mostrar la cantidad de colocaciones de crédito agropecuario que se otorgaron por las regiones de Colombia considerando la línea de crédito y el tipo de productor"), #
            html.P(children= "Los datos que se tienen son de tipo tabla ya que está cuenta con 4 atributos, 3 categóricos: Línea de crédito, región y tipo de productor y atributo cuantitativo ordenado secuencial que indica la cantidad de colocaciones de crédito que se realizaron. "), 
            html.P(children= "En sus acciones la visualización analiza y presenta ya que el propósito es mostrar las colocaciones de créditos por línea de crédito, tipo de productor y región. Así mismo, el gráfico consulta y compara como acción ya que a partir de este se puede comparar la cantidad de colocaciones de crédito por cada una de las regiones de Colombia. El objetivo es distribución dado que por medio del gráfico se pueden identificar las características de los datos y como se distribuyen estos según su cantidad de colocaciones por tipo de productor y línea de crédito"),
          
            html.Div(children='''
                
                Linea de credito
            
            '''),#
            dcc.Dropdown(
                id='crossfilter_lineacred1',
                 options=[{'label': x, 'value': x} 
                            for x in available_lineacredito],
                value = ['Inversión','Normalización de Cartera'],
                multi = True
                ),
            html.Div(children='''
                
                Tipo productor
            
            '''),#
            dcc.RadioItems(
                id='crossfilter_prod1',
                 options=[{'label': x, 'value': x} 
                            for x in available_tipo_productor],
                value = 'GRANDE',
                labelStyle={'display': 'inline-block'}
                ),
            dcc.Graph(
                id='example-graph-1'
            ),  
        ], className='six columns'),

###Grafico 2
        html.Div([
            html.H1(children='Gráfico 2'),
            html.P(children="El segundo gráfico busca mostrar la cantidad de colocaciones de crédito agropecuario que se otorgaron por departamentos considerando la línea de crédito y el tipo de productor"),#
            html.P(children= "Los datos que se tienen son tabla de tipo geométrica - Geometría geográfica, para este caso la tabla presenta 4 atributos que representan la posición: Latitud, longitud, departamento, Id Depto. Adicional a estos atributos de posición, hay dos atributos categóricos línea de crédito y tipo de productor, y un atributo cuantitativo que muestra la cantidad de colocaciones de créditos agropecuarios por línea de crédito, tipo de productor y departamento"),
            html.P(children= "En en sus acciones la visualización Analiza y presenta ya que a partir de esta se pueden visualizar los departamentos de Colombia con mayor cantidad de colocaciones de crédito, al igual que realizar la comparación de colocaciones en los departamentos por las líneas de crédito y por tipo de productor. Así mismo, el gráfico identifica ubicaciones ya que se puede identificar los departamentos de Colombia con menor y mayor cantidad de colocaciones. Con respecto al objetivo, este es Distribuciones geográficas dado que los datos son de geometría geográfica por lo cual el objetivo es identificar los departamentos según la cantidad de colocaciones, tipo productor y linea de crédito"),

            html.Div(children='''
                
                Linea de credito
            
            '''),#
            dcc.Dropdown(
                id='crossfilter_lineacred2',
                 options=[{'label': x, 'value': x} 
                            for x in available_lineacredito2],
                value = ['Inversión', 'Normalización de Cartera'],
                multi = True
                ),
            dcc.Graph(
                id='example-graph-2'
            ),  
        ], className='six columns'),#
    ], className='row'),#

		

])

@app.callback(
    dash.dependencies.Output('example-graph-1', 'figure'),
    [dash.dependencies.Input('crossfilter_lineacred1', 'value'),
     dash.dependencies.Input('crossfilter_prod1', 'value')]
    )

    
def update_graph(tipo_lineacred_value, tipo_prod_value):

    query1 = df_dedupped[df_dedupped['Linea de Credito'].isin(tipo_lineacred_value)]
    query1 = query1[query1['Tipo Productor'] == tipo_prod_value]
    
    query1 = pd.pivot_table(query1, 
                        values='CANTIDAD', 
                        index=['Linea de Credito', 'Tipo Productor', 'Region'],
                        aggfunc=np.sum)
    query1 = query1.reset_index().rename_axis(None, axis=1)
    query1 = query1.sort_values(by=['CANTIDAD'],ascending=False)

    fig1 = px.bar(query1, x='CANTIDAD', y='Region', color = 'Linea de Credito' )

  
    return fig1

@app.callback(
    dash.dependencies.Output('example-graph-2', 'figure'),
    [dash.dependencies.Input('crossfilter_lineacred2', 'value')]
    )


def update_graph(tipo_lineacred_value):

    query2 = df_dedupped[df_dedupped['Linea de Credito'].isin(tipo_lineacred_value)]
        
    query2 = pd.pivot_table(query2, 
                        values='CANTIDAD', 
                        index=['ID Depto', 'Departamento Inversion', 'lat', 'lon', 'Tipo Productor'],
                        aggfunc=np.sum)
    query2 = query2.reset_index().rename_axis(None, axis=1)
   

    fig2 = px.choropleth_mapbox(query2, geojson=departamentos, featureidkey='properties.DPTO', locations='ID Depto', 
                        color="CANTIDAD", center = {"lat": 4.570868, "lon": -74.297333}, animation_frame="Tipo Productor", color_continuous_scale=["yellow", "gray", "green"], zoom=3.5, mapbox_style="carto-positron",
                        opacity=0.5)
    fig2.update_layout(mapbox_style="open-street-map",
                  showlegend=False,
                  margin={"r":0,"t":0,"l":0,"b":0}, 
                  width=600, 
                  height=500
                  )


  
    return fig2
	  
if __name__ == "__main__":
    app.run_server(debug=True)