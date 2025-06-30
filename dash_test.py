from dash import Dash, dcc, callback, Output, Input
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd

df = pd.read_excel('C:/Users/cln87/UTSA Files/CIS/SOS_Data/cleaned_clients.xlsx')

app = Dash(__name__, external_stylesheets=[dbc.themes.QUARTZ])
app.layout= dbc.Container(
    [
        dcc.Markdown('## **This is a test dashboard**'),
        
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            dcc.Graph(id='test-graph'),
                            dcc.Dropdown(id='age-drop',
                                         options=df['Age at Sign Up'].unique(),
                                         value=16)
                        ]),
                        className='my=3'
                    ),
                    width=6
                )
            ]
        )
    ]
)

@callback(
    Output('test-graph','figure'),
    Input('age-drop','value')
)
def pie_chart(age):
    age_chosen = int(age)
    age_df = df[df['Age at Sign Up']==age_chosen]
    pie = px.pie(age_df, names='District')
    return pie

if __name__ == '__main__':
    app.run(debug=True)