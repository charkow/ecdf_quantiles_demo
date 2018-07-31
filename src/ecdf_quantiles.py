import numpy as np
import pandas as pd


def performance_quantiles(data, performance_measure):
    """Calculates quantiles of the performance measure (EUR, CUM).

    Args:
        data: pandas dataframe with well_id, performance measure, ecdf_parameter.
        performance_measure: string representing performance measure to calculate quantiles of.
    Returns:
        Pandas dataframe with well_id, performance_measure, ecdf_parameter, performance_measure_quantiles.
    Example:
        data: well_id, cum_oil, lateral_length
        >>> performance_quantiles(data, cum_oil)
        >>> data_quantiles
        data_quantiles: well_id, cum_oil, lateral_length, cum_oil_quantiles
    """
    quantiles = pd.qcut(x=data[performance_measure], q=4, labels=['q1', 'q2', 'q3', 'q4'])
    bins = quantiles.to_frame(name=performance_measure + '_quantiles')
    data_quantiles = pd.merge(data, bins, right_index=True, left_index=True)
    data_quantiles.dropna(inplace=True)
    data_quantiles.sort_values(performance_measure + '_quantiles', inplace=True)
    return data_quantiles


def ecdf_quantiles(data_quantiles, performance_measure, ecdf_parameter):
    """Divides data by performance quantiles and calculates empirical
       cumulative distribution function of selected parameter for each performance quantile.

       Args:
           data_quantiles: dataframe with well_id, performance_measure, ecdf_parameter,
                           performance_measure_quantiles.
            performance_measure: string representing performance measure to calculate quantiles of.
            ecdf_parameter: sting representing parameter to calculate ecdf for.
        Returns:
            tuple with statsmodel ecdfs for each performance quantiles.
       """
    from statsmodels.distributions.empirical_distribution import ECDF

    data_q1 = data_quantiles[data_quantiles[performance_measure + '_quantiles'].isin(['q1'])]
    data_q2 = data_quantiles[data_quantiles[performance_measure + '_quantiles'].isin(['q2'])]
    data_q3 = data_quantiles[data_quantiles[performance_measure + '_quantiles'].isin(['q3'])]
    data_q4 = data_quantiles[data_quantiles[performance_measure + '_quantiles'].isin(['q4'])]

    ecdf_q1 = ECDF(data_q1[ecdf_parameter])
    ecdf_q2 = ECDF(data_q2[ecdf_parameter])
    ecdf_q3 = ECDF(data_q3[ecdf_parameter])
    ecdf_q4 = ECDF(data_q4[ecdf_parameter])

    return ecdf_q1, ecdf_q2, ecdf_q3, ecdf_q4


def ecdf_plot(ecdf_q1, ecdf_q2, ecdf_q3, ecdf_q4, performance_measure, ecdf_parameter):
    """Generates Plotly plot with ECDFs of the investigated parameter.

    Args:
        ecdf1, ... ecdf4: statsmodel ecdfs.
        performance_measure: string representing performance measure to calculate quantiles of.
        ecdf_parameter: sting representing parameter to calculate ecdf for.
    Returns:
        Plotly plot.
    """
    from plotly.offline import iplot
    import plotly.graph_objs as go

    performance_measure = performance_measure.replace('_', ' ').capitalize()
    ecdf_parameter = ecdf_parameter.replace('_', ' ').capitalize()

    ecdf_1 = go.Scatter(x=ecdf_q1.x,
                        y=ecdf_q1.y,
                        name='0 to 25',
                        mode='lines+markers',
                        marker=dict(size='7', color='#0C3383'))
    ecdf_2 = go.Scatter(x=ecdf_q2.x,
                        y=ecdf_q2.y,
                        name='25 to 50',
                        mode='lines+markers',
                        marker=dict(size='7', color='#57A18F'))
    ecdf_3 = go.Scatter(x=ecdf_q3.x,
                        y=ecdf_q3.y,
                        name='50 to 75',
                        mode='lines+markers',
                        marker=dict(size='7', color='#F2A638'))
    ecdf_4 = go.Scatter(x=ecdf_q4.x,
                        y=ecdf_q4.y,
                        name='75 to 100 (best wells)',
                        mode='lines+markers',
                        marker=dict(size='7', color='#D91E1E'))

    data = [ecdf_1, ecdf_2, ecdf_3, ecdf_4]

    layout = go.Layout(height=650,
                       width=650,
                       title='ECDF ' + ecdf_parameter,
                       titlefont=dict(size=18),

                       xaxis=dict(title=ecdf_parameter,
                                  titlefont=dict(size=16),
                                  type=None,
                                  zeroline=False,
                                  showgrid=True,
                                  showline=False,
                                  autorange=True),

                       yaxis=dict(title='Cumulative Probability',
                                  titlefont=dict(size=16),
                                  showgrid=True,
                                  showline=False,
                                  zeroline=False,
                                  tickvals=[0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1],
                                  range=[-0.03, 1.03]),

                       legend=dict(x=0.65, y=0.1, font=dict(size=14)),
                       margin={'l': 50, 'r': 10, 'b': 50, 't': 85})

    layout.update(dict(annotations=[go.Annotation(text='Quantiles: ' + performance_measure,
                                                  x=np.max(ecdf_q4.x),
                                                  y=0.3,
                                                  showarrow=False,
                                                  bgcolor='#FFFFFF',
                                                  font=dict(size=16))]))

    plot = go.Figure(data=data, layout=layout)

    iplot(plot, show_link=False)
