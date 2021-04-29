import os
import pandas as pd
from utils_30min import *
from buy_sell_signal import *
from summary import *


def do_signal_processing(stock, name_head, close_bar, start_time, current_end, full_signal_file):
    temp_path = os.path.join(name_head, '{}'.format(current_end.strftime('%Y%m%d')))
    if not os.path.exists(temp_path):
        os.mkdir(temp_path)
    close_bar_temp = close_bar[(close_bar['date'] < current_end)
                               & (close_bar['date'] >= start_time)]
    chan = Chan()
    signal_v1 = [False for i in range(6)]
    buy_signal_1_v3, sell_signal_1_v3 = False, False
    real_date = None
    data_name = os.path.join(temp_path, 'summary_' + stock[:-5] + '.csv')
    chan_name = os.path.join(temp_path, stock[:-5] + 'chan.pkl')

    output_data = pd.DataFrame(columns=['buy/sell', 'date', 'neighbor_up_down', 'm_H', 'm_L', 'n_H',
                                        'n_L', 'm_H2', 'm_L2', 'n_H2', 'n_L2'])

    for i in range(len(close_bar_temp)):
        temp_x = close_bar_temp[i:i + 1].values[0]
        temp_df = pd.DataFrame({'high': temp_x[3], 'low': temp_x[2], 'date': temp_x[4]},
                               index=[0], columns=['high', 'low', 'date'])
        b_new_area_v3, b_new_line, b_new_area_v1, b_new_area_v2 = chan.update(temp_df)

        chan.update_trend()
        trend_signal, real_date = signal_processing_trend(chan, close_bar)
        for j in range(len(trend_signal)):
            if trend_signal[j]:
                temp_data = pd.DataFrame(
                    {'level': 4 + j // 2 + 1, 'buy/sell': (j + 1) % 2, 'date': temp_x[4], 'neighbor_up_down': 0,
                     'n_H': 0, 'n_L': 0,
                     'n_H2': 0, 'n_L2': 0, 'real_date': real_date},
                    index=[0], columns=['level', 'buy/sell', 'date', 'neighbor_up_down',
                                        'm_H', 'm_L', 'n_H', 'n_L', 'm_H2', 'm_L2', 'n_H2', 'n_L2',
                                        'real_date'])
                output_data = output_data.append(temp_data, sort=True)
                trend_signal[j] = False
        signal_v1, real_date = signal_processing_v1(chan, close_bar)
        output_data = output_v1(signal_v1[0], signal_v1[1],
                                signal_v1[2], signal_v1[3],
                                signal_v1[4], signal_v1[5],
                                buy_signal_1_v3, sell_signal_1_v3,
                                real_date, chan, temp_x, output_data)
        signal_v1 = [False for i in range(6)]
        buy_signal_1, sell_signal_1 = False, False
        buy_signal_2, sell_signal_2 = False, False
        buy_signal_3, sell_signal_3 = False, False
        buy_signal_1_v3, sell_signal_1_v3 = False, False
    output_data.to_csv(data_name)
    output_hal = open(chan_name, 'wb')
    str_chan = pickle.dumps(chan)
    output_hal.write(str_chan)
    output_hal.close()
    if len(full_signal_file) == 0:
        full_signal_file = output_data
    else:
        last_date = full_signal_file.tail(1)['date'].values[0]
        last_date = pd.to_datetime(last_date)
        output_data = output_data[output_data['date'] > last_date]
        full_signal_file = full_signal_file.append(output_data)
    return full_signal_file