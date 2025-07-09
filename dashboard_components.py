import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import html, dcc
import statistics as stat
from scipy import stats as scipystat
import math
import geopandas as gpd
import json
import numpy as np

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

        # Use actual client count data directly for color mapping
        min_clients = merged['Client_Count'].min()
        max_clients = merged['Client_Count'].max()
        
        # If all values are the same, add small range to prevent color scaling issues
        if max_clients == min_clients:
            max_clients = min_clients + 1

        # Create map using actual client count data for colors
        geojson = json.loads(merged.to_json())
        fig = px.choropleth_mapbox(
            merged,
            geojson=geojson,
            locations=merged.index,
            color='Client_Count',  # Use actual client count data directly
            color_continuous_scale=['#f7f7f7', '#deebf7', '#c6dbef', '#9ecae1', '#6baed6', '#4292c6', '#2171b5', '#08519c', '#08306b', '#05196e', '#021942'],
            range_color=[min_clients, max_clients],  # Set range based on actual data
            mapbox_style="open-street-map",
            zoom=9,
            center={"lat": 29.4241, "lon": -98.4936},
            opacity=0.8,
            hover_name='NAME',
            title="San Antonio School District Client Distribution"
        )

        fig.update_traces(
            hovertemplate="<b>%{hovertext}</b><br>Clients: %{z}<extra></extra>",
            hovertext=merged['NAME']
        )

        # Create clean, simple tick values for the colorbar
        data_range = max_clients - min_clients
        
        # Always include min and max values, plus 3-5 intermediate values
        if data_range <= 5:
            # Small range: show every value
            tick_values = list(range(min_clients, max_clients + 1))
        elif data_range <= 20:
            # Small-medium range: show every few values
            step = max(1, data_range // 4)
            tick_values = list(range(min_clients, max_clients + 1, step))
            if max_clients not in tick_values:
                tick_values.append(max_clients)
        elif data_range <= 100:
            # Medium range: show nice round numbers
            step = 10 if data_range <= 50 else 20
            tick_values = []
            current = min_clients
            while current <= max_clients:
                tick_values.append(current)
                current += step
            if max_clients not in tick_values:
                tick_values.append(max_clients)
        else:
            # Large range: show major intervals
            if data_range <= 500:
                step = 50
            elif data_range <= 1000:
                step = 100
            else:
                step = 200
            
            tick_values = []
            current = min_clients
            while current <= max_clients:
                tick_values.append(current)
                current += step
            if max_clients not in tick_values:
                tick_values.append(max_clients)
        
        # Ensure values are sorted and clean
        tick_values = sorted(list(set(tick_values)))

        # Update layout with colorbar showing actual data values and enable zoom controls
        fig.update_layout(
            title={'text': "San Antonio School District Client Distribution", 'x': 0.5, 'xanchor': 'center'},
            height=750,
            margin=dict(l=0, r=0, t=50, b=0),
            coloraxis_colorbar=dict(
                title="Number of Clients",
                tickmode="array",
                tickvals=tick_values,
                ticktext=[str(val) for val in tick_values],
                len=0.7,
                thickness=25,
                title_font_size=14,
                tickfont_size=12
            ),
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