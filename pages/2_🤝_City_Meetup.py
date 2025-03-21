import streamlit as st
import folium
from streamlit_folium import st_folium
from utils.meetup_utils import load_city_data, run_search, haversine_distance
st.logo(
    image="https://upload.wikimedia.org/wikipedia/en/4/41/Flag_of_India.svg",
    link="https://www.linkedin.com/in/mahantesh-hiremath/",
    icon_image="https://upload.wikimedia.org/wikipedia/en/4/41/Flag_of_India.svg"
)
st.set_page_config(page_title="City Meetup Search", page_icon="🤝", layout="wide")

st.title("Optimal Common Meetup Search")
st.markdown("""
Find the optimal meeting point between two cities in India. The search considers:
- Straight-line distance or realistic road distance as heuristics
- Different search strategies (A* and Greedy Best-First Search)
- Time taken for each person to reach the meeting point
""")

# Load city data
cities, neighbors = load_city_data()

# Sidebar controls
with st.sidebar:
    st.header("Search Configuration")
    col1, col2 = st.columns(2)
    
    with col1:
        state1 = st.selectbox(
            "Your State",
            sorted(set(city["state"] for city in cities.values()))
        )
    with col2:
        state2 = st.selectbox(
            "Friend's State",
            sorted(set(city["state"] for city in cities.values())),
            index=1
        )
    
    # Filter cities by selected states
    cities_state1 = {name: info for name, info in cities.items() if info["state"] == state1}
    cities_state2 = {name: info for name, info in cities.items() if info["state"] == state2}
    
    my_city = st.selectbox("Your City", sorted(cities_state1.keys()))
    friend_city = st.selectbox("Friend's City", sorted(cities_state2.keys()))
    
    st.markdown("---")
    
    heuristic = st.selectbox(
        "Heuristic Function",
        ["Straight-line", "Road Distance"],
        help="Straight-line uses direct distance, Road Distance adds 40% to account for actual roads"
    )
    
    algorithm = st.selectbox(
        "Search Algorithm",
        ["A*", "Greedy Best-First"],
        help="A* considers both path cost and heuristic, Greedy only uses heuristic"
    )

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Interactive Map")
    
    # Create map centered between the two cities
    center_lat = (cities[my_city]["lat"] + cities[friend_city]["lat"]) / 2
    center_lon = (cities[my_city]["lon"] + cities[friend_city]["lon"]) / 2
    m = folium.Map(location=[center_lat, center_lon], zoom_start=5)
    
    # Add markers for all cities
    for city, info in cities.items():
        color = "green" if city == my_city else "blue" if city == friend_city else "gray"
        icon = "star" if city in [my_city, friend_city] else "info-sign"
        
        folium.Marker(
            location=[info["lat"], info["lon"]],
            popup=f"{city} ({info['state']})",
            icon=folium.Icon(color=color, icon=icon)
        ).add_to(m)
        
    # Add lines for neighboring cities
    for city, city_neighbors in neighbors.items():
        for neighbor in city_neighbors:
            points = [
                [cities[city]["lat"], cities[city]["lon"]],
                [cities[neighbor]["lat"], cities[neighbor]["lon"]]
            ]
            folium.PolyLine(
                points,
                weight=2,
                color="gray",
                opacity=0.5
            ).add_to(m)
    
    # Display the map
    st_folium(m, width=700, height=500)

with col2:
    st.subheader("Current Selection")
    st.write(f"**Your Location:** {my_city}, {cities[my_city]['state']}")
    st.write(f"**Friend's Location:** {friend_city}, {cities[friend_city]['state']}")
    
    # Calculate direct distance
    direct_distance = haversine_distance(
        cities[my_city]["lat"], cities[my_city]["lon"],
        cities[friend_city]["lat"], cities[friend_city]["lon"]
    )
    st.write(f"**Direct Distance:** {direct_distance:.1f} km")

# Search section
st.markdown("---")
if st.button("Find Optimal Meeting Point", type="primary"):
    with st.spinner("Searching for optimal meeting point..."):
        result = run_search(
            my_city, friend_city,
            algorithm=algorithm,
            heuristic_type=heuristic,
            cities=cities,
            neighbors=neighbors
        )
        
        if result and result["path"] is not None and result["total_cost"] is not None:
            st.success("Found optimal meeting point! 🎯")
            
            # Show metrics in columns
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Travel Cost", f"{result['total_cost']:.1f} km")
            with col2:
                st.metric("Nodes Generated", result['nodes_generated'])
            with col3:
                st.metric("Search Time", f"{result['time_taken']*1000:.6f} ms")
            
            # Show path details in an expander
            with st.expander("View Detailed Path"):
                if isinstance(result['path'], list):
                    st.write("Path sequence:", " → ".join(result['path']))
                    if result['meeting_point']:
                        st.write(f"Meeting Point: {result['meeting_point']}")
                else:
                    st.write("No valid path found")
                
        else:
            st.error("No valid meeting point found! This could be because:")
            st.write("- The cities are too far apart")
            st.write("- No valid path exists between the cities")
            st.write("- The search exceeded the maximum allowed steps")
            st.write("\nTry selecting different cities or changing the search parameters.")
            
            # Still show search statistics if available
            if result and result["nodes_generated"] is not None:
                st.write(f"Nodes explored: {result['nodes_generated']}")
                st.write(f"Search time: {result['time_taken']*1000:.1f} ms")

# Adding a footer

st.markdown(
    '''
    <style>
    .streamlit-expanderHeader {
        background-color: blue;
        color: white; # Adjust this for expander header color
    }
    .streamlit-expanderContent {
        background-color: blue;
        color: white; # Expander content color
    }
    </style>
    ''',
    unsafe_allow_html=True
)

footer="""<style>

.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
background-color: #2C1E5B;
color: white;
text-align: center;
}
</style>
<div class="footer">
<p>Developed with ❤️ by <a style='display: inline; text-align: center;' href="https://www.linkedin.com/in/mahantesh-hiremath/" target="_blank">MAHANTESH HIREMATH</a></p>
</div>
"""
st.markdown(footer,unsafe_allow_html=True)