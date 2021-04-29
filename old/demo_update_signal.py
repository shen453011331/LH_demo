# coding=gbk
# import datetime
# from chinese_calendar import is_workday
# import time
# import os
# import pickle
# from utils_30min import *
from buy_sell_signal import *
from signal_processing_test import *
from summary import *
import pandas as pd
import shutil
from dateutil.relativedelta import relativedelta

# from jqdatasdk import *
# auth('18744019737', 'JUkuan133245')
# 对当前时间进行判断，若为休息日休眠1天
# 若为工作日，且当前hour为非开盘时间，休眠30分钟
# 若为工作日，且当前hour为开盘时间，运行程序，运行后休眠1h
import argparse
parser = argparse.ArgumentParser(description='Argument parser')
parser.add_argument('--end_time', dest='end_time', type=str, default='2020-07-20-20:00', help='# stock code')
parser.add_argument('--stock_list', dest='stock_list', type=str, default='C:\\Users\Administrator\Desktop\chanhuice\quant\chan_ts\data\hs300\hs_2009-06-30.csv', help='# stock code')
parser.add_argument('--python_head', dest='python_head', type=str, default='C:\\Users\Administrator\Desktop\chanhuice\quant\chan_ts', help='# stock code')

args = parser.parse_args()




if __name__ == '__main__':
    python_head = args.python_head
    end_time = datetime.datetime.strptime(args.end_time, '%Y-%m-%d-%H:%M')
    path_head = 'C:\\Users\Administrator\Desktop\chanhuice\quant\chan_ts\data\hs300'
    # name = ['2009-06-30', '2009-12-30', '2010-06-30', '2010-12-30',
    #         '2011-06-30', '2011-12-30', '2012-06-25', '2012-12-25',
    #         '2013-06-25', '2013-12-30', '2014-06-30', '2014-12-30',
    #         '2015-06-30']
    # filename = [os.path.join(path_head, 'hs_{}.csv'.format(i)) for i in name]
    # stocks = [pd.read_csv(i, index_col=0) for i in filename]
    # stock_tmp = stocks[1]
    # for i in range(2, 13):
    #     stock_tmp = stock_tmp.append(stocks[i])
    # stock_tmp.drop_duplicates(inplace=True)
    # stock_gt = stocks[0]
    # for i in range(len(stock_gt)):
    #     stock_tmp = stock_tmp[~stock_tmp['name'].isin([stock_gt.iloc[i]['name']])]
    stock_list = pd.read_csv(args.stock_list, index_col=0)
    # stock_list = stock_tmp

    len_data = 1e5
    for i, stock in enumerate(stock_list['name'].values.tolist()):
        print('{}信号开始更新'.format(stock[:-5]))

        b_restart = False
        name_head = os.path.join(python_head, 'data', stock[:-5])
        # for huice  get data every year in one files
        k_data_1min = os.path.join(name_head, stock[:-5] + '.csv')
        close_bar = pd.read_csv(k_data_1min, index_col=0, parse_dates=True)
        close_bar['date'] = pd.to_datetime(close_bar['date'])
        start_time = close_bar.head(1)['date'].values[0]
        start_time = pd.to_datetime(start_time)
        full_signal_file = pd.DataFrame(columns=['buy/sell', 'date', 'neighbor_up_down', 'm_H', 'm_L', 'n_H',
                                                 'n_L', 'm_H2', 'm_L2', 'n_H2', 'n_L2'])
        while end_time > (start_time + relativedelta(months=18)):
            next_start = start_time + relativedelta(years=1)
            current_end = next_start + relativedelta(months=6)
            full_signal_file = do_signal_processing(stock, name_head, close_bar, start_time, current_end, full_signal_file)
            start_time = next_start
            print('{}信号更新至{}'.format(stock[:-5], current_end.strftime('%Y-%m-%d')))
        full_signal_file = do_signal_processing(stock, name_head, close_bar, start_time, end_time, full_signal_file)
        data_name = os.path.join(name_head, 'summary_' + stock[:-5] + '.csv')
        full_signal_file.to_csv(data_name)
        print('{}信号更新完成'.format(stock[:-5]))
        #
        #
        #
        #
        # data_name = os.path.join(name_head, 'summary_' + stock[:-5] + '.csv')
        # chan_name = os.path.join(name_head, stock[:-5] + 'chan.pkl')
        # if os.path.exists(os.path.join(name_head, stock[:-5] + 'chan.pkl')):
        #     # shutil.copyfile(chan_name,
        #     #                 os.path.join(name_head, stock[:-5] + 'chan_bak.pkl'))
        #     with open(os.path.join(name_head, stock[:-5] + 'chan.pkl'), 'rb') as file:
        #         # print(os.path.join(name_head, stock[:-5] + 'chan.pkl'))
        #         chan = pickle.loads(file.read())
        #         last_end_date = pd.to_datetime(str(chan.x_seq.tail(1)['date'].values[0]))
        # else:
        #     chan = Chan()
        #     b_restart = True
        #
        # if os.path.exists(data_name):
        #     shutil.copyfile(data_name,
        #                     os.path.join(name_head, 'summary_' + stock[:-5] + '_bak.csv'))
        #     output_data = pd.read_csv(data_name, index_col=0, parse_dates=True)
        # else:
        #     output_data = pd.DataFrame(columns=['buy/sell', 'date', 'neighbor_up_down', 'm_H', 'm_L', 'n_H',
        #                                         'n_L', 'm_H2', 'm_L2', 'n_H2', 'n_L2'])
        #
        # k_data_1min = os.path.join(name_head, stock[:-5] + '.csv')
        # k_data_day = os.path.join(name_head, stock[:-5] + '_day' + '.csv')
        # close_bar = pd.read_csv(k_data_1min, index_col=0, parse_dates=True)
        # close_bar['date'] = pd.to_datetime(close_bar['date'])
        # # close_bar_1d = pd.read_csv(k_data_day, index_col=0, parse_dates=True)
        # close_bar_temp = close_bar[(close_bar['date'] < end_time) & (close_bar['date'] > last_end_date)] \
        #     if not b_restart else close_bar
        # signal_v1 = [False for i in range(6)]
        # buy_signal_1_v3, sell_signal_1_v3 = False, False
        # real_date = None
        # for i in range(len(close_bar_temp)):
        #     temp_x = close_bar_temp[i:i + 1].values[0]
        #     temp_df = pd.DataFrame({'high': temp_x[3], 'low': temp_x[2], 'date': temp_x[4]},
        #                            index=[0], columns=['high', 'low', 'date'])
        #     b_new_area_v3, b_new_line, b_new_area_v1, b_new_area_v2 = chan.update(temp_df)
        #
        #     chan.update_trend()
        #     trend_signal, real_date = signal_processing_trend(chan, close_bar)
        #     for j in range(len(trend_signal)):
        #         if trend_signal[j]:
        #             temp_data = pd.DataFrame(
        #                 {'level': 4 + j // 2 + 1, 'buy/sell': (j + 1) % 2, 'date': temp_x[4], 'neighbor_up_down': 0,
        #                  'n_H': 0, 'n_L': 0,
        #                  'n_H2': 0, 'n_L2': 0, 'real_date': real_date},
        #                 index=[0], columns=['level', 'buy/sell', 'date', 'neighbor_up_down',
        #                                     'm_H', 'm_L', 'n_H', 'n_L', 'm_H2', 'm_L2', 'n_H2', 'n_L2', 'real_date'])
        #             output_data = output_data.append(temp_data, sort=True)
        #             trend_signal[j] = False
        #     signal_v1, real_date = signal_processing_v1(chan, close_bar)
        #     output_data = output_v1(signal_v1[0], signal_v1[1],
        #                             signal_v1[2], signal_v1[3],
        #                             signal_v1[4], signal_v1[5],
        #                             buy_signal_1_v3, sell_signal_1_v3,
        #                             real_date, chan, temp_x, output_data)
        #     signal_v1 = [False for i in range(6)]
        #     signal_v1 = [False for i in range(6)]
        #     buy_signal_1, sell_signal_1 = False, False
        #     buy_signal_2, sell_signal_2 = False, False
        #     buy_signal_3, sell_signal_3 = False, False
        #     buy_signal_1_v3, sell_signal_1_v3 = False, False
        # output_data.to_csv(data_name)
        # output_hal = open(chan_name, 'wb')
        # str_chan = pickle.dumps(chan)
        # output_hal.write(str_chan)
        # output_hal.close()
        # print('{}信号更新完成'.format(stock[:-5]))
