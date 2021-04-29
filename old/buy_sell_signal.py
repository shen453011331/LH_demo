import numpy as np
import pandas as pd
import datetime
import talib as ta


def process_time(time):
    return pd.to_datetime(str(time))


def get_sum_macd_err(start, end, close_bar, b_zero):
    # b_zero = 1 找负err，=-1 找正err
    # start and end must be datetime class
    MACD_value = [13, 26, 9]
    start_time_1d = start - datetime.timedelta(days=20)
    end_time_1d = end
    temp = close_bar[(close_bar['date'] > start_time_1d) & (close_bar['date'] < end_time_1d)].copy()
    temp['date'] = pd.to_datetime(temp['date'])
    temp.set_index("date", inplace=True)
    close = temp['close']
    # close = close_bar[start_time_1d.strftime('%Y-%m-%d'):end_time_1d.strftime('%Y-%m-%d')]['close']
    macd, signal_macd, hist = ta.MACD(close, fastperiod=MACD_value[0], slowperiod=MACD_value[1],
                                      signalperiod=MACD_value[2])
    err = macd - signal_macd
    cross = np.array(err[start.strftime('%Y-%m-%d %H:%M'):].values)
    if b_zero:
        return np.abs(np.sum(cross[cross > 0]))
    else:
        return np.abs(np.sum(cross[cross < 0]))


def signal_processing_v1(chan, close_bar):
    buy_signal_1, sell_signal_1 = False, False
    buy_signal_2, sell_signal_2 = False, False
    buy_signal_3, sell_signal_3 = False, False
    real_date = None
    # 1类买卖点
    if chan.b_new_area and len(chan.c_seq_v1) > 3 and len(chan.c_seq_v3) > 1:
        buy_signal_1, sell_signal_1, real_date = get_signal_1_v1(close_bar, chan)

    # 新二类买卖点
    if chan.b_new_area and len(chan.c_seq_v1) > 1 and len(chan.c_seq_v3) > 1:
        # print('二类买卖点判断')
        buy_signal_2, sell_signal_2, real_date = get_signal_2_v1(close_bar, chan)
        if buy_signal_2 or sell_signal_2:
            print('2class real_date:{}'.format(real_date))

    # 新3类买卖点
    if chan.b_new_line and len(chan.c_seq_v1) > 0:
        buy_signal_3, sell_signal_3, real_date = get_signal_3_v1(close_bar, chan)
    return [buy_signal_1, sell_signal_1, buy_signal_2, sell_signal_2, buy_signal_3, sell_signal_3], real_date


def signal_processing_trend(chan, close_bar):
    buy_signal_1, sell_signal_1 = False, False
    buy_signal_2, sell_signal_2 = False, False
    buy_signal_3, sell_signal_3 = False, False
    real_date = None
    # 1类买卖点
    if chan.b_new_trend_area and len(chan.c_trend_seq) > 3:
        buy_signal_1, sell_signal_1, real_date = get_signal_1_v1(close_bar, chan, 3) # 3 means using trend

    # 新二类买卖点
    if chan.b_new_trend_area and len(chan.c_trend_seq) > 1:
        # print('二类买卖点判断')
        buy_signal_2, sell_signal_2, real_date = get_signal_2_v1(close_bar, chan, 3)
        # if buy_signal_2 or sell_signal_2:
        #     print('2class real_date:{}'.format(real_date))

    # 新3类买卖点
    if chan.b_new_trend_line and len(chan.c_trend_seq) > 0:
        buy_signal_3, sell_signal_3, real_date = get_signal_3_v1(close_bar, chan, 3)
    return [buy_signal_1, sell_signal_1, buy_signal_2, sell_signal_2, buy_signal_3, sell_signal_3], real_date



def get_signal_1_v3(close_bar, close_bar_30m, chan, temp_chan, bar_mn, temp_x):
    buy_signal_1_v3, sell_signal_1_v3 = False, False
    real_date = None
    A_start, A_end = bar_mn['date_end'].values[0], bar_mn['date_start'].values[1]
    C_start, C_end = bar_mn['date_end'].values[1], None
    A_start, A_end = process_time(A_start), process_time(A_end)
    close_bar_30m = close_bar_30m[close_bar_30m['date'] >= C_start]
    C_start = process_time(C_start)
    num_m, num_n = chan.get_line_num(chan.c_seq_v3.iloc[-2:-1]), chan.get_line_num(chan.c_seq_v3.tail(1))
    if bar_mn['high2'].values[1] < bar_mn['low2'].values[0] and num_m < 24 and num_n < 24:
        assert len(close_bar_30m) > 40
        for j in range(len(close_bar_30m)):
            temp_x_30m = close_bar_30m[j:j + 1].values[0]
            temp_df_30m = pd.DataFrame({'high': temp_x_30m[3], 'low': temp_x_30m[2],
                                        'date': temp_x_30m[4]},
                                       index=[0], columns=['high', 'low', 'date'])
            temp_chan.get_first_line(temp_df_30m)
            if len(temp_chan.l_seq) > 1:
                b_last_up_down = temp_chan.get_l_direction(temp_chan.l_seq[0])
                if b_last_up_down:
                    C_end = temp_chan.l_seq[0]
                    break
                else:
                    if len(temp_chan.l_seq) > 2:
                        C_end = temp_chan.l_seq[1]
                        break
        if C_end is not None:
            C_end = process_time(C_end)
            # print('找到c段终点{}'.format(C_end.strftime('%Y-%m-%d')))
        else:
            # print('到目前没有线段出现,设为当前时间')
            C_end = temp_x[4]
        real_date = C_start.date()
        sum_a = get_sum_macd_err(A_start, A_end, close_bar, -1)
        sum_c = get_sum_macd_err(C_start, C_end, close_bar, -1)
        if sum_a > sum_c:
            buy_signal_1_v3 = True
            print('v3:buy_signal_1, current time is {}'.format(temp_x[4].date()))
    elif bar_mn['high2'].values[0] < bar_mn['low2'].values[1] and num_m < 81 and num_n < 81:
        for j in range(len(close_bar_30m)):
            temp_x_30m = close_bar_30m[j:j + 1].values[0]
            temp_df_30m = pd.DataFrame({'high': temp_x_30m[3], 'low': temp_x_30m[2], 'date': temp_x_30m[4]},
                                       index=[0], columns=['high', 'low', 'date'])
            temp_chan.get_first_line(temp_df_30m)
            if len(temp_chan.l_seq) > 1:
                b_last_up_down = temp_chan.get_l_direction(temp_chan.l_seq[0])
                if not b_last_up_down:
                    C_end = temp_chan.l_seq[0]
                    break
                else:
                    if len(temp_chan.l_seq) > 2:
                        C_end = temp_chan.l_seq[1]
                        break
        if C_end is not None:
            C_end = process_time(C_end)
            # print('找到c段终点{}'.format(C_end.strftime('%Y-%m-%d')))
        else:
            # print('到目前没有线段出现,设为当前时间')
            C_end = temp_x[4]
        real_date = C_start.date()
        sum_a = get_sum_macd_err(A_start, A_end, close_bar, 1)
        sum_c = get_sum_macd_err(C_start, C_end, close_bar, 1)
        # print('suma:{},sumc:{}'.format(sum_a, sum_c))
        if sum_a > sum_c:
            sell_signal_1_v3 = True
            print('v3:sell_signal_1, current time is {}'.format(temp_x[4].date()))
    return buy_signal_1_v3, sell_signal_1_v3, None


def get_signal_1_v1(close_bar, chan, level=1):
    buy_signal_1, sell_signal_1 = False, False
    bar_mn = chan.c_seq_v1.iloc[-4:-1] if level == 1 else chan.c_trend_seq.iloc[-4:-1]
    A_start, A_end = bar_mn['date_end'].values[0], bar_mn['date_start'].values[1]
    C_start, C_end = bar_mn['date_end'].values[1], bar_mn['date_start'].values[2]
    A_start, A_end = process_time(A_start), process_time(A_end)
    C_start, C_end = process_time(C_start), process_time(C_end)
    real_date = C_start.date()
    if bar_mn['high2'].values[1] < bar_mn['low2'].values[0] \
            and bar_mn['high'].values[1] > bar_mn['high'].values[2] \
            and bar_mn['low'].values[1] > bar_mn['low'].values[2]:
        sum_a = get_sum_macd_err(A_start, A_end, close_bar, -1)
        sum_c = get_sum_macd_err(C_start, C_end, close_bar, -1)
        if sum_a > sum_c:
            buy_signal_1 = True
            # print('buy_signal_1, current time is {}'.format(temp_x[4].date()))
    elif bar_mn['high2'].values[0] < bar_mn['low2'].values[1] \
            and bar_mn['high'].values[1] < bar_mn['high'].values[2] \
            and bar_mn['low'].values[1] < bar_mn['low'].values[2]:
        sum_a = get_sum_macd_err(A_start, A_end, close_bar, 1)
        sum_c = get_sum_macd_err(C_start, C_end, close_bar, 1)
        # print('suma:{},sumc:{}'.format(sum_a, sum_c))
        if sum_a > sum_c:
            sell_signal_1 = True
    return buy_signal_1, sell_signal_1, real_date


def get_signal_2_v1(close_bar, chan, level=1):
    buy_signal_2, sell_signal_2 = False, False
    real_date = None
    bar_mn = chan.c_seq_v1.tail(2) if level == 1 else chan.c_trend_seq.tail(2)
    if bar_mn['high2'].values[1] < bar_mn['low2'].values[0]:
        if level == 1:
            end_num = chan.l_seq.index(chan.c_seq_v1.tail(1)['date_end'].values[0])
            b_last_up_down = chan.get_l_direction(chan.l_seq[end_num - 1])
            if b_last_up_down:
                A_start, A_end = chan.l_seq[end_num - 4], chan.l_seq[end_num - 3]
                C_start, C_end = chan.l_seq[end_num - 2], chan.l_seq[end_num - 1]
            else:
                A_start, A_end = chan.l_seq[end_num - 3], chan.l_seq[end_num - 2]
                C_start, C_end = chan.l_seq[end_num - 1], chan.l_seq[end_num]
        else:
            temp_l_seq = chan.l_trend_seq[chan.l_trend_seq['date_end']
                                              <=chan.c_trend_seq.tail(1)['date_end'].values[0]]
            b_last_up_down = temp_l_seq.tail(1)['ud'].values[0]
            if b_last_up_down:
                line_s, line_e = temp_l_seq.iloc[-4:-3].values[0], temp_l_seq.iloc[-2:-1].values[0]
            else:
                line_s, line_e = temp_l_seq.iloc[-2:-1].values[0], temp_l_seq.iloc[-1:].values[0]
            A_start, A_end = line_s[2], line_s[3]
            C_start, C_end = line_e[2], line_e[3]

        A_start, A_end = process_time(A_start), process_time(A_end)
        C_start, C_end = process_time(C_start), process_time(C_end)
        # print('AC时间端,A:{}-{},C:{}-{}'.format(A_start, A_end, C_start, C_end))
        sum_a = get_sum_macd_err(A_start, A_end, close_bar, -1)
        sum_c = get_sum_macd_err(C_start, C_end, close_bar, -1)
        if sum_a > sum_c:
            # print('2类买点')
            buy_signal_2 = True
            real_date = C_start.date()
    elif bar_mn['low2'].values[1] > bar_mn['high2'].values[0]:
        if level == 1:
            end_num = chan.l_seq.index(chan.c_seq_v1.tail(1)['date_end'].values[0])
            b_last_up_down = chan.get_l_direction(chan.l_seq[end_num - 1])
            if not b_last_up_down:
                A_start, A_end = chan.l_seq[end_num - 4], chan.l_seq[end_num - 3]
                C_start, C_end = chan.l_seq[end_num - 2], chan.l_seq[end_num - 1]
            else:
                A_start, A_end = chan.l_seq[end_num - 3], chan.l_seq[end_num - 2]
                C_start, C_end = chan.l_seq[end_num - 1], chan.l_seq[end_num]
        else:
            temp_l_seq = chan.l_trend_seq[chan.l_trend_seq['date_end']
                                          <= chan.c_trend_seq.tail(1)['date_end'].values[0]]
            b_last_up_down = temp_l_seq.tail(1)['ud'].values[0]
            if not b_last_up_down:
                line_s, line_e = temp_l_seq.iloc[-4:-3].values[0], temp_l_seq.iloc[-2:-1].values[0]
            else:
                line_s, line_e = temp_l_seq.iloc[-2:-1].values[0], temp_l_seq.iloc[-1:].values[0]
            A_start, A_end = line_s[2], line_s[3]
            C_start, C_end = line_e[2], line_e[3]
        A_start, A_end = process_time(A_start), process_time(A_end)
        C_start, C_end = process_time(C_start), process_time(C_end)
        # print('AC时间端,A:{}-{},C:{}-{}'.format(A_start, A_end, C_start, C_end))
        sum_a = get_sum_macd_err(A_start, A_end, close_bar, 1)
        sum_c = get_sum_macd_err(C_start, C_end, close_bar, 1)
        if sum_a > sum_c:
            # print('2类卖点')
            sell_signal_2 = True
            real_date = C_start.date()
    return buy_signal_2, sell_signal_2, real_date


def get_signal_3_v1(close_bar, chan, level=1):
    buy_signal_3, sell_signal_3 = False, False
    real_date = None
    if level == 1:
        end_num = chan.l_seq.index(chan.c_seq_v1.tail(1)['date_end'].values[0])
        if len(chan.l_seq) > end_num + 3:
            target_num = end_num + 1
            b_last_up_down = chan.get_l_direction(chan.l_seq[target_num])
            if not b_last_up_down:
                end_date = chan.l_seq[target_num + 1]
                end = chan.u_t_seq[chan.u_t_seq['date_start'] == end_date]
                if len(end) == 0:
                    end = chan.u_seq[chan.u_seq['date_start'] == end_date]
                if end['low'].values[0] > chan.c_seq_v1.tail(1)['high2'].values[0]:
                    A_start, A_end = chan.l_seq[target_num - 1], chan.l_seq[target_num]
                    C_start, C_end = chan.l_seq[target_num + 1], chan.l_seq[target_num + 2]
                    A_start, A_end = process_time(A_start), process_time(A_end)
                    C_start, C_end = process_time(C_start), process_time(C_end)
                    sum_a = get_sum_macd_err(A_start, A_end, close_bar, -1)
                    sum_c = get_sum_macd_err(C_start, C_end, close_bar, -1)
                    if sum_a > sum_c:
                        buy_signal_3 = True
                        real_date = C_start.date()
            else:
                end_date = chan.l_seq[target_num + 1]
                end = chan.d_t_seq[chan.d_t_seq['date_start'] == end_date]
                if len(end) == 0:
                    end = chan.d_seq[chan.d_seq['date_start'] == end_date]
                if end['high'].values[0] < chan.c_seq_v1.tail(1)['low2'].values[0]:
                    A_start, A_end = chan.l_seq[target_num - 1], chan.l_seq[target_num]
                    C_start, C_end = chan.l_seq[target_num + 1], chan.l_seq[target_num + 2]
                    A_start, A_end = process_time(A_start), process_time(A_end)
                    C_start, C_end = process_time(C_start), process_time(C_end)
                    sum_a = get_sum_macd_err(A_start, A_end, close_bar, 1)
                    sum_c = get_sum_macd_err(C_start, C_end, close_bar, 1)
                    if sum_a > sum_c:
                        sell_signal_3 = True
                        real_date = C_start.date()
    else:
        temp_l_seq = chan.l_trend_seq[chan.l_trend_seq['date_end']
                                      > chan.c_trend_seq.tail(1)['date_end'].values[0]]
        if len(temp_l_seq) > 3:
            b_last_up_down = temp_l_seq.iloc[1:2]['ud'].values[0]
            line_s, line_e = temp_l_seq.iloc[0:1].values[0], temp_l_seq.iloc[2:3].values[0]
            A_start, A_end = line_s[2], line_s[3]
            C_start, C_end = line_e[2], line_e[3]
            A_start, A_end = process_time(A_start), process_time(A_end)
            C_start, C_end = process_time(C_start), process_time(C_end)
            if not b_last_up_down:
                if temp_l_seq.iloc[1:2]['low'].values[0] > chan.c_trend_seq.tail(1)['high2'].values[0]:
                    sum_a = get_sum_macd_err(A_start, A_end, close_bar, -1)
                    sum_c = get_sum_macd_err(C_start, C_end, close_bar, -1)
                    if sum_a > sum_c:
                        buy_signal_3 = True
                        real_date = C_start.date()
            else:
                if temp_l_seq.iloc[1:2]['high'].values[0] < chan.c_trend_seq.tail(1)['low2'].values[0]:
                    sum_a = get_sum_macd_err(A_start, A_end, close_bar, 1)
                    sum_c = get_sum_macd_err(C_start, C_end, close_bar, 1)
                    if sum_a > sum_c:
                        sell_signal_3 = True
                        real_date = C_start.date()
    return buy_signal_3, sell_signal_3, real_date

#
# def get_signal_2_v3():
#     # 二类买卖点
#     if b_new_area_v2:
#         b_area_v2_ok_2 = True
#     if not b_new_area_v3 and len(chan.c_seq_v3) > 2 and not b_second and b_new_line and b_area_v2_ok_2:
#         # print('二类买卖点查询')
#         if bar_mn['high2'].values[1] < bar_mn['low2'].values[0] and num_m < 24 and num_n < 24:
#             # print('二类买点')
#             assert len(chan.l_seq) > 5
#             b_last_up_down = chan.get_l_direction(chan.l_seq[-3])
#             if not b_last_up_down:  # 线段背驰
#                 a_start_line, a_end_line = chan.l_seq[-5], chan.l_seq[-4]
#                 c_start_line, c_end_line = chan.l_seq[-3], chan.l_seq[-2]
#                 a_start_line, a_end_line = process_time(a_start_line), process_time(a_end_line)
#                 c_start_line, c_end_line = process_time(c_start_line), process_time(c_end_line)
#                 sum_a = get_sum_macd_err(a_start_line, a_end_line, jq_symbol, -1)
#                 sum_c = get_sum_macd_err(c_start_line, c_end_line, jq_symbol, -1)
#                 if sum_a > sum_c:
#                     print('买:线段背驰line:suma:{},sumc:{}'.format(sum_a, sum_c))
#                     # assert len(chan.c_seq_v1) > 2
#                     # bar_mn_v1 = chan.c_seq_v1.tail(2)
#                     # if bar_mn_v1['high2'].values[1] < bar_mn_v1['high2'].values[0] and \
#                     #         bar_mn_v1['low2'].values[1] < bar_mn_v1['low2'].values[0]:
#                     #     A_start_v1, A_end_v1 = bar_mn_v1['date_end'].values[0], bar_mn_v1['date_start'].values[1]
#                     #     C_start_v1, C_end_v1 = bar_mn_v1['date_end'].values[1], chan.l_seq[-2]
#                     #     if chan.x_seq[chan.x_seq['date'] == C_start_v1]['low'].values[0] > \
#                     #             chan.x_seq[chan.x_seq['date'] == C_end_v1]['high'].values[0]:
#                     #         A_start_v1, A_end_v1 = process_time(A_start_v1), process_time(A_end_v1)
#                     #         C_start_v1, C_end_v1 = process_time(C_start_v1), process_time(C_end_v1)
#                     #         sum_a = get_sum_macd_err(A_start_v1, A_end_v1, jq_symbol, -1)
#                     #         sum_c = get_sum_macd_err(C_start_v1, C_end_v1, jq_symbol, -1)
#                     #         if sum_a > sum_c:
#                     #             print('中枢1级背驰areav1:suma:{},sumc:{}'.format(sum_a, sum_c))
#                     assert len(chan.c_seq_v2) > 2
#                     bar_mn_v2 = chan.c_seq_v2.tail(2)
#                     if bar_mn_v2['high2'].values[1] < bar_mn_v2['high2'].values[0] and \
#                             bar_mn_v2['low2'].values[1] < bar_mn_v2['low2'].values[0]:
#                         A_start_v2, A_end_v2 = bar_mn_v2['date_end'].values[0], \
#                                                bar_mn_v2['date_start'].values[1]
#                         C_start_v2, C_end_v2 = bar_mn_v2['date_end'].values[1], chan.l_seq[-2]
#                         if chan.x_seq[chan.x_seq['date'] == C_start_v2]['low'].values[0] > \
#                                 chan.x_seq[chan.x_seq['date'] == C_end_v2]['high'].values[0]:
#                             A_start_v2, A_end_v2 = process_time(A_start_v2), process_time(A_end_v2)
#                             C_start_v2, C_end_v2 = process_time(C_start_v2), process_time(C_end_v2)
#                             sum_a = get_sum_macd_err(A_start_v2, A_end_v2, jq_symbol, -1)
#                             sum_c = get_sum_macd_err(C_start_v2, C_end_v2, jq_symbol, -1)
#                             print('areav2:suma:{},sumc:{}'.format(sum_a, sum_c))
#                             if sum_a > sum_c and temp_x[1] > bar_mn['low'].values[1]:
#                                 b_second = True
#                                 buy_signal_2 = True
#                                 print('buy_signal_2, current time is {}'.format(temp_x[4].date()))
#                             else:
#                                 b_area_v2_ok_2 = False
#         elif bar_mn['high2'].values[0] < bar_mn['low2'].values[1] and num_m < 24 and num_n < 24:
#             # print('二类卖点')
#             assert len(chan.l_seq) > 5
#             b_last_up_down = chan.get_l_direction(chan.l_seq[-3])
#             if b_last_up_down:
#                 a_start_line, a_end_line = chan.l_seq[-5], chan.l_seq[-4]
#                 c_start_line, c_end_line = chan.l_seq[-3], chan.l_seq[-2]
#                 a_start_line, a_end_line = process_time(a_start_line), process_time(a_end_line)
#                 c_start_line, c_end_line = process_time(c_start_line), process_time(c_end_line)
#                 sum_a = get_sum_macd_err(a_start_line, a_end_line, jq_symbol, 1)
#                 sum_c = get_sum_macd_err(c_start_line, c_end_line, jq_symbol, 1)
#                 if sum_a > sum_c:
#                     print('卖:线段背驰suma:{},sumc:{}'.format(sum_a, sum_c))
#                     # assert len(chan.c_seq_v1) > 2
#                     # bar_mn_v1 = chan.c_seq_v1.tail(2)
#                     # if bar_mn_v1['high2'].values[1] > bar_mn_v1['high2'].values[0] and \
#                     #         bar_mn_v1['low2'].values[1] > bar_mn_v1['low2'].values[0]:
#                     #     A_start_v1, A_end_v1 = bar_mn_v1['date_end'].values[0], bar_mn_v1['date_start'].values[1]
#                     #     C_start_v1, C_end_v1 = bar_mn_v1['date_end'].values[1], chan.l_seq[-2]
#                     #     if chan.x_seq[chan.x_seq['date'] == C_start_v1]['high'].values[0] < \
#                     #             chan.x_seq[chan.x_seq['date'] == C_end_v1]['low'].values[0]:
#                     #         A_start_v1, A_end_v1 = process_time(A_start_v1), process_time(A_end_v1)
#                     #         C_start_v1, C_end_v1 = process_time(C_start_v1), process_time(C_end_v1)
#                     #         sum_a = get_sum_macd_err(A_start_v1, A_end_v1, jq_symbol, 1)
#                     #         sum_c = get_sum_macd_err(C_start_v1, C_end_v1, jq_symbol, 1)
#                     #         if sum_a > sum_c:
#                     #             print('中枢1级背驰areav1:suma:{},sumc:{}'.format(sum_a, sum_c))
#                     assert len(chan.c_seq_v2) > 2
#                     bar_mn_v2 = chan.c_seq_v2.tail(2)
#                     if bar_mn_v2['high2'].values[1] > bar_mn_v2['high2'].values[0] and \
#                             bar_mn_v2['low2'].values[1] > bar_mn_v2['low2'].values[0]:
#                         A_start_v2, A_end_v2 = bar_mn_v2['date_end'].values[0], \
#                                                bar_mn_v2['date_start'].values[1]
#                         C_start_v2, C_end_v2 = bar_mn_v2['date_end'].values[1], chan.l_seq[-2]
#                         if chan.x_seq[chan.x_seq['date'] == C_start_v2]['high'].values[0] < \
#                                 chan.x_seq[chan.x_seq['date'] == C_end_v2]['low'].values[0]:
#                             A_start_v2, A_end_v2 = process_time(A_start_v2), process_time(A_end_v2)
#                             C_start_v2, C_end_v2 = process_time(C_start_v2), process_time(C_end_v2)
#                             sum_a = get_sum_macd_err(A_start_v2, A_end_v2, jq_symbol, 1)
#                             sum_c = get_sum_macd_err(C_start_v2, C_end_v2, jq_symbol, 1)
#                             print('areav2:suma:{},sumc:{}'.format(sum_a, sum_c))
#                             if sum_a > sum_c and temp_x[1] > bar_mn['high'].values[1]:
#                                 b_second = True
#                                 sell_signal_2 = True
#                                 print('sell_signal_2, current time is {}'.format(temp_x[4].date()))
#                             else:
#                                 b_area_v2_ok_2 = False
#
#
# def get_signal_3_v3():
#     # 寻找3类信号
#     if b_new_area_v1:
#         b_area_v1_ok_3_buy, b_area_v1_ok_3_sell = True, True
#     if b_new_area_v2:
#         b_area_v2_ok_3_buy, b_area_v2_ok_3_sell = True, True
#     if len(chan.c_seq_v3) > 0 and b_new_line:
#         if b_new_area_v3:
#             b_third_sell, b_third_buy = False, False
#         assert len(chan.l_seq) > 5
#         b_last_up_down = chan.get_l_direction(chan.l_seq[-3])
#         if not b_last_up_down and not b_third_buy and b_area_v1_ok_3_buy and b_area_v2_ok_3_buy:  # 线段背驰
#             a_start_line, a_end_line = chan.l_seq[-5], chan.l_seq[-4]
#             c_start_line, c_end_line = chan.l_seq[-3], chan.l_seq[-2]
#             a_start_line, a_end_line = process_time(a_start_line), process_time(a_end_line)
#             c_start_line, c_end_line = process_time(c_start_line), process_time(c_end_line)
#             sum_a = get_sum_macd_err(a_start_line, a_end_line, jq_symbol, -1)
#             sum_c = get_sum_macd_err(c_start_line, c_end_line, jq_symbol, -1)
#             if sum_a > sum_c:
#                 print('买：3级线段背驰line:suma:{},sumc:{}'.format(sum_a, sum_c))
#                 assert len(chan.c_seq_v1) > 2
#                 bar_mn_v1 = chan.c_seq_v1.tail(2)
#                 if bar_mn_v1['high2'].values[1] < bar_mn_v1['high2'].values[0] and \
#                         bar_mn_v1['low2'].values[1] < bar_mn_v1['low2'].values[0]:
#                     A_start_v1, A_end_v1 = bar_mn_v1['date_end'].values[0], bar_mn_v1['date_start'].values[1]
#                     C_start_v1, C_end_v1 = bar_mn_v1['date_end'].values[1], chan.l_seq[-2]
#                     if chan.x_seq[chan.x_seq['date'] == C_start_v1]['low'].values[0] > \
#                             chan.x_seq[chan.x_seq['date'] == C_end_v1]['high'].values[0]:
#                         A_start_v1, A_end_v1 = process_time(A_start_v1), process_time(A_end_v1)
#                         C_start_v1, C_end_v1 = process_time(C_start_v1), process_time(C_end_v1)
#                         sum_a = get_sum_macd_err(A_start_v1, A_end_v1, jq_symbol, -1)
#                         sum_c = get_sum_macd_err(C_start_v1, C_end_v1, jq_symbol, -1)
#                         if sum_a > sum_c:
#                             print('中枢1级背驰areav1:suma:{},sumc:{}'.format(sum_a, sum_c))
#                             if len(chan.c_seq_v2) > 2:
#                                 bar_mn_v2 = chan.c_seq_v2.tail(2)
#                                 if bar_mn_v2['high2'].values[1] < bar_mn_v2['high2'].values[0] and \
#                                         bar_mn_v2['low2'].values[1] < bar_mn_v2['low2'].values[0]:
#                                     A_start_v2, A_end_v2 = bar_mn_v2['date_end'].values[0], \
#                                                            bar_mn_v2['date_start'].values[1]
#                                     C_start_v2, C_end_v2 = bar_mn_v2['date_end'].values[1], chan.l_seq[-2]
#                                     if chan.x_seq[chan.x_seq['date'] == C_start_v2]['low'].values[0] > \
#                                             chan.x_seq[chan.x_seq['date'] == C_end_v2]['high'].values[0]:
#                                         A_start_v2, A_end_v2 = process_time(A_start_v2), process_time(A_end_v2)
#                                         C_start_v2, C_end_v2 = process_time(C_start_v2), process_time(C_end_v2)
#                                         sum_a = get_sum_macd_err(A_start_v2, A_end_v2, jq_symbol, -1)
#                                         sum_c = get_sum_macd_err(C_start_v2, C_end_v2, jq_symbol, -1)
#                                         print('areav2:suma:{},sumc:{}'.format(sum_a, sum_c))
#                                         if sum_a > sum_c and temp_x[1] > bar_mn['high'].values[1]:
#                                             b_third_buy = True
#                                             buy_signal_3 = True
#                                             print('buy_signal_3, current time is {}'.format(temp_x[4].date()))
#                                         else:
#                                             b_area_v2_ok_3_buy = False
#                         else:
#                             b_area_v1_ok_3_buy = False
#
#         elif b_last_up_down and not b_third_sell and b_area_v1_ok_3_sell and b_area_v2_ok_3_sell:
#             a_start_line, a_end_line = chan.l_seq[-5], chan.l_seq[-4]
#             c_start_line, c_end_line = chan.l_seq[-3], chan.l_seq[-2]
#             a_start_line, a_end_line = process_time(a_start_line), process_time(a_end_line)
#             c_start_line, c_end_line = process_time(c_start_line), process_time(c_end_line)
#             sum_a = get_sum_macd_err(a_start_line, a_end_line, jq_symbol, 1)
#             sum_c = get_sum_macd_err(c_start_line, c_end_line, jq_symbol, 1)
#             if sum_a > sum_c:
#                 print('卖：3级线段背驰suma:{},sumc:{}'.format(sum_a, sum_c))
#                 assert len(chan.c_seq_v1) > 2
#                 bar_mn_v1 = chan.c_seq_v1.tail(2)
#                 if bar_mn_v1['high2'].values[1] > bar_mn_v1['high2'].values[0] and \
#                         bar_mn_v1['low2'].values[1] > bar_mn_v1['low2'].values[0]:
#                     A_start_v1, A_end_v1 = bar_mn_v1['date_end'].values[0], bar_mn_v1['date_start'].values[1]
#                     C_start_v1, C_end_v1 = bar_mn_v1['date_end'].values[1], chan.l_seq[-2]
#                     if chan.x_seq[chan.x_seq['date'] == C_start_v1]['high'].values[0] < \
#                             chan.x_seq[chan.x_seq['date'] == C_end_v1]['low'].values[0]:
#                         A_start_v1, A_end_v1 = process_time(A_start_v1), process_time(A_end_v1)
#                         C_start_v1, C_end_v1 = process_time(C_start_v1), process_time(C_end_v1)
#                         sum_a = get_sum_macd_err(A_start_v1, A_end_v1, jq_symbol, 1)
#                         sum_c = get_sum_macd_err(C_start_v1, C_end_v1, jq_symbol, 1)
#                         if sum_a > sum_c:
#                             print('中枢1级背驰areav1:suma:{},sumc:{}'.format(sum_a, sum_c))
#                             if len(chan.c_seq_v2) > 2:
#                                 bar_mn_v2 = chan.c_seq_v2.tail(2)
#                                 if bar_mn_v2['high2'].values[1] > bar_mn_v2['high2'].values[0] and \
#                                         bar_mn_v2['low2'].values[1] > bar_mn_v2['low2'].values[0]:
#                                     A_start_v2, A_end_v2 = bar_mn_v2['date_end'].values[0], \
#                                                            bar_mn_v2['date_start'].values[1]
#                                     C_start_v2, C_end_v2 = bar_mn_v2['date_end'].values[1], chan.l_seq[-2]
#                                     if chan.x_seq[chan.x_seq['date'] == C_start_v2]['high'].values[0] < \
#                                             chan.x_seq[chan.x_seq['date'] == C_end_v2]['low'].values[0]:
#                                         A_start_v2, A_end_v2 = process_time(A_start_v2), process_time(A_end_v2)
#                                         C_start_v2, C_end_v2 = process_time(C_start_v2), process_time(C_end_v2)
#                                         sum_a = get_sum_macd_err(A_start_v2, A_end_v2, jq_symbol, 1)
#                                         sum_c = get_sum_macd_err(C_start_v2, C_end_v2, jq_symbol, 1)
#                                         print('areav2:suma:{},sumc:{}'.format(sum_a, sum_c))
#                                         if sum_a > sum_c and temp_x[1] < bar_mn['low'].values[1]:
#                                             b_third_sell = True
#                                             sell_signal_2 = True
#                                             print('sell_signal_2, current time is {}'.format(temp_x[4].date()))
#                                         else:
#                                             b_area_v2_ok_3_sell = False
#                         else:
#                             b_area_v1_ok_3_sell = False