import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import html, dcc
import statistics as stat
from scipy import stats as scipystat
import math
import geopandas as gpd
import json
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Initialize global variables for frequency functions
hours = pd.DataFrame()
clients = pd.DataFrame()

def update_global_dataframes(new_hours, new_clients):
    """Update global DataFrames for frequency table functions"""
    global hours, clients
    
    # Update hours DataFrame
    hours = new_hours.copy() if not new_hours.empty else pd.DataFrame()
    
    # Ensure year column exists in hours DataFrame
    if not hours.empty and 'Event Date' in hours.columns and 'year' not in hours.columns:
        try:
            hours['year'] = pd.to_datetime(hours['Event Date']).dt.year.astype(int)
        except:
            pass  # If conversion fails, continue without year column
    
    # Update clients DataFrame
    clients = new_clients.copy() if not new_clients.empty else pd.DataFrame()
    
    # Ensure numeric columns are properly typed
    if not clients.empty:
        # Convert Age columns to int if they exist
        for col in ['Age at Sign Up', 'Age Now']:
            if col in clients.columns:
                try:
                    clients[col] = pd.to_numeric(clients[col], errors='coerce').astype(int)
                except:
                    pass
        
        # Convert Zip Code to int if it exists
        if 'Zip Code' in clients.columns:
            try:
                clients['Zip Code'] = pd.to_numeric(clients['Zip Code'], errors='coerce').astype(int)
            except:
                pass
        
        # Ensure binary columns are regular Python integers for proper filtering
        for col in ['Follow Through', 'Club']:
            if col in clients.columns:
                try:
                    # Convert to numeric first, then to regular Python int
                    clients[col] = pd.to_numeric(clients[col], errors='coerce').astype(int)
                except:
                    pass

def create_empty_pie_chart():
    """Create empty pie chart for when no data is available"""
    fig = px.pie(values=[1], names=['No Data Available'])
    fig.update_layout(
        title="Upload data to view chart",
        margin=dict(l=20, r=20, t=40, b=20),
        font=dict(size=11),
        height=320
    )
    return fig

def create_district_pie_chart(clients, age):
    """Create pie chart for student distribution by district"""
    if clients.empty or 'Age at Sign Up' not in clients.columns:
        return create_empty_pie_chart()
    
    age_chosen = int(age) if age else 16
    age_df = clients[clients['Age at Sign Up'] == age_chosen]
    
    if age_df.empty or 'District' not in age_df.columns:
        fig = px.pie(values=[1], names=['No Data for Selected Age'])
        fig.update_layout(
            title=f"No data available for age {age_chosen}",
            margin=dict(l=20, r=20, t=40, b=20),
            font=dict(size=11),
            height=320
        )
        return fig
    
    fig = px.pie(age_df, names='District')
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
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
    return fig

def create_district_heat_map(clients):
    """Create district heat map using actual client count data for color mapping"""
    if clients.empty or 'District' not in clients.columns:
        # Create empty map
        fig = px.scatter_mapbox(
            lat=[29.4241], lon=[-98.4936],
            zoom=9,
            mapbox_style="open-street-map",
            title="Upload data to view District Heat Map",
            height=750
        )
        fig.update_layout(
            title={'text': "Upload data to view District Heat Map", 'x': 0.5, 'xanchor': 'center'},
            height=750,
            margin=dict(l=0, r=0, t=50, b=0)
        )
        return fig
    
    try:
        # Get district counts from current data
        district_counts = clients['District'].value_counts().reset_index()
        district_counts.columns = ['District_Name', 'Client_Count']
        
        # Try to read the district shapes file
        try:
            district_shapes = gpd.read_file('School_Districts_2025_.geojson')
        except FileNotFoundError:
            # If the geojson file doesn't exist, create a fallback visualization
            fig = px.bar(district_counts.head(10), 
                        x='District_Name', y='Client_Count',
                        title="District Client Distribution (GeoJSON file not found)")
            fig.update_layout(
                title={'text': "District Client Distribution", 'x': 0.5, 'xanchor': 'center'},
                height=750,
                margin=dict(l=20, r=20, t=50, b=20),
                xaxis_title="School District",
                yaxis_title="Number of Clients"
            )
            fig.update_xaxes(tickangle=45)
            return fig

        # District mapping for proper matching
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

        # Use actual client count data directly for color mapping with log scaling
        min_clients = merged['Client_Count'].min()
        max_clients = merged['Client_Count'].max()
        
        # If all values are the same, add small range to prevent color scaling issues
        if max_clients == min_clients:
            max_clients = min_clients + 1

        # Apply log scaling to client counts (add 1 to handle zeros)
        merged['Client_Count_Log'] = np.log1p(merged['Client_Count'])

        # Create map using log-scaled client count data with same color scale as client distribution
        geojson = json.loads(merged.to_json())
        fig = px.choropleth_mapbox(
            merged,
            geojson=geojson,
            locations=merged.index,
            color='Client_Count_Log',  # Use log-scaled client count data
            color_continuous_scale=['#e8f4fd', '#b3d9f2', '#80b3d9', '#4d94bf', '#1a75a6', '#005580'],
            mapbox_style="open-street-map",
            zoom=9,
            center={"lat": 29.4241, "lon": -98.4936},
            opacity=0.8,
            hover_name='NAME',
            title="San Antonio School District Client Distribution (Log Scale)"
        )

        fig.update_traces(
            hovertemplate="<b>%{hovertext}</b><br>Clients: %{z}<extra></extra>",
            hovertext=merged['NAME']
        )

        # Update layout without colorbar for simpler appearance
        fig.update_layout(
            title={'text': "San Antonio School District Client Distribution (Log Scale)", 'x': 0.5, 'xanchor': 'center'},
            height=750,
            margin=dict(l=0, r=0, t=50, b=0),
            showlegend=False,
            mapbox=dict(
                style="open-street-map",
                zoom=9,
                center={"lat": 29.4241, "lon": -98.4936}
            )
        )
        
        # Ensure zoom controls are enabled
        fig.update_mapboxes(
            style="open-street-map",
            zoom=9,
            center={"lat": 29.4241, "lon": -98.4936}
        )

        # Remove colorbar
        fig.update_coloraxes(showscale=False)

        return fig
    
    except Exception as e:
        # Fallback to bar chart if there are any issues
        district_counts = clients['District'].value_counts().reset_index()
        district_counts.columns = ['District_Name', 'Client_Count']
        
        fig = px.bar(district_counts.head(10), 
                    x='District_Name', y='Client_Count',
                    title=f"District Client Distribution (Error: {str(e)})")
        fig.update_layout(
            title={'text': "District Client Distribution", 'x': 0.5, 'xanchor': 'center'},
            height=750,
            margin=dict(l=20, r=20, t=50, b=20),
            xaxis_title="School District",
            yaxis_title="Number of Clients"
        )
        fig.update_xaxes(tickangle=45)
        return fig

def create_heatmap_from_dataframe(clients_df, height=600):
    """Create heatmap from clients dataframe with colorful background and borders"""
    try:
        # Prepare data
        clients_data = clients_df.copy()
        clients_data['Zip Code'] = clients_data['Zip Code'].astype(str)
        
        # Load ZIP shapes
        zip_shapes = gpd.read_file("texas_zcta_2024_simplified.geojson")
        
        # Count clients per ZIP code
        zip_counts = clients_data['Zip Code'].value_counts().reset_index()
        zip_counts.columns = ['ZIP_CODE', 'CLIENT_COUNT']
        
        # Coverage area ZIP codes
        coverage_zips = [
            # Bexar County
            '78201', '78202', '78203', '78204', '78205', '78206', '78207', '78208', '78209',
            '78210', '78211', '78212', '78213', '78214', '78215', '78216', '78217', '78218',
            '78219', '78220', '78221', '78222', '78223', '78224', '78225', '78226', '78227',
            '78228', '78229', '78230', '78231', '78232', '78233', '78234', '78235', '78236',
            '78237', '78238', '78239', '78240', '78241', '78242', '78243', '78244', '78245',
            '78246', '78247', '78248', '78249', '78250', '78251', '78252', '78253', '78254',
            '78255', '78256', '78257', '78258', '78259', '78260', '78261', '78263', '78264',
            '78265', '78266', '78268', '78269', '78270', '78278', '78279', '78280', '78283',
            '78284', '78285', '78288', '78289', '78291', '78292', '78293', '78294', '78295',
            '78296', '78297', '78298', '78299',
            # Surrounding counties
            '78130', '78132', '78133', '78135',  # Comal
            '78108', '78123', '78154', '78155',  # Guadalupe
            '78114', '78118',                    # Wilson
            '78016', '78017', '78073',           # Medina
            '78006', '78015', '78024', '78025', '78070',  # Kendall
            '78003', '78055', '78063', '78883', '78885'   # Bandera
        ]
        
        # Filter and merge data
        filtered_zips = zip_shapes[zip_shapes['ZCTA5CE20'].isin(coverage_zips)]
        merged = filtered_zips.merge(zip_counts, left_on='ZCTA5CE20', right_on='ZIP_CODE', how='left')
        merged['CLIENT_COUNT'] = merged['CLIENT_COUNT'].fillna(0)
        
        # Ensure proper coordinate reference system
        merged = merged.to_crs('EPSG:4326')
        
        # Apply log scaling to client counts (add 1 to handle zeros)
        merged['CLIENT_COUNT_LOG'] = np.log1p(merged['CLIENT_COUNT'])
        
        # Create GeoJSON
        geojson = json.loads(merged.to_json())
        
        # Create choropleth map with red gradient using log scale
        fig = px.choropleth_mapbox(
            merged,
            geojson=geojson,
            locations=merged.index,
            color='CLIENT_COUNT_LOG',
            color_continuous_scale=['#e8f4fd', '#b3d9f2', '#80b3d9', '#4d94bf', '#1a75a6', '#005580'],
            mapbox_style="open-street-map",
            zoom=9.2,
            center={"lat": 29.4241, "lon": -98.4936},
            opacity=0.8,
            hover_name='ZCTA5CE20',
            title="San Antonio Area - ZIP Code Client Distribution (Log Scale)"
        )

        # Update hover template and styling
        fig.update_traces(
            hovertemplate="<b>ZIP Code:</b> %{hovertext}<br><b>Client Count:</b> %{z}<extra></extra>",
            hovertext=merged['ZCTA5CE20']
        )
        # Remove colorbar
        fig.update_coloraxes(showscale=False)
        
        # Update layout for consistent styling
        fig.update_layout(
            title={'text': "San Antonio Area - ZIP Code Client Distribution (Log Scale)", 'x': 0.5, 'xanchor': 'center'},
            height=height,
            margin=dict(l=0, r=0, t=50, b=0),
            font=dict(family="Arial, sans-serif", size=12, color="#2c3e50"),
            paper_bgcolor='white',
            plot_bgcolor='white',
            showlegend=False
        )
        
        return fig
        
    except Exception as e:
        print(f"Error creating heatmap: {e}")
        # Fallback bar chart
        zip_counts = clients_df['Zip Code'].value_counts().head(20)
        fig = px.bar(
            x=zip_counts.index.astype(str), 
            y=zip_counts.values,
            title='Client Distribution by ZIP Code (Top 20)',
            labels={'x': 'ZIP Code', 'y': 'Number of Clients'},
            height=height
        )
        fig.update_layout(title={'x': 0.5, 'xanchor': 'center'})
        return fig

def get_virtual_events_count(hours_df):
    """Count service events with missing or 0 ZIP codes (virtual/other events)"""
    virtual_events = hours_df[hours_df['zipCodeNeed'].isna() | (hours_df['zipCodeNeed'] == 0)].shape[0]
    return virtual_events

def get_located_events_count(hours_df):
    """Count service events that have ZIP code location data"""
    located_events = hours_df[hours_df['zipCodeNeed'].notna()].shape[0]
    return located_events

def get_service_zip_count(hours_df):
    """Get number of unique ZIP codes where services were provided"""
    return hours_df[hours_df['zipCodeNeed'].notna()]['zipCodeNeed'].nunique()

def get_total_service_hours_virtual(hours_df):
    """Get total service hours for virtual/other events"""
    virtual_hours = hours_df[hours_df['zipCodeNeed'].isna() | (hours_df['zipCodeNeed'] == 0)]['hours'].sum()
    return virtual_hours

def get_total_service_hours_located(hours_df):
    """Get total service hours for located events"""
    located_hours = hours_df[hours_df['zipCodeNeed'].notna()]['hours'].sum()
    return located_hours

def create_service_events_heatmap(hours_df, height=450):
    """Create ZIP code heatmap showing where service events were hosted with colorful background"""
    try:
        # Process hours data to count service events by ZIP code
        hours_clean = hours_df[hours_df['zipCodeNeed'].notna()].copy()
        hours_clean['zipCodeNeed'] = hours_clean['zipCodeNeed'].astype(str).str[:5]
        
        # Count service events per ZIP code
        event_counts = hours_clean.groupby('zipCodeNeed').agg({
            'Galaxy ID': 'count',  # Number of service events
            'hours': 'sum'         # Total hours served
        }).reset_index()
        event_counts.columns = ['ZIP_CODE', 'SERVICE_EVENTS', 'TOTAL_HOURS']
        
        # Load ZIP shapes
        try:
            zip_shapes = gpd.read_file("texas_zcta_2024_simplified.geojson")
        except:
            # If ZIP shapes not available, create a simple bar chart
            fig = px.bar(event_counts.head(20), 
                        x='ZIP_CODE', 
                        y='SERVICE_EVENTS',
                        title='Service Events by ZIP Code (Top 20)',
                        labels={'SERVICE_EVENTS': 'Number of Service Events'})
            return fig
        
        # Get coverage area ZIP codes
        coverage_zips = [str(zip_code) for zip_code in [
            # Bexar County (San Antonio)
            78201, 78202, 78203, 78204, 78205, 78206, 78207, 78208, 78209,
            78210, 78211, 78212, 78213, 78214, 78215, 78216, 78217, 78218,
            78219, 78220, 78221, 78222, 78223, 78224, 78225, 78226, 78227,
            78228, 78229, 78230, 78231, 78232, 78233, 78234, 78235, 78236,
            78237, 78238, 78239, 78240, 78241, 78242, 78243, 78244, 78245,
            78246, 78247, 78248, 78249, 78250, 78251, 78252, 78253, 78254,
            78255, 78256, 78257, 78258, 78259, 78260, 78261, 78263, 78264,
            78265, 78266, 78268, 78269, 78270, 78278, 78279, 78280, 78283,
            78284, 78285, 78288, 78289, 78291, 78292, 78293, 78294, 78295,
            78296, 78297, 78298, 78299,
            # Surrounding counties
            78130, 78132, 78133, 78135,  # Comal
            78108, 78123, 78154, 78155,  # Guadalupe
            78114, 78118,                # Wilson
            78016, 78017, 78073,         # Medina
            78006, 78015, 78024, 78025, 78070,  # Kendall
            78003, 78055, 78063, 78883, 78885   # Bandera
        ]]
        
        # Filter ZIP shapes to coverage area
        filtered_zips = zip_shapes[zip_shapes['ZCTA5CE20'].isin(coverage_zips)]
        
        # Merge with service events data
        merged = filtered_zips.merge(event_counts, left_on='ZCTA5CE20', right_on='ZIP_CODE', how='left')
        merged['SERVICE_EVENTS'] = merged['SERVICE_EVENTS'].fillna(0)
        merged['TOTAL_HOURS'] = merged['TOTAL_HOURS'].fillna(0)
        
        # Apply log scaling to service events (add 1 to handle zeros)
        merged['SERVICE_EVENTS_LOG'] = np.log1p(merged['SERVICE_EVENTS'])
        
        # Ensure proper coordinate reference system
        merged = merged.to_crs('EPSG:4326')
        
        # Create GeoJSON
        geojson = json.loads(merged.to_json())
        
        # Create choropleth map with blue gradient using log scale
        fig = px.choropleth_mapbox(
            merged,
            geojson=geojson,
            locations=merged.index,
            color='SERVICE_EVENTS_LOG',
            color_continuous_scale='Blues',
            mapbox_style="open-street-map",
            zoom=9.2,
            center={"lat": 29.4241, "lon": -98.4936},
            opacity=0.8,
            hover_name='ZCTA5CE20',
            title="Service Events by ZIP Code - Where Services Are Provided (Log Scale)"
        )

        # Update hover template and styling
        fig.update_traces(
            hovertemplate="<b>ZIP Code:</b> %{hovertext}<br><b>Service Events:</b> %{customdata[0]}<br><b>Total Hours:</b> %{customdata[1]:.1f}<br><extra></extra>",
            hovertext=merged['ZCTA5CE20'],
            customdata=np.column_stack([merged['SERVICE_EVENTS'], merged['TOTAL_HOURS']])
        )
        
        # Update layout for consistent styling
        fig.update_layout(
            title={'text': "Service Events by ZIP Code - Where Services Are Provided (Log Scale)", 'x': 0.5, 'xanchor': 'center'},
            height=height,
            margin=dict(l=0, r=0, t=50, b=0),
            font=dict(family="Arial, sans-serif", size=12, color="#2c3e50"),
            paper_bgcolor='white',
            plot_bgcolor='white',
            showlegend=False
        )
        
        # Remove colorbar
        fig.update_coloraxes(showscale=False)

        return fig
        
    except Exception as e:
        print(f"Error creating service events heatmap: {e}")
        # Create a simple bar chart as fallback
        hours_clean = hours_df[hours_df['zipCodeNeed'].notna()].copy()
        hours_clean['zipCodeNeed'] = hours_clean['zipCodeNeed'].astype(str).str[:5]
        event_counts = hours_clean['zipCodeNeed'].value_counts().head(15)
        
        fig = px.bar(
            x=event_counts.index, 
            y=event_counts.values,
            title='Service Events by ZIP Code (Top 15)',
            labels={'x': 'ZIP Code', 'y': 'Number of Service Events'}
        )
        return fig

def get_events_summary_stats(hours_df):
    """Get comprehensive summary statistics for events"""
    stats = {
        'total_events': len(hours_df),
        'virtual_events': get_virtual_events_count(hours_df),
        'located_events': get_located_events_count(hours_df),
        'unique_service_zips': get_service_zip_count(hours_df),
        'total_hours': hours_df['hours'].sum(),
        'virtual_hours': get_total_service_hours_virtual(hours_df),
        'located_hours': get_total_service_hours_located(hours_df),
        'avg_hours_per_event': hours_df['hours'].mean(),
        'virtual_percentage': (get_virtual_events_count(hours_df) / len(hours_df)) * 100,
        'located_percentage': (get_located_events_count(hours_df) / len(hours_df)) * 100
    }
    return stats

def calculate_club_confidence_intervals(schoolclub_hours):
    """Calculate confidence intervals for club vs no club comparison"""
    if schoolclub_hours.empty or len(schoolclub_hours) == 0:
        return 0, 0, 0, 0
    
    try:
        alpha = 0.05
        
        # Club data
        club_data = schoolclub_hours[schoolclub_hours['Club'] == '1']['Hours']
        if len(club_data) <= 1:
            club_lower, club_upper = 0, 0
        else:
            club_mu = club_data.mean()
            if len(club_data) == 1:
                club_lower = club_upper = club_mu
            else:
                club_sigma = stat.stdev(club_data)
                club_n = len(club_data)
                club_conf_t = abs(round(scipystat.t.ppf(alpha/2, club_n-1), 2))
                club_lower = round(club_mu - club_conf_t*(club_sigma/math.sqrt(club_n)), 2)
                club_upper = round(club_mu + club_conf_t*(club_sigma/math.sqrt(club_n)), 2)

        # No club data
        noclub_data = schoolclub_hours[schoolclub_hours['Club'] == '0']['Hours']
        if len(noclub_data) <= 1:
            noclub_lower, noclub_upper = 0, 0
        else:
            noclub_mu = noclub_data.mean()
            if len(noclub_data) == 1:
                noclub_lower = noclub_upper = noclub_mu
            else:
                noclub_sigma = stat.stdev(noclub_data)
                noclub_n = len(noclub_data)
                noclub_conf_t = abs(round(scipystat.t.ppf(alpha/2, noclub_n-1), 2))
                noclub_lower = round(noclub_mu - noclub_conf_t*(noclub_sigma/math.sqrt(noclub_n)), 2)
                noclub_upper = round(noclub_mu + noclub_conf_t*(noclub_sigma/math.sqrt(noclub_n)), 2)

        return club_lower, club_upper, noclub_lower, noclub_upper
    except:
        return 0, 0, 0, 0

def create_club_comparison_chart(schoolclub_hours):
    """Create club vs no club comparison chart"""
    if schoolclub_hours.empty:
        empty_fig = px.line(x=[0, 1], y=[0, 1])
        empty_fig.update_layout(
            title="Upload data to view Club vs No Club comparison",
            xaxis_title="Hours Range",
            yaxis_title="Club Status",
            height=220,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        return empty_fig, html.P("Upload data to see confidence intervals", className="text-muted text-center")
    
    # Calculate confidence intervals
    club_low, club_high, noclub_low, noclub_high = calculate_club_confidence_intervals(schoolclub_hours)
    
    # Create chart data
    ci_data = pd.DataFrame([
        {'x': noclub_low, 'Category': 0},
        {'x': noclub_high, 'Category': 0},
        {'x': club_low, 'Category': 1},
        {'x': club_high, 'Category': 1}
    ])
    
    fig = px.line(ci_data, x='x', y='Category', color='Category', 
                  markers=True, line_shape='linear')
    fig.update_layout(
        title="Range for Average Hours Given",
        xaxis_title="Estimated Average Hours",
        yaxis_title="Club?",
        yaxis=dict(tickmode='array', tickvals=[0, 1], ticktext=['No Club', 'Club']),
        showlegend=False,
        height=220,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    # Create confidence intervals display
    intervals_display = html.Div([
        html.Div([
            html.Small("Average Hours Given By Schools With Clubs:", 
                    style={'fontWeight': '600', 'color': '#34495e'}),
            html.Small(f" {club_low} - {club_high}", 
                    style={'marginLeft': '5px'})
        ], className="d-flex justify-content-center mb-1"),
        html.Div([
            html.Small("Average Hours Given By Schools Without Clubs:", 
                    style={'fontWeight': '600', 'color': '#34495e'}),
            html.Small(f" {noclub_low} - {noclub_high}", 
                    style={'marginLeft': '5px'})
        ], className="d-flex justify-content-center")
    ])
    
    return fig, intervals_display

def create_quarter_volunteers_chart(qtr_vol_counts):
    """Create active volunteers by quarter chart"""
    if qtr_vol_counts.empty:
        empty_fig = px.line(x=[0], y=[0])
        empty_fig.update_layout(
            title="Upload data to view Active Volunteers by Quarter",
            xaxis_title="Quarter",
            yaxis_title="Active Volunteers",
            height=340,
            margin=dict(l=30, r=30, t=40, b=30)
        )
        return empty_fig
    
    fig = px.line(qtr_vol_counts, x='QTR', y='Active Volunteers', markers=True)
    fig.update_layout(
        title="Active Volunteers by Quarter",
        margin=dict(l=30, r=30, t=40, b=30),
        font=dict(size=12),
        height=340
    )
    return fig

def create_monthly_volunteers_chart(hours_df):
    """Create active volunteers by month chart"""
    if hours_df.empty:
        empty_fig = px.line(x=[0], y=[0])
        empty_fig.update_layout(
            title="Upload data to view Active Volunteers by Month",
            xaxis_title="Month",
            yaxis_title="Active Volunteers",
            height=340,
            margin=dict(l=30, r=30, t=40, b=30)
        )
        return empty_fig
    
    try:
        # Create month-year column if it doesn't exist
        if 'mon-year' not in hours_df.columns:
            hours_df['mon-year'] = hours_df['Event Date'].dt.to_period('M').astype(str)
        
        # Create monthly volunteer counts
        mon_vol_counts = pd.DataFrame(
            list(hours_df.groupby('mon-year')['Galaxy ID'].nunique().to_dict().items()),
            columns=['Month', 'Active Volunteers']
        )
        
        # Convert to datetime and sort
        mon_vol_counts['Month'] = pd.to_datetime(mon_vol_counts['Month'], format='%Y-%m')
        mon_vol_counts = mon_vol_counts.sort_values('Month')
        
        # Create the line chart
        fig = px.line(mon_vol_counts, x='Month', y='Active Volunteers', markers=True)
        fig.update_layout(
            title="Active Volunteers by Month",
            margin=dict(l=30, r=30, t=40, b=30),
            font=dict(size=12),
            height=340
        )
        return fig
        
    except Exception as e:
        # Fallback empty chart
        empty_fig = px.line(x=[0], y=[0])
        empty_fig.update_layout(
            title=f"Error creating monthly chart: {str(e)}",
            xaxis_title="Month",
            yaxis_title="Active Volunteers",
            height=340,
            margin=dict(l=30, r=30, t=40, b=30)
        )
        return empty_fig

def calculate_hours_value(clients):
    """Calculate total value of volunteered hours"""
    if clients.empty or 'Hours' not in clients.columns:
        return '0.00'
    total_hours = clients['Hours'].sum()
    total_value = total_hours * 31
    return '{:,.2f}'.format(total_value)

def get_age_dropdown_options(clients):
    """Get options for age dropdown"""
    if clients.empty or 'Age at Sign Up' not in clients.columns:
        return [{'label': 'Upload data first', 'value': 16}]
    
    ages = sorted(clients['Age at Sign Up'].unique())
    return [{'label': f'Age {age}', 'value': age} for age in ages]

collected_freq_cols = ['Learn Participation 2022', 'Explore Participation', 'Make It Happen Badge (Yes/No)', 
                       'Trip Eligible (Yes/No)', 'Scholarship Badge (Yes/No)', 'Step']

notcollected_freq_cols = ['Age at Sign Up', 'Zip Code', 'School', 
                          'District', 'Race/Ethnicity', 'Gender', 
                          'Income Range (Thousands)', 'Club', 'County']

filter_populations = ['Follow Through', 'District', 'Trip Eligible (Yes/No)',
                      'Explore Participation','Make It Happen Badge (Yes/No)','Learn Participation 2022',
                      'Scholarship Badge (Yes/No)', 'Income Range (Thousands)', 'School', 'Gender']

def slice_by_active(year):
    hours_slice = hours[hours['year']==year]
    active_galaxy = hours_slice['Galaxy ID'].unique()
    active_in_year = clients[clients['Galaxy ID'].isin(active_galaxy)]
    return active_in_year

# Debug function removed - using fixed version below
def single_var_freq(var, pop='all', pop_value=None, slice='all'):
    
    # Check if clients DataFrame is available and has data
    if clients.empty:
        return pd.DataFrame()
        
    if var not in clients.columns:
        return pd.DataFrame()
    
    # Convert string values to int for binary columns (Follow Through, Club)
    # But NOT for categorical string columns like Income Range
    if pop_value is not None and pop in ['Follow Through', 'Club']:
        try:
            pop_value = int(pop_value)
        except (ValueError, TypeError):
            pass  # Keep original value if conversion fails
    
    # For string-based categorical columns, ensure pop_value is treated as string
    if pop_value is not None and pop in ['Income Range (Thousands)', 'District', 'School', 'Gender', 'Race/Ethnicity']:
        pop_value = str(pop_value)

    if slice == 'all':
        if pop == 'all':
            freq_table = pd.DataFrame(clients[var].value_counts().sort_index().reset_index())
        elif pop in filter_populations:
            if pop not in clients.columns:
                print(f"ERROR: Filter population '{pop}' not found in clients columns")
                return pd.DataFrame()
            
            # Filter the data - handle string comparisons properly
            if pop in ['Income Range (Thousands)', 'District', 'School', 'Gender', 'Race/Ethnicity']:
                # For categorical string columns, use string comparison
                filtered_clients = clients[clients[pop].astype(str) == str(pop_value)]
            else:
                # For numeric columns, use regular comparison
                filtered_clients = clients[clients[pop] == pop_value]
            
            if filtered_clients.empty:
                return pd.DataFrame()
            
            freq_table = pd.DataFrame(filtered_clients[var].value_counts().sort_index().reset_index())
        else:
            return pd.DataFrame()

    elif slice in range(2020,2100):
        sliced_clients = slice_by_active(slice)
        if sliced_clients.empty:
            return pd.DataFrame()
            
        if pop == 'all':
            freq_table = pd.DataFrame(sliced_clients[var].value_counts().sort_index().reset_index())
        elif pop in filter_populations:
            if pop not in sliced_clients.columns:
                return pd.DataFrame()
            
            # Filter the data - handle string comparisons properly
            if pop in ['Income Range (Thousands)', 'District', 'School', 'Gender', 'Race/Ethnicity']:
                # For categorical string columns, use string comparison
                filtered_sliced = sliced_clients[sliced_clients[pop].astype(str) == str(pop_value)]
            else:
                # For numeric columns, use regular comparison
                filtered_sliced = sliced_clients[sliced_clients[pop] == pop_value]
            
            if filtered_sliced.empty:
                return pd.DataFrame()
            
            freq_table = pd.DataFrame(filtered_sliced[var].value_counts().sort_index().reset_index())
        else:
            return pd.DataFrame()
    else:
        return pd.DataFrame()

    return freq_table

def multi_var_freq(var1, var2, pop='all', pop_value=None, slice='all'):
    
    # Check if clients DataFrame is available and has data
    if clients.empty:
        return pd.DataFrame()
        
    if var1 not in clients.columns or var2 not in clients.columns:
        return pd.DataFrame()
    
    # Convert string values to int for binary columns (Follow Through, Club)
    # But NOT for categorical string columns like Income Range
    if pop_value is not None and pop in ['Follow Through', 'Club']:
        try:
            pop_value = int(pop_value)
        except (ValueError, TypeError):
            pass  # Keep original value if conversion fails
    
    # For string-based categorical columns, ensure pop_value is treated as string
    if pop_value is not None and pop in ['Income Range (Thousands)', 'District', 'School', 'Gender', 'Race/Ethnicity']:
        pop_value = str(pop_value)
    
    if slice == 'all':
        if pop == 'all':
            freq_table = pd.crosstab(clients[var1], clients[var2])
        elif pop in filter_populations:
            if pop not in clients.columns:
                return pd.DataFrame()
            
            # Filter the data - handle string comparisons properly
            if pop in ['Income Range (Thousands)', 'District', 'School', 'Gender', 'Race/Ethnicity']:
                # For categorical string columns, use string comparison
                filtered_clients = clients[clients[pop].astype(str) == str(pop_value)]
            else:
                # For numeric columns, use regular comparison
                filtered_clients = clients[clients[pop] == pop_value]
            
            if filtered_clients.empty:
                return pd.DataFrame()
            
            freq_table = pd.crosstab(filtered_clients[var1], filtered_clients[var2])
        else:
            return pd.DataFrame()

    elif slice in range(2020,2100):
        sliced_clients = slice_by_active(slice)
        if sliced_clients.empty:
            return pd.DataFrame()
            
        if pop == 'all':
            freq_table = pd.crosstab(sliced_clients[var1], sliced_clients[var2])
        elif pop in filter_populations:
            if pop not in sliced_clients.columns:
                return pd.DataFrame()
            
            # Filter the data - handle string comparisons properly
            if pop in ['Income Range (Thousands)', 'District', 'School', 'Gender', 'Race/Ethnicity']:
                # For categorical string columns, use string comparison
                filtered_sliced = sliced_clients[sliced_clients[pop].astype(str) == str(pop_value)]
            else:
                # For numeric columns, use regular comparison
                filtered_sliced = sliced_clients[sliced_clients[pop] == pop_value]
            
            if filtered_sliced.empty:
                return pd.DataFrame()
            
            freq_table = pd.crosstab(filtered_sliced[var1], filtered_sliced[var2])
        else:
            return pd.DataFrame()
    else:
        return pd.DataFrame()

    return freq_table 

def create_zipcode_map():
    """
    Create a heat map showing service hours by zipcode
    """
    # Access global variables
    global clients, hours
    
    # Check if data is available
    if clients.empty or hours.empty:
        # Create empty map if no data
        fig = px.scatter_mapbox(
            lat=[29.4241], lon=[-98.4936],
            zoom=9.2,
            mapbox_style="open-street-map",
            title="Upload data to view Service Hours by Zipcode",
            height=600
        )
        fig.update_layout(
            title={'text': "Upload data to view Service Hours by Zipcode", 'x': 0.5, 'xanchor': 'center'},
            height=600,
            margin=dict(l=0, r=0, t=50, b=0)
        )
        return fig
    
    try:
        print(f"Creating zipcode map - clients shape: {clients.shape}, hours shape: {hours.shape}")
        
        # Calculate total hours per Galaxy ID
        hours_sum = hours.groupby('Galaxy ID')['hours'].sum().reset_index()
        hours_sum.columns = ['Galaxy ID', 'Total Hours']
        
        # Merge clients with their total hours
        clients_with_hours = clients.merge(hours_sum, on='Galaxy ID', how='left')
        
        # Group by zipcode and sum hours
        zipcode_hours = clients_with_hours.groupby('Zip Code')['Total Hours'].sum().reset_index()
        zipcode_hours = zipcode_hours[zipcode_hours['Total Hours'] > 0]  # Only zipcodes with hours
        
        if zipcode_hours.empty:
            # Create empty map if no hours data
            fig = px.scatter_mapbox(
                lat=[29.4241], lon=[-98.4936],
                zoom=9.2,
                mapbox_style="open-street-map",
                title="No service hours data available",
                height=600
            )
            fig.update_layout(
                title={'text': "No service hours data available", 'x': 0.5, 'xanchor': 'center'},
                height=600,
                margin=dict(l=0, r=0, t=50, b=0)
            )
            return fig
        
        # Load Texas zipcode geojson
        gdf = gpd.read_file('texas_zcta_2024_simplified.geojson')
        gdf['ZCTA5CE20'] = pd.to_numeric(gdf['ZCTA5CE20'], errors='coerce')
        
        # Convert zip codes to string for matching
        zipcode_hours['Zip Code'] = zipcode_hours['Zip Code'].astype(int).astype(str)
        gdf['ZCTA5CE20'] = gdf['ZCTA5CE20'].astype(int).astype(str)
        
        # Merge with our data
        merged = gdf.merge(zipcode_hours, left_on='ZCTA5CE20', right_on='Zip Code', how='left')
        merged['Total Hours'] = merged['Total Hours'].fillna(0)
        
        # Apply log scaling to total hours (add 1 to handle zeros)
        merged['Total Hours Log'] = np.log1p(merged['Total Hours'])
        
        merged = merged.to_crs('EPSG:4326')
        geojson = json.loads(merged.to_json())
        
        # Create the map using log scale
        fig = px.choropleth_mapbox(
            merged,
            geojson=geojson,
            locations=merged.index,
            color='Total Hours Log',
            color_continuous_scale=[
                '#e0fff4',  # very light mint
                '#b2f7ef',  # light mint
                '#7de2d1',  # medium mint
                '#40c9a2',  # deeper mint
                '#2ec4b6'   # strong mint
            ],  # Custom mint gradient
            mapbox_style='open-street-map',
            zoom=9.2,
            center={"lat": 29.4241, "lon": -98.4936},
            opacity=0.8,
            hover_name='ZCTA5CE20',
            title="SOS Service Hours by Zipcode (Log Scale)"
        )
        
        # Update hover template and styling
        fig.update_traces(
            hovertemplate="<b>ZIP Code:</b> %{hovertext}<br><b>Total Hours:</b> %{z}<extra></extra>",
            hovertext=merged['ZCTA5CE20']
        )
        
        # Update layout for consistent styling
        fig.update_layout(
            title={'text': "SOS Service Hours by Zipcode (Log Scale)", 'x': 0.5, 'xanchor': 'center'},
            height=600,
            margin=dict(l=0, r=0, t=50, b=0),
            font=dict(family="Arial, sans-serif", size=12, color="#2c3e50"),
            paper_bgcolor='white',
            plot_bgcolor='white',
            showlegend=False
        )
        
        # Remove colorbar
        fig.update_coloraxes(showscale=False)

        return fig
        
    except Exception as e:
        print(f"Error creating zipcode map: {e}")
        # Fallback to bar chart if geojson not available
        if not zipcode_hours.empty:
            # Apply log scaling to the fallback chart data
            zipcode_hours['Total Hours Log'] = np.log1p(zipcode_hours['Total Hours'])
            fig = px.bar(
                zipcode_hours.sort_values('Total Hours', ascending=False).head(20),
                x='Zip Code',
                y='Total Hours Log',
                title='Top 20 Zipcodes by Service Hours (Log Scale)',
                labels={'Total Hours Log': 'Total Service Hours (Log Scale)', 'Zip Code': 'Zip Code'},
                color='Total Hours Log',
                color_continuous_scale=[
                    '#e0fff4',  # very light mint
                    '#b2f7ef',  # light mint
                    '#7de2d1',  # medium mint
                    '#40c9a2',  # deeper mint
                    '#2ec4b6'   # strong mint
                ]  # Custom mint gradient
            )
            fig.update_layout(
                title_x=0.5,
                title_font_size=20,
                xaxis_tickangle=-45,
                height=600
            )
            return fig
        else:
            # Create empty chart if no data
            fig = px.bar(x=[], y=[], title='No service hours data available')
            fig.update_layout(height=600)
            return fig 

def create_funnel_chart():
    """
    Create a funnel chart showing student progression through volunteer stages
    """
    # Access global variables
    global clients, hours
    
    # Check if data is available
    if clients.empty:
        # Create empty funnel if no data
        fig = go.Figure()
        fig.add_trace(go.Funnel(
            y=['No Data Available'],
            x=[1],
            textinfo="label",
            textfont=dict(size=16, color='white'),
            marker=dict(color=['#DFE6E8'])
        ))
        fig.update_layout(
            title={'text': "Upload data to view Funnel Chart", 'x': 0.5, 'xanchor': 'center'},
            height=600,
            margin=dict(l=50, r=50, t=80, b=50)
        )
        return fig
    
    try:
        # Calculate funnel stages based on available data
        # Stage 1: All registered students (total in clients)
        stage1_count = len(clients)
        
        # Stage 2: Students who signed up to volunteer (have some volunteer activity or hours > 0)
        stage2_count = len(clients[clients['Hours'] > 0]) if 'Hours' in clients.columns else 0
        
        # Stage 3: Students who showed up to volunteer events (have actual service hours)
        if not hours.empty and 'Galaxy ID' in hours.columns:
            active_volunteers = hours['Galaxy ID'].unique()
            stage3_count = len(clients[clients['Galaxy ID'].isin(active_volunteers)])
        else:
            stage3_count = stage2_count
        
        # Stage 4: Students who became eligible for Explore (Trip Eligible = Yes)
        if 'Trip Eligible (Yes/No)' in clients.columns:
            stage4_count = len(clients[clients['Trip Eligible (Yes/No)'] == 1])
        else:
            # Fallback: use students with significant hours (>= 10 hours)
            stage4_count = len(clients[clients['Hours'] >= 10]) if 'Hours' in clients.columns else 0
        
        # Stage 5: Students who participated in Explore
        if 'Explore Participation' in clients.columns:
            stage5_count = len(clients[clients['Explore Participation'] == 1])
        else:
            # Fallback: use students with very high hours (>= 20 hours)
            stage5_count = len(clients[clients['Hours'] >= 20]) if 'Hours' in clients.columns else 0
        
        # Ensure funnel logic (each stage should be <= previous stage)
        stage2_count = min(stage2_count, stage1_count)
        stage3_count = min(stage3_count, stage2_count)
        stage4_count = min(stage4_count, stage3_count)
        stage5_count = min(stage5_count, stage4_count)
        
        # Create funnel_df
        funnel_df = pd.DataFrame(data={
            'Step': [
                'Registered for Galaxy',
                'Signed up to volunteer',
                'Showed up to volunteer events',
                'Became eligible for Explore',
                'Participated in Explore'
            ],
            'Count': [stage1_count, stage2_count, stage3_count, stage4_count, stage5_count]
        })

        # Define your brand colors
        primary_colors = {
            'blue': '#2A8EC1',
            'gold': '#C1A351',
            'dark': '#241D21',
            'light_gray': '#DFE6E8'
        }

        secondary_colors = {
            'dark_blue': '#0E4573',
            'light_gold': '#DBCFA3',
            'gray': '#646061',
            'green': '#7C946C'
        }

        # Create funnel_colors list using your brand colors
        funnel_colors = [
            primary_colors['blue'],      # '#2A8EC1'
            primary_colors['gold'],      # '#C1A351'
            secondary_colors['dark_blue'], # '#0E4573'
            secondary_colors['light_gold'], # '#DBCFA3'
            secondary_colors['green'],   # '#7C946C'
            secondary_colors['gray'],    # '#646061'
            primary_colors['dark'],      # '#241D21'
            primary_colors['light_gray'] # '#DFE6E8'
        ]

        # Create the funnel chart
        fig_custom = go.Figure()

        # Get the steps and counts from your dataframe
        steps = funnel_df['Step'].tolist()
        counts = funnel_df['Count'].tolist()

        fig_custom.add_trace(go.Funnel(
            y=steps,
            x=counts,
            textinfo="label+value+percent initial",
            textfont=dict(size=16, color='white'),
            marker=dict(
                color=funnel_colors[:len(steps)],
                line=dict(color=primary_colors['dark'], width=2)
            ),
            connector=dict(
                line=dict(color=secondary_colors['gray'], width=3)
            )
        ))

        fig_custom.update_layout(
            title={
                'text': 'Student Volunteers at each Stage',
                'x': 0.5,
                'xanchor': 'center',
                'font': {
                    'size': 24,
                    'color': primary_colors['dark'],
                    'family': 'Arial, sans-serif'
                }
            },
            paper_bgcolor=primary_colors['light_gray'],
            plot_bgcolor='white',
            font={
                'color': primary_colors['dark'],
                'size': 14,
                'family': 'Arial, sans-serif'
            },
            margin=dict(l=50, r=50, t=80, b=50),
            height=600,
            showlegend=False
        )

        return fig_custom
        
    except Exception as e:
        print(f"Error creating funnel chart: {e}")
        # Create empty chart if error
        fig = go.Figure()
        fig.add_trace(go.Funnel(
            y=['Error loading data'],
            x=[1],
            textinfo="label",
            textfont=dict(size=16, color='white'),
            marker=dict(color=['#DFE6E8'])
        ))
        fig.update_layout(
            title={'text': "Error loading funnel data", 'x': 0.5, 'xanchor': 'center'},
            height=600,
            margin=dict(l=50, r=50, t=80, b=50)
        )
        return fig 

def create_likert_pie_card(survey_df, card_id_prefix="senior-survey"):
    """
    Create a Dash card for Senior Survey Responses Likert pie chart.
    survey_df: DataFrame with Likert data (columns are questions)
    card_id_prefix: prefix for component IDs to allow multiple instances if needed
    """
    # Determine which columns to show (use [0, 18, 19] if possible, else all)
    if not survey_df.empty:
        if len(survey_df.columns) > 19:
            likert_columns = [survey_df.columns[i] for i in [0, 18, 19]]
        else:
            likert_columns = list(survey_df.columns)
    else:
        likert_columns = []
    
    default_value = likert_columns[0] if likert_columns else None

    return dbc.Card([
        dbc.CardHeader([
            html.H6("Senior Survey Responses", className="mb-0 text-center", style={'color': 'white', 'fontWeight': '600', 'fontSize': '16px'})
        ], className="card-header"),
        dbc.CardBody([
            html.Div([
                html.Label("Select Question:", className="form-label mb-2", style={'fontWeight': '600', 'fontSize': '14px', 'color': '#2c3e50'}),
                dcc.Dropdown(
                    id=f'{card_id_prefix}-likert-question-drop',
                    options=[{'label': col, 'value': col} for col in likert_columns],
                    value=default_value,
                    style={'marginBottom': '15px', 'fontSize': '14px'},
                    className="likert-dropdown"  # Add CSS class for styling
                )
            ], className="dropdown-container"),
            dcc.Graph(id=f'{card_id_prefix}-likert-pie', style={'height': '250px'}, className="graph-container")
        ], className="card-body")
    ], className='card equal-height-card')

def get_likert_pie_figure(survey_df, selected_question):
    """
    Generate a pie chart figure for the selected Likert question.
    """
    if survey_df.empty or selected_question is None or selected_question not in survey_df.columns:
        return px.pie(title="No data available for Senior Survey Responses")

    # Count occurrences of each response for the selected question
    counts = survey_df[selected_question].value_counts().reset_index()
    counts.columns = ['Response', 'Count']

    fig = px.pie(
        counts,
        names='Response',
        values='Count',
        title=f"Responses for: {selected_question}",
        hole=0.3,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    # Update layout to reduce spacing
    fig.update_layout(
        margin=dict(l=10, r=10, t=20, b=10),  # Reduced top margin from 50 to 20
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02,
            font=dict(size=10)
        ),
        height=200,  # Reduced from 280 to 200 to fit in 250px container
        font=dict(size=11)
    )
    
    # Update traces for better text display
    fig.update_traces(
        textinfo='percent+label',
        pull=[0.05] * len(counts),
        textposition='inside',
        textfont=dict(size=10)
    )
    
    return fig 