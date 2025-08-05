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

# Import functions from the dashboard components module
from dashboard_components import (
    create_service_events_heatmap, 
    get_events_summary_stats,
    create_heatmap_from_dataframe,
    create_monthly_volunteers_chart
)

# Import our new modular components
from dashboard_components import (
    create_district_pie_chart,
    create_club_comparison_chart,
    create_quarter_volunteers_chart,
    calculate_hours_value,
    get_age_dropdown_options,
    create_district_heat_map,
    create_zipcode_map,
    create_funnel_chart,
    single_var_freq,
    multi_var_freq,
    slice_by_active,
    collected_freq_cols,
    notcollected_freq_cols,
    filter_populations,
    update_global_dataframes,
    create_likert_pie_card,
    get_likert_pie_figure
)

from data_processing import (
    process_uploaded_data,
    create_processing_summary
)

# Import dashboard_components module to set global variables
import dashboard_components
# Import create_zipcode_map from dashboard_components (no separate import needed)

# Initialize empty datasets - data will be loaded through File Uploader tab
clients_raw = pd.DataFrame()
hours = pd.DataFrame()
survey_raw = pd.DataFrame()
clients = pd.DataFrame()
schoolclub_hours = pd.DataFrame(columns=['School', 'Hours', 'Club'])
qtr_vol_counts = pd.DataFrame(columns=['QTR', 'Active Volunteers'])

# Initialize global variables in dashboard_components for frequency functions
dashboard_components.hours = hours
dashboard_components.clients = clients

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

# --- THEME & FONTS ---
# Use Flatly theme and Font Awesome icons for a modern look

# Initialize the Dash app first
app = Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,  # Use Bootstrap theme for better base styling
        dbc.icons.FONT_AWESOME, 
        '/assets/custom_designer.css', 
        '/assets/likert_dropdown.css'
    ],
    suppress_callback_exceptions=True
)

# Update the app initialization with SOS branding
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>SOS Students of Service - Volunteer Analytics Dashboard</title>
        {%favicon%}
        {%css%}
        <style>
            /* SOS Students of Service Branded Dashboard */
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
                background-size: cover;
                background-attachment: fixed;
                margin: 0;
                padding: 0;
                min-height: 100vh;
                color: #2c3e50;
            }
            
            .dashboard-container {
                background: rgba(255, 255, 255, 0.98);
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
                margin: 20px;
                backdrop-filter: blur(10px);
                padding: 30px;
                min-height: calc(100vh - 40px);
                height: auto;
            }
            
            .card {
                border: none;
                border-radius: 15px;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
                transition: all 0.3s ease;
                background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
                overflow: hidden;
            }
            
            .card:hover {
                transform: translateY(-5px);
                box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
            }
            
            .card-header {
                background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
                color: white;
                border-radius: 15px 15px 0 0 !important;
                border: none;
                padding: 20px;
                position: relative;
                overflow: hidden;
            }
            
            .card-header::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, transparent 100%);
                pointer-events: none;
            }
            
            .card-header h5, .card-header h6 {
                margin: 0;
                font-weight: 600;
                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                position: relative;
                z-index: 1;
            }
            
            .card-body {
                padding: 25px;
                background: rgba(255, 255, 255, 0.95);
            }
            
            .sidebar {
                background: #A7C7E7;
                border-radius: 0;
                box-shadow: 4px 0 20px rgba(0, 0, 0, 0.15);
                position: relative;
                overflow: hidden;
                border-right: 1px solid rgba(255, 255, 255, 0.1);
                height: 100vh !important;
                min-height: 100vh !important;
                display: flex;
                flex-direction: column;
            }
            
            .sidebar-nav {
                position: relative;
                z-index: 2;
                flex: 1;
                display: flex;
                flex-direction: column;
            }
            
            .nav-link {
                color: rgba(255, 255, 255, 0.85) !important;
                border-radius: 12px;
                margin: 8px 12px;
                padding: 12px 16px !important;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                font-weight: 500;
                position: relative;
                z-index: 1;
                border: 1px solid transparent;
                backdrop-filter: blur(10px);
                font-size: 14px;
                letter-spacing: 0.5px;
            }
            
            .nav-link:hover {
                background: rgba(255, 255, 255, 0.15);
                color: #ffffff !important;
                transform: translateX(8px);
                border-color: rgba(255, 255, 255, 0.2);
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            }
            
            .nav-link.active {
                background: linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, rgba(255, 255, 255, 0.1) 100%);
                color: #ffffff !important;
                box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
                border-color: rgba(255, 255, 255, 0.3);
                transform: translateX(4px);
            }
            
            .nav-link i {
                margin-right: 12px;
                font-size: 16px;
                width: 20px;
                text-align: center;
                opacity: 0.9;
            }
            
            #sidebar-toggle {
                background: linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, rgba(255, 255, 255, 0.1) 100%);
                border: 1px solid rgba(255, 255, 255, 0.2);
                color: white;
                border-radius: 10px;
                transition: all 0.3s ease;
                backdrop-filter: blur(10px);
                font-size: 14px;
                padding: 8px 12px;
                margin-bottom: 20px;
            }
            
            #sidebar-toggle:hover {
                background: linear-gradient(135deg, rgba(255, 255, 255, 0.3) 0%, rgba(255, 255, 255, 0.2) 100%);
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            }
            
            .dropdown-container {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 15px;
                border: 1px solid rgba(52, 152, 219, 0.1);
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            }
            
            .metric-display {
                background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
                color: white;
                border-radius: 15px;
                padding: 30px;
                text-align: center;
                box-shadow: 0 8px 25px rgba(39, 174, 96, 0.3);
                position: relative;
                overflow: hidden;
            }
            
            .metric-display::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, transparent 100%);
                pointer-events: none;
            }
            
            .metric-value {
                font-size: 3rem;
                font-weight: bold;
                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                position: relative;
                z-index: 1;
            }
            
            .upload-area {
                border: 2px dashed #3498db;
                border-radius: 15px;
                padding: 40px;
                text-align: center;
                background: rgba(52, 152, 219, 0.05);
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }
            
            .upload-area:hover {
                border-color: #2980b9;
                background: rgba(52, 152, 219, 0.1);
                transform: scale(1.02);
            }
            
            .upload-area::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: linear-gradient(45deg, rgba(52, 152, 219, 0.1) 0%, transparent 100%);
                pointer-events: none;
            }
            
            .status-indicator {
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: 600;
                font-size: 0.9rem;
                display: inline-block;
                text-align: center;
                min-width: 120px;
            }
            
            .status-success {
                background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
                color: white;
                box-shadow: 0 4px 15px rgba(39, 174, 96, 0.3);
            }
            
            .status-warning {
                background: linear-gradient(135deg, #d4af37 0%, #b8941f 100%);
                color: white;
                box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3);
            }
            
            .status-error {
                background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
                color: white;
                box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);
            }
            
            .tab-content {
                background: rgba(255, 255, 255, 0.98);
                border-radius: 15px;
                padding: 20px;
                margin-top: 20px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            }
            
            .graph-container {
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
                background: white;
            }
            
            .sos-header {
                background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
                color: white;
                padding: 20px;
                border-radius: 15px;
                margin-bottom: 30px;
                text-align: center;
                box-shadow: 0 8px 25px rgba(52, 152, 219, 0.3);
                position: relative;
                overflow: hidden;
            }
            
            .sos-header::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, transparent 100%);
                pointer-events: none;
            }
            
            .sos-title {
                font-size: 2.5rem;
                font-weight: 700;
                margin: 0;
                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                position: relative;
                z-index: 1;
            }
            
            .sos-subtitle {
                font-size: 1.2rem;
                font-weight: 500;
                margin: 10px 0 0 0;
                opacity: 0.9;
                position: relative;
                z-index: 1;
            }
            
            .sos-tagline {
                font-size: 1rem;
                font-style: italic;
                margin: 5px 0 0 0;
                opacity: 0.8;
                position: relative;
                z-index: 1;
            }
            
            .nav-tabs .nav-link.active {
                background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
                color: white;
                box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
            }
            
            .nav-tabs .nav-link:hover {
                background: rgba(52, 152, 219, 0.1);
                color: #3498db;
                transform: translateY(-2px);
            }
            
            /* Ensure tab labels are black */
            .nav-tabs .nav-link {
                color: black !important;
                font-weight: 500;
            }
            
            .nav-tabs .nav-link.active {
                color: white !important;
            }
            
            /* Collapsed sidebar styles */
            .sidebar.collapsed {
                min-width: 50px !important;
                max-width: 50px !important;
                width: 50px !important;
            }
            
            .sidebar.collapsed .nav-link {
                padding: 12px 8px !important;
                margin: 4px 6px;
                text-align: center;
            }
            
            .sidebar.collapsed .nav-link i {
                margin-right: 0;
                font-size: 18px;
                width: auto;
            }
            
            .sidebar.collapsed #sidebar-toggle {
                padding: 6px 8px;
                font-size: 12px;
            }
            .dbc-row, .dbc-container {
                min-height: 100vh;
                height: 100vh;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# --- LAYOUT CHANGES ---
# Move navigation to a vertical sidebar
sidebar = dbc.Col([
    # Sidebar header
    html.Div([
        html.H5("SOS Dashboard", 
                style={'color': 'white', 'fontWeight': '600', 'marginBottom': '5px', 'textAlign': 'center'}),
        html.Hr(style={'border': '1px solid rgba(255,255,255,0.2)', 'margin': '15px 0'}),
    ], className="mb-3"),
    
    # Toggle button for sidebar
    html.Div([
        dbc.Button([
            html.I(className="fas fa-bars")
        ], id="sidebar-toggle", color="light", className="mb-3", size="sm", style={'width': '100%'})
    ], className="text-center"),
    
    # Navigation links
    dbc.Nav([
        dbc.NavLink([
            html.I(className="fas fa-chart-line me-2"),
            html.Span("Dashboard", id="dashboard-text")
        ], id="tab-dashboard", href="#", className="nav-link"),
        dbc.NavLink([
            html.I(className="fas fa-database me-2"),
            html.Span("Internal Analytics", id="internal-text")
        ], id="tab-internal", href="#", className="nav-link"),
        dbc.NavLink([
            html.I(className="fas fa-upload me-2"),
            html.Span("File Uploader", id="uploader-text")
        ], id="tab-file-uploader", href="#", className="nav-link"),
    ], vertical=True, pills=True, className="sidebar-nav", id="sidebar-nav")
], width=2, className="sidebar", id="sidebar", style={'height': '100vh', 'minWidth': '250px', 'transition': 'all 0.3s ease'})

main_content = dbc.Col([
    dcc.Store(id="active-tab-store", data="dashboard"),
    dcc.Store(id="sidebar-collapsed", data=False),
    html.Div(id="tab-content", style={'padding': '30px 20px', 'height': '100%', 'overflowY': 'auto'}),
    html.Div(id="data-store", style={'display': 'none'})
], width=10, id="main-content", style={'padding': '0', 'transition': 'all 0.3s ease', 'height': '100vh'})

app.layout = dbc.Container([
    dbc.Row([
        sidebar,
        main_content
    ], style={'height': '100vh', 'margin': '0', 'flexWrap': 'nowrap', 'minHeight': '100vh'})
], fluid=True, style={'padding': '0', 'maxWidth': '100vw', 'overflowX': 'hidden', 'height': '100vh', 'minHeight': '100vh'})

# Define layouts
likert_indices = [0, 18, 19]  # Indices of Likert questions to show in dropdown (match working_pie.py)

def get_likert_columns():
    if not survey_raw.empty:
        # If there are at least 20 columns, use [0, 18, 19] as in working_pie.py
        if len(survey_raw.columns) > 19:
            return [survey_raw.columns[i] for i in [0, 18, 19]]
        # Otherwise, just use all columns
        return list(survey_raw.columns)
    return []

# Update the dashboard layout with equal card sizing and proper sidebar
dashboard_layout = html.Div([
    # SOS Branded Header
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1("SOS", className="sos-title"),
                html.H2("STUDENTS OF SERVICE", className="sos-subtitle"),
                html.Hr(style={'border': '1px solid rgba(255,255,255,0.3)', 'margin': '10px auto', 'width': '200px'}),
                html.P("Learn. Serve. Explore.", className="sos-tagline")
            ], className="sos-header")
        ], width=12)
    ], className="mb-4"),
    
    # First row with stacked Club vs No Club and Total Value cards
    dbc.Row([
        dbc.Col([
            # Senior Survey Responses card (full height)
            html.Div(id="senior-survey-card-container", className="equal-height-card")
        ], width=4, className="mb-2"),
        
        dbc.Col([
            # Club vs No Club Comparison card
            dbc.Card([
                dbc.CardHeader([
                    html.H6("Club vs No Club Comparison", 
                        className="mb-0 text-center",
                        style={'color': 'white', 'fontWeight': '600', 'fontSize': '16px'})
                ], className="card-header"),
                dbc.CardBody([
                    html.Div([
                        dcc.Graph(id='club-comparison-chart', 
                                 style={'height': '250px'},
                                 className="graph-container")
                    ], className="mb-3"),
                    html.Div(id='club-confidence-intervals', 
                            style={'fontSize': '14px', 'textAlign': 'center', 'color': '#2c3e50'})
                ], className="card-body")  
            ], className='card equal-height-card')
        ], width=4, className="mb-2"),
        
        dbc.Col([
            # Total Value of Volunteered Time card (compact)
            dbc.Card([
                dbc.CardHeader([
                    html.H6("Total Value of Volunteered Time", 
                           className="mb-0 text-center",
                           style={'color': 'white', 'fontWeight': '600', 'fontSize': '12px', 'padding': '8px'})
                ], className="card-header"),
                dbc.CardBody([
                    html.Div([
                        html.H2(id='total-value-display', 
                               className='metric-value',
                               style={'color': '#228B22', 'fontWeight': 'bold', 'textAlign': 'center', 'margin': '0', 'fontSize': '1.8rem'})
                    ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center', 'height': '30px'})
                ], style={'padding': '3px', 'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'})
            ], className='card', style={'minHeight': '60px'})
        ], width=4, className="mb-2")
    ], className="mb-4 equal-height-row"),
    
    # Second row with Active Volunteers by Time Period (horizontal rectangle)
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H6("Active Volunteers by Time Period", 
                           className="mb-0 text-center",
                           style={'color': 'white', 'fontWeight': '600', 'fontSize': '18px'})
                ], className="card-header"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.Label("Time Period:", 
                                         className="form-label mb-3",
                                         style={'fontWeight': '600', 'fontSize': '16px', 'color': '#2c3e50'}),
                                dcc.Dropdown(
                                    id='time-period-dropdown',
                                    options=[
                                        {'label': 'By Quarter', 'value': 'quarter'},
                                        {'label': 'By Month', 'value': 'month'}
                                    ],
                                    value='quarter',
                                    style={'marginBottom': '20px', 'fontSize': '14px'}
                                ),
                                html.Div([
                                    html.I(className="fas fa-chart-line", 
                                           style={'color': '#3498db', 'fontSize': '24px', 'marginBottom': '10px'}),
                                    html.P("Select a time period to view volunteer activity trends", 
                                           className="text-muted",
                                           style={'fontSize': '12px', 'marginTop': '10px'})
                                ], className="text-center")
                            ], className="dropdown-container", 
                               style={'padding': '20px', 'borderRadius': '10px', 'backgroundColor': 'rgba(52, 152, 219, 0.05)'})
                        ], width=3),
                        dbc.Col([
                            html.Div([
                                dcc.Graph(id='volunteers-time-chart', 
                                         style={'height': '350px'},
                                         className="graph-container")
                            ], style={'padding': '10px'})
                        ], width=9)
                    ], className="align-items-center")
                ], className="card-body", style={'padding': '25px'})
            ], className='card', style={'borderRadius': '15px', 'boxShadow': '0 8px 25px rgba(0, 0, 0, 0.1)'})
        ], width=12, className="mb-4")
    ]),
    
    # Third row with full-width map
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H6("Geographic Distribution Map", 
                           className="mb-0 text-center",
                           style={'color': 'white', 'fontWeight': '600', 'fontSize': '16px'})
                ], className="card-header"),
                dbc.CardBody([
                    html.Div([
                        html.Label("Select Map Type:", 
                                 className="form-label mb-2",
                                 style={'fontWeight': '600', 'fontSize': '14px', 'color': '#2c3e50'}),
                        dcc.Dropdown(
                            id='map-type-dropdown',
                            options=[
                                {'label': 'Client Distribution', 'value': 'clients'},
                                {'label': 'Service Events', 'value': 'events'},
                                {'label': 'District Heat Map', 'value': 'district_heat'},
                                {'label': 'Service Hours by Zipcode', 'value': 'zipcode_hours'}
                            ],
                            value='clients',
                            style={'marginBottom': '20px', 'fontSize': '14px'}
                        )
                    ], className="dropdown-container"),
                    html.Div(id='map-display-area', 
                            style={'height': '600px', 'width': '100%'},
                            className="graph-container")
                ], className="card-body")
            ], className='card equal-height-card')
        ], width=12, className="mb-3")
    ], className="equal-height-row")
], className="dashboard-container")

# Internal tab layout
internal_layout = html.Div([
    dbc.Tabs([
        dbc.Tab(label="Population Statistics", tab_id="population-stats", 
                active_tab_style={"textTransform": "uppercase", "fontWeight": "bold", "backgroundColor": "#3498db", "color": "white"},
                tab_style={"fontSize": "14px", "padding": "12px 20px", "borderRadius": "8px", "margin": "0 5px", "color": "black"}),
        dbc.Tab(label="Frequency Tables", tab_id="frequency-tables", 
                active_tab_style={"textTransform": "uppercase", "fontWeight": "bold", "backgroundColor": "#3498db", "color": "white"},
                tab_style={"fontSize": "14px", "padding": "12px 20px", "borderRadius": "8px", "margin": "0 5px", "color": "black"}),
        dbc.Tab(label="Pie Chart", tab_id="pie-chart", 
                active_tab_style={"textTransform": "uppercase", "fontWeight": "bold", "backgroundColor": "#3498db", "color": "white"},
                tab_style={"fontSize": "14px", "padding": "12px 20px", "borderRadius": "8px", "margin": "0 5px", "color": "black"}),
        dbc.Tab(label="Funnel", tab_id="funnel", 
                active_tab_style={"textTransform": "uppercase", "fontWeight": "bold", "backgroundColor": "#3498db", "color": "white"},
                tab_style={"fontSize": "14px", "padding": "12px 20px", "borderRadius": "8px", "margin": "0 5px", "color": "black"}),
    ], id="internal-subtabs", active_tab="population-stats", className="mb-4"),
    html.Div(id="internal-subtab-content", className="tab-content")
], className="dashboard-container")

# Update population statistics layout
population_stats_layout = [
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5("Population Statistics", 
                            className="mb-0 text-center",
                            style={'color': 'white', 'fontWeight': '600', 'fontSize': '18px'})
                ], className="card-header"),
                dbc.CardBody([
                    html.Div([
                        html.Label("Select Variable:", 
                                 className="form-label mb-3",
                                 style={'fontWeight': '600', 'fontSize': '16px', 'color': '#2c3e50'}),
                        dcc.Dropdown(
                            id='popstat-drop',
                            options=[{'label': col, 'value': col} for col in ['Zip Code', 'Age at Sign Up', 'Age Now',
                                'School', 'District', 'Race/Ethnicity', 'Gender', 'Income Range (Thousands)']],
                            value='District',
                            style={'marginBottom': '20px', 'fontSize': '14px'}
                        )
                    ], className="dropdown-container"),
                    html.Div(id='popstat-table-container', 
                            style={'height': '550px', 'overflowY': 'auto'},
                            className="graph-container")
                ], className="card-body")
            ], className='card')
        ], width=12)
    ])
]

# Update frequency tables layout
frequency_tables_layout = [
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5("Single Variable Frequency Table", 
                           className="mb-0 text-center",
                           style={'color': 'white', 'fontWeight': '600'})
                ], className="card-header"),
                dbc.CardBody([
                    # 4 dropdowns for single variable frequency table
                    html.Div([
                        html.Div([
                            html.Label("Variable (Required):", 
                                     className="form-label mb-1", 
                                     style={'fontWeight': '600', 'fontSize': '12px', 'color': '#e74c3c'}),
                            dcc.Dropdown(
                                id='freq-single-var1',
                                placeholder="Select variable for frequency table...",
                                style={'marginBottom': '10px', 'fontSize': '12px'}
                            )
                        ], className="dropdown-container"),
                        html.Div([
                            html.Label("Filter Population:", 
                                     className="form-label mb-1", 
                                     style={'fontWeight': '500', 'fontSize': '12px'}),
                            dcc.Dropdown(
                                id='freq-single-var2',
                                placeholder="Select population filter...",
                                style={'marginBottom': '10px', 'fontSize': '12px'}
                            )
                        ], className="dropdown-container"),
                        html.Div([
                            html.Label("Filter Value:", 
                                     className="form-label mb-1", 
                                     style={'fontWeight': '500', 'fontSize': '12px'}),
                            dcc.Dropdown(
                                id='freq-single-var3',
                                placeholder="Select filter value...",
                                style={'marginBottom': '10px', 'fontSize': '12px'}
                            )
                        ], className="dropdown-container"),
                        html.Div([
                            html.Label("Year Slice:", 
                                     className="form-label mb-1", 
                                     style={'fontWeight': '500', 'fontSize': '12px'}),
                            dcc.Dropdown(
                                id='freq-single-var4',
                                placeholder="Select year...",
                                style={'marginBottom': '10px', 'fontSize': '12px'}
                            )
                        ], className="dropdown-container")
                    ]),
                    html.Div(id='single-freq-results', 
                            style={'height': '400px', 'overflowY': 'auto'},
                            className="graph-container")
                ], className="card-body")
            ], className='card mb-4')
        ], width=6),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5("Multi Variable Frequency Table", 
                           className="mb-0 text-center",
                           style={'color': 'white', 'fontWeight': '600'})
                ], className="card-header"),
                dbc.CardBody([
                    # 5 dropdowns for multi variable frequency table
                    html.Div([
                        html.Div([
                            html.Label("Variable 1 (Required):", 
                                     className="form-label mb-1", 
                                     style={'fontWeight': '600', 'fontSize': '12px', 'color': '#e74c3c'}),
                            dcc.Dropdown(
                                id='freq-multi-var1',
                                placeholder="Select first variable...",
                                style={'marginBottom': '10px', 'fontSize': '12px'}
                            )
                        ], className="dropdown-container"),
                        html.Div([
                            html.Label("Variable 2 (Required):", 
                                     className="form-label mb-1", 
                                     style={'fontWeight': '600', 'fontSize': '12px', 'color': '#e74c3c'}),
                            dcc.Dropdown(
                                id='freq-multi-var2',
                                placeholder="Select second variable...",
                                style={'marginBottom': '10px', 'fontSize': '12px'}
                            )
                        ], className="dropdown-container"),
                        html.Div([
                            html.Label("Filter Population:", 
                                     className="form-label mb-1", 
                                     style={'fontWeight': '500', 'fontSize': '12px'}),
                            dcc.Dropdown(
                                id='freq-multi-var3',
                                placeholder="Select population filter...",
                                style={'marginBottom': '10px', 'fontSize': '12px'}
                            )
                        ], className="dropdown-container"),
                        html.Div([
                            html.Label("Filter Value:", 
                                     className="form-label mb-1", 
                                     style={'fontWeight': '500', 'fontSize': '12px'}),
                            dcc.Dropdown(
                                id='freq-multi-var4',
                                placeholder="Select filter value...",
                                style={'marginBottom': '10px', 'fontSize': '12px'}
                            )
                        ], className="dropdown-container"),
                        html.Div([
                            html.Label("Year Slice:", 
                                     className="form-label mb-1", 
                                     style={'fontWeight': '500', 'fontSize': '12px'}),
                            dcc.Dropdown(
                                id='freq-multi-var5',
                                placeholder="Select year...",
                                style={'marginBottom': '10px', 'fontSize': '12px'}
                            )
                        ], className="dropdown-container")
                    ]),
                    html.Div(id='multi-freq-results', 
                            style={'height': '400px', 'overflowY': 'auto'},
                            className="graph-container")
                ], className="card-body")
            ], className='card mb-4')
        ], width=6)
    ])
]

# Pie Chart Generator layout
pie_chart_layout = [
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5("Pie Chart Generator", className="mb-0 text-center", style={'color': '#34495e', 'fontWeight': '600'})
                ]),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Choose Population"),
                            dcc.Dropdown(
                                id='analytics-population-drop',
                                options=[
                                    {'label': 'Race/Ethnicity', 'value': 'Race/Ethnicity'},
                                    {'label': 'Gender', 'value': 'Gender'},
                                    {'label': 'District', 'value': 'District'},
                                    {'label': 'School', 'value': 'School'},
                                    {'label': 'Zip Code', 'value': 'Zip Code'},
                                ],
                                value='Race/Ethnicity',
                                clearable=False,
                                style={'marginBottom': '10px'}
                            ),
                        ], width=6),
                        dbc.Col([
                            html.Label("Choose Feature"),
                            dcc.Dropdown(
                                id='analytics-feature-drop',
                                options=[
                                    {'label': 'Hours', 'value': 'Hours'},
                                    {'label': 'Service Count', 'value': 'Service Count'},
                                    {'label': 'Responses', 'value': 'Responses'},
                                    {'label': 'Follow Through', 'value': 'Follow Through'},
                                    {'label': 'Trip Eligible (Yes Only)', 'value': 'Trip Eligible (Yes Only)'},
                                    {'label': 'Learn Participation (Yes Only)', 'value': 'Learn Participation (Yes Only)'},
                                    {'label': 'Explore Participation (Yes Only)', 'value': 'Explore Participation (Yes Only)'},
                                    {'label': 'Make It Happen Badge (Yes Only)', 'value': 'Make It Happen Badge (Yes Only)'},
                                    {'label': 'Scholarship Badge (Yes Only)', 'value': 'Scholarship Badge (Yes Only)'},
                                ],
                                value='Hours',
                                clearable=False,
                                style={'marginBottom': '10px'}
                            ),
                            html.Label("Smallest Portion Shown:", className="form-label mb-2", style={'fontWeight': '500', 'fontSize': '14px'}),
                            dcc.Dropdown(
                            id='pie-min-portion-drop',
                            options=[
                                {'label': '1%', 'value': 0.01},
                                {'label': '2%', 'value': 0.02},
                                {'label': '3%', 'value': 0.03},
                                {'label': '5%', 'value': 0.05},
                                {'label': '10%', 'value': 0.10},
                            ],
                            value=0.01,
                            style={'marginBottom': '10px'}
                        ),
                        ], width=6),
                    ]),
                    dcc.Graph(id='analytics-pie-chart', style={'height': '350px'})
                ])
            ], className='shadow-sm', style={'height': '100%'})
        ], width=12)
    ], className="mb-3"),
]


# Funnel layout
funnel_layout = [
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5("Student Volunteer Funnel", 
                           className="mb-0 text-center",
                           style={'color': '#34495e', 'fontWeight': '600'})
                ]),
                dbc.CardBody([
                    dcc.Graph(id='funnel-chart', style={'height': '600px'})
                ])
            ], className='shadow-lg', style={'height': '700px', 'borderRadius': '12px'})
        ], width=12)
    ])
]



# File uploader layout
file_uploader_layout = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5("Data Upload", 
                           className="mb-0 text-center",
                           style={'color': 'white', 'fontWeight': '600', 'fontSize': '18px'})
                ], className="card-header"),
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-cloud-upload-alt fa-3x mb-3", 
                               style={'color': '#3498db'}),
                        html.H4("Upload Your Dataset", 
                               className="mb-3",
                               style={'color': '#2c3e50', 'fontWeight': '600'}),
                        html.P("Drag and drop your Excel file here or click to browse", 
                              className="text-muted mb-4"),
                        dcc.Upload(
                            id='upload-data',
                            children=html.Div([
                                html.I(className="fas fa-file-excel me-2"),
                                'Drag and Drop or ',
                                html.A('Select Files')
                            ]),
                            style={
                                'width': '100%',
                                'height': '60px',
                                'lineHeight': '60px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'margin': '10px'
                            },
                            multiple=False
                        )
                    ], className="upload-area text-center")
                ], className="card-body")
            ], className='card mb-4')
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5("Upload Status", 
                           className="mb-0 text-center",
                           style={'color': 'white', 'fontWeight': '600'})
                ], className="card-header"),
                dbc.CardBody([
                    html.Div(id='upload-status', className="mb-3"),
                    html.Div([
                        html.H6("Dataset Information", 
                               className="mb-3",
                               style={'color': '#2c3e50', 'fontWeight': '600'}),
                        html.Div([
                            html.Div([
                                html.I(className="fas fa-file me-2"),
                                html.Span("File: ", style={'fontWeight': '600'}),
                                html.Span(id='dataset-file-info')
                            ], className="mb-2"),
                            html.Div([
                                html.I(className="fas fa-users me-2"),
                                html.Span("Total Clients: ", style={'fontWeight': '600'}),
                                html.Span(id='dataset-client-count')
                            ], className="mb-2"),
                            html.Div([
                                html.I(className="fas fa-clock me-2"),
                                html.Span("Total Service Hours Records: ", style={'fontWeight': '600'}),
                                html.Span(id='dataset-hours-count')
                            ], className="mb-2"),
                            html.Div([
                                html.I(className="fas fa-check-circle me-2"),
                                html.Span("Status: ", style={'fontWeight': '600'}),
                                html.Span(id='dataset-status', className="status-indicator")
                            ])
                        ], style={'fontSize': '14px', 'color': '#2c3e50'})
                    ])
                ], className="card-body")
            ], className='card')
        ], width=12)
    ])
], className="dashboard-container")

# CALLBACKS

# Tab switching
from dash import ctx, MATCH

# Sidebar toggle callback
@callback(
    [Output("sidebar-collapsed", "data"),
     Output("sidebar", "style"),
     Output("sidebar", "className"),
     Output("main-content", "width"),
     Output("dashboard-text", "style"),
     Output("internal-text", "style"),
     Output("uploader-text", "style")],
    [Input("sidebar-toggle", "n_clicks")],
    [State("sidebar-collapsed", "data")],
    prevent_initial_call=True
)
def toggle_sidebar(n_clicks, collapsed):
    if n_clicks is None:
        return collapsed, {}, "sidebar", 10, {}, {}, {}
    
    new_collapsed = not collapsed
    
    if new_collapsed:
        # Collapsed state - much narrower
        sidebar_style = {
            'padding': '15px 8px', 
            'height': '100vh', 
            'minWidth': '50px', 
            'maxWidth': '50px',
            'width': '50px',
            'transition': 'all 0.3s ease',
            'overflow': 'hidden'
        }
        sidebar_class = "sidebar collapsed"
        main_width = 11
        text_style = {'display': 'none'}
    else:
        # Expanded state
        sidebar_style = {
            'padding': '25px 15px', 
            'height': '100vh', 
            'minWidth': '250px',
            'width': '250px',
            'transition': 'all 0.3s ease'
        }
        sidebar_class = "sidebar"
        main_width = 10
        text_style = {'display': 'inline'}
    
    return new_collapsed, sidebar_style, sidebar_class, main_width, text_style, text_style, text_style

# Callback to update the active tab in dcc.Store when a NavLink is clicked
@callback(
    Output("active-tab-store", "data"),
    [Input("tab-dashboard", "n_clicks"),
     Input("tab-internal", "n_clicks"),
     Input("tab-file-uploader", "n_clicks")],
    [State("active-tab-store", "data")],
    prevent_initial_call=True
)
def update_active_tab(dash, internal, uploader, current):
    triggered = ctx.triggered_id
    if triggered == "tab-dashboard":
        return "dashboard"
    elif triggered == "tab-internal":
        return "internal"
    elif triggered == "tab-file-uploader":
        return "file-uploader"
    return current

# Callback to update the 'active' property of each NavLink based on the current tab
@callback(
    [Output("tab-dashboard", "active"),
     Output("tab-internal", "active"),
     Output("tab-file-uploader", "active")],
    Input("active-tab-store", "data")
)
def update_sidebar_active(tab):
    return [tab == "dashboard", tab == "internal", tab == "file-uploader"]

@callback(
    Output("tab-content", "children"),
    Input("active-tab-store", "data")
)
def render_tab_content(active_tab):
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
    if active_subtab == "population-stats":
        return population_stats_layout
    elif active_subtab == "frequency-tables":
        return frequency_tables_layout
    elif active_subtab == "pie-chart":
        return pie_chart_layout
    elif active_subtab == "chi-square":
        return chi_square_layout
    elif active_subtab == "funnel":
        return funnel_layout
    return population_stats_layout

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
    if contents is None:
        return (
            dbc.Alert("No file uploaded", color="info", className="status-indicator"),
            "", "No file loaded", "Total Clients: 0", "Total Service Hours Records: 0", 
            html.Span("No file uploaded", className="status-indicator status-warning")
        )
    
    try:
        # Decode the uploaded file
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        # Read Excel file
        excel_file = pd.ExcelFile(io.BytesIO(decoded))
        print("Excel sheet names:", excel_file.sheet_names)
        
        # Only require 'Clients' and 'Service Hours' for upload
        required_sheets = ['Clients', 'Service Hours']
        missing_sheets = [sheet for sheet in required_sheets if sheet not in excel_file.sheet_names]
        
        if missing_sheets:
            return (
                dbc.Alert(
                    f"Error: Missing required sheets: {', '.join(missing_sheets)}. "
                    f"Found sheets: {', '.join(excel_file.sheet_names)}",
                    color="danger",
                    className="status-indicator status-error"
                ), 
                "", "File: No file loaded", "Total Clients: 0", "Total Service Hours Records: 0", 
                html.Span("Upload failed", className="status-indicator status-error")
            )
        
        # Read the sheets
        clients_raw = pd.read_excel(io.BytesIO(decoded), sheet_name='Clients')
        hours = (pd.read_excel(io.BytesIO(decoded), sheet_name='Service Hours')
                .rename({'userId': 'Galaxy ID'}, axis=1))
        
        # Try to load 'Likert Scale' sheet for survey_raw
        if 'Likert Scale' in excel_file.sheet_names:
            survey_raw = pd.read_excel(io.BytesIO(decoded), sheet_name='Likert Scale')
            print("Likert DataFrame shape:", survey_raw.shape)
            print("Likert DataFrame columns:", list(survey_raw.columns))
        else:
            survey_raw = pd.DataFrame()  # fallback if not present
        
        # Process the data
        clients, schoolclub_hours, qtr_vol_counts = process_uploaded_data(
            clients_raw, hours, survey_raw, county_zips, zip_incomes, 
            county_incomes, schools_with_clubs, yes_no_cols
        )
        
        # Update global variables
        globals().update({
            'clients_raw': clients_raw,
            'hours': hours,
            'survey_raw': survey_raw,
            'clients': clients,
            'schoolclub_hours': schoolclub_hours,
            'qtr_vol_counts': qtr_vol_counts
        })
        
        # Update dashboard_components globals
        dashboard_components.hours = hours
        dashboard_components.clients = clients
        
        # Create summary
        summary = create_processing_summary(clients_raw, hours, survey_raw, clients, schoolclub_hours, qtr_vol_counts, filename)
        
        return (
            dbc.Alert(
                f"Successfully uploaded {filename}",
                color="success",
                className="status-indicator status-success"
            ),
            summary,
            f"File: {filename}",
            f"Total Clients: {len(clients_raw)}",
            f"Total Service Hours Records: {len(hours)}",
            html.Span("Upload successful", className="status-indicator status-success")
        )
        
    except Exception as e:
        return (
            dbc.Alert(
                f"Error processing file: {str(e)}",
                color="danger",
                className="status-indicator status-error"
            ),
            "", "File: Error processing", "Total Clients: 0", "Total Service Hours Records: 0",
            html.Span("Upload failed", className="status-indicator status-error")
        )

# Update all dashboard components when data changes
@callback(
    [Output('club-comparison-chart', 'figure'),
     Output('club-confidence-intervals', 'children'),
     Output('total-value-display', 'children')],
    [Input('data-store', 'children')]
)
def update_dashboard_components(data_store):
    # Create all dashboard components using our modular functions
    club_fig, club_intervals = create_club_comparison_chart(schoolclub_hours)
    total_value = f"${calculate_hours_value(clients)}"
    
    return club_fig, club_intervals, total_value

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
                config={'responsive': True, 'displayModeBar': True, 'modeBarButtonsToRemove': ['lasso2d', 'select2d', 'toggleSpikelines']}
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
                config={'responsive': True, 'displayModeBar': True, 'modeBarButtonsToRemove': ['lasso2d', 'select2d', 'toggleSpikelines']}
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
                config={'responsive': True, 'displayModeBar': True, 'modeBarButtonsToRemove': ['lasso2d', 'select2d', 'toggleSpikelines']}
            )
        
        elif map_type == 'zipcode_hours':
            fig = create_zipcode_map()
            return dcc.Graph(
                figure=fig,
                style={'height': '750px', 'width': '100%'},
                config={'responsive': True, 'displayModeBar': True, 'modeBarButtonsToRemove': ['lasso2d', 'select2d', 'toggleSpikelines']}
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

# Frequency Tables Callbacks

# Single Variable Frequency Table Callback
@callback(
    Output('single-freq-results', 'children'),
    [Input('freq-single-var1', 'value'),
     Input('freq-single-var2', 'value'),
     Input('freq-single-var3', 'value'),
     Input('freq-single-var4', 'value'),
     Input('data-store', 'children')]
)
def update_single_frequency_table(variable, filter_pop, filter_value, year_slice, data_store):
    """Generate single variable frequency table"""
    # Use global clients DataFrame from New_Dashboard.py
    global clients
    from dashboard_components import single_var_freq
    
    # Update dashboard_components globals to ensure they have the latest data
    import dashboard_components
    dashboard_components.clients = clients
    
    if clients.empty:
        return html.Div([
            html.P("Upload data to generate frequency tables", 
                   className="text-muted text-center",
                   style={'padding': '20px'})
        ])
    
    if not variable:
        return html.Div([
            html.P("Please select a variable to generate frequency table", 
                   className="text-muted text-center",
                   style={'padding': '20px', 'fontSize': '14px'})
        ])
    
    try:
        # Set up parameters for single_var_freq function
        pop = filter_pop if filter_pop and filter_pop != 'all' else 'all'
        pop_value = filter_value if filter_value is not None else None
        slice_param = year_slice if year_slice and year_slice != 'all' else 'all'
        
        # Generate frequency table
        freq_table = single_var_freq(variable, pop=pop, pop_value=pop_value, slice=slice_param)
        
        if freq_table.empty:
            return html.Div([
                html.P("No data available for the selected parameters", 
                       className="text-muted text-center",
                       style={'padding': '20px'}),
                html.P("Try selecting different filter values or check if data exists for the selected criteria", 
                       className="text-muted text-center",
                       style={'padding': '5px', 'fontSize': '12px'})
            ])
        
        # Create title with parameters
        title_parts = [f"Frequency Table: {variable}"]
        if pop != 'all' and pop_value is not None:
            title_parts.append(f"Filtered by {pop} = {pop_value}")
        if slice_param != 'all':
            title_parts.append(f"Year: {slice_param}")
        
        title = " | ".join(title_parts)
        
        # Format the frequency table for display
        freq_table.columns = [variable, 'Count']
        
        # Add summary statistics
        total_count = freq_table['Count'].sum()
        unique_values = len(freq_table)
        
        return html.Div([
            html.H6(title, style={'fontSize': '14px', 'fontWeight': 'bold', 'marginBottom': '10px'}),
            html.P(f"Total records: {total_count:,} | Unique values: {unique_values}", 
                   style={'fontSize': '12px', 'color': '#666', 'marginBottom': '10px'}),
            dbc.Table.from_dataframe(
                freq_table, 
                striped=True, 
                bordered=True, 
                hover=True,
                size='sm',
                style={'fontSize': '12px', 'width': '100%'},
                responsive=True
            )
        ], style={'padding': '10px'})
        
    except Exception as e:
        return html.Div([
            html.P(f"Error generating frequency table: {str(e)}", 
                   className="text-danger text-center",
                   style={'padding': '20px', 'fontSize': '14px'})
        ])

# Multivariable Frequency Table Callback  
@callback(
    Output('multi-freq-results', 'children'),
    [Input('freq-multi-var1', 'value'),
     Input('freq-multi-var2', 'value'),
     Input('freq-multi-var3', 'value'),
     Input('freq-multi-var4', 'value'),
     Input('freq-multi-var5', 'value'),
     Input('data-store', 'children')]
)
def update_multi_frequency_table(var1, var2, filter_pop, filter_value, year_slice, data_store):
    """Generate multivariable frequency tables (cross-tabulations)"""
    # Use global clients DataFrame from New_Dashboard.py
    global clients
    from dashboard_components import multi_var_freq
    
    # Update dashboard_components globals to ensure they have the latest data
    import dashboard_components
    dashboard_components.clients = clients
    
    if clients.empty:
        return html.Div([
            html.P("Upload data to generate cross-tabulations", 
                   className="text-muted text-center",
                   style={'padding': '20px'})
        ])
    
    if not var1 or not var2:
        return html.Div([
            html.P("Please select both variables to generate cross-tabulation", 
                   className="text-muted text-center",
                   style={'padding': '20px', 'fontSize': '14px'})
        ])
    
    try:
        # Set up parameters for multi_var_freq function
        pop = filter_pop if filter_pop and filter_pop != 'all' else 'all'
        pop_value = filter_value if filter_value is not None else None
        slice_param = year_slice if year_slice and year_slice != 'all' else 'all'
        
        # Generate cross-tabulation
        crosstab = multi_var_freq(var1, var2, pop=pop, pop_value=pop_value, slice=slice_param)
        
        if crosstab.empty:
            return html.Div([
                html.P("No data available for the selected parameters", 
                       className="text-muted text-center",
                       style={'padding': '20px'}),
                html.P("Try selecting different filter values or check if data exists for the selected criteria", 
                       className="text-muted text-center",
                       style={'padding': '5px', 'fontSize': '12px'})
            ])
        
        # Create title with parameters
        title_parts = [f"Cross-tabulation: {var1} × {var2}"]
        if pop != 'all' and pop_value is not None:
            title_parts.append(f"Filtered by {pop} = {pop_value}")
        if slice_param != 'all':
            title_parts.append(f"Year: {slice_param}")
        
        title = " | ".join(title_parts)
        
        # Convert crosstab to dataframe for display
        crosstab_df = crosstab.reset_index()
        
        # Add summary statistics
        total_count = crosstab_df.iloc[:, 1:].sum().sum()
        rows = len(crosstab_df)
        cols = len(crosstab_df.columns) - 1
        
        return html.Div([
            html.H6(title, style={'fontSize': '14px', 'fontWeight': 'bold', 'marginBottom': '10px'}),
            html.P(f"Total records: {total_count:,} | Rows: {rows} | Columns: {cols}", 
                   style={'fontSize': '12px', 'color': '#666', 'marginBottom': '10px'}),
            dbc.Table.from_dataframe(
                crosstab_df,
                striped=True,
                bordered=True,
                hover=True,
                size='sm',
                style={'fontSize': '12px', 'width': '100%'},
                responsive=True
            )
        ], style={'padding': '10px'})
        
    except Exception as e:
        return html.Div([
            html.P(f"Error generating cross-tabulation: {str(e)}", 
                   className="text-danger text-center",
                   style={'padding': '20px', 'fontSize': '14px'})
        ])

# Update dropdown options when data changes
@callback(
    [Output('freq-single-var1', 'options'),
     Output('freq-single-var2', 'options'),
     Output('freq-single-var4', 'options'),
     Output('freq-multi-var1', 'options'),
     Output('freq-multi-var2', 'options'),
     Output('freq-multi-var3', 'options'),
     Output('freq-multi-var5', 'options')],
    Input('data-store', 'children')
)
def update_frequency_dropdown_options(data_store):
    """Update dropdown options based on available data columns"""
    if clients.empty:
        empty_options = [{'label': 'Upload data first', 'value': None}]
        return [empty_options] * 7
    
    # Get categorical columns suitable for frequency analysis
    categorical_columns = ['District', 'School', 'Race/Ethnicity', 'Gender', 'County', 
                          'Income Range (Thousands)', 'Age at Sign Up', 'Age Now',
                          'Follow Through', 'Club', 'Learn Participation 2022', 
                          'Explore Participation', 'Make It Happen Badge (Yes/No)',
                          'Trip Eligible (Yes/No)', 'Scholarship Badge (Yes/No)',
                          'Zip Code']
    
    # Filter to only include columns that exist in the data
    available_columns = [col for col in categorical_columns if col in clients.columns]
    
    # Variable options (for dropdowns 1)
    var_options = [{'label': col, 'value': col} for col in available_columns]
    var_options.insert(0, {'label': 'Select variable...', 'value': None})
    
    # Filter population options (from filter_populations)
    filter_pop_options = [{'label': pop, 'value': pop} for pop in filter_populations if pop in clients.columns]
    filter_pop_options.insert(0, {'label': 'All (no filter)', 'value': 'all'})
    
    # Year options (from hours data if available)
    year_options = [{'label': 'All years', 'value': 'all'}]
    if not hours.empty and 'Event Date' in hours.columns:
        years = sorted(hours['Event Date'].dt.year.unique())
        year_options.extend([{'label': str(year), 'value': year} for year in years])
    
    return (
        var_options,  # freq-single-var1 (variable)
        filter_pop_options,  # freq-single-var2 (filter population)
        year_options,  # freq-single-var4 (year slice)
        var_options,  # freq-multi-var1 (variable 1)
        var_options,  # freq-multi-var2 (variable 2)  
        filter_pop_options,  # freq-multi-var3 (filter population)
                 year_options   # freq-multi-var5 (year slice)
     )

# Update filter value options based on selected filter population
@callback(
    Output('freq-single-var3', 'options'),
    [Input('freq-single-var2', 'value'),
     Input('data-store', 'children')]
)
def update_single_filter_values(filter_pop, data_store):
    """Update filter value options based on selected filter population"""
    # Import here to ensure we're using the latest global dataframes
    from dashboard_components import clients
    
    if clients.empty or not filter_pop or filter_pop == 'all':
        return [{'label': 'No filter selected', 'value': None}]
    
    if filter_pop in clients.columns:
        unique_values = sorted(clients[filter_pop].dropna().unique())
        # Convert to regular Python int for binary columns (Follow Through, Club) 
        # to ensure proper type matching
        if filter_pop in ['Follow Through', 'Club']:
            try:
                options = [{'label': str(val), 'value': int(val)} for val in unique_values]
            except (ValueError, TypeError):
                options = [{'label': str(val), 'value': val} for val in unique_values]
        else:
            options = [{'label': str(val), 'value': val} for val in unique_values]
        options.insert(0, {'label': 'Select value...', 'value': None})
        return options
    
    return [{'label': 'Invalid filter population', 'value': None}]

@callback(
    Output('freq-multi-var4', 'options'),
    [Input('freq-multi-var3', 'value'),
     Input('data-store', 'children')]
)
def update_multi_filter_values(filter_pop, data_store):
    """Update filter value options based on selected filter population"""
    # Import here to ensure we're using the latest global dataframes
    from dashboard_components import clients
    
    if clients.empty or not filter_pop or filter_pop == 'all':
        return [{'label': 'No filter selected', 'value': None}]
    
    if filter_pop in clients.columns:
        unique_values = sorted(clients[filter_pop].dropna().unique())
        # Convert to regular Python int for binary columns (Follow Through, Club) 
        # to ensure proper type matching
        if filter_pop in ['Follow Through', 'Club']:
            try:
                options = [{'label': str(val), 'value': int(val)} for val in unique_values]
            except (ValueError, TypeError):
                options = [{'label': str(val), 'value': val} for val in unique_values]
        else:
            options = [{'label': str(val), 'value': val} for val in unique_values]
        options.insert(0, {'label': 'Select value...', 'value': None})
        return options
    
    return [{'label': 'Invalid filter population', 'value': None}]

# Combined volunteers time chart callback
@callback(
    Output('volunteers-time-chart', 'figure'),
    [Input('time-period-dropdown', 'value'),
     Input('data-store', 'children')]
)
def update_volunteers_time_chart(time_period, data_store):
    """Update the volunteers chart based on selected time period (quarter or month)"""
    if time_period == 'quarter':
        if qtr_vol_counts.empty:
            return create_quarter_volunteers_chart(pd.DataFrame())
        return create_quarter_volunteers_chart(qtr_vol_counts)
    
    elif time_period == 'month':
        if hours.empty:
            return create_monthly_volunteers_chart(pd.DataFrame())
        return create_monthly_volunteers_chart(hours)
    
    # Default to quarter view
    return create_quarter_volunteers_chart(qtr_vol_counts)

# Funnel chart callback
@callback(
    Output('funnel-chart', 'figure'),
    Input('data-store', 'children')
)
def update_funnel_chart(data_store):
    """Update the funnel chart when data changes"""
    return create_funnel_chart()



# Pie chart generator callback
@callback(
    Output('analytics-pie-chart', 'figure'),
    Input('analytics-population-drop', 'value'),
    Input('analytics-feature-drop', 'value'),
    Input('pie-min-portion-drop', 'value'),
    Input('data-store', 'children')
)
def update_custom_pie(population, feature, min_portion, data_store):
    if clients.empty or not population or not feature:
        return px.pie(title="No data")
    df = clients.copy()

    # Map dropdown values to actual DataFrame columns
    feature_map = {
        'Trip Eligible (Yes Only)': 'Trip Eligible (Yes/No)',
        'Learn Participation (Yes Only)': 'Learn Participation 2022',
        'Explore Participation (Yes Only)': 'Explore Participation',
        'Make It Happen Badge (Yes Only)': 'Make It Happen Badge (Yes/No)',
        'Scholarship Badge (Yes Only)': 'Scholarship Badge (Yes/No)',
        'Hours': 'Hours',
        'Service Count': 'Service Count',
        'Responses': 'Responses',
        'Follow Through': 'Follow Through'
    }
    col = feature_map.get(feature, feature)

    yes_no_features = [
        'Trip Eligible (Yes Only)', 'Learn Participation (Yes Only)', 'Explore Participation (Yes Only)',
        'Make It Happen Badge (Yes Only)', 'Scholarship Badge (Yes Only)'
    ]
    if feature in yes_no_features:
        if col not in df.columns:
            return px.pie(title=f"Feature '{col}' not found in data")
        # Clean and filter for "yes" responses robustly
        filtered = df[df[col] == 1]
        if filtered.empty:
            return px.pie(title=f"No students marked 'Yes' for {feature}")
        values = filtered.groupby(population).size()
        name = "Count"
    else:
        if col not in df.columns:
            return px.pie(title=f"Feature '{col}' not found in data")
        values = df.groupby(population)[col].sum()
        name = col
    if values.sum() == 0:
        return px.pie(title="No data to display")
    values = values[(values / values.sum()) >= min_portion]
    if values.empty:
        return px.pie(title="No group meets the minimum portion threshold")
    fig = px.pie(
        names=values.index,
        values=values.values,
        title=f"{feature} by {population} (min {int(min_portion*100)}%)",
        labels={name: feature}
    )
    fig.update_traces(textinfo='percent+label')
    return fig

@callback(
    Output('senior-survey-likert-pie', 'figure'),
    Input('senior-survey-likert-question-drop', 'value')
)
def update_senior_survey_likert_pie(selected_question):
    return get_likert_pie_figure(survey_raw, selected_question)

@callback(
    Output("senior-survey-card-container", "children"),
    Input("data-store", "children")
)
def update_senior_survey_card(_):
    return create_likert_pie_card(survey_raw, card_id_prefix="senior-survey")

if __name__ == '__main__':
    Timer(1, lambda: webbrowser.open("http://localhost:8000")).start()
    app.run(debug=False, host='localhost', port=8000) 