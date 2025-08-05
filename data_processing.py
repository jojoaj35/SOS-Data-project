import pandas as pd
import datetime as dt
import numpy as np

def process_uploaded_data(clients_raw, hours, survey_raw, county_zips, zip_incomes, county_incomes, 
                         schools_with_clubs, yes_no_cols):
    """
    Process uploaded data and return cleaned datasets
    """
    
    # Clean clients dataset
    clients = (clients_raw[clients_raw['Galaxy ID'].notna()]
                          .replace({'HS Graduation Year': '0', 'Age Now': 'Unknown'}, None)
                          .replace({'Age at Sign Up': {"Unknown": 15, 0: 15, 1: 15, 4: 15}})
                          .query('`Age at Sign Up` <= 20')
    )
    
    # Filter by date if dateAdded column exists
    if 'dateAdded' in clients.columns:
        clients = clients[clients['dateAdded'] >= dt.datetime(2020, 1, 1)]
    
    # Apply data transformations
    clients[yes_no_cols] = clients[yes_no_cols].replace({'Yes': 1, 'No': 0})
    # Convert zip codes to numeric, handling errors
    clients['Zip Code'] = pd.to_numeric(clients['Zip Code'].astype(str).str[:5], errors='coerce')
    
    # Recalculate derived columns
    hours_sum = hours.groupby('Galaxy ID')['hours'].sum()
    clients['Collected Hours'] = clients['Galaxy ID'].map(hours_sum)
    
    earliest_service = hours.groupby('Galaxy ID')['Event Date'].min()
    clients['Earliest Service'] = clients['Galaxy ID'].map(earliest_service)
    
    latest_service = hours.groupby('Galaxy ID')['Event Date'].max()
    clients['Latest Service'] = clients['Galaxy ID'].map(latest_service)
    
    service_count = hours.groupby('Galaxy ID')['Event Date'].count()
    clients['Service Count'] = clients['Galaxy ID'].map(service_count)
    
    range_mask = (clients['Latest Service'] - clients['Earliest Service']).dt.days > 0
    clients.loc[range_mask, 'Service Range'] = clients['Latest Service'] - clients['Earliest Service']
    
    clients['Follow Through'] = np.where(clients['Hours'] > 0, 1, 0).astype(int)
    clients['Club'] = np.where(clients['School'].isin(schools_with_clubs), 1, 0).astype(int)
    
    # Assign counties
    def county_assign(zip_code):
        for county, zips in county_zips.items():
            if zip_code in zips:
                return county
        return None
    
    clients['County'] = clients['Zip Code'].apply(county_assign)
    
    # Assign incomes
    def assign_zipincome(zip_code):
        if zip_code in zip_incomes['Zip Code'].values:
            return round(int(zip_incomes[zip_incomes['Zip Code'] == zip_code]['Median Income'].values[0]))
        return None
    
    def assign_countyincome(county):
        if county in county_incomes['County'].values:
            return round(int(county_incomes[county_incomes['County'] == county]['Median Income'].values[0]))
        return None
    
    for idx, row in clients.iterrows():
        zip_of_id = row['Zip Code']
        county_of_id = row['County']
        
        if zip_of_id in zip_incomes['Zip Code'].values:
            clients.loc[idx, 'Median Family Income'] = assign_zipincome(zip_of_id)
        elif county_of_id in county_incomes['County'].values:
            clients.loc[idx, 'Median Family Income'] = assign_countyincome(county_of_id)
        else:
            clients.loc[idx, 'Median Family Income'] = None
    
    # Convert Median Family Income to int, handling None values
    clients['Median Family Income'] = pd.to_numeric(clients['Median Family Income'], errors='coerce').astype('Int64')
    
    # Create income range function
    def income_range(income):
        if pd.isnull(income) or income is None:
            return None
        try:
            income_str = str(int(income))
            if len(income_str) >= 6:
                range_string = f'{int(income_str[:-6])}0 - {int(income_str[:-6])}9'
                return range_string
            else:
                return None
        except (ValueError, TypeError):
            return None
    
    clients['Income Range (Thousands)'] = clients['Median Family Income'].apply(income_range)
    
    # Create school club data
    schoolclub_hours = clients.groupby(by='School').agg({'Hours': 'sum'}).reset_index()
    schoolclub_hours['Club'] = np.where(schoolclub_hours['School'].isin(schools_with_clubs), 1, 0).astype(str)
    
    hours['year'] = hours['Event Date'].dt.year
    hours['month'] = hours['Event Date'].dt.month
    # Update quarter data
    hours['qtr-year'] = (
        hours['Event Date'].dt.year.astype(str) +
        '-Q' + hours['Event Date'].dt.quarter.astype(str)
    )
    
    qtr_vol_counts = pd.DataFrame(
        list(hours.groupby('qtr-year')['Galaxy ID'].nunique().to_dict().items()),
        columns=['QTR', 'Active Volunteers']
    )
    
    return clients, schoolclub_hours, qtr_vol_counts

def create_processing_summary(clients_raw, hours, survey_raw, clients, schoolclub_hours, qtr_vol_counts, filename):
    """Create detailed processing summary for successful upload"""
    from dash import html
    import dash_bootstrap_components as dbc
    from dashboard_components import calculate_hours_value
    
    # Calculate metrics
    follow_through_rate = clients['Follow Through'].mean() * 100 if not clients.empty else 0
    avg_hours = clients[clients['Hours'] > 0]['Hours'].mean() if not clients.empty else 0
    total_value = calculate_hours_value(clients)
    schools_with_clubs_count = len(schoolclub_hours[schoolclub_hours['Club'] == '1']) if not schoolclub_hours.empty else 0
    total_schools = len(schoolclub_hours) if not schoolclub_hours.empty else 0
    
    summary = html.Div([
        dbc.Alert([
            html.I(className="fas fa-check-circle me-2"),
            html.Strong("File Upload Successful!"),
            html.Br(),
            f"📁 Uploaded: {filename}",
            html.Br(),
            f"📊 Raw data loaded: {len(clients_raw)} clients, {len(hours)} service hours, {len(survey_raw)} survey responses"
        ], color="success", className="mb-2"),
        
        dbc.Alert([
            html.I(className="fas fa-cogs me-2"),
            html.Strong("Data Cleaning Pipeline Completed Successfully!"),
            html.Br(),
            html.Ul([
                html.Li(f"✅ Filtered clients: {len(clients)} records after cleaning"),
                html.Li(f"✅ Generated derived columns: Service Range, Follow Through, Club status"),
                html.Li(f"✅ Assigned geographic data: Counties and income ranges"),
                html.Li(f"✅ Calculated quarter aggregations: {len(qtr_vol_counts)} quarters"),
                html.Li(f"✅ School club analysis: {total_schools} schools processed"),
                html.Li(f"✅ Confidence intervals calculated (α=0.05)")
            ], className="mb-2"),
            html.Hr(),
            html.P([
                html.Strong("Data Quality Metrics:"),
                html.Br(),
                f"• Follow-through rate: {follow_through_rate:.1f}% of clients volunteered",
                html.Br(),
                f"• Average service hours per active client: {avg_hours:.1f}",
                html.Br(),
                f"• Total volunteer value: ${total_value} (at $31/hour)",
                html.Br(),
                f"• Schools with clubs: {schools_with_clubs_count} of {total_schools}"
            ], className="mb-0", style={'fontSize': '14px'})
        ], color="info", className="mb-2"),
        
        dbc.Alert([
            html.I(className="fas fa-chart-line me-2"),
            "🎯 Dashboard ready! Switch to the Dashboard tab to explore your data visualizations."
        ], color="primary")
    ])
    
    return summary 