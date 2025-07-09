import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

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
        import geopandas as gpd
        import json
        
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
        
        # Ensure proper coordinate reference system
        merged = merged.to_crs('EPSG:4326')
        
        # Create color bins for better visualization
        max_val = merged['SERVICE_EVENTS'].max()
        if max_val > 0:
            color_bins = [0, 1, 2, 5, 10, 15, 25, 50, 100, max_val]
            color_bins = sorted(list(set([b for b in color_bins if b <= max_val] + [max_val])))
        else:
            color_bins = [0, 1]

        def assign_color_category(value):
            if value == 0:
                return 0
            for i, bin_val in enumerate(color_bins[1:], 1):
                if value <= bin_val:
                    return i
            return len(color_bins) - 1

        merged['Color_Category'] = merged['SERVICE_EVENTS'].apply(assign_color_category)
        
        # Create GeoJSON
        geojson = json.loads(merged.to_json())
        
        # Create choropleth map with district-style appearance
        fig = px.choropleth_mapbox(
            merged,
            geojson=geojson,
            locations=merged.index,
            color='Color_Category',
            color_continuous_scale=['#f7fbff', '#deebf7', '#c6dbef', '#9ecae1', '#6baed6', '#4292c6', '#2171b5', '#08519c', '#08306b'],  # Blues style
            range_color=(0, len(color_bins) - 1),
            mapbox_style="open-street-map",  # Colorful background like district map
            zoom=9.2,
            center={"lat": 29.4241, "lon": -98.4936},
            opacity=0.8,
            hover_name='ZCTA5CE20',
            title="Service Events by ZIP Code - Where Services Are Provided"
        )

        # Update hover template and styling
        fig.update_traces(
            hovertemplate="<b>ZIP Code:</b> %{hovertext}<br><b>Service Events:</b> %{customdata[0]}<br><b>Total Hours:</b> %{customdata[1]:.1f}<br><extra></extra>",
            hovertext=merged['ZCTA5CE20'],
            customdata=np.column_stack([merged['SERVICE_EVENTS'], merged['TOTAL_HOURS']])
        )
        
        # Update layout for consistent styling
        fig.update_layout(
            title={'text': "Service Events by ZIP Code - Where Services Are Provided", 'x': 0.5, 'xanchor': 'center'},
            height=height,
            margin=dict(l=0, r=0, t=50, b=0),
            font=dict(family="Arial, sans-serif", size=12, color="#2c3e50"),
            paper_bgcolor='white',
            plot_bgcolor='white'
        )
        
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