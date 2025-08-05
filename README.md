# SOS Students of Service Dashboard

A comprehensive analytics dashboard for the SOS (Students of Service) program, built with Dash and Python.

## Features

- 📊 **Interactive Dashboard**: Real-time analytics and visualizations
- 📈 **Population Statistics**: Detailed demographic analysis
- 📋 **Frequency Tables**: Single and multi-variable frequency analysis
- 🥧 **Pie Charts**: Customizable pie chart generator
- 🗺️ **Geographic Maps**: Interactive maps with multiple visualization types
- 📁 **File Upload**: Upload Excel datasets for analysis
- 📊 **Survey Analysis**: Likert scale response analysis

## Local Development

### Prerequisites

- Python 3.8+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/jojoaj35/SOS-Data-project.git
cd SOS-Data-project

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
python New_Dashboard.py
```

The dashboard will be available at `http://localhost:8000`

## Required Data Files

The dashboard includes two geojson files for map functionality:

1. **`texas_zcta_2024_simplified.geojson`** (19MB) - Texas ZIP code boundaries
2. **`School_Districts_2025_.geojson`** (2.4MB) - School district boundaries

These files are included in the repository and will be automatically available when you clone the project.

## Deployment to Render

### Option 1: Using GitHub Integration (Recommended)

1. **Push to GitHub** (if not already done):

   ```bash
   git push origin main
   ```

2. **Connect to Render**:

   - Go to [render.com](https://render.com)
   - Sign up/Login with your GitHub account
   - Click "New +" → "Web Service"
   - Connect your GitHub repository: `jojoaj35/SOS-Data-project`

3. **Configure the Service**:

   - **Name**: `sos-dashboard`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python New_Dashboard.py`
   - **Plan**: Free (or choose paid plan)

4. **Environment Variables** (optional):

   - `RENDER`: `true` (automatically set by Render)

5. **Deploy**: Click "Create Web Service"

### Option 2: Using render.yaml

The repository includes a `render.yaml` file for automatic deployment configuration.

### Option 3: Manual Deployment

1. **Create a new Web Service** on Render
2. **Connect your GitHub repository**
3. **Use these settings**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python New_Dashboard.py`

## File Structure

```
SOS-Data-project/
├── New_Dashboard.py          # Main dashboard application
├── dashboard_components.py    # Dashboard components and functions
├── data_processing.py        # Data processing utilities
├── requirements.txt          # Python dependencies
├── assets/                   # CSS styling files
│   ├── custom_designer.css
│   └── likert_dropdown.css
├── texas_zcta_2024_simplified.geojson  # Texas ZIP code data (19MB)
├── School_Districts_2025_.geojson       # School districts data (2.4MB)
├── render.yaml              # Render deployment config
├── Procfile                 # Render deployment config
└── README.md               # This file
```

## Data Requirements

The dashboard expects Excel files with the following sheets:

- **Clients**: Student/client information
- **Service Hours**: Service activity records
- **Likert Scale** (optional): Survey responses

## Technologies Used

- **Dash**: Web framework for building analytical web applications
- **Plotly**: Interactive plotting library
- **Pandas**: Data manipulation and analysis
- **GeoPandas**: Geospatial data processing
- **Bootstrap**: CSS framework for styling

## Support

For issues or questions, please contact the development team.

---

**SOS Students of Service** - Learn. Serve. Explore.
