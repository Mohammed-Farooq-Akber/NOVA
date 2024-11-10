from django.shortcuts import render, HttpResponse

from datetime import datetime
import os


# Create your views here.
def hello(request):
    return HttpResponse("Hello")


def get_street_network(area):
    # Set a cache key
    cache_key = f"street_network_{area}"
    
    # Try to get data from the cache
    street_network = cache.get(cache_key)
    
    # If not cached, fetch it and store it in the cache
    if not street_network:
        street_network = ox.graph_from_place(area, network_type='walk')
        # Cache the result for a period (e.g., 24 hours)
        cache.set(cache_key, street_network, timeout=86400)
    
    return street_network

def load_sample_food_banks():
    data = {
        'name': [
            'Food Bank For New York City',
            'City Harvest',
            'New York Common Pantry',
            'Holy Apostles Soup Kitchen',
            'St. John\'s Bread & Life',
            'Part of the Solution (POTS)',
            'Bowery Mission',
            'Food Bank of Lower Fairfield County',
            'Hope Community Services',
            'Feeding Westchester'
        ],
        'address': [
            '39 Broadway, New York, NY 10006',
            '6 East 32nd Street, New York, NY 10016',
            '8 East 109th Street, New York, NY 10029',
            '296 9th Avenue, New York, NY 10001',
            '795 Lexington Ave, Brooklyn, NY 11221',
            '2759 Webster Avenue, Bronx, NY 10458',
            '227 Bowery, New York, NY 10002',
            '461 Glenbrook Road, Stamford, CT 06906',
            '50 Washington Avenue, New Rochelle, NY 10801',
            '200 Clearbrook Road, Elmsford, NY 10523'
        ],
        'phone': [
            '(212) 566-7855',
            '(646) 412-0600',
            '(917) 720-9700',
            '(212) 924-0167',
            '(718) 574-0058',
            '(718) 220-4892',
            '(212) 674-3456',
            '(203) 358-8898',
            '(914) 636-4010',
            '(914) 923-1100'
        ],
        'hours': [
            'Mon-Fri 9AM-5PM',
            'Mon-Fri 8AM-6PM',
            'Mon-Sat 9AM-5PM',
            'Mon-Fri 10:30AM-1:30PM',
            'Mon-Fri 8AM-4PM',
            'Mon-Sat 9:30AM-3:30PM',
            'Mon-Sat 8AM-6PM',
            'Mon-Fri 8AM-4PM',
            'Mon-Fri 9AM-5PM',
            'Mon-Fri 8AM-5PM'
        ],
        'needs': [
            'Canned goods, rice, pasta',
            'Fresh produce, canned goods',
            'Non-perishable foods',
            'Canned foods, dry goods',
            'Canned goods, baby food',
            'Non-perishable items',
            'Canned goods, hygiene items',
            'Non-perishable foods',
            'Canned goods, pasta',
            'Fresh produce, canned goods'
        ]
    }
    return pd.DataFrame(data)

def geocode_address(address):
    try:
        geocode_result = gmaps.geocode(address)
        if geocode_result:
            location = geocode_result[0]['geometry']['location']
            return location['lat'], location['lng']
        return None
    except Exception as e:
        st.error(f"Error geocoding address: {str(e)}")
        return None

def get_route(G, origin_coords, dest_coords):
    try:
        orig_node = ox.nearest_nodes(G, X=origin_coords[1], Y=origin_coords[0])
        dest_node = ox.nearest_nodes(G, X=dest_coords[1], Y=dest_coords[0])
        route = nx.shortest_path(G, orig_node, dest_node, weight='length')
        route_coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in route]
        route_length = nx.shortest_path_length(G, orig_node, dest_node, weight='length')
        return {
            'coords': route_coords,
            'distance': route_length,
            'path': route
        }
    except Exception as e:
        st.error(f"Error calculating route: {str(e)}")
        return None

def create_geopandas_df(df):
    geometries = []
    coordinates = []
    for address in df['address']:
        coords = geocode_address(address)
        if coords:
            geometries.append(Point(coords[1], coords[0]))
            coordinates.append(coords)
        else:
            geometries.append(None)
            coordinates.append(None)
    gdf = gpd.GeoDataFrame(df, geometry=geometries)
    gdf['coordinates'] = coordinates
    return gdf.dropna(subset=["geometry"])

def create_map(gdf, user_location=None, max_distance=None, route_details=None):
    if user_location:
        center = user_location
    else:
        center = [gdf.geometry.y.mean(), gdf.geometry.x.mean()]
    
    m = folium.Map(location=center, zoom_start=12)
    marker_cluster = MarkerCluster().add_to(m)
    
    for idx, row in gdf.iterrows():
        if row.geometry:
            distance_text = ""
            if user_location:
                distance = calculate_distance(user_location, (row.geometry.y, row.geometry.x))
                if max_distance and distance > max_distance:
                    continue
                distance_text = f"<br>Distance: {distance:.1f} km"
            
            popup_content = f"""
                <b>{row['name']}</b><br>
                Address: {row['address']}<br>
                Phone: {row['phone']}<br>
                Hours: {row['hours']}<br>
                Needs: {row['needs']}{distance_text}
            """
            
            folium.Marker(
                location=[row.geometry.y, row.geometry.x],
                popup=folium.Popup(popup_content, max_width=300),
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(marker_cluster)
    
    if user_location:
        folium.Marker(
            location=user_location,
            popup='Your Location',
            icon=folium.Icon(color='blue', icon='user')
        ).add_to(m)
    
    if route_details:
        folium.PolyLine(
            locations=route_details['coords'],
            weight=4,
            color='blue',
            opacity=0.5
        ).add_to(m)
    
    return m

def calculate_distance(point1, point2):
    return geodesic(point1, point2).kilometers