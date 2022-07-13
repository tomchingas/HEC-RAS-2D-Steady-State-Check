import modules
import os
import pandas as pd
import numpy as np
import h5py
import matplotlib.pyplot as plt
import geopandas as gdp

dirname = os.path.dirname(__file__)


def create_pandas_dataframe_from_hdf5_HECRAS_output_cell_WS_results(hdf_file_name, flow_area_name):

    # load hdf file
    # needs to be saved in same directory as this python script

    ### add option to include file path

    hf = h5py.File(hdf_file_name, 'r')

    # load data from hdf file

    hdf_datasets = hf.get('Results/Unsteady/Output/Output Blocks/Base Output/Unsteady Time Series/2D Flow Areas/' + str(flow_area_name))

    ## prints dataset names so you can target the desired dataset
    #print(hdf_datasets.items())

    # retrieve Water Surface dataset
    water_surface_dataset = hdf_datasets.get('Water Surface')

    # create numpy array from Water Surface dataset
    water_surface_np_array = np.array(water_surface_dataset)

    hf.close()

    # create pandas dataframe from numpy array
    df_WS = pd.DataFrame(water_surface_np_array)

    return df_WS



def remove_rows_in_df_WS_so_comparison_time_matches_output_time_intervals(df_WS, comparison_time_interval, output_time_interval):

    ### remove rows from df_WS if output time interval is not equal to comparison time interval

    if comparison_time_interval != output_time_interval:
        divider = comparison_time_interval / output_time_interval

        index_list = df_WS.index

        for i in index_list:
            if (i % divider) != 0:
                df_WS = df_WS.drop(labels=[i], axis=0)
        
    return df_WS



def create_list_of_wetted_cells_from_df_WS(df_WS, WSE_change_limit):
    ### create list of wetted cells
    # Get a series containing difference of maximum and minimum value of each column (column name is a cell, rows are WS elev at each time step)

    Max_Min_WS_diff_series = df_WS.max() - df_WS.min()

    wetted_cell_list = []

    for index, value in Max_Min_WS_diff_series.items():
        if value > WSE_change_limit:
            wetted_cell_list.append(index)
    
    return wetted_cell_list



def create_dataframe_time_cells_wetted(df_WS, wetted_cell_list, comparison_time_interval, output_time_interval):
    ### create dataframe with time interval of first wetted cell

    # create pandas dataframe of differences between row and previous row value
    df_WS_diff = df_WS.diff()


    # create empty dictionary to store column names (key) and wetted cell [value]
    first_wetted_cell_dict = {}

    for column_name in wetted_cell_list:

        # turn column from df_WS_diff into a numpy array
        numpy_array_column_values = np.asarray(df_WS_diff[[column_name]])

        # get time of first wetted cell
        # first value in array that is greater than zero

        list_of_cell_diffs_greater_than_zero = np.where(numpy_array_column_values > 0)

        if len(list_of_cell_diffs_greater_than_zero[0]) == 0:
            wet_time = 1
        else:
            wet_time = list_of_cell_diffs_greater_than_zero[0][0]

        first_wetted_cell_dict[int(column_name)] = (wet_time * (comparison_time_interval / output_time_interval))

    df_wetted_cell_time = pd.DataFrame(first_wetted_cell_dict, index=['wetted',])

    return df_wetted_cell_time



def create_dataframe_time_cells_reached_steady_state(df_WS, wetted_cell_list, WSE_change_limit, comparison_time_interval, output_time_interval):
    ### create dataframe with time interval cell to stabilize

    # create empty dictionary to store column names (key) and last stabilized values
    last_stabilized_cell_dict = {}
    df_WS_diff = df_WS.diff()

    for column_name in wetted_cell_list:

        # turn column from df_WS_diff into a numpy array
        numpy_array_column_values = np.asarray(df_WS_diff[[column_name]])

        # get time of stabilized cell
        # check if first value in reversed array greater than WSE_change_limit is greater than 0
        # reverse array and get first value greater than WSE_change_limit
        reversed_numpy_array_column_values = numpy_array_column_values[::-1]

        if np.nanmax(numpy_array_column_values) < WSE_change_limit:
            list_of_cell_diffs_greater_than_zero = np.where(numpy_array_column_values > 0)

            if len(list_of_cell_diffs_greater_than_zero[0]) == 0:
                wet_time = 1
            else:
                wet_time = list_of_cell_diffs_greater_than_zero[0][0]
                last_stabilized_time = wet_time

        else:
            list_of_cell_diffs_greater_than_WSE_change_limit = np.where(reversed_numpy_array_column_values > WSE_change_limit)

            last_stabilized_time = (len(numpy_array_column_values) - list_of_cell_diffs_greater_than_WSE_change_limit[0][0])

        last_stabilized_cell_dict[int(column_name)] = (last_stabilized_time * (comparison_time_interval / output_time_interval))

    df_steady_state_cell_time = pd.DataFrame(last_stabilized_cell_dict, index=['SteadyState',])

    return df_steady_state_cell_time



def create_dataframe_CellStabilizationSummary(df_time_cells_wetted, df_steady_state_cell_time, df_cell_water_surface_elevations_per_timestep):
    # calculate number of cells that did not stabilize
    df_stabilized_cell_numpy_array = df_steady_state_cell_time.to_numpy()

    cells_not_stabilized_count = np.count_nonzero(df_stabilized_cell_numpy_array == len(df_cell_water_surface_elevations_per_timestep.index))

    print(f'{cells_not_stabilized_count} CELLS DID NOT STABILIZE!')

    ### create data frame with wetted cell time interval, last stabilized cell time interval

    df_stab = pd.DataFrame()

    # add wetted cell time interval

    df_stab = df_stab.append(df_time_cells_wetted)

    # add last stabilized cell time interval

    df_stab = df_stab.append(df_steady_state_cell_time)

    ### add time to stabilize to df_stab dataframe

    # create dataframe of difference between rows of df_stab
    df_stab_time = df_stab.diff()

    # rename index stab to stab_time
    df_stab_time = df_stab_time.rename(index={'SteadyState': 'SteadyState_time'})

    # add stab_time row to df_stab
    stab_time = df_stab_time.loc[['SteadyState_time']]
    df_stab = df_stab.append([stab_time])

    return df_stab



def load_2D_cell_shapefile_add_SteadyStateTime_field_and_write_new_2D_cell_shapefile(df_cell_water_surface_elevations_per_timestep, df_time_cells_wetted, df_cell_stabilization_summary, two_d_cell_shapefile):
    cell_index_list = list(df_cell_water_surface_elevations_per_timestep)

    wetted_cell_list = list(df_time_cells_wetted)

    # create empty dictionary to store cell index as key and time to stabilize as value
    stab_time_dict = {}

    # populate cell stabilize dictionary
    for index in cell_index_list:
        if index in wetted_cell_list:
            stab_time = df_cell_stabilization_summary.at['SteadyState_time', index]
            stab_time_dict[index] = stab_time

        else:
            # add index and null value to df
            stab_time_dict[index] = 9999


    df_stab_time_dict = pd.DataFrame.from_dict(stab_time_dict, orient='index')

    df_stab_time_dict = df_stab_time_dict.rename(columns={0: 'SS_Time'})

    ### load 2d cell shapefile and add stabilize time field
    gdp_two_d_cells = gdp.read_file(two_d_cell_shapefile)

    # add time to stabilze values
    gdp_two_d_cells_merged = gdp_two_d_cells.merge(df_stab_time_dict, left_on = 'Cell Index', right_index = True)

    # write 2d cell shapefile with time to stabilize field populated to shapefile
    gdp_two_d_cells_merged.to_file(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'data/2d_cells_stab_time.shp')))