import pandas as pd
import seaborn as sns
import datetime as dt
import statistics as stat
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px

#Load dataset
file_path = 'C:/Users/cln87/UTSA Files/CIS/SOS_Data/UTSA Client Dataset - Students of Service (SOS).xlsx'

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
clients = (clients_raw[clients_raw['Galaxy ID'].notna()] #Remove rows with no Galaxy ID
                       .replace({'HS Graduation Year': '0', 'Age Now': 'Unknown'}, None) #Replace unknown ages and grad years with None instead of the string)
                       .replace({'Age at Sign Up' : {"Unknown":15, 0:15, 1:15, 4:15}}) #Replace unknown and too low ages at sign up with 16
                       .query('`Age at Sign Up` <= 20') #Filter out ages over 20
                       [clients_raw['dateAdded'] >= dt.datetime(2020, 1, 1)] #Filter out clients added before 2020
)

yes_no_cols = ['Learn Participation 2022', 
               'Explore Participation',
               'Make It Happen Badge (Yes/No)', 
               'Trip Eligible (Yes/No)',
               'Scholarship Badge (Yes/No)']

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

clients['Median Family Income'] = clients['Median Family Income'].astype('int')

def income_range(income):
    if pd.isnull(income):
        None
    else:
        range_string = f'{int(str(income)[:-6])}0 - {int(str(income)[:-6])}9'
        return range_string

clients['Income Range (Thousands)'] = clients['Median Family Income'].apply(income_range)

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

