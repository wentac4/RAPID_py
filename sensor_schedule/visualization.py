import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

import random
import math


river_network_shp_path = '../rapid_data/NHDFlowline_San_Guad/NHDFlowline_San_Guad.shp'
river_network_dbf_path = '../rapid_data/NHDFlowline_San_Guad/NHDFlowline_San_Guad.dbf'
river_network_shx_path = '../rapid_data/NHDFlowline_San_Guad/NHDFlowline_San_Guad.shx'
river_network_prj_path = '../rapid_data/NHDFlowline_San_Guad/NHDFlowline_San_Guad.prj'

streamgages_shp_path = '../rapid_data/StreamGageEvent_San_Guad_comid_withdir_full_2010_2013/StreamGageEvent_San_Guad_comid_withdir_full_2010_2013.shp'
streamgages_dbf_path = '../rapid_data/StreamGageEvent_San_Guad_comid_withdir_full_2010_2013/StreamGageEvent_San_Guad_comid_withdir_full_2010_2013.dbf'
streamgages_shx_path = '../rapid_data/StreamGageEvent_San_Guad_comid_withdir_full_2010_2013/StreamGageEvent_San_Guad_comid_withdir_full_2010_2013.shx'
streamgages_prj_path = '../rapid_data/StreamGageEvent_San_Guad_comid_withdir_full_2010_2013/StreamGageEvent_San_Guad_comid_withdir_full_2010_2013.prj'


river_network = gpd.read_file(river_network_shp_path)
streamgages = gpd.read_file(streamgages_shp_path)


G = len(streamgages)  # number of sensors in ground set
K = 12                # number of sensors to be selected

Q = list(range(0, G))


gauge_locations = {index: point.coords[0][0:2] for index, point in enumerate(streamgages['geometry'])}

lon_range = (-99.0, -97.5)
lat_range = (28.50, 30.25)

drone_locations = {i: [random.uniform(lon_range[0], lon_range[1]), random.uniform(lat_range[0], lat_range[1])] for i in range(K)}  # {drone_index: drone_coordinates}


frames_per_second = 20
seconds_per_selection = 2
number_of_selections = 5


fig, ax = plt.subplots()

S = []
closest_gauges_to_drones = {i: None for i in range(K)}  # {drone_index: ((index_of_closest_gauge, coordinates_of_closest_gauge), (x_distance_to_closest_gauge, y_distance_to_closest_gauge))}

drone_velocities = {i: [0.0, 0.0] for i in range(K)}     # {drone_index: [velocity_in_x_direction, velocity_in_y_direction]}
drone_accelerations = {i: [0.0, 0.0] for i in range(K)}  # {drone_index: [acceleration_in_x_direction, acceleration_in_y_direction]}

def update(frame):
    ax.clear()
    river_network.plot(ax=ax, label='River Network', zorder=1)
    
    if (frame % (frames_per_second*seconds_per_selection) == 0):
        global S
        S = random.sample(Q, K)

        selected_gauge_locations = {gauge_index: gauge_coords for gauge_index, gauge_coords in gauge_locations.items() if gauge_index in S}
        for drone_index in range(K):
            distances_to_gauges = {gauge_index: (gauge_coords[0]-drone_locations[drone_index][0], gauge_coords[1]-drone_locations[drone_index][1]) for gauge_index, gauge_coords in selected_gauge_locations.items()}
            closest_gauge = min(selected_gauge_locations.items(), key=lambda item: math.sqrt(math.pow(distances_to_gauges[item[0]][0], 2.0) + math.pow(distances_to_gauges[item[0]][0], 2.0)))
            closest_gauges_to_drones[drone_index] = (closest_gauge, distances_to_gauges[closest_gauge[0]])
            selected_gauge_locations.pop(closest_gauges_to_drones[drone_index][0][0])

        # global drone_velocities
        # drone_velocities = {i: [closest_gauges_to_drones[i][1][0] / (frames_per_second*seconds_per_selection/2.0), closest_gauges_to_drones[i][1][1] / (frames_per_second*seconds_per_selection/2.0)] for i in range(K)}
        # global drone_accelerations
        # drone_accelerations = {i: [-closest_gauges_to_drones[i][1][0] / (frames_per_second*seconds_per_selection*10.0), -closest_gauges_to_drones[i][1][1] / (frames_per_second*seconds_per_selection*10.0)] for i in range(K)}
    
    for i in range(K):
        drone_velocities[i][0] = ((closest_gauges_to_drones[i][0][1][0]-drone_locations[i][0])*2.0 + closest_gauges_to_drones[i][1][0]*0.3) / (frames_per_second*seconds_per_selection)
        drone_velocities[i][1] = ((closest_gauges_to_drones[i][0][1][1]-drone_locations[i][1])*2.0 + closest_gauges_to_drones[i][1][1]*0.3) / (frames_per_second*seconds_per_selection)
        drone_locations[i][0] += drone_velocities[i][0]
        drone_locations[i][1] += drone_velocities[i][1]
        # drone_velocities[i][0] += drone_accelerations[i][0]
        # drone_velocities[i][1] += drone_accelerations[i][1]

    streamgages.loc[list(set(Q)-set(S)), 'geometry'].plot(ax=ax, color='blue', edgecolor='purple', label='Gauges', zorder=2)
    streamgages.loc[S, 'geometry'].plot(ax=ax, color='red', edgecolor='purple', label='Selected Gauges', zorder=3)

    for drone_coords in drone_locations.values():
        ax.plot(drone_coords[0], drone_coords[1], marker='x', color='black', label='Drones', zorder=4)

    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    # plt.legend()

ani = FuncAnimation(fig, update, frames=frames_per_second*seconds_per_selection*number_of_selections, repeat=False)


# plt.show()
ani.save('visualization.gif', writer='pillow', fps=frames_per_second)
