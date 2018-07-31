import os
import sys
import pandas as pd
import ipywidgets as widgets

from src import ecdf_quantiles as eq

# filesystem
path_root = os.path.normpath(os.getcwd())
path_data_raw = os.path.join(path_root, 'data', 'raw')

data = pd.read_csv(os.path.join(path_data_raw, 'completion_data.csv'), index_col='well_id')

# view
ecdf_param_w = widgets.Dropdown(options=data.columns)
ecdf_param_label_w = widgets.HBox([widgets.Label(value='Completion Parameter:'), ecdf_param_w])
out_ecdf_plot_w = widgets.Output()
ecdf_app = widgets.VBox([ecdf_param_label_w, out_ecdf_plot_w])

# controller
@out_ecdf_plot_w.capture(clear_output=True, wait=True)
def on_ecdf_param_select(change):
    performance_measure = 'Gas Cum 365 / 100 m'
    ecdf_parameter = change['new']
    try:
        data_plot = data[[performance_measure, ecdf_parameter]]
        data_quantiles = eq.performance_quantiles(data_plot, performance_measure)
        ecdf_q1, ecdf_q2, ecdf_q3, ecdf_q4 = eq.ecdf_quantiles(data_quantiles, performance_measure, ecdf_parameter)
        plot = eq.ecdf_plot(ecdf_q1, ecdf_q2, ecdf_q3, ecdf_q4,
                            performance_measure, ecdf_parameter)
        return plot
    except TypeError:
        print('Error: Selected parameter is not numeric.')


ecdf_param_w.observe(on_ecdf_param_select, names='value')
