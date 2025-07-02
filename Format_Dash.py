import pandas as pd
import datetime as dt
import statistics as stat
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import Dash, dcc, callback, Output, Input, html
import webbrowser
from threading import Timer
import datetime as dt
from scipy import stats as scipystat
import math


#Load dataset
file_path = '/Users/joelwilson/Desktop/SOS-Data-project-1/UTSA Client Dataset - Students of Service (SOS).xlsx'

clients_raw = pd.read_excel(file_path, sheet_name='Clients')  #Convert dates to datetime objects

hours = (pd.read_excel(file_path, sheet_name='Service Hours') #Rename the userID column to 'Galaxy ID'
         .rename({'userId': 'Galaxy ID'}, axis=1)
)

survey_raw = pd.read_excel(file_path, sheet_name='Survey Responses')


#Zip code lists for county assignemnts

bexar_zips = [78245,78254,78249,78253,78251,
78228,78250,78240,78247,78207,
78223,78258,78201,78227,78230,
78233,78213,78221,78216,
78109,78209,78244,78237,
78218,78232,78260,78210,78023,
78229,78217,78242,78239,78211,
78238,78212,78222,78259,78261,
78148,78214,78224,78015,78219,
78220,78255,78248,78264,
78252,78225,78204,78256,
78073,78202,78112,78231,
78236,78002,78226,78203,
78257,78263,78208,
78215,78152,78234,78205,78235,
78243,78206,78262,78275,78286,
78287,78054,78150,78241,78246,
78265,78268,78270,78269,78278,
78280,78279,78284,78283,78285,
78288,78291,78289,78293,78292,
78295,78294,78297,78296,78299,
78298]

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

all_zips = []

for key in county_zips:
    for i in county_zips[key]:
        all_zips.append(i)

zips_for_incomes = [78002, 78003, 78004, 78006, 78008, 78009, 
                    78011, 78012, 78013, 78015, 78016, 78023, 
                    78026, 78027, 78039, 78050, 78052, 78055, 
                    78056, 78057, 78059, 78062, 78063, 78064, 
                    78065, 78066, 78069, 78070, 78073, 78074, 
                    78101, 78108, 78109, 78112, 78113, 78114, 
                    78121, 78123, 78124, 78130, 78132, 78133, 
                    78140, 78143, 78147, 78148, 78150, 78152, 
                    78154, 78155, 78160, 78161, 78163, 78201, 
                    78202, 78203, 78204, 78205, 78207, 78208, 
                    78209, 78210, 78211, 78212, 78213, 78214, 
                    78215, 78216, 78217, 78218, 78219, 78220, 
                    78221, 78222, 78223, 78224, 78225, 78226, 
                    78227, 78228, 78229, 78230, 78231, 78232, 
                    78233, 78234, 78235, 78236, 78237, 78238, 
                    78239, 78240, 78242, 78243, 78244, 78245, 
                    78247, 78248, 78249, 78250, 78251, 78252, 
                    78253, 78254, 78255, 78256, 78257, 78258, 
                    78259, 78260, 78261, 78263, 78264, 78266, 
                    78606, 78623, 78638, 78648, 78655, 78666, 
                    78670, 78850, 78861, 78883, 78884, 78885, 78886]

zip_income_list = ['64082', '54500', '160147', '110955', '-', 
                    '102724', '29089', '47708', '79770', '155488', 
                    '57609', '129701', '77257', '108434', '74013', 
                    '91212', '69018', '71635', '122026', '63967', 
                    '72254', '-', '79066', '69407', '63653', 
                    '92813', '71071', '115076', '65342', '-', 
                    '90413', '117304', '87635', '54445', '90191', 
                    '84260', '126726', '95700', '82534', '84426', 
                    '126934', '80777', '49032', '-', '72961', 
                    '75395', '-', '102212', '97465', '71367', 
                    '62188', '75966', '133681', '46129', '43708', 
                    '34815', '54667', '34631', '30655', '23194', 
                    '84180', '51990', '54279', '60222', '53342', 
                    '41334', '82128', '55488', '56852', '56833', 
                    '52147', '41244', '63114', '64251', '50352', 
                    '57965', '46829', '32340', '48049', '50865', 
                    '46718', '71564', '103538', '84633', '73729', 
                    '100096', '64919', '96771', '40233', '56227', 
                    '71455', '62203', '48979', '-', '67789', 
                    '87890', '89184', '130605', '80851', '80289', 
                    '78025', '79635', '104260', '115823', '151673', 
                    '72797', '74540', '116133', '109429', '150705', 
                    '140120', '81793', '60245', '132470', '89980', 
                    '122143', '82760', '56533', '48409', '55478', 
                    '76591', '77344', '64491', '36189', '82292', '70833', '119276']

zip_incomes_withblanks = pd.DataFrame(data={'Zip Code': zips_for_incomes, 'Median Income': zip_income_list})

zip_incomes = zip_incomes_withblanks[zip_incomes_withblanks['Median Income'] != '-']

county_incomes = pd.DataFrame(data={'County': ['Kendall','Bandera','Comal','Guadalupe','Wilson','Atascosa','Medina', 'Bexar'],
                                     'Median Income':[110498,69073,99193,95953,92461,69413,73462,69807]})

def assign_zipincome(zip):
    if zip in zip_incomes['Zip Code'].values:
        return round((int(zip_incomes[zip_incomes['Zip Code']==zip]['Median Income'].values[0])))
    
def assign_countyincome(county):
    if county in county_incomes['County'].values:
        return round(int(county_incomes[county_incomes['County']==county]['Median Income'].values[0]))
    

#Clean clients dataset
clients_temp = (clients_raw[clients_raw['Galaxy ID'].notna()] #Remove rows with no Galaxy ID
                       .replace({'HS Graduation Year': '0', 'Age Now': 'Unknown'}, None) #Replace unknown ages and grad years with None instead of the string)
                       .replace({'Age at Sign Up' : {"Unknown":15, 0:15, 1:15, 4:15}}) #Replace unknown and too low ages at sign up with 16
                       .query('`Age at Sign Up` <= 20') #Filter out ages over 20
)

clients = clients_temp[clients_temp['dateAdded'] >= dt.datetime(2020, 1, 1)] #Filter out clients added before 2020

yes_no_cols = ['Learn Participation 2022', 
               'Explore Participation',
               'Make It Happen Badge (Yes/No)', 
               'Trip Eligible (Yes/No)',
               'Scholarship Badge (Yes/No)']

schools_with_clubs = ['Brackenridge High School','Whittier Middle School', 'Driscoll Middle school', 'Advanced Learning Academy', 
                      "Young Women's Leadership Academy", 'CAST Med High School', 'International School of the Americas', 'South San High School', 
                      'Churchill High School', 'Johnson High School', 'CAST Tech High School' , 'IDEA Converse', 'RISE Inspire Academy', 
                      'Nimitz Middle School', 'Thomas Jefferson High School', "Young Men's Leadership Academy", 'Southside High School']

#Convert Yes/No columns to 1/0
clients[yes_no_cols] = clients[yes_no_cols].replace({'Yes': 1, 'No': 0}) 

#Truncate zip coes to 5 digits
clients['Zip Code'] = pd.to_numeric(clients['Zip Code'].astype(str).str[:5]) 

#Create a new column for hours collected from hours table to compare to hours in original table
hours_sum = hours.groupby('Galaxy ID')['hours'].sum()
clients['Collected Hours'] = clients['Galaxy ID'].map(hours_sum) 

#Get earliest volunteer date for each ID
earliest_service = hours.groupby('Galaxy ID')['Event Date'].min()  
clients['Earliest Service'] = clients['Galaxy ID'].map(earliest_service)

#Get latest volunteer date for each ID
latest_service = hours.groupby('Galaxy ID')['Event Date'].max()   
clients['Latest Service'] = clients['Galaxy ID'].map(latest_service)

#Get total events per ID
service_count = hours.groupby('Galaxy ID')['Event Date'].count()  
clients['Service Count'] = clients['Galaxy ID'].map(service_count)

#Calculate active service length
clients['Service Range'] = clients['Latest Service'] - clients['Earliest Service']  

#Create a 'Follow Through' Column to show if client actualy volunteered after signing up
clients['Follow Through'] = np.where(clients['Hours']>0, 1, 0).astype(int) 

#Create 'Club' column to show if a club exists at a clients school
clients['Club'] = np.where(clients['School'].isin(schools_with_clubs),1,0).astype(int)

hours['qtr-year'] = (
    hours['Event Date'].dt.year.astype(str) +
    '-Q' + hours['Event Date'].dt.quarter.astype(str)
)

qtr_vol_counts = month_vol_counts = pd.DataFrame(
    list(hours.groupby('qtr-year')['Galaxy ID'].nunique().to_dict().items()), columns=['QTR', 'Active Volunteers']
)


#Match zip codes to counties
def county_assign(zip):            
    for key in county_zips.keys():
        if zip in county_zips[key]:
            return key

#Match zip codes to counties
clients['County'] = clients['Zip Code'].apply(county_assign)  

#Assign incomes by zip code or county
for id in clients['Galaxy ID'].values:   #iterate through galaxy ids

    zip_of_id = clients.loc[clients['Galaxy ID']==id, 'Zip Code'].values[0]   #obtain zip code for the galaxy id
    county_of_id = clients.loc[clients['Galaxy ID']==id, 'County'].values[0]  #obtain county for the galaxy id

    if zip_of_id in zip_incomes.values:  #check if the zip code has a zip specific income
        clients.loc[clients['Galaxy ID']==id, 'Median Family Income'] = assign_zipincome(zip_of_id)  #assign income based on zip code
    else:
        if county_of_id in county_zips.keys():   #check if county is in the area
            clients.loc[clients['Galaxy ID']==id, 'Median Family Income'] = assign_countyincome(county_of_id)   #assign income based on county
        else:
            clients.loc[clients['Galaxy ID']==id, 'Median Family Income'] = None  #if zip code is outside range, assign 'None' to income

#Change type of median family income to an integer
clients['Median Family Income'] = clients['Median Family Income'].astype('Int64')

#Create function to get an income range
def income_range(income):
    if pd.isnull(income): #ignore items with no income
        return None
    else:
        income_str = str(income)
        if len(income_str) <= 6:  # Handle cases where income has 6 or fewer digits
            return f"0 - 99"
        else:
            tens_thousands = income_str[:-6] if income_str[:-6] else "0"
            range_string = f'{int(tens_thousands)}0 - {int(tens_thousands)}9' #slice all but the thousands place then create range based off of that
            return range_string

#Create an income range column based on the income_range(income) function
clients['Income Range (Thousands)'] = clients['Median Family Income'].apply(income_range)

#get current year and month to iterate up to
curr_year=max(clients['Latest Service']).year
curr_month=max(clients['Latest Service']).month

def population_stat(df, col):
    """
    This function will create two dataframes based around the specific column provided.
    It will group the data in the specified column and return an Agg dataframe with multilevel columns and a flat dataframe with standard single-level columns
    
    Parameters:
    df: Dataframe (This should formatted specifically like the clients DataFrame)
    col: str (Columnn name to get population statistics for)

    Example:
    zip_agg, zip_flat = population_stat(clients, 'Zip Code')
    """
    #Define columns and stats to get for each one while aggregating the target dataframe by target column
    agg_name = df.groupby(by=col).agg(
        {'Galaxy ID': 'count',
        'Age at Sign Up': ['mean', 'median', 'min', 'max'],
        'Service Range': 'mean',
        'Hours': ['sum', 'mean'],
        'Follow Through': ['sum', 'mean'],
        'Trip Eligible (Yes/No)': ['sum', 'mean'],
        'Service Count': ['mean', 'sum'],
        'Responses' : ['mean', 'sum'],
        'Make It Happen Badge (Yes/No)': ['sum', 'mean'],
        'Scholarship Badge (Yes/No)': ['sum', 'mean'],
        'Explore Participation': ['sum', 'mean'],}
    )

    #Make service range stat more readable by only including days
    agg_name['Service Range'] = agg_name['Service Range','mean'].dt.days

    #Sort by frequency in dataframe and round all numbers to 2 decimal places
    agg_name.sort_values(by=('Galaxy ID', 'count'), ascending=False, inplace=True)
    agg_name = agg_name.round(2)

    #Create a flat dataframe that has no super headers for ease of calling
    flat_name = agg_name.copy()
    flat_name.columns = ['_'.join(col).strip() for col in flat_name.columns.values]
    flat_name.rename(columns={'Zip Code_': 'Zip Code'}, inplace=True)
    flat_name.reset_index(inplace=True)
    flat_name = flat_name.round(2)

    return agg_name, flat_name

#Get value of hours using 31 dollars per hour then format in dollar format
def get_hours_value():
    return '{:,.2f}'.format(clients['Hours'].sum()*31)

#Create dataframe with school based volunteer hours means depending on whether they have a club or not.
schoolclub_hours = clients.groupby(by='School').agg({'Hours':'sum'}).reset_index()
schoolclub_hours['Club'] = np.where(schoolclub_hours['School'].isin(schools_with_clubs),1,0).astype(str)

#returns the lower and upper margin of error limits for schools with clubs vs schools without clubs
def get_club_ci():
    alpha=0.05
    club_mu = schoolclub_hours[schoolclub_hours['Club']=='1']['Hours'].mean()
    club_sigma = stat.stdev(schoolclub_hours[schoolclub_hours['Club']=='1']['Hours'])
    club_n = len(schoolclub_hours[schoolclub_hours['Club']=='1'])
    club_conf_t = abs(round(scipystat.t.ppf(alpha/2, club_n-1),2))
    noclub_mu = schoolclub_hours[schoolclub_hours['Club']=='0']['Hours'].mean()
    noclub_sigma = stat.stdev(schoolclub_hours[schoolclub_hours['Club']=='0']['Hours'])
    noclub_n = len(schoolclub_hours[schoolclub_hours['Club']=='0'])
    noclub_conf_t = abs(round(scipystat.t.ppf(alpha/2, noclub_n-1),2))

    club_lower = round(club_mu - club_conf_t*(club_sigma/math.sqrt(club_n)),2)
    club_upper = round(club_mu + club_conf_t*(club_sigma/math.sqrt(club_n)),2)

    noclub_lower = round(noclub_mu - noclub_conf_t*(noclub_sigma/math.sqrt(noclub_n)),2)
    noclub_upper = round(noclub_mu + noclub_conf_t*(noclub_sigma/math.sqrt(noclub_n)),2)

    return club_lower, club_upper, noclub_lower, noclub_upper

club_low, club_high, noclub_low, noclub_high = get_club_ci()

#Create schools with club volunteer hours comparison bar chart
def club_hours_comparison_bar():
    clubhours_filter = schoolclub_hours.copy()
    clubhours_filter['Club'] = clubhours_filter['Club'].replace({'0':'No Club', '1':'Club'})
    chart = px.bar(clubhours_filter.groupby(by='Club')['Hours'].mean().reset_index(), x='Club', y='Hours')
    return chart

#holds values for line graph
vol_counts_store = {}
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
        # Main Dashboard Tab
        dbc.Tab(label="Dashboard", tab_id="dashboard", active_tab_style={"textTransform": "uppercase"}),
        # Secondary Tab  
        dbc.Tab(label="Analytics", tab_id="analytics", active_tab_style={"textTransform": "uppercase"}),
    ], id="tabs", active_tab="dashboard", className="mb-3"),
    
    # Tab content
    html.Div(id="tab-content")
    
], fluid=True, style={'height': '100vh', 'padding': '15px', 'backgroundColor': '#f8f9fa'})

# Main Dashboard Layout (Original layout with heatmap placeholder)
dashboard_layout = [
    # Top row
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
                            options=[{'label': f'Age {age}', 'value': age} 
                                    for age in sorted(clients['Age at Sign Up'].unique())],
                            value=16,
                            style={'marginBottom': '10px'}
                        )
                    ])
                ])
            ],
            className='shadow-sm',
            style={'height': '400px', 'marginBottom': '20px'}
            )
        ], width=4),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H6("Club vs No Club Comparison", 
                           className="mb-0 text-center",
                           style={'color': '#34495e', 'fontWeight': '600'})
                ]),
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-users fa-3x mb-3", 
                              style={'color': '#9b59b6'}),
                        dcc.Graph(figure=club_hours_comparison_bar()),
                        dcc.Markdown(f'Club C.I.: {club_low} - {club_high}\nNo Club C.I.: {noclub_low} - {noclub_high}')
                    ], className="d-flex flex-column align-items-center justify-content-center h-100")
                ])
            ],
            className='shadow-sm',
            style={'height': '400px', 'marginBottom': '20px'}
            )
        ], width=4),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H6("Active Volunteers by Quarter", 
                           className="mb-0 text-center",
                           style={'color': '#34495e', 'fontWeight': '600'})
                ]),
                dbc.CardBody([
                    dcc.Graph(
                        figure=px.line(qtr_vol_counts, x='QTR', y='Active Volunteers')
                                .update_layout(
                                    margin=dict(l=30, r=30, t=20, b=30),
                                    font=dict(size=12),
                                    height=340
                                ),
                        style={'height': '340px'}
                    )
                ])
            ],
            className='shadow-sm',
            style={'height': '400px', 'marginBottom': '20px'}
            )
        ], width=4)
    ], className="mb-3"),
    
    # Bottom row
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
                        html.H2(f"${get_hours_value()}", 
                               className='mb-0',
                               style={'color': '#27ae60', 'fontWeight': 'bold'})
                    ], className="text-center d-flex flex-column align-items-center justify-content-center h-100")
                ])
            ],
            className='shadow-sm',
            style={'height': '300px'}
            )
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
                        html.I(className="fas fa-map-marked-alt fa-3x mb-3", 
                              style={'color': '#3498db'}),
                        html.P("Interactive map visualization will be displayed here", 
                              className="text-muted mb-0",
                              style={'fontSize': '16px'})
                    ], className="d-flex flex-column align-items-center justify-content-center h-100")
                ])
            ],
            className='shadow-sm',
            style={'height': '300px'}
            )
        ], width=8)
    ])
]

# Analytics Tab Layout (Second page)
analytics_layout = [
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5("Advanced Analytics Dashboard", 
                           className="mb-0 text-center",
                           style={'color': '#34495e', 'fontWeight': '600'})
                ]),
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-chart-line fa-4x mb-3", 
                              style={'color': '#e74c3c'}),
                        html.H4("Coming Soon", className="mb-2"),
                        html.P("Advanced analytics and reporting features will be available here", 
                              className="text-muted",
                              style={'fontSize': '18px'})
                    ], className="d-flex flex-column align-items-center justify-content-center h-100")
                ])
            ], className='shadow-sm', style={'height': '400px'})
        ], width=12, className="mb-3")
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H6("Geographic Analysis", className="mb-0 text-center")
                ]),
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-map-marked-alt fa-3x mb-2", 
                              style={'color': '#3498db'}),
                        html.P("Interactive map visualization", 
                              className="text-muted mb-0")
                    ], className="d-flex flex-column align-items-center justify-content-center h-100")
                ])
            ], className='shadow-sm', style={'height': '300px'})
        ], width=6),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H6("Report Generation", className="mb-0 text-center")
                ]),
                dbc.CardBody([
                    html.Div([
                        dbc.Button("Generate Monthly Report", color="primary", className="mb-3 w-75"),
                        dbc.Button("Export Data", color="secondary", className="mb-3 w-75"),
                        dbc.Button("Download Charts", color="info", className="w-75")
                    ], className="d-flex flex-column align-items-center justify-content-center h-100")
                ])
            ], className='shadow-sm', style={'height': '300px'})
        ], width=6)
    ])
]

# Callback for tab switching
@callback(
    Output("tab-content", "children"),
    Input("tabs", "active_tab")
)
def switch_tab(active_tab):
    if active_tab == "dashboard":
        return dashboard_layout
    elif active_tab == "analytics":  
        return analytics_layout
    return dashboard_layout

@callback(
    Output('test-graph','figure'),
    Input('age-drop','value')
)
def pie_chart(age):
    age_chosen = int(age)
    age_df = clients[clients['Age at Sign Up']==age_chosen]
    pie = px.pie(age_df, names='District')
    pie.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        font=dict(size=11),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02
        ),
        height=320
    )
    return pie

if __name__ == '__main__':
    Timer(1, lambda: webbrowser.open("http://localhost:8000")).start()
    app.run(debug=False, host= 'localhost', port=8000)
    
    