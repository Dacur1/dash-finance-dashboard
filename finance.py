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
load_dotenv()
key = os.getenv('ALPHA_VANTAGE_API_KEY')

# exit()
# -------------------------------------------------------------------------------------

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
                    src="/assets/goog.png",
                    top=True,
                    style={"width": "8rem"},
                    className='ml-3'
                ),

                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.P("CHANGE (1D)", className='ml-3')
                        ], width={'size': 5, 'offset': 1}),
                        dbc.Col([
                            dcc.Graph(
                                id='indicator-graph',
                                figure={},
                                config={'displayModeBar': False}
                            )
                        ], width={'size': 3, 'offset': 2})
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='daily-line', figure={},
                                      config={'displayModeBar': False})
                        ], width=12)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Button('SELL')
                        ], width=4),
                        dbc.Col([
                            dbc.Button('BUY')
                        ], width=4)
                    ], justify='between'),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label(
                                id='low-price',
                                children='12.237',
                                className='mt-2 ml-5 bg-white p-1 border border-primary border-top-0'
                            ),
                        ], width=4),
                        dbc.Col([
                            dbc.Label(
                                id='high-price',
                                children='13.418',
                                className="mt-2 bg-white p-1 border border-primary border-top-0"
                            ),
                        ], width=4)
                    ], justify='between')
                ]),
            ],
                style={'width': '24rem'},
                className='mt-3'
            )
        ],
            width=6)
    ], justify='center'),
    dcc.Store(id='intermediate-value'),
    # Api allows 500 requests per day rougly every 2,88 min (or 173 sec)
    dcc.Interval(id='update', n_intervals=0, interval=1000 * 173)
])


@app.callback(
    Output('intermediate-value', 'data'),
    Input('update', 'n_intervals')
)
# Calling API and formatting response
# Choose your output format or default to JSON (python dict)

def request_data(timer):
    ts = TimeSeries(key, output_format='pandas')  # 'pandas' or 'json' or 'csv'
    goog_data, goog_meta_data = ts.get_intraday(symbol='GOOG', interval='1min', outputsize='compact')
    df = goog_data.copy()
    df = df.transpose()
    df.rename(index={"1. open": "open", "2. high": "high", "3. low": "low",
                     "4. close": "close", "5. volume": "volume"}, inplace=True)
    df = df.reset_index().rename(columns={'index': 'indicator'})
    df = pd.melt(df, id_vars=['indicator'], var_name='date', value_name='rate')
    df = df[df['indicator'] != 'volume']
    print("API GOT CALLED!")

    return df.to_json("./data/data.json", index=False, orient='table')


# Indicator Graph -------------------------------------------------------------------------------------
@app.callback(
    Output('indicator-graph', 'figure'),
    Input('intermediate-value', 'data')
)
def update_graph(updated_json):
    # Read data from csv
    dff = pd.read_json("./data/data.json", orient='table')
    dff = dff[dff.indicator.isin(['high'])]

    # Clean data for usage
    dff_rv = dff.iloc[::-1]
    day_start = dff_rv[dff_rv['date'] == dff_rv['date'].min()]['rate'].values[0]
    day_end = dff_rv[dff_rv['date'] == dff_rv['date'].max()]['rate'].values[0]

    fig = go.Figure(go.Indicator(
        mode="delta",
        value=day_end,
        delta={'reference': day_start, 'relative': True, 'valueformat': '.2%'}))
    fig.update_traces(delta_font={'size': 12})
    fig.update_layout(height=30, width=70)

    if day_end >= day_start:
        fig.update_traces(delta_increasing_color='green')
    elif day_end < day_start:
        fig.update_traces(delta_decreasing_color='red')

    return fig


# Line Graph -------------------------------------------------------------------------------------
@app.callback(
    Output('daily-line', 'figure'),
    Input('intermediate-value', 'data')
)
def update_graph(updated_json):
    # Read data from csv
    dff = pd.read_json("./data/data.json", orient='table')
    dff = dff[dff.indicator.isin(['high'])]

    # Clean data for usage
    dff_rv = dff.iloc[::-1]
    fig = px.line(dff_rv, x='date', y='rate',
                  range_y=[dff_rv['rate'].min(), dff_rv['rate'].max()],
                  height=120).update_layout(margin=dict(t=0, r=0, l=0, b=20),
                                            paper_bgcolor='rgba(0,0,0,0)',
                                            plot_bgcolor='rgba(0,0,0,0)',
                                            yaxis=dict(
                                                title=None,
                                                showgrid=False,
                                                showticklabels=False
                                            ),
                                            xaxis=dict(
                                                title=None,
                                                showgrid=False,
                                                showticklabels=False
                                            ))

    day_start = dff_rv[dff_rv['date'] == dff_rv['date'].min()]['rate'].values[0]
    day_end = dff_rv[dff_rv['date'] == dff_rv['date'].max()]['rate'].values[0]

    if day_end >= day_start:
        return fig.update_traces(fill='tozeroy', line={'color': 'green'})
    elif day_end < day_start:
        return fig.update_traces(fill='tozeroy',
                                 line={'color': 'red'})


# Below the buttons ------------------------------------------------------------------------------
@app.callback(
    Output('high-price', 'children'),
    Output('high-price', 'className'),
    Input('intermediate-value', 'data')
)
def update_graph(updated_json):
    # Read data from csv
    dff = pd.read_json("./data/data.json", orient='table')
    dff = dff[dff.indicator.isin(['high'])]

    # Clean data for usage
    dff['date'] = pd.to_datetime(dff['date'])
    two_recent_times = dff['date'].nlargest(2)
    df = dff[dff['date'].isin(two_recent_times.values)]
    recent_high = df['rate'].iloc[0]
    older_high = df['rate'].iloc[1]

    if recent_high > older_high:
        return recent_high, "mt-2 bg-success text-white p-1 border border-primary border-top-0"
    elif recent_high == older_high:
        return recent_high, "mt-2 bg-white p-1 border border-primary border-top-0"
    elif recent_high < older_high:
        return recent_high, "mt-2 bg-danger text-white p-1 border border-primary border-top-0"


if __name__ == '__main__':
    app.run_server(debug=True, port=3000)
