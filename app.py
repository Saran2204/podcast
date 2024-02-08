import dash
from dash import dcc, html
from flask import Flask
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Intialize the app
server = Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP])

# Read the files
df = pd.read_csv('book1.csv')

# Bulid the components
header = html.H1("Podcast Analytics Dashboard", style={'color': 'darkcyan','text-align': 'center'})
Overview = html.H3("Overview",style={'color': 'red'})
total_downloads = df.groupby('episode_id')['downloads'].sum().reset_index()
fig = px.line(total_downloads, x='episode_id', y='downloads', title='Total Number of Downloads by Episode',
              labels={'downloads': 'Total Downloads', 'episode_id': 'Episode ID'})

episode_downloads = df.groupby('episode_id')['downloads'].sum().reset_index()

# Sort by downloads in descending order to get top episodes
top_episodes = episode_downloads.sort_values(by='downloads', ascending=False).head(10)

# Create a bar plot using Plotly Express
fig2 = px.bar(top_episodes, x='episode_id', y='downloads', title='Top 10 Most Downloaded Episodes',
              labels={'downloads': 'Total Downloads', 'episode_id': 'Episode ID'})

df['action_date'] = pd.to_datetime(df['action_date'], format='%d-%m-%Y')

data = pd.read_csv('book1.csv')

df1 = pd.DataFrame(data)

# Drop rows with missing values in the listeners column
df1 = df.dropna(subset=['listeners'])

overall_downloads = df['downloads'].sum()

# Design the app layout
app.layout = html.Div([
    header,
    html.Br(),
    Overview,
    html.Br(),
        dbc.Row([dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H4("Overall downloads", className="card-title"),
                    html.P(id="overall-downloads", className="card-text")]),
                style={'backgroundColor': '#3498db'}  # Blue color
            )
            
            ),
            dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H4("last 7 days downloads", className="card-title"),
                    html.P(id="last-7-days-downloads", className="card-text")]),
                style={'backgroundColor': '#e74c3c'}  # Red color
            )),
            dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H4("last 30 days downloads", className="card-title"),
                    html.P(id="last-30-days-downloads", className="card-text")])
                ,style={'backgroundColor': '#2ecc71'}  # Green color
            ))
    ]),
    dbc.Row([
        dbc.Col([dcc.Graph(figure=fig)]),
        dbc.Col([dcc.Graph(figure=fig2)])
    ]),
    dbc.Row([
        dbc.Col(dcc.DatePickerRange(
            id='date-picker-range',
            start_date=df['action_date'].min(),
            end_date=df['action_date'].max(),
            display_format='DD-MM-YYYY',
    )),
        dcc.Graph(id='daily-listeners-plot', style={'height': '75vh'}),

        dbc.Col(dcc.Graph(
                    figure=px.scatter_geo(
                    df,
                    locations='country',
                    locationmode='country names',
                    size='listeners',  # Size of the marker based on listener counts
                    color='listeners',  # Color of the marker based on listener counts
                    hover_name='country',  # Display country/region names on hover
                    projection='equirectangular',  # Choose the map projection
                    title='Geographical Distribution of Listeners',
                ),
                style={'height': '75vh'}
            )
        )      
]),
])
# Define callback to update the plot based on date picker selection
@app.callback(
    Output('daily-listeners-plot', 'figure'),
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_plot(start_date, end_date):
    filtered_df = df[(df['action_date'] >= start_date) & (df['action_date'] <= end_date)]
    daily_listeners = filtered_df.groupby('action_date')['listeners'].sum().reset_index()
    fig = px.bar(daily_listeners, x='action_date', y='listeners', title='Daily Listeners Count',
                 labels={'listeners': 'Daily Listeners Count', 'action_date': 'Date'})
    return fig

#overall downloads
@app.callback(
    Output('overall-downloads', 'children'),
    [Input('overall-downloads', 'children')]
)
def update_overall_downloads(overall_downloads):
    overall_downloads = df['downloads'].sum()
    return f"{overall_downloads} Downloads"
#last 7 days downloads
@app.callback(
    Output('last-7-days-downloads', 'children'),
    [Input('last-7-days-downloads', 'children')]
)
def update_last_7_days_downloads(overall_downloads):
    last_7_days_downloads = df['downloads'].tail(7).sum()
    return f"{last_7_days_downloads} Downloads"
#last 30 days downloads
@app.callback(
    Output('last-30-days-downloads', 'children'),
    [Input('last-30-days-downloads', 'children')]
)
def update_last_30_days_downloads(overall_downloads):
    last_30_days_downloads = df['downloads'].tail(30).sum()
    return f"{last_30_days_downloads} Downloads"

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
