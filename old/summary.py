import numpy as np
import pandas as pd
import datetime
import talib as ta
import os
import pickle
from utils_30min import *


def output_chan(chan, name_head, filename):
    dirs = os.path.join(name_head, 'orj')
    if not os.path.exists(dirs):
        os.mkdir(dirs)
    output_hal = open(os.path.join(name_head, 'orj', filename), 'wb')
    str = pickle.dumps(chan)
    output_hal.write(str)
    output_hal.close()
    print('final date is {}'.format(chan.x_seq.tail(1)['date'].values[0]))


def load_chan(chan, name_head, filename):
    with open(os.path.join(name_head, 'orj', filename), 'rb') as file:
        chan = pickle.loads(file.read())
        return chan

def save_k_line(close_bar, close_bar_1d, name_head, jq_symbol, frequency):
    bar_name = jq_symbol[:-5] + '_10min.csv' if frequency == '10m' else jq_symbol[:-5] + '.csv'
    close_bar.to_csv(os.path.join(name_head, bar_name))
    close_bar_1d.to_csv(os.path.join(name_head, jq_symbol[:-5] + '_day.csv'))


def load_k_line(name_head, jq_symbol, frequency):
    bar_name = jq_symbol[:-5] + '_10min.csv' if frequency == '10m' else jq_symbol[:-5] + '.csv'
    close_bar = pd.read_csv(os.path.join(name_head, 'orj', bar_name), index_col=0, parse_dates=True)
    close_bar['date'] = pd.to_datetime(close_bar['date'])
    close_bar_1d = pd.read_csv(os.path.join(name_head, 'orj', jq_symbol[:-5] + '_day.csv'), index_col=0, parse_dates=True)
    return close_bar, close_bar_1d

def output_v1(buy_signal_1, sell_signal_1,
              buy_signal_2, sell_signal_2,
              buy_signal_3, sell_signal_3,
              buy_signal_1_v3, sell_signal_1_v3, real_date, chan, temp_x, output_data):
    if buy_signal_1:
        c = chan.c_seq_v3.tail(2)
        neighbor_up_down = 1 if temp_x[1] > c['high'].values[1] else 0
        neighbor_up_down = -1 if c['low'].values[1] > temp_x[1] else 0
        temp_data = pd.DataFrame({'level': 1, 'buy/sell': 1, 'date': temp_x[4],
                                  'neighbor_up_down': neighbor_up_down,
                                  'm_H': c['high'].values[0], 'm_L': c['low'].values[0],
                                  'n_H': c['high'].values[1], 'n_L': c['low'].values[1],
                                  'm_H2': c['high2'].values[0], 'm_L2': c['low2'].values[0],
                                  'n_H2': c['high2'].values[1], 'n_L2': c['low2'].values[1]},
                                 index=[0], columns=['level', 'buy/sell', 'date', 'neighbor_up_down',
                                                     'm_H', 'm_L', 'n_H', 'n_L', 'm_H2', 'm_L2',
                                                     'n_H2', 'n_L2'])
        output_data = output_data.append(temp_data, sort=True)
    elif sell_signal_1:
        c = chan.c_seq_v3.tail(2)
        neighbor_up_down = 1 if temp_x[1] > c['high'].values[1] else 0
        neighbor_up_down = -1 if c['low'].values[1] > temp_x[1] else 0
        temp_data = pd.DataFrame({'level': 1, 'buy/sell': 0, 'date': temp_x[4],
                                  'neighbor_up_down': neighbor_up_down,
                                  'm_H': c['high'].values[0], 'm_L': c['low'].values[0],
                                  'n_H': c['high'].values[1], 'n_L': c['low'].values[1],
                                  'm_H2': c['high2'].values[0], 'm_L2': c['low2'].values[0],
                                  'n_H2': c['high2'].values[1], 'n_L2': c['low2'].values[1]},
                                 index=[0], columns=['level', 'buy/sell', 'date', 'neighbor_up_down',
                                                     'm_H', 'm_L', 'n_H', 'n_L', 'm_H2', 'm_L2',
                                                     'n_H2', 'n_L2'])
        output_data = output_data.append(temp_data, sort=True)
    if buy_signal_2:
        c = chan.c_seq_v3.tail(2)
        neighbor_up_down = 1 if temp_x[1] > c['high'].values[1] else 0
        neighbor_up_down = -1 if c['low'].values[1] > temp_x[1] else 0
        # print('real_date{}'.format(real_date))
        temp_data = pd.DataFrame({'level': 2, 'buy/sell': 1, 'date': temp_x[4],
                                  'neighbor_up_down': neighbor_up_down,
                                  'm_H': c['high'].values[0], 'm_L': c['low'].values[0],
                                  'n_H': c['high'].values[1], 'n_L': c['low'].values[1],
                                  'm_H2': c['high2'].values[0], 'm_L2': c['low2'].values[0],
                                  'n_H2': c['high2'].values[1], 'n_L2': c['low2'].values[1],
                                  'real_date': real_date},
                                 index=[0], columns=['level', 'buy/sell', 'date', 'neighbor_up_down',
                                                     'm_H', 'm_L', 'n_H', 'n_L', 'm_H2', 'm_L2',
                                                     'n_H2', 'n_L2', 'real_date'])
        output_data = output_data.append(temp_data, sort=True)
    elif sell_signal_2:
        c = chan.c_seq_v3.tail(2)
        neighbor_up_down = 1 if temp_x[1] > c['high'].values[1] else 0
        neighbor_up_down = -1 if c['low'].values[1] > temp_x[1] else 0
        temp_data = pd.DataFrame({'level': 2, 'buy/sell': 0, 'date': temp_x[4],
                                  'neighbor_up_down': neighbor_up_down,
                                  'm_H': c['high'].values[0], 'm_L': c['low'].values[0],
                                  'n_H': c['high'].values[1], 'n_L': c['low'].values[1],
                                  'm_H2': c['high2'].values[0], 'm_L2': c['low2'].values[0],
                                  'n_H2': c['high2'].values[1], 'n_L2': c['low2'].values[1],
                                  'real_date': real_date},
                                 index=[0], columns=['level', 'buy/sell', 'date', 'neighbor_up_down',
                                                     'm_H', 'm_L', 'n_H', 'n_L', 'm_H2', 'm_L2', 'n_H2', 'n_L2',
                                                     'real_date'])
        output_data = output_data.append(temp_data, sort=True)
    if buy_signal_3:
        c = chan.c_seq_v3.tail(1)
        if len(c) == 0:
            temp_data = pd.DataFrame(
                {'level': 3, 'buy/sell': 1, 'date': temp_x[4], 'neighbor_up_down': 0,
                 'n_H': 0, 'n_L': 0,
                 'n_H2': 0, 'n_L2': 0, 'real_date': real_date},
                index=[0], columns=['level', 'buy/sell', 'date', 'neighbor_up_down',
                                    'm_H', 'm_L', 'n_H', 'n_L', 'm_H2', 'm_L2', 'n_H2', 'n_L2', 'real_date'])
        else:
            neighbor_up_down = 1 if temp_x[1] > c['high'].values[0] else 0
            neighbor_up_down = -1 if c['low'].values[0] > temp_x[1] else 0
            temp_data = pd.DataFrame(
                {'level': 3, 'buy/sell': 1, 'date': temp_x[4], 'neighbor_up_down': neighbor_up_down,
                 'n_H': c['high'].values[0], 'n_L': c['low'].values[0],
                 'n_H2': c['high2'].values[0], 'n_L2': c['low2'].values[0], 'real_date': real_date},
                index=[0], columns=['level', 'buy/sell', 'date', 'neighbor_up_down',
                                    'm_H', 'm_L', 'n_H', 'n_L', 'm_H2', 'm_L2', 'n_H2', 'n_L2', 'real_date'])
        output_data = output_data.append(temp_data, sort=True)
    elif sell_signal_3:
        c = chan.c_seq_v3.tail(1)
        if len(c) == 0:
            temp_data = pd.DataFrame(
                {'level': 3, 'buy/sell': 1, 'date': temp_x[4], 'neighbor_up_down': 0,
                 'n_H': 0, 'n_L': 0,
                 'n_H2': 0, 'n_L2': 0, 'real_date': real_date},
                index=[0], columns=['level', 'buy/sell', 'date', 'neighbor_up_down',
                                    'm_H', 'm_L', 'n_H', 'n_L', 'm_H2', 'm_L2', 'n_H2', 'n_L2', 'real_date'])
        else:
            neighbor_up_down = 1 if temp_x[1] > c['high'].values[0] else 0
            neighbor_up_down = -1 if c['low'].values[0] > temp_x[1] else 0
            temp_data = pd.DataFrame(
                {'level': 3, 'buy/sell': 0, 'date': temp_x[4], 'neighbor_up_down': neighbor_up_down,
                 'n_H': c['high'].values[0], 'n_L': c['low'].values[0],
                 'n_H2': c['high2'].values[0], 'n_L2': c['low2'].values[0], 'real_date': real_date},
                index=[0], columns=['level', 'buy/sell', 'date', 'neighbor_up_down',
                                    'm_H', 'm_L', 'n_H', 'n_L', 'm_H2', 'm_L2', 'n_H2', 'n_L2', 'real_date'])
        output_data = output_data.append(temp_data, sort=True)
    if buy_signal_1_v3:
        temp_data = pd.DataFrame(
            {'level': 4, 'buy/sell': 1, 'date': temp_x[4], 'neighbor_up_down': 0,
             'n_H': 0, 'n_L': 0,
             'n_H2': 0, 'n_L2': 0, 'real_date': real_date},
            index=[0], columns=['level', 'buy/sell', 'date', 'neighbor_up_down',
                                'm_H', 'm_L', 'n_H', 'n_L', 'm_H2', 'm_L2', 'n_H2', 'n_L2', 'real_date'])
        output_data = output_data.append(temp_data, sort=True)
    elif sell_signal_1_v3:
        temp_data = pd.DataFrame(
            {'level': 4, 'buy/sell': 0, 'date': temp_x[4], 'neighbor_up_down': 0,
             'n_H': 0, 'n_L': 0,
             'n_H2': 0, 'n_L2': 0, 'real_date': real_date},
            index=[0], columns=['level', 'buy/sell', 'date', 'neighbor_up_down',
                                'm_H', 'm_L', 'n_H', 'n_L', 'm_H2', 'm_L2', 'n_H2', 'n_L2', 'real_date'])
        output_data = output_data.append(temp_data, sort=True)
    return output_data


def output_RB(buy_signal_1, sell_signal_1,
              buy_signal_2, sell_signal_2,
              buy_signal_3, sell_signal_3,
              buy_signal_1_v3, sell_signal_1_v3, real_date, chan, temp_x, output_data):

    if buy_signal_1:
        temp_data = pd.DataFrame(
            {'level': 1, 'buy/sell': 1, 'date': temp_x[4], 'neighbor_up_down': 0,
             'n_H': 0, 'n_L': 0,
             'n_H2': 0, 'n_L2': 0, 'real_date': real_date},
            index=[0], columns=['level', 'buy/sell', 'date', 'neighbor_up_down',
                                'm_H', 'm_L', 'n_H', 'n_L', 'm_H2', 'm_L2', 'n_H2', 'n_L2', 'real_date'])
        output_data = output_data.append(temp_data, sort=True)
    elif sell_signal_1:
        temp_data = pd.DataFrame(
            {'level': 1, 'buy/sell': 0, 'date': temp_x[4], 'neighbor_up_down': 0,
             'n_H': 0, 'n_L': 0,
             'n_H2': 0, 'n_L2': 0, 'real_date': real_date},
            index=[0], columns=['level', 'buy/sell', 'date', 'neighbor_up_down',
                                'm_H', 'm_L', 'n_H', 'n_L', 'm_H2', 'm_L2', 'n_H2', 'n_L2', 'real_date'])
        output_data = output_data.append(temp_data, sort=True)
    if buy_signal_2:
        temp_data = pd.DataFrame(
            {'level': 2, 'buy/sell': 1, 'date': temp_x[4], 'neighbor_up_down': 0,
             'n_H': 0, 'n_L': 0,
             'n_H2': 0, 'n_L2': 0, 'real_date': real_date},
            index=[0], columns=['level', 'buy/sell', 'date', 'neighbor_up_down',
                                'm_H', 'm_L', 'n_H', 'n_L', 'm_H2', 'm_L2', 'n_H2', 'n_L2', 'real_date'])
        output_data = output_data.append(temp_data, sort=True)
        output_data = output_data.append(temp_data, sort=True)
    elif sell_signal_2:
        temp_data = pd.DataFrame(
            {'level': 2, 'buy/sell': 1, 'date': temp_x[4], 'neighbor_up_down': 0,
             'n_H': 0, 'n_L': 0,
             'n_H2': 0, 'n_L2': 0, 'real_date': real_date},
            index=[0], columns=['level', 'buy/sell', 'date', 'neighbor_up_down',
                                'm_H', 'm_L', 'n_H', 'n_L', 'm_H2', 'm_L2', 'n_H2', 'n_L2', 'real_date'])
        output_data = output_data.append(temp_data, sort=True)
        output_data = output_data.append(temp_data, sort=True)


    return output_data


def output_lines(chan, output_line):
    num = len(chan.l_seq)
    if num > 2:
        i = num - 3
        start_date = chan.l_seq[i]
        end_date = chan.l_seq[i + 1]
        b_last_up_down = chan.get_l_direction(start_date)
        if b_last_up_down:
            # print('第{}线段为，上升线段'.format(i + 1))
            start = chan.u_t_seq[chan.u_t_seq['date_start'] == start_date]
            if len(start) == 0:
                start = chan.u_seq[chan.u_seq['date_start'] == start_date]
            end = chan.d_t_seq[chan.d_t_seq['date_start'] == end_date]
            if len(end) == 0:
                end = chan.d_seq[chan.d_seq['date_start'] == end_date]
            # assert len(start)+len(end) == 2
            # print('value %.2f 到 %.2f ' % (start['low'].values[0],
            #                               end['high'].values[0]))
            temp_line = pd.DataFrame({'number': i + 1, 'start_value': start['low'].values[0],
                                      'date_start': get_time(start['date_start']),
                                      'date_end': get_time(end['date_start'])},
                                     index=[0], columns=['number', 'start_value', 'date_start', 'date_end'])
            output_line = output_line.append(temp_line)
        else:
            # print('第{}线段为，下降线段'.format(i + 1))
            start = chan.d_t_seq[chan.d_t_seq['date_start'] == start_date]
            if len(start) == 0:
                start = chan.d_seq[chan.d_seq['date_start'] == start_date]
            end = chan.u_t_seq[chan.u_t_seq['date_start'] == end_date]
            if len(end) == 0:
                end = chan.u_seq[chan.u_seq['date_start'] == end_date]
            temp_line = pd.DataFrame({'number': i + 1, 'start_value': start['high'].values[0],
                                      'date_start': get_time(start['date_start']),
                                      'date_end': get_time(end['date_start'])},
                                     index=[0], columns=['number', 'start_value', 'date_start', 'date_end'])
            output_line = output_line.append(temp_line)
    return output_line