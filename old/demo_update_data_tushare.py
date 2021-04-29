# coding=gbk
import datetime
from chinese_calendar import is_workday
import time
import os
import pandas as pd
import tushare as ts
ts.set_token('27c34453f1c35a3a12014ab30820d3c1a34b785afc89fb6ea94bcc80')
from dateutil.relativedelta import relativedelta

# auth('18744019737', 'JUkuan133245')

# 对当前时间进行判断，若为休息日休眠1天
# 若为工作日，且当前hour为非开盘时间，休眠30分钟
# 若为工作日，且当前hour为开盘时间，运行程序，运行后休眠1h
import argparse
parser = argparse.ArgumentParser(description='Argument parser')
parser.add_argument('--end_time', dest='end_time', type=str, default='2020-07-20-00:00', help='# stock code')
parser.add_argument('--stock_list', dest='stock_list', type=str, default='C:\\Users\Administrator\Desktop\chanhuice\quant\chan_ts\data\hs300\hs_2009-06-30.csv', help='# stock code')
parser.add_argument('--python_head', dest='python_head', type=str, default='C:\\Users\Administrator\Desktop\chanhuice\quant\chan_ts', help='# stock code')
parser.add_argument('--len_data', dest='len_data', type=int, default=100000, help='# stock code')
parser.add_argument('--b_update', dest='b_update', type=int, default=1, help='# to show the exit file need to be update or not,0 not need ,1 need')


args = parser.parse_args()


def get_data_1min(stock, start_time, end_time):
    # change data from tushare to joinquant format
    # tushare is for huice so time is daily time but obtain minute data
    if stock[0] == '6':
        new_stock = stock[:6] + '.SH'
    else:
        new_stock = stock[:6] + '.SZ'

    df = ts.pro_bar(ts_code=new_stock, adj='qfq',
                    start_date=start_time.strftime('%Y%m%d'),
                    end_date=end_time.strftime('%Y%m%d'),
                    freq='1min')
    if df is None:
        df = pd.DataFrame(columns=['ts_code', 'trade_time', 'open', 'close', 'high', 'low', 'vol', 'amount'])
    if len(df) != 0:
        df = df.sort_index(axis=0, ascending=False)
    df = df.rename(columns={"trade_time": "date"})
    df = df[['open', 'close', 'low', 'high', 'date']]
    df['date'] = pd.to_datetime(df['date'])
    df = df.reset_index(drop=True)
    return df


def get_data_1min_multi_month(stock, start_time, end_time):
    temp_time = start_time
    df_full = None
    while end_time > temp_time + relativedelta(months=1):

        temp_end = temp_time + relativedelta(months=1)
        df = get_data_1min(stock, temp_time, temp_end)
        if df_full is None:
            df_full = df
        elif len(df) == 0:
            break
        else:
            df_full = df_full.append(df)
        temp_time = temp_end
    df = get_data_1min(stock, temp_time, end_time)
    if len(df) == 0:
        return df_full
    if df_full is None:
        df_full = df
    else:
        df_full = df_full.append(df)
        df_full = df_full.reset_index(drop=True)
    return df_full


def get_data_1day(stock, start_time, end_time):
    # change data from tushare to joinquant format
    # tushare is for huice so time is daily time but obtain minute data
    if stock[0] == '6':
        new_stock = stock[:6] + '.SH'
    else:
        new_stock = stock[:6] + '.SZ'

    df = ts.pro_bar(ts_code=new_stock, adj='qfq',
                    start_date=start_time.strftime('%Y%m%d'),
                    end_date=end_time.strftime('%Y%m%d'))
    if df is None:
        df = pd.DataFrame(columns=['ts_code', 'trade_date', 'open', 'high', 'low', 'close', 'pre_close', 'change', 'pct_chg', 'vol', 'amount'])
    if len(df)!=0:
        df = df.sort_index(axis=0, ascending=False)
    df = df.rename(columns={"trade_date": "date"})
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date')
    df = df[['close']]
    return df


if __name__ == '__main__':
    python_head = args.python_head
    end_time = datetime.datetime.strptime(args.end_time, '%Y-%m-%d-%H:%M')
    stock_list = pd.read_csv(args.stock_list, index_col=0)
    # stock_list = stock_list.iloc[5:]
    len_data = args.len_data
    for i, stock in enumerate(stock_list['name'].values.tolist()):
        name_head = os.path.join(python_head, 'data', stock[:-5])
        if not os.path.exists(name_head):
            os.mkdir(name_head)
        k_data_1min = os.path.join(name_head, stock[:-5] + '.csv')
        k_data_day = os.path.join(name_head, stock[:-5] + '_day' + '.csv')
        if not os.path.exists(k_data_1min):
            last_end_time = end_time - relativedelta(months=6)
            temp_bar = get_data_1min_multi_month(stock, last_end_time, end_time)
            # temp_bar = get_bars(stock, len_data,
            #                     end_dt=end_time.strftime('%Y-%m-%d %H:%M:%S'),
            #                     unit='1m', fields=['open', 'close', 'low', 'high', 'date'])
            if len(temp_bar) != 0:
                temp_bar.to_csv(k_data_1min)
                start_time = pd.to_datetime(temp_bar.head(1)['date'].values[0])
                end_time = pd.to_datetime(temp_bar.tail(1)['date'].values[0])
                # close_bar_1d = get_price(stock, start_date=start_time.strftime('%Y-%m-%d'),
                #                          end_date=end_time.strftime('%Y-%m-%d'), frequency='daily', fields=['close'],
                #                          skip_paused=False, fq=None)
                close_bar_1d = get_data_1day(stock, last_end_time, end_time)
                close_bar_1d.to_csv(k_data_day)
            else:
                print('NO. {} download error'.format(i))
        else:
            if args.b_update:
                close_bar = pd.read_csv(k_data_1min, index_col=0, parse_dates=True)
                if len(close_bar) == 0:
                    os.remove(k_data_1min)
                    os.remove(k_data_day)
                    break
                close_bar['date'] = pd.to_datetime(close_bar['date'])
                last_end_time = pd.to_datetime(close_bar.tail(1)['date'].values[0])
                # count = get_query_count()
                # if count['spare'] < 10000:
                #     print('更新{}条数不足10000，明天继续'.format(stock[:-5]))
                #     break
                temp_bar = get_data_1min_multi_month(stock, last_end_time, end_time)
                # temp_bar = get_price(stock, start_date=last_end_time.strftime('%Y-%m-%d %H:%M:%S'),
                #                      end_date=end_time.strftime('%Y-%m-%d %H:%M:%S'), frequency='1m',
                #                      fields=['open', 'close', 'low', 'high'],
                #                      skip_paused=False, fq=None)
                # temp_bar['date'] = temp_bar.index
                close_bar = close_bar.append(temp_bar)
                close_bar.drop_duplicates(keep='first', inplace=True)
                close_bar.reset_index(drop=True)
                close_bar.to_csv(k_data_1min)
                close_bar_1d = pd.read_csv(k_data_day, index_col=0, parse_dates=True)
                close_bar_1d = close_bar_1d[['close']]
                temp_bar_1d = get_data_1day(stock, last_end_time, end_time)

                # temp_bar_1d = get_price(stock, start_date=last_end_time.strftime('%Y-%m-%d'),
                #                         end_date=end_time.strftime('%Y-%m-%d'), frequency='daily', fields=['close'],
                #                         skip_paused=False, fq=None)[close_bar_1d.tail(1).index.values[0]:]
                close_bar_1d = close_bar_1d.append(temp_bar_1d)
                close_bar_1d.reset_index(drop=True)
                close_bar_1d.to_csv(k_data_day)
        print('{}更新完成'.format(stock[:-5]))
