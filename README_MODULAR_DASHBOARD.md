# Modular Dashboard Setup Guide

## Overview

The dashboard has been restructured into separate, modular files to improve maintainability and fix the callback issues you were experiencing.

## File Structure

```
📁 sos data project 3/
├── Format_Dash_Fixed.py         # Main dashboard application
├── dashboard_components.py      # Chart and visualization components
├── data_processing.py          # Data processing and upload functions
├── heatmap.py                  # Geographic heatmap functions
├── events_analysis.py          # Service events analysis
└── requirements.txt            # Dependencies
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Dashboard

```bash
python Format_Dash_Fixed.py
```

### 3. Access the Dashboard

Open your browser and go to: http://localhost:8000

## Key Features

### 🔧 **Modular Architecture**

- **dashboard_components.py**: Contains all chart creation functions
- **data_processing.py**: Handles data cleaning and processing
- **Format_Dash_Fixed.py**: Main application with simplified callbacks

### 📊 **Three Main Tabs**

#### 1. **Dashboard Tab**

- **Student Distribution by District**: Interactive pie chart with age filtering
- **Club vs No Club Comparison**: Confidence interval analysis (α=0.05)
- **Active Volunteers by Quarter**: Time series visualization
- **Total Value of Volunteered Time**: Monetary value display ($31/hour)
- **Geographic Distribution Map**: Interactive choropleth maps

#### 2. **Internal Tab**

- **Settings**: Population statistics with dropdown selection
- **Analytics**: Two-column layout for custom analytics
- **Reports**: Report generation section

#### 3. **File Uploader Tab**

- **Drag & Drop Interface**: Upload Excel files (.xlsx/.xls)
- **Data Validation**: Checks for required sheets (Clients, Service Hours, Survey Responses)
- **Processing Pipeline**: Automatic data cleaning and transformation
- **Status Feedback**: Detailed upload and processing status

## How to Use

### Upload New Data

1. Go to the **File Uploader** tab
2. Drag and drop your Excel file or click to browse
3. Wait for processing to complete
4. Check the status messages for success/error information
5. Switch to the **Dashboard** tab to view updated visualizations

### View Analytics

1. **Dashboard**: All main visualizations update automatically after data upload
2. **Internal > Settings**: Select different population statistics from dropdown
3. **Internal > Analytics**: Custom analytics in two-column layout
4. **Internal > Reports**: Generate reports (customizable)

### Geographic Maps

1. In the Dashboard tab, use the **Geographic Distribution Map** section
2. Select map type: "Client Distribution" or "Service Events"
3. Interactive maps show data by ZIP code with color-coded intensity

## Data Processing Pipeline

When you upload a file, the system automatically:

1. **Validates** file format and required sheets
2. **Cleans** data (removes invalid entries, handles missing values)
3. **Transforms** data (converts Yes/No to 1/0, processes ZIP codes)
4. **Enriches** data (adds counties, income ranges, club status)
5. **Aggregates** data (creates quarter summaries, school club data)
6. **Calculates** metrics (confidence intervals, service ranges)

## Fixed Issues

### ✅ **Callback Problems Resolved**

- Simplified callback structure with data store mechanism
- Proper state management for dynamic updates
- No more circular callback dependencies

### ✅ **Modular Design**

- Each component is in its own file for easy maintenance
- Functions are reusable and testable
- Clear separation of concerns

### ✅ **Error Handling**

- Graceful handling of empty datasets
- Proper error messages for failed uploads
- Data validation before processing

## Troubleshooting

### Dashboard Not Loading

- Check if all dependencies are installed: `pip install -r requirements.txt`
- Verify the dashboard is running: `curl http://localhost:8000`
- Check for Python version compatibility (recommended: Python 3.8+)

### Upload Errors

- Ensure Excel file has exactly 3 sheets: Clients, Service Hours, Survey Responses
- Check that Service Hours sheet has 'userId' column (auto-renamed to 'Galaxy ID')
- Verify file format is .xlsx or .xls

### Charts Not Updating

- Make sure to upload data through the File Uploader tab first
- Check that the data contains required columns (Age at Sign Up, District, etc.)
- Refresh the browser if visualizations don't update

## Customization

### Adding New Charts

1. Create chart functions in `dashboard_components.py`
2. Add the chart to the layout in `Format_Dash_Fixed.py`
3. Create a callback to handle updates

### Modifying Data Processing

1. Edit functions in `data_processing.py`
2. The `process_uploaded_data()` function handles all data transformations
3. Add new derived columns or calculations as needed

### Styling Changes

1. Modify the layout components in `Format_Dash_Fixed.py`
2. Update CSS classes and styles in the card components
3. Colors and themes can be changed in the Dash Bootstrap Components

## Performance Notes

- The dashboard uses lazy loading - components only render when tabs are active
- Data processing happens once during upload, not on every chart update
- Geographic maps are optimized for performance with simplified GeoJSON data

## Future Enhancements

- Add export functionality for charts and data
- Implement data caching for faster load times
- Add more interactive filters and controls
- Include advanced analytics and ML insights
