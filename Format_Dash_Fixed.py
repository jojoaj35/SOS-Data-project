import pandas as pd
import datetime as dt
import statistics as stat
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import Dash, dcc, callback, Output, Input, html, dash_table, State
import webbrowser
from threading import Timer
import datetime as dt
from scipy import stats as scipystat
import math
import base64
import io

# Import functions from the map modules
from events_analysis import (
    create_service_events_heatmap, 
    get_events_summary_stats
)
from heatmap import create_heatmap_from_dataframe

# Import our new modular components
from dashboard_components import (
    create_district_pie_chart,
    create_club_comparison_chart,
    create_quarter_volunteers_chart,
    calculate_hours_value,
    get_age_dropdown_options,
    create_district_heat_map
)

from data_processing import (
    process_uploaded_data,
    create_processing_summary
)

# Initialize empty datasets - data will be loaded through File Uploader tab
clients_raw = pd.DataFrame()
hours = pd.DataFrame()
survey_raw = pd.DataFrame()
clients = pd.DataFrame()
schoolclub_hours = pd.DataFrame(columns=['School', 'Hours', 'Club'])
qtr_vol_counts = pd.DataFrame(columns=['QTR', 'Active Volunteers'])

# Configuration data
bexar_zips = [78245,78254,78249,78253,78251,78228,78250,78240,78247,78207,78223,78258,78201,78227,78230,78233,78213,78221,78216,78109,78209,78244,78237,78218,78232,78260,78210,78023,78229,78217,78242,78239,78211,78238,78212,78222,78259,78261,78148,78214,78224,78015,78219,78220,78255,78248,78264,78252,78225,78204,78256,78073,78202,78112,78231,78236,78002,78226,78203,78257,78263,78208,78215,78152,78234,78205,78235,78243,78206,78262,78275,78286,78287,78054,78150,78241,78246,78265,78268,78270,78269,78278,78280,78279,78284,78283,78285,78288,78291,78289,78293,78292,78295,78294,78297,78296,78299,78298]

kendall_zips = [78006,78013,78606,78004,78027,78074]
bandera_zips = [78063,78003,78055,78884,78885,78883]
comal_zips = [78130,78132,78133,78070,78163,78266,78623,78131,78135]
guadalupe_zips = [78666,78155,78108,78154,78648,78124,78655,78638,78123,78670,78115,78156]
wilson_zips = [78114,78121,78101,78160,78140,78113,78161,78147,78143]
atascosa_zips = [78064,78065,78026,78052,78069,78011,78008,78050,78062,78012]
medina_zips = [78861,78016,78009,78059,78039,78056,78057,78850,78066,78886]

county_zips = {
    'Bexar': bexar_zips,
    'Kendall': kendall_zips,
    'Bandera': bandera_zips,
    'Comal': comal_zips,
    'Guadalupe': guadalupe_zips,
    'Wilson': wilson_zips,
    'Atascosa': atascosa_zips,
    'Medina': medina_zips
}

zips_for_incomes = [78002, 78003, 78004, 78006, 78008, 78009, 78011, 78012, 78013, 78015, 78016, 78023, 78026, 78027, 78039, 78050, 78052, 78055, 78056, 78057, 78059, 78062, 78063, 78064, 78065, 78066, 78069, 78070, 78073, 78074, 78101, 78108, 78109, 78112, 78113, 78114, 78121, 78123, 78124, 78130, 78132, 78133, 78140, 78143, 78147, 78148, 78150, 78152, 78154, 78155, 78160, 78161, 78163, 78201, 78202, 78203, 78204, 78205, 78207, 78208, 78209, 78210, 78211, 78212, 78213, 78214, 78215, 78216, 78217, 78218, 78219, 78220, 78221, 78222, 78223, 78224, 78225, 78226, 78227, 78228, 78229, 78230, 78231, 78232, 78233, 78234, 78235, 78236, 78237, 78238, 78239, 78240, 78242, 78243, 78244, 78245, 78247, 78248, 78249, 78250, 78251, 78252, 78253, 78254, 78255, 78256, 78257, 78258, 78259, 78260, 78261, 78263, 78264, 78266, 78606, 78623, 78638, 78648, 78655, 78666, 78670, 78850, 78861, 78883, 78884, 78885, 78886]

zip_income_list = ['64082', '54500', '160147', '110955', '-', '102724', '29089', '47708', '79770', '155488', '57609', '129701', '77257', '108434', '74013', '91212', '69018', '71635', '122026', '63967', '72254', '-', '79066', '69407', '63653', '92813', '71071', '115076', '65342', '-', '90413', '117304', '87635', '54445', '90191', '84260', '126726', '95700', '82534', '84426', '126934', '80777', '49032', '-', '72961', '75395', '-', '102212', '97465', '71367', '62188', '75966', '133681', '46129', '43708', '34815', '54667', '34631', '30655', '23194', '84180', '51990', '54279', '60222', '53342', '41334', '82128', '55488', '56852', '56833', '52147', '41244', '63114', '64251', '50352', '57965', '46829', '32340', '48049', '50865', '46718', '71564', '103538', '84633', '73729', '100096', '64919', '96771', '40233', '56227', '71455', '62203', '48979', '-', '67789', '87890', '89184', '130605', '80851', '80289', '78025', '79635', '104260', '115823', '151673', '72797', '74540', '116133', '109429', '150705', '140120', '81793', '60245', '132470', '89980', '122143', '82760', '56533', '48409', '55478', '76591', '77344', '64491', '36189', '82292', '70833', '119276']

zip_incomes_withblanks = pd.DataFrame(data={'Zip Code': zips_for_incomes, 'Median Income': zip_income_list})
zip_incomes = zip_incomes_withblanks[zip_incomes_withblanks['Median Income'] != '-']

county_incomes = pd.DataFrame(data={'County': ['Kendall','Bandera','Comal','Guadalupe','Wilson','Atascosa','Medina', 'Bexar'],
                                     'Median Income':[110498,69073,99193,95953,92461,69413,73462,69807]})

yes_no_cols = ['Learn Participation 2022', 
               'Explore Participation',
               'Make It Happen Badge (Yes/No)', 
               'Trip Eligible (Yes/No)',
               'Scholarship Badge (Yes/No)']

schools_with_clubs = ['Brackenridge High School','Whittier Middle School', 'Driscoll Middle school', 'Advanced Learning Academy', 
                      "Young Women's Leadership Academy", 'CAST Med High School', 'International School of the Americas', 'South San High School', 
                      'Churchill High School', 'Johnson High School', 'CAST Tech High School' , 'IDEA Converse', 'RISE Inspire Academy', 
                      'Nimitz Middle School', 'Thomas Jefferson High School', "Young Men's Leadership Academy", 'Southside High School']

general_agg_stats = {'Galaxy ID': 'count',
            'Age at Sign Up': ['mean', 'median', 'min', 'max'],
            'Service Range': 'mean',
            'Hours': ['sum', 'mean'],
            'Follow Through': ['sum', 'mean'],
            'Trip Eligible (Yes/No)': ['sum', 'mean'],
            'Service Count': ['mean', 'sum'],
            'Responses' : ['mean', 'sum'],
            'Make It Happen Badge (Yes/No)': ['sum', 'mean'],
            'Scholarship Badge (Yes/No)': ['sum', 'mean'],
            'Explore Participation': ['sum', 'mean']}

age_agg_stats = {'Galaxy ID': 'count',
            'Service Range': 'mean',
            'Hours': ['sum', 'mean'],
            'Follow Through': ['sum', 'mean'],
            'Trip Eligible (Yes/No)': ['sum', 'mean'],
            'Service Count': ['mean', 'sum'],
            'Responses' : ['mean', 'sum'],
            'Make It Happen Badge (Yes/No)': ['sum', 'mean'],
            'Scholarship Badge (Yes/No)': ['sum', 'mean'],
            'Explore Participation': ['sum', 'mean']}

def population_stat(df, col):
    """Population statistics function"""
    if df.empty or col not in df.columns:
        return pd.DataFrame(), pd.DataFrame()
    
    if col != 'Age at Sign Up':
        agg_name = df.groupby(by=col).agg(general_agg_stats)
    else:
        agg_name = df.groupby(by=col).agg(age_agg_stats)
    
    if 'Service Range' in agg_name.columns:
        agg_name['Service Range'] = agg_name['Service Range','mean'].dt.days

    agg_name.sort_values(by=('Galaxy ID', 'count'), ascending=False, inplace=True)
    agg_name = agg_name.round(2)

    flat_name = agg_name.copy()
    flat_name.columns = ['_'.join(col).strip() for col in flat_name.columns.values]
    flat_name.reset_index(inplace=True)
    flat_name = flat_name.round(2)

    return agg_name, flat_name

# Initialize the Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB])

app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("Students of Service Data Display", 
                   className="text-center mb-3",
                   style={'color': '#2c3e50', 'fontWeight': 'bold'})
        ])
    ], className="mb-3"),
    
    # Tabs
    dbc.Tabs([
        dbc.Tab(label="Dashboard", tab_id="dashboard", active_tab_style={"textTransform": "uppercase"}),
        dbc.Tab(label="Internal", tab_id="internal", active_tab_style={"textTransform": "uppercase"}),
        dbc.Tab(label="File Uploader", tab_id="file-uploader", active_tab_style={"textTransform": "uppercase"}),
    ], id="tabs", active_tab="dashboard", className="mb-3"),
    
    # Tab content
    html.Div(id="tab-content"),
    
    # Hidden div to store data state
    html.Div(id="data-store", style={'display': 'none'})
    
], fluid=True, style={
    'minHeight': '100vh', 
    'padding': '15px', 
    'backgroundColor': '#f8f9fa',
    'overflowY': 'auto',
    'overflowX': 'hidden'
})

# Define layouts
dashboard_layout = [
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H6("Student Distribution by District", 
                           className="mb-0 text-center",
                           style={'color': '#34495e', 'fontWeight': '600'})
                ]),
                dbc.CardBody([
                    dcc.Graph(id='test-graph', style={'height': '300px'}),
                    html.Div([
                        html.Label("Select Age:", 
                                 className="form-label mb-2",
                                 style={'fontWeight': '500', 'fontSize': '14px'}),
                        dcc.Dropdown(
                            id='age-drop',
                            options=get_age_dropdown_options(clients),
                            value=16,
                            style={'marginBottom': '10px'}
                        )
                    ])
                ])
            ], className='shadow-sm', style={'height': '400px', 'marginBottom': '20px'})
        ], width=4),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H6("Club vs No Club Comparison (alpha=0.05)", 
                        className="mb-0 text-center",
                        style={'color': '#34495e', 'fontWeight': '600'})
                ]),
                dbc.CardBody([
                    html.Div([
                        dcc.Graph(id='club-comparison-chart', style={'height': '220px'})
                    ], className="mb-2"),
                    html.Div(id='club-confidence-intervals', style={'fontSize': '18px'})
                ], style={'padding': '15px'})  
            ], className='shadow-sm', style={'height': '400px', 'marginBottom': '20px'})
        ], width=4),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H6("Active Volunteers by Quarter", 
                           className="mb-0 text-center",
                           style={'color': '#34495e', 'fontWeight': '600'})
                ]),
                dbc.CardBody([
                    dcc.Graph(id='quarter-volunteers-chart', style={'height': '340px'})
                ])
            ], className='shadow-sm', style={'height': '400px', 'marginBottom': '20px'})
        ], width=4)
    ], className="mb-3"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H6("Total Value of Volunteered Time", 
                           className="mb-0 text-center",
                           style={'color': '#34495e', 'fontWeight': '600'})
                ]),
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-dollar-sign fa-3x mb-3", 
                              style={'color': '#27ae60'}),
                        html.H2(id='total-value-display', 
                               className='mb-0',
                               style={'color': '#27ae60', 'fontWeight': 'bold', 'fontSize':'80px'})
                    ], className="text-center d-flex flex-column align-items-center justify-content-center h-100")
                ])
            ], className='shadow-sm', style={'height': '300px'})
        ], width=4),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H6("Geographic Distribution Map", 
                           className="mb-0 text-center",
                           style={'color': '#34495e', 'fontWeight': '600'})
                ]),
                dbc.CardBody([
                    html.Div([
                        html.Label("Select Map Type:", 
                                 className="form-label mb-2",
                                 style={'fontWeight': '500', 'fontSize': '14px'}),
                        dcc.Dropdown(
                            id='map-type-dropdown',
                            options=[
                                {'label': 'Client Distribution', 'value': 'clients'},
                                {'label': 'Service Events', 'value': 'events'},
                                {'label': 'District Heat Map', 'value': 'district_heat'}
                            ],
                            value='clients',
                            style={'marginBottom': '15px'}
                        )
                    ]),
                    html.Div(id='map-display-area', style={
                        'height': '750px', 
                        'width': '100%',
                        'overflow': 'visible'
                    })
                ], style={'padding': '15px', 'overflow': 'visible'})
            ], className='shadow-sm', style={'height': '850px', 'marginBottom': '50px'})
        ], width=8)
    ])
]

# Internal tab layout
internal_layout = [
    dbc.Tabs([
        dbc.Tab(label="Settings", tab_id="settings-sub", active_tab_style={"textTransform": "uppercase"}),
        dbc.Tab(label="Analytics", tab_id="analytics-sub", active_tab_style={"textTransform": "uppercase"}),
        dbc.Tab(label="Reports", tab_id="reports-sub", active_tab_style={"textTransform": "uppercase"}),
    ], id="internal-subtabs", active_tab="settings-sub", className="mb-3"),
    html.Div(id="internal-subtab-content")
]

# Analytics sub-tab layout
analytics_subtab_layout = [
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5("Analytics Column 1", 
                           className="mb-0 text-center",
                           style={'color': '#34495e', 'fontWeight': '600'})
                ]),
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-chart-line fa-4x mb-3", 
                              style={'color': '#e74c3c'}),
                        html.H4("Column 1 Content", className="mb-2"),
                        html.P("Add your analytics content here", 
                              className="text-muted",
                              style={'fontSize': '18px'})
                    ], className="d-flex flex-column align-items-center justify-content-center h-100")
                ])
            ], className='shadow-sm', style={'height': '400px'})
        ], width=6, className="mb-3"),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5("Analytics Column 2", 
                           className="mb-0 text-center",
                           style={'color': '#34495e', 'fontWeight': '600'})
                ]),
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-chart-bar fa-4x mb-3", 
                              style={'color': '#3498db'}),
                        html.H4("Column 2 Content", className="mb-2"),
                        html.P("Add your analytics content here", 
                              className="text-muted",
                              style={'fontSize': '18px'})
                    ], className="d-flex flex-column align-items-center justify-content-center h-100")
                ])
            ], className='shadow-sm', style={'height': '400px'})
        ], width=6, className="mb-3")
    ]),
]

# Reports and settings layouts
reports_subtab_layout = [
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5("Reports Dashboard", 
                           className="mb-0 text-center",
                           style={'color': '#34495e', 'fontWeight': '600'})
                ]),
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-file-alt fa-4x mb-3", 
                              style={'color': '#f39c12'}),
                        html.H4("Reports Section", className="mb-2"),
                        html.P("Generate and manage reports here", 
                              className="text-muted",
                              style={'fontSize': '18px'})
                    ], className="d-flex flex-column align-items-center justify-content-center h-100")
                ])
            ], className='shadow-sm', style={'height': '400px'})
        ], width=12)
    ])
]

settings_subtab_layout = [
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5("Population Statistics", 
                            className="mb-0 text-center",
                            style={'color': '#34495e', 'fontWeight': '600'})
                ]),
                dcc.Dropdown(
                    id='popstat-drop',
                    options=[{'label': col, 'value': col} for col in ['Zip Code', 'Age at Sign Up', 'Age Now',
                        'School', 'District', 'Race/Ethnicity', 'Gender', 'Income Range (Thousands)']],
                    value='District',
                ),
                dbc.CardBody(
                    html.Div(id='popstat-table-container')
                )
            ], className='shadow-sm', style={'height': '400px'})
        ], className="d-flex flex-column align-items-center justify-content-center h-100")
    ])
]

# File uploader layout
file_uploader_layout = [
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5("Upload New Dataset", 
                           className="mb-0 text-center",
                           style={'color': '#34495e', 'fontWeight': '600'})
                ]),
                dbc.CardBody([
                    html.Div([
                        dcc.Upload(
                            id='upload-data',
                            children=html.Div([
                                html.I(className="fas fa-cloud-upload-alt fa-3x mb-3", 
                                      style={'color': '#3498db'}),
                                html.H4('Drag and Drop or Click to Select Files'),
                                html.P('Supported formats: Excel (.xlsx, .xls)', 
                                      className='text-muted'),
                                html.P('Expected sheets: Clients, Service Hours, Survey Responses', 
                                      className='text-muted text-sm')
                            ], className="text-center"),
                            style={
                                'width': '100%',
                                'height': '200px',
                                'lineHeight': '200px',
                                'borderWidth': '2px',
                                'borderStyle': 'dashed',
                                'borderRadius': '10px',
                                'borderColor': '#3498db',
                                'textAlign': 'center',
                                'margin': '10px',
                                'cursor': 'pointer',
                                'backgroundColor': '#f8f9fa'
                            },
                            multiple=False
                        )
                    ], className="mb-3"),
                    
                    html.Div(id='upload-status', className="mt-3"),
                    
                    html.Div([
                        html.H6("Current Dataset Information:", 
                               style={'color': '#34495e', 'fontWeight': '600'}),
                        html.P(id='dataset-file-info', className='text-muted mb-1'),
                        html.P(id='dataset-client-count', className='text-muted mb-1'),
                        html.P(id='dataset-hours-count', className='text-muted mb-1'),
                        html.P(id='dataset-status', className='text-muted')
                    ], className="mt-4 p-3", 
                       style={'backgroundColor': '#e8f4f8', 'borderRadius': '5px'})
                ])
            ], className='shadow-sm')
        ], width=8, className="mx-auto")
    ], className="justify-content-center"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H6("File Upload Instructions", 
                           className="mb-0 text-center",
                           style={'color': '#34495e', 'fontWeight': '600'})
                ]),
                dbc.CardBody([
                    html.Ul([
                        html.Li("Upload Excel files (.xlsx or .xls format)"),
                        html.Li("File must contain exactly 3 sheets: 'Clients', 'Service Hours', 'Survey Responses'"),
                        html.Li("Clients sheet should contain Galaxy ID, Age, School, District, etc."),
                        html.Li("Service Hours sheet should contain userId (will be renamed to Galaxy ID), Event Date, hours, etc."),
                        html.Li("Survey Responses sheet should contain survey data"),
                        html.Li("After successful upload, refresh the dashboard to see updated data")
                    ], className="mb-0")
                ])
            ], className='shadow-sm')
        ], width=8, className="mx-auto mt-3")
    ], className="justify-content-center")
]

# CALLBACKS

# Tab switching
@callback(
    Output("tab-content", "children"),
    Input("tabs", "active_tab")
)
def switch_tab(active_tab):
    if active_tab == "dashboard":
        return dashboard_layout
    elif active_tab == "internal":  
        return internal_layout
    elif active_tab == "file-uploader":
        return file_uploader_layout
    return dashboard_layout

# Internal sub-tab switching
@callback(
    Output("internal-subtab-content", "children"),
    Input("internal-subtabs", "active_tab")
)
def switch_internal_subtab(active_subtab):
    if active_subtab == "analytics-sub":
        return analytics_subtab_layout
    elif active_subtab == "reports-sub":
        return reports_subtab_layout
    elif active_subtab == "settings-sub":
        return settings_subtab_layout
    return analytics_subtab_layout

# File upload and data processing
@callback(
    [Output('upload-status', 'children'),
     Output('data-store', 'children'),
     Output('dataset-file-info', 'children'),
     Output('dataset-client-count', 'children'),
     Output('dataset-hours-count', 'children'),
     Output('dataset-status', 'children')],
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def handle_file_upload(contents, filename):
    global clients_raw, hours, survey_raw, clients, schoolclub_hours, qtr_vol_counts
    
    # Update dataset info display
    if contents is None:
        file_info = f"File: {'No file loaded' if clients_raw.empty else 'Dataset loaded via upload'}"
        client_count = f"Total Clients: {len(clients_raw) if not clients_raw.empty else '0'}"
        hours_count = f"Total Service Hours Records: {len(hours) if not hours.empty else '0'}"
        status = f"Status: {'Ready to upload data' if clients_raw.empty else 'Data loaded successfully'}"
        return html.Div(), "", file_info, client_count, hours_count, status
    
    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            excel_file = pd.ExcelFile(io.BytesIO(decoded))
            
            required_sheets = ['Clients', 'Service Hours', 'Survey Responses']
            missing_sheets = [sheet for sheet in required_sheets if sheet not in excel_file.sheet_names]
            
            if missing_sheets:
                return dbc.Alert(
                    f"Error: Missing required sheets: {', '.join(missing_sheets)}. "
                    f"Found sheets: {', '.join(excel_file.sheet_names)}",
                    color="danger",
                    dismissable=True
                ), "", "File: No file loaded", "Total Clients: 0", "Total Service Hours Records: 0", "Status: Upload failed"
            
            # Read the sheets
            clients_raw = pd.read_excel(io.BytesIO(decoded), sheet_name='Clients')
            hours = (pd.read_excel(io.BytesIO(decoded), sheet_name='Service Hours')
                    .rename({'userId': 'Galaxy ID'}, axis=1))
            survey_raw = pd.read_excel(io.BytesIO(decoded), sheet_name='Survey Responses')
            
            # Process the data using our modular function
            clients, schoolclub_hours, qtr_vol_counts = process_uploaded_data(
                clients_raw, hours, survey_raw, county_zips, zip_incomes, 
                county_incomes, schools_with_clubs, yes_no_cols
            )
            
            # Create success summary
            success_summary = create_processing_summary(
                clients_raw, hours, survey_raw, clients, schoolclub_hours, qtr_vol_counts, filename
            )
            
            # Update dataset info
            file_info = f"File: {filename}"
            client_count = f"Total Clients: {len(clients_raw)}"
            hours_count = f"Total Service Hours Records: {len(hours)}"
            status = "Status: Data loaded and processed successfully"
            
            return success_summary, "data_updated", file_info, client_count, hours_count, status
            
        else:
            return dbc.Alert(
                "Error: Please upload an Excel file (.xlsx or .xls)",
                color="danger",
                dismissable=True
            ), "", "File: No file loaded", "Total Clients: 0", "Total Service Hours Records: 0", "Status: Upload failed"
            
    except Exception as e:
        return dbc.Alert(
            f"Error processing file: {str(e)}",
            color="danger",
            dismissable=True
        ), "", "File: No file loaded", "Total Clients: 0", "Total Service Hours Records: 0", "Status: Upload failed"

# Update all dashboard components when data changes
@callback(
    [Output('test-graph', 'figure'),
     Output('age-drop', 'options'),
     Output('club-comparison-chart', 'figure'),
     Output('club-confidence-intervals', 'children'),
     Output('quarter-volunteers-chart', 'figure'),
     Output('total-value-display', 'children')],
    [Input('data-store', 'children'),
     Input('age-drop', 'value')]
)
def update_dashboard_components(data_store, selected_age):
    # Create all dashboard components using our modular functions
    pie_fig = create_district_pie_chart(clients, selected_age)
    age_options = get_age_dropdown_options(clients)
    club_fig, club_intervals = create_club_comparison_chart(schoolclub_hours)
    quarter_fig = create_quarter_volunteers_chart(qtr_vol_counts)
    total_value = f"${calculate_hours_value(clients)}"
    
    return pie_fig, age_options, club_fig, club_intervals, quarter_fig, total_value

# Population statistics
@callback(
    Output('popstat-table-container', 'children'),
    [Input('popstat-drop', 'value'),
     Input('data-store', 'children')]
)
def popstat_dashtable(popstat, data_store):
    if clients.empty or popstat not in clients.columns:
        return html.Div([
            html.P("No data available. Please upload a dataset first.", 
                   className="text-muted text-center",
                   style={'padding': '20px'})
        ])
    
    try:
        agg_stat, flat_stat = population_stat(clients, popstat)
        return dbc.Table.from_dataframe(agg_stat.reset_index().sort_values(by=popstat))
    except Exception as e:
        return html.Div([
            html.P(f"Error generating statistics: {str(e)}", 
                   className="text-danger text-center",
                   style={'padding': '20px'})
        ])

# Map display
@callback(
    Output('map-display-area', 'children'),
    [Input('map-type-dropdown', 'value'),
     Input('data-store', 'children')]
)
def update_map_display(map_type, data_store):
    try:
        if map_type == 'clients':
            if clients.empty:
                return html.P("Upload data to view client distribution map", 
                             className="text-muted text-center",
                             style={'padding': '50px'})
            fig = create_heatmap_from_dataframe(clients, height=750)
            return dcc.Graph(
                figure=fig, 
                style={'height': '750px', 'width': '100%'},
                config={'responsive': True, 'displayModeBar': False}
            )
        
        elif map_type == 'events':
            if hours.empty:
                return html.P("Upload data to view service events map", 
                             className="text-muted text-center",
                             style={'padding': '50px'})
            fig = create_service_events_heatmap(hours, height=750)
            return dcc.Graph(
                figure=fig, 
                style={'height': '750px', 'width': '100%'},
                config={'responsive': True, 'displayModeBar': False}
            )
        
        elif map_type == 'district_heat':
            if clients.empty:
                return html.P("Upload data to view district heat map", 
                             className="text-muted text-center",
                             style={'padding': '50px'})
            fig = create_district_heat_map(clients)
            return dcc.Graph(
                figure=fig, 
                style={'height': '750px', 'width': '100%'},
                config={'responsive': True, 'displayModeBar': False}
            )
        
        else:
            return html.P("Select a map type to view visualization", 
                         className="text-muted text-center",
                         style={'padding': '50px'})
    
    except Exception as e:
        return html.Div([
            html.P(f"Error loading map: {str(e)}", 
                   className="text-danger text-center",
                   style={'padding': '20px'}),
            html.P("Please check data availability and try again", 
                   className="text-muted text-center")
        ])

if __name__ == '__main__':
    Timer(1, lambda: webbrowser.open("http://localhost:8000")).start()
    app.run(debug=False, host='localhost', port=8000) 