import os
import dash  # pip install dash
from dash import dcc
from dash import html
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc  # pip install dash-bootstrap-components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from alpha_vantage.timeseries import TimeSeries  # pip install alpha-vantage
from dotenv import load_dotenv

# -------------------------------------------------------------------------------------
# # Set up Alpha Vantage Key and financial category
# load_dotenv()
# key = os.getenv('ALPHA_VANTAGE_API_KEY')
#
# # Calling API and formatting response
# # Choose your output format or default to JSON (python dict)
# ts = TimeSeries(key, output_format='pandas') # 'pandas' or 'json' or 'csv'
# ttm_data, ttm_meta_data = ts.get_intraday(symbol='GOOG',interval='1min', outputsize='compact')
# df = ttm_data.copy()
# df=df.transpose()
# df.rename(index={"1. open":"open", "2. high":"high", "3. low":"low",
#                  "4. close":"close","5. volume":"volume"},inplace=True)
# df=df.reset_index().rename(columns={'index': 'indicator'})
# df = pd.melt(df,id_vars=['indicator'],var_name='date',value_name='rate')
# df = df[df['indicator']!='volume']
#
# # print(df.head(10))
#
# df.to_csv("./data/data.csv", index=False)
# exit()
# -------------------------------------------------------------------------------------
# Read data from csv
dff = pd.read_csv("./data/data.csv")
dff = dff[dff.indicator.isin(['high'])]

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
                meta_tags=[{
                    'name': 'viewport',
                    'content': 'width=device-width, initial-scale=1.0'
                }])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardImg(
                    src="/assets/goog.png"
                ),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([

                        ]),
                        dbc.Col([

                        ])
                    ]),
                    dbc.Row([
                        dbc.Col([

                        ])
                    ]),
                    dbc.Row([
                        dbc.Col([

                        ]),
                        dbc.Col([

                        ])
                    ]),
                    dbc.Row([
                        dbc.Col([

                        ]),
                        dbc.Col([

                        ])
                    ])
                ])
            ])
        ])
    ])
])