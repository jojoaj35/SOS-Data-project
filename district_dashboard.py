import pandas as pd 
import geopandas as gpd 
import plotly.express as px
import json
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

# Initialize Dash app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

def create_district_map():
    """Create the district heat map figure"""
    # Read data
    clients_data = pd.read_csv('cleaned_clients.csv')
    district_counts = clients_data['District'].value_counts().reset_index()
    district_counts.columns = ['District_Name', 'Client_Count']
    district_shapes = gpd.read_file('School_Districts_2025_.geojson')

    # District mapping
    district_mapping = {
        'NISD': 'Northside ISD (Bexar)',
        'NEISD': 'North East ISD',
        'SAISD': 'San Antonio ISD',
        'South San ISD': 'South San Antonio ISD',
        'Judson ISD': 'Judson ISD',
        'Edgewood ISD': 'Edgewood ISD (Bexar)',
        'SCUC ISD': 'Schertz-Cibolo-Universal City ISD',
        'East Central ISD': 'East Central ISD',
        'Southwest ISD': 'Southwest ISD',
        'Boerne ISD': 'Boerne ISD',
        'Ft Sam Houston ISD': 'Fort Sam Houston ISD',
        'SWISD': 'Southwest ISD'
    }

    district_counts['Mapped_District_Name'] = district_counts['District_Name'].map(district_mapping).fillna(district_counts['District_Name'])

    # Merge data
    merged = district_shapes.merge(district_counts, left_on='NAME', right_on='Mapped_District_Name', how='left')
    merged['Client_Count'] = merged['Client_Count'].fillna(0).astype(int)
    merged = merged.to_crs('EPSG:4326')

    # Create color bins
    max_val = merged['Client_Count'].max()
    color_bins = [0, 1, 5, 10, 20, 50, 100, 200, 400, 700, max_val]
    color_bins = sorted(list(set([b for b in color_bins if b <= max_val] + [max_val])))

    def assign_color_category(value):
        if value == 0:
            return 0
        for i, bin_val in enumerate(color_bins[1:], 1):
            if value <= bin_val:
                return i
        return len(color_bins) - 1

    merged['Color_Category'] = merged['Client_Count'].apply(assign_color_category)

    # Create map
    geojson = json.loads(merged.to_json())
    fig = px.choropleth_mapbox(
        merged,
        geojson=geojson,
        locations=merged.index,
        color='Color_Category',
        color_continuous_scale=['#f7f7f7', '#deebf7', '#c6dbef', '#9ecae1', '#6baed6', '#4292c6', '#2171b5', '#08519c', '#08306b', '#05196e', '#021942'],
        range_color=(0, len(color_bins) - 1),
        mapbox_style="open-street-map",
        zoom=9,
        center={"lat": 29.4241, "lon": -98.4936},
        opacity=0.8,
        hover_name='NAME',
        title="San Antonio School District Client Distribution"
    )

    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>Clients: %{customdata}<extra></extra>",
        hovertext=merged['NAME'],
        customdata=merged['Client_Count']
    )

    fig.update_layout(
        title={'text': "San Antonio School District Client Distribution", 'x': 0.5, 'xanchor': 'center'},
        height=600,
        margin=dict(l=0, r=0, t=50, b=0)
    )

    return fig

# Create the layout
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("SOS Client Distribution Dashboard", 
                   className="text-center mb-4",
                   style={'color': '#2c3e50', 'fontWeight': 'bold'})
        ])
    ]),
    
    # Main content with card
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H4("School District Heat Map", 
                           className="mb-0",
                           style={'color': '#34495e'})
                ]),
                dbc.CardBody([
                    dcc.Graph(
                        id='district-map',
                        figure=create_district_map(),
                        style={'height': '600px'}
                    )
                ])
            ], style={'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'})
        ], width=12)
    ]),
    
    # Footer with statistics
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Quick Stats", className="card-title"),
                    html.Div([
                        html.P(f"Total Clients: {pd.read_csv('cleaned_clients.csv').shape[0]:,}", 
                              className="mb-2"),
                        html.P(f"Districts Covered: {pd.read_csv('cleaned_clients.csv')['District'].nunique()}", 
                              className="mb-0")
                    ])
                ])
            ], style={'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.1)'})
        ], width=12)
    ], className="mt-4")
    
], fluid=True, style={'backgroundColor': '#f8f9fa', 'minHeight': '100vh', 'padding': '20px'})

if __name__ == '__main__':
    app.run_server(debug=True) 