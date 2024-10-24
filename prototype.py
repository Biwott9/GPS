import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
from geopy.distance import geodesic
from folium.plugins import Draw, locate_control

# Set page configuration
st.set_page_config(
    page_title="Dedan Kimathi University Navigation",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define university locations with boundaries (radius in meters)
locations = pd.DataFrame({
    'name': [
        'Main Gate', 
        'Library', 
        'Administration Block', 
        'Engineering Block', 
        'Student Center'
    ],
    'latitude': [-0.3918, -0.3925, -0.3920, -0.3928, -0.3922],
    'longitude': [36.9630, 36.9635, 36.9638, 36.9632, 36.9640],
    'type': ['Entry', 'Academic', 'Administrative', 'Academic', 'Services'],
    'radius': [50, 70, 60, 80, 65]  # radius in meters for each location
})

def create_dark_overlay(map_obj):
    """Create a dark overlay for the entire map"""
    bounds = [[-0.3950, 36.9600], [-0.3900, 36.9700]]  # Adjusted to cover university area
    folium.Rectangle(
        bounds=bounds,
        color='#000000',
        fill=True,
        fillColor='#000000',
        fillOpacity=0.5,
        weight=0
    ).add_to(map_obj)

def create_map(center_lat=-0.3923, center_lon=36.9634, zoom=17, highlight_name=None):
    """Create a Folium map with highlighted location"""
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom,
        tiles="OpenStreetMap"
    )
    
    # Add dark overlay if a location is highlighted
    if highlight_name:
        create_dark_overlay(m)
    
    # Add location markers
    for idx, row in locations.iterrows():
        is_highlighted = highlight_name and row['name'] == highlight_name
        
        # Create marker
        marker = folium.Marker(
            [row['latitude'], row['longitude']],
            popup=f"""
                <b>{row['name']}</b><br>
                Type: {row['type']}<br>
                Lat: {row['latitude']:.4f}<br>
                Lon: {row['longitude']:.4f}
            """,
            tooltip=row['name']
        )
        
        # If this is the highlighted location
        if is_highlighted:
            # Add highlight circle
            folium.Circle(
                location=[row['latitude'], row['longitude']],
                radius=row['radius'],
                color='#FFD700',
                fill=True,
                fillColor='#FFD700',
                fillOpacity=0.3,
                weight=2
            ).add_to(m)
            
            # Add glowing marker
            icon_html = f'''
                <div style="
                    width: 20px;
                    height: 20px;
                    background-color: #FFD700;
                    border-radius: 50%;
                    box-shadow: 0 0 20px #FFD700;
                    animation: pulse 2s infinite;
                ">
                </div>
                <style>
                    @keyframes pulse {{
                        0% {{ box-shadow: 0 0 0 0 rgba(255, 215, 0, 0.7); }}
                        70% {{ box-shadow: 0 0 0 20px rgba(255, 215, 0, 0); }}
                        100% {{ box-shadow: 0 0 0 0 rgba(255, 215, 0, 0); }}
                    }}
                </style>
            '''
            marker = folium.Marker(
                [row['latitude'], row['longitude']],
                popup=f"""
                    <b>{row['name']}</b><br>
                    Type: {row['type']}<br>
                    Lat: {row['latitude']:.4f}<br>
                    Lon: {row['longitude']:.4f}
                """,
                tooltip=row['name'],
                icon=DivIcon(html=icon_html)
            )
            
        marker.add_to(m)
    
    # Add drawing and location controls
    Draw(
        export=False,
        position='topleft',
        draw_options={
            'polyline': True,
            'marker': True,
            'circle': True,
            'rectangle': False,
            'polygon': False,
            'circlemarker': False
        }
    ).add_to(m)
    
    Locate().add_to(m)
    
    return m

def main():
    # Title and description
    st.title("🗺 Dedan Kimathi University Navigation System")
    
    # Initialize session state for highlighted location if not exists
    if 'highlighted_location' not in st.session_state:
        st.session_state.highlighted_location = None
    
    # Create sidebar for controls
    with st.sidebar:
        st.header("Navigation Controls")
        
        # Search functionality
        st.subheader("🔍 Location Search")
        search_term = st.text_input(
            "Search for a location",
            placeholder="Enter location name..."
        )
        
        # Filter locations based on type
        st.subheader("🏢 Filter by Type")
        selected_type = st.selectbox(
            "Select location type",
            ["All"] + list(locations['type'].unique())
        )
        
        # Show location list
        st.subheader("📍 All Locations")
        if selected_type != "All":
            filtered_locations = locations[locations['type'] == selected_type]
        else:
            filtered_locations = locations
        
        selected_location = st.selectbox(
            "Select a location to view",
            filtered_locations['name']
        )

    # Initialize highlight_name based on search or selection
    highlight_name = None
    
    # Update highlighted location based on search or selection
    if search_term:
        found_locations = locations[
            locations['name'].str.lower().str.contains(search_term.lower())
        ]
        if not found_locations.empty:
            highlight_name = found_locations.iloc[0]['name']
            st.session_state.highlighted_location = highlight_name
            map_center = (
                found_locations.iloc[0]['latitude'],
                found_locations.iloc[0]['longitude']
            )
            m = create_map(map_center[0], map_center[1], zoom=18, 
                           highlight_name=st.session_state.highlighted_location)
        else:
            st.session_state.highlighted_location = None
            m = create_map()
    elif selected_location:
        highlight_name = selected_location
        st.session_state.highlighted_location = highlight_name
        loc = locations[locations['name'] == selected_location].iloc[0]
        m = create_map(loc['latitude'], loc['longitude'], zoom=18, 
                       highlight_name=st.session_state.highlighted_location)
    else:
        st.session_state.highlighted_location = None
        m = create_map()

    # Create two columns for map and info
    col1, col2 = st.columns([7, 3])
    
    with col1:
        # Display the map
        folium_static(m, width=800, height=600)

    with col2:
        # Information panel
        st.subheader("📌 Location Information")
        if selected_location:
            loc = locations[locations['name'] == selected_location].iloc[0]
            st.write(f"*Name:* {loc['name']}")
            st.write(f"*Type:* {loc['type']}")
            st.write(f"*Coordinates:* ({loc['latitude']:.4f}, {loc['longitude']:.4f})")
            
            # Calculate distances to other locations
            st.subheader("📏 Distances to Other Locations")
            selected_coords = (loc['latitude'], loc['longitude'])
            
            distances = []
            for idx, row in locations.iterrows():
                if row['name'] != selected_location:
                    target_coords = (row['latitude'], row['longitude'])
                    distance = geodesic(selected_coords, target_coords).meters
                    distances.append({
                        'location': row['name'],
                        'distance': f"{distance:.0f} meters"
                    })
            
            distance_df = pd.DataFrame(distances)
            st.dataframe(distance_df, hide_index=True)

    # Footer with instructions
    st.markdown("---")
with st.expander("ℹ How to Use"):
        # Footer with instructions
    st.markdown("---")
with st.expander("ℹ How to Use"):
    st.markdown("""
        1. *Search*: Use the search box in the sidebar to find specific locations
        2. *Filter*: Filter locations by type using the dropdown
        3. *Navigation*: Click on markers to see location details
        4. *Highlighting*: Selected locations will be highlighted with the rest of the map dimmed
        5. *Drawing*: Use the drawing tools on the left side of the map to:
           - Mark custom points
           - Draw paths
           - Measure distances
        6. *Location*: Use the location button to find your current position on the map
    """)
