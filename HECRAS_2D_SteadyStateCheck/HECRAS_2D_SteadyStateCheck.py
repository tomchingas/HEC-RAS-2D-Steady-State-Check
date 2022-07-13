import modules
import os
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings("ignore")

dirname = os.path.dirname(__file__)


### UPDATE THESE PARAMETERS PER MODEL AND STABILIZATION REQUIREMENTS
# This script only works if the quotient of the comparison time interval divided by the output time interval is an integer
hdf_file_name = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'data/Sather_Dam.p04.hdf'))
Flow_Area_Name = '2D Flow Area'     # Name of 2D flow area in model
output_time_interval = 60           # minutes
comparison_time_interval = 60       # minutes
WSE_change_limit = 0.01             # ft
two_d_cell_shapefile = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'data/2d_cells_SatherDam.shp'))



df_cell_water_surface_elevations_per_timestep = modules.create_pandas_dataframe_from_hdf5_HECRAS_output_cell_WS_results(hdf_file_name, Flow_Area_Name)

print(type(df_cell_water_surface_elevations_per_timestep))
print('Water surface dataframe shape: ' + str(df_cell_water_surface_elevations_per_timestep.shape))



df_cell_water_surface_elevations_per_timestep = modules.remove_rows_in_df_WS_so_comparison_time_matches_output_time_intervals(df_cell_water_surface_elevations_per_timestep, comparison_time_interval, output_time_interval)

print('Water surface dataframe with time steps removed shape: ' + str(df_cell_water_surface_elevations_per_timestep.shape))



wetted_cell_list = modules.create_list_of_wetted_cells_from_df_WS(df_cell_water_surface_elevations_per_timestep, WSE_change_limit)

print(f'wetted_cell_list {type(wetted_cell_list)}')
print('Number of wetted cells: ' + str(len(wetted_cell_list)))



df_time_cells_wetted = modules.create_dataframe_time_cells_wetted(df_cell_water_surface_elevations_per_timestep, wetted_cell_list, comparison_time_interval, output_time_interval)

print('Cell wetted time dataframe shape: ' + str(df_time_cells_wetted.shape))



df_steady_state_cell_time = modules.create_dataframe_time_cells_reached_steady_state(df_cell_water_surface_elevations_per_timestep, wetted_cell_list, WSE_change_limit, comparison_time_interval, output_time_interval)

print('Last stabilized cell at time interval dataframe shape: ' + str(df_steady_state_cell_time.shape))



df_cell_stabilization_summary = modules.create_dataframe_CellStabilizationSummary(df_time_cells_wetted, df_steady_state_cell_time, df_cell_water_surface_elevations_per_timestep)

print(' Time to stabilize summary dataframe shape: ' + str(df_cell_stabilization_summary.shape))


# write 2d cell shapefile with time to stabilize field added
modules.load_2D_cell_shapefile_add_SteadyStateTime_field_and_write_new_2D_cell_shapefile(df_cell_water_surface_elevations_per_timestep, df_time_cells_wetted, df_cell_stabilization_summary, two_d_cell_shapefile)




### plot data

print(f'Number of rows in each column:  \n {df_cell_stabilization_summary.count(1)} \n')



# wetted time histogram

plot = df_time_cells_wetted.iloc[0].T.hist(bins=20, figsize=(12,8), color='#86bf91', zorder=2, rwidth=0.9)

plot.set_title('Cell Wetted Time Histogram')
plot.set_xlabel("Time Cell Was Wetted (hours)")
plot.set_ylabel("Number of Cells")

plt.show()


# stabilized time histogram

plot = df_steady_state_cell_time.iloc[0].T.hist(bins=20, figsize=(12,8), color='#86bf91', zorder=2, rwidth=0.9)

plot.set_title('Time Cell Stabilized Histogram')
plot.set_xlabel("Time Cell Stabilized (hours)")
plot.set_ylabel("Number of Cells")

plt.show()


# time for a cell to stabilize histogram

plot = df_cell_stabilization_summary.iloc[2].T.hist(bins=20, figsize=(12,8), color='#86bf91', zorder=2, rwidth=0.9)

plot.set_title('Time for a Cell to Stabilize Histogram')
plot.set_xlabel("Time for Cell to Stabilize (hours)")
plot.set_ylabel("Number of Cells")

plt.show()
