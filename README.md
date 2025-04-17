# ERA5 Interactive Climate Explorer

This project is a web-based tool to explore reanalysis climate data from the ERA5 dataset. It offers an interactive and intuitive interface for scientists, analysts, and technical users to:

- Visualize spatial climate fields.
- Explore temporal patterns with custom aggregation.
- Select regions or points and generate climate indices.
- Compare time series of those indices interactively.
- Export the generated data for further analysis.

---

## 📊 Core Features

### 1. Variable Selection
- Drop-down menu of available ERA5 variables (`t2m`, `tp`, `msl`, etc.).
- Loads and displays the most recent available map for the selected variable.

### 2. Spatial Visualization
- Interactive heatmap using Plotly.
- Hover for value inspection.
- Fixed projection and view (e.g., South America or custom domain).
- Option to view single date or aggregate over time range (`mean`, `sum`, etc).

### 3. Spatial Selection
- Click on the map to select a point.
- Use sliders or bounding box to select a region.
- Predefined region list (optional).
- Generates a new index per selection.

### 4. Time Series Viewer
- Interactive Plotly line chart.
- Add multiple indices to same plot.
- Zoom, pan, and hover enabled.
- Colored legend and removable series.

### 5. Export
- Button to export generated indices as `.csv`.
- Format: `date, index1, index2, ...`


---

## ✉️ Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/your-user/era5_viewer.git
   cd era5_viewer
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:
   ```bash
   streamlit run app.py
   ```


