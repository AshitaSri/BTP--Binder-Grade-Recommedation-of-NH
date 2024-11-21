import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

def determine_vg_grade(mean_temp):
    """
    Determine VG grade based on mean temperature according to IRC:SP:73-2018 guidelines
    """
    if mean_temp < 30:
        return "VG-10"
    elif mean_temp < 38:
        return "VG-20"
    elif mean_temp < 45:
        return "VG-30"
    elif mean_temp > 45:
        return "VG-40"
    else:
        return "VG-50"

def get_vg_grade_color(vg_grade):
    """
    Assign colors to each VG grade for visualization
    """
    colors = {
        "VG-10": "#1f77b4",  # Blue
        "VG-20": "#ff7f0e",  # Orange
        "VG-30": "#2ca02c",  # Green
        "VG-40": "#d62728",  # Red
        "VG-50": "#9467bd"   # Purple
    }
    return colors.get(vg_grade, "#7f7f7f")  # Default gray if grade not found

def visualize_highway_chainage(folder_path):
    """
    Visualize highway chainages from saved CSV files
    """
    st.title("📊 Highway Temperature Chainage Analysis")
    st.markdown(
        "Analyze highway segments, their temperatures, and VG grades based on mean temperatures. "
        "Interactive visualizations and insights are provided for better decision-making."
    )
    st.divider()

    # List all highway files in the folder
    change_point_files = [f for f in os.listdir(folder_path) if f.endswith('_change_points_coordinates.csv')]
    
    # Dropdown to select highway
    selected_highway = st.selectbox(
        "🛣️ Select Highway", 
        [f.replace('_change_points_coordinates.csv', '') for f in change_point_files]
    )
    st.divider()

    # Construct full file paths
    change_points_file = os.path.join(folder_path, f"{selected_highway}_change_points_coordinates.csv")
    segments_file = os.path.join(folder_path, f"{selected_highway}_segments_chainage.csv")

    # Load data
    change_points_df = pd.read_csv(change_points_file)
    segments_df = pd.read_csv(segments_file)

    # Add VG grades and assign colors
    segments_df['vg_grade'] = segments_df['mean_temp'].apply(determine_vg_grade)
    segments_df['color'] = segments_df['vg_grade'].apply(get_vg_grade_color)

    # Map visualization
    st.subheader("🌍 Highway Map Visualization")
    fig = go.Figure(go.Scattermapbox(
        lat=change_points_df['Latitude'],
        lon=change_points_df['Longitude'],
        mode='markers+lines',
        marker={'size': 12, 'color': '#1f77b4'},  # Blue for points
        text=[f'Change Point {i+1}' for i in range(len(change_points_df))]
    ))
    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox=dict(
            center=dict(
                lat=change_points_df['Latitude'].mean(),
                lon=change_points_df['Longitude'].mean()
            ),
            zoom=6
        ),
        height=700,  # Larger map
        margin={"l": 0, "r": 0, "t": 0, "b": 0}
    )
    st.plotly_chart(fig, use_container_width=True)

    # Segments table
    st.subheader("📋 Highway Segments Details")
    st.markdown("Detailed information about highway segments and their corresponding VG grades.")
    st.dataframe(
        segments_df[['start_km', 'end_km', 'mean_temp', 'vg_grade']], 
        hide_index=False,
        use_container_width=True,
        height=400
    )

    # Additional insights
    st.divider()
    st.subheader("🔍 Segment Insights")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("🛣️ Total Highway Length", f"{segments_df['end_km'].max():.2f} km")
    with col2:
        st.metric("📊 Number of Segments", len(segments_df))

    # Temperature distribution
    st.subheader("🌡️ Temperature Distribution by VG Grade")
    temp_fig = go.Figure()
    for _, row in segments_df.iterrows():
        temp_fig.add_trace(go.Bar(
            x=[f"Segment {int(row.name) + 1}"], 
            y=[row['mean_temp']], 
            text=row['vg_grade'],
            hovertemplate='<b>%{x}</b><br>Mean Temp: %{y:.2f}°C<br>VG Grade: %{text}<extra></extra>',
            marker_color=row['color']
        ))
    temp_fig.update_layout(
        title=dict(
            text='Mean Temperature per Segment',
            x=0.5,
            font=dict(size=18, family='Arial')
        ),
        xaxis_title='Segment',
        yaxis_title='Mean Temperature (°C)',
        height=500,
        margin={"l": 40, "r": 40, "t": 40, "b": 40},
        showlegend=False  # No need for a legend since grade info is in hovertemplate
    )
    st.plotly_chart(temp_fig, use_container_width=True)

def main():
    # Page header
    st.set_page_config(page_title="Highway Analysis", layout="wide")

    # Sidebar for folder input
    st.sidebar.title("🔧 Configuration")
    folder_path = st.sidebar.text_input("Enter the folder path containing highway CSV files:")
    st.sidebar.markdown(
        "Ensure the folder contains CSV files in the correct format:\n"
        "- `<highway_name>_change_points_coordinates.csv`\n"
        "- `<highway_name>_segments_chainage.csv`"
    )

    if folder_path and os.path.exists(folder_path):
        visualize_highway_chainage(folder_path)
    elif folder_path:
        st.sidebar.error("❌ Invalid folder path. Please check the directory.")
    else:
        st.sidebar.info("Enter a valid folder path to begin.")

if __name__ == "__main__":
    main()
