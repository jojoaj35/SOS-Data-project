import pandas as pd 
import geopandas as gpd 
import plotly.graph_objects as go
import plotly.express as px
import json
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def create_heatmap_from_dataframe(clients_df, height=600):
    """Create heatmap from clients dataframe"""
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
        
        # Create map
        merged_json = json.loads(merged.to_json())
        custom_data = np.column_stack([merged['ZCTA5CE20']])
        
        fig = go.Figure(go.Choroplethmapbox(
            geojson=merged_json,
            locations=merged.index,
            z=merged['CLIENT_COUNT'],
            colorscale='OrRd',
            marker_opacity=0.85,
            marker_line_width=0.5,
            marker_line_color='white',
            colorbar=dict(title="Number of Clients", len=0.7, thickness=20),
            hovertemplate="<b>ZIP Code:</b> %{customdata[0]}<br><b>Client Count:</b> %{z}<br><extra></extra>",
            customdata=custom_data,
            name=""
        ))
        
        # Center and layout
        bounds = merged.total_bounds
        center_lat = (bounds[1] + bounds[3]) / 2
        center_lon = (bounds[0] + bounds[2]) / 2
        
        fig.update_layout(
            mapbox_style="carto-positron",
            mapbox_zoom=9.2,  # Higher zoom for horizontal rectangle format
            mapbox_center={"lat": center_lat, "lon": center_lon},
            margin={"r":20,"t":60,"l":20,"b":20},
            height=height,
            title={
                'text': "San Antonio Area - ZIP Code Client Distribution", 
                'x': 0.5, 
                'xanchor': 'center',
                'font': {'size': 16, 'color': '#2c3e50'}
            },
            autosize=True
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
