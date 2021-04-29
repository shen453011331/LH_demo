import numpy as np
import pandas as pd
import datetime
import talib as ta



def compare_include(data1, data2_):
    # data1 is full t_data, data2 is new data, they are all pandas dataframe
    # print(data2_['date'].values[0])
    final_1 = data1.tail(1).values[0][:2]
    data2 = data2_.values[0][:2]
    # print('t-1: %d, %d, t: %d, %d' % (final_1[0], final_1[1], data2[0], data2[1]))
    include_signal = 0
    if final_1[0] >= data2[0]:
        if final_1[1] <= data2[1]:
            # print('forward include')
            include_signal = 1
    if final_1[0] <= data2[0]:
        if final_1[1] >= data2[1]:
        # print('backward include')
            include_signal = -1
    if include_signal == 0:
        # print('no include')
        data1 = data1.append(data2_, ignore_index=True)
    else:
        high_2_tail = data1.tail(2)['high'].values
        low_2_tail = data1.tail(2)['low'].values
        if high_2_tail[0] < high_2_tail[1]:
            high = np.max([high_2_tail[1], data2_['high'].values[0]])
            low = np.max([low_2_tail[1], data2_['low'].values[0]])
        else:
            high = np.min([high_2_tail[1], data2_['high'].values[0]])
            low = np.min([low_2_tail[1], data2_['low'].values[0]])
        # print('t-2 data :%d, %d' % (high_2_tail[0], low_2_tail[0]))
        # print('data after inclulde %d, %d' % (high, low))
        date = data2_['date'].values[0]
        temp_df = pd.DataFrame({'high': high, 'low': low, 'date': date},
                               index=[0], columns=['high', 'low', 'date'])
        data1.drop(data1.tail(1).index, inplace=True)
        data1 = data1.append(temp_df, ignore_index=True)
    return data1


def compare_include_trend(data1, data2_):
    # data1 is full t_data, data2 is new data, they are all pandas dataframe
    # print(data2_['date'].values[0])
    final_1 = data1.tail(1).values[0][:2]
    data2 = data2_.values[0][:2]
    # print('t-1: %d, %d, t: %d, %d' % (final_1[0], final_1[1], data2[0], data2[1]))
    include_signal = 0
    if final_1[0] >= data2[0]:
        if final_1[1] <= data2[1]:
            # print('forward include')
            include_signal = 1
    if final_1[0] <= data2[0]:
        if final_1[1] >= data2[1]:
        # print('backward include')
            include_signal = -1
    if include_signal == 0:
        # print('no include')
        data1 = data1.append(data2_, ignore_index=True)
    else:
        high_2_tail = data1.tail(2)['high'].values
        low_2_tail = data1.tail(2)['low'].values
        if high_2_tail[0] < high_2_tail[1]:
            high = np.max([high_2_tail[1], data2_['high'].values[0]])
            low = np.max([low_2_tail[1], data2_['low'].values[0]])
        else:
            high = np.min([high_2_tail[1], data2_['high'].values[0]])
            low = np.min([low_2_tail[1], data2_['low'].values[0]])
        # print('t-2 data :%d, %d' % (high_2_tail[0], low_2_tail[0]))
        # print('data after inclulde %d, %d' % (high, low))
        date = data1.tail(1)['date'].values[0]
        date_end = data2_['date_end'].values[0]
        temp_df = pd.DataFrame({'high': high, 'low': low, 'date': date, 'date_end': date_end},
                               index=[0], columns=['high', 'low', 'date', 'date_end'])
        data1.drop(data1.tail(1).index, inplace=True)
        data1 = data1.append(temp_df, ignore_index=True)
    return data1


def get_p_seq(function, p_seq, t_seq, t_num_after):
    # function can be get_p_value or get_p_value_du
    p_num = len(p_seq)
    index_3 = t_seq.tail(3).index.values
    p_val = function(t_seq[index_3[0]:index_3[0] + 1],
                     t_seq[index_3[1]:index_3[1] + 1],
                     t_seq[index_3[2]:index_3[2] + 1])
    if t_num_after == 3:
        if len(p_seq) == 0:
            p_seq.append(p_val)
        else:
            p_seq[0] = p_val
    elif t_num_after >= 4:
        if p_num == t_num_after - 2:
            # print('update p')
            p_seq[-1] = p_val
        elif p_num == t_num_after - 3:
            # print('append p')
            p_seq.append(p_val)
        else:
            print('error number of p and t is not match')
    return p_seq


def get_p_value(data1, data2, data3):
    # data1,2,3 分别是 需要计算顶角的1 2 3 个bar，都为 dataframe
    full_data = data1.append(data2, ignore_index=True)
    full_data = full_data.append(data3, ignore_index=True)
    high_value = full_data['high'].values
    low_value = full_data['low'].values
    if high_value[1] > high_value[0] and high_value[1] > high_value[2] and \
            low_value[1] > low_value[0] and low_value[1] > low_value[2]:
        # print('顶分')
        return 1
    elif low_value[1] < low_value[0] and low_value[1] < low_value[2] and \
            high_value[1] < high_value[0] and high_value[1] < high_value[2]:
        # print('底分')
        return -1
    else:
        # print('无角')
        return 0


def get_pen_t_data(data_ud_t, temp_df, b_up_down):
    # b_up_down = 1 上笔

    num_t = len(data_ud_t)
    if num_t == 0:
        # print('第一个笔-t数据')
        data_ud_t = data_ud_t.append(temp_df, ignore_index=True)
    elif num_t > 0:
        # print('增加或融合笔-t数据')
        data_ud_t = compare_include_du(data_ud_t, temp_df, b_up_down)
    return data_ud_t


def compare_include_du(data1, data2_, b_up_down):
    # data1 is full t_data, data2 is new data, they are all pandas dataframe
    # print(data1.tail(1)['date_start'].values[0], data1.tail(1)['date_end'].values[0])
    # print(data2_['date_start'].values[0], data2_['date_end'].values[0])
    final_1 = data1.tail(1).values[0][:2]
    data2 = data2_.values[0][:2]
    # print('t-1: %d, %d, t: %d, %d' % (final_1[0], final_1[1], data2[0], data2[1]))
    include_signal = 0
    if final_1[0] >= data2[0]:
        if final_1[1] <= data2[1]:
            # print('forward include')
            include_signal = 1
    if final_1[0] <= data2[0]:
        if final_1[1] >= data2[1]:
            # print('backward include')
            include_signal = -1
    if include_signal == 0:
        # print('no include')
        data1 = data1.append(data2_, ignore_index=True)
    else:
        high_2_tail = data1.tail(2)['high'].values
        low_2_tail = data1.tail(2)['low'].values
        if len(data1) == 1:
            if b_up_down:
                high = np.min([high_2_tail[0], data2_['high'].values[0]])
                low = np.min([low_2_tail[0], data2_['low'].values[0]])
            else:
                high = np.max([high_2_tail[0], data2_['high'].values[0]])
                low = np.max([low_2_tail[0], data2_['low'].values[0]])
        else:
            if high_2_tail[0] < high_2_tail[1]:
                high = np.max([high_2_tail[1], data2_['high'].values[0]])
                low = np.max([low_2_tail[1], data2_['low'].values[0]])
            else:
                high = np.min([high_2_tail[1], data2_['high'].values[0]])
                low = np.min([low_2_tail[1], data2_['low'].values[0]])
        # print('t-2 data :%d, %d' % (high_2_tail[0], low_2_tail[0]))
        # print('data after inclulde %d, %d' % (high, low))

        # date_start = data2_['date_start'].values[0]
        # date_end = data2_['date_end'].values[0]
        # 根据笔得方向确认当前融合笔对应得笔得时间
        if b_up_down:
            if low == data2_['low'].values[0]:
                date_start = data2_['date_start'].values[0]
                date_end = data2_['date_end'].values[0]
            else:
                date_start = data1.tail(1)['date_start'].values[0]
                date_end = data1.tail(1)['date_end'].values[0]
        else:
            if high == data2_['high'].values[0]:
                date_start = data2_['date_start'].values[0]
                date_end = data2_['date_end'].values[0]
            else:
                date_start = data1.tail(1)['date_start'].values[0]
                date_end = data1.tail(1)['date_end'].values[0]

        temp_df = pd.DataFrame({'high': high, 'low': low, 'date_start': date_start, 'date_end': date_end},
                               index=[0], columns=['high', 'low', 'date_start', 'date_end'])
        data1.drop(data1.tail(1).index, inplace=True)
        data1 = data1.append(temp_df, ignore_index=True)
    return data1


def get_p_value_du(data1, data2, data3):
    # data1,2,3 分别是 需要计算顶角的1 2 3 个bar，都为 dataframe
    full_data = data1.append(data2, ignore_index=True)
    full_data = full_data.append(data3, ignore_index=True)
    high_value = full_data['high'].values
    low_value = full_data['low'].values
    # print('high:')
    # print(high_value)
    # print('low:')
    # print(low_value)
    if high_value[1] > high_value[0] and high_value[1] > high_value[2] and \
            low_value[1] > low_value[0] and low_value[1] > low_value[2]:
        # print('顶分')
        return 1
    elif low_value[1] < low_value[0] and low_value[1] < low_value[2] and \
            high_value[1] < high_value[0] and high_value[1] < high_value[2]:
        # print('底分')
        return -1
    else:
        # print('无角')
        return 0


def get_time(time_):
    # time_ is a time in pandas
    return pd.to_datetime(str(time_.values[0])).strftime('%Y-%m-%d-%H:%M')


def print_pd_data(df):
    print('date_start:{},date_end:{},high:{},low:{}'.format(get_time(df['date_start']),
                                                            get_time(df['date_end']),
                                                            df['high'].values[0],
                                                            df['low'].values[0]))


class Chan(object):
    def __init__(self):
        # data sequence
        self.x_seq = pd.DataFrame(columns=['high', 'low', 'date'])
        self.t_seq = pd.DataFrame(columns=['high', 'low', 'date'])
        self.p_seq = []  # 0, 1, -1
        self.y_seq = []  # bar index of p_seq
        self.u_seq = pd.DataFrame(columns=['high', 'low', 'date_start', 'date_end'])  # up pen
        self.d_seq = pd.DataFrame(columns=['high', 'low', 'date_start', 'date_end'])  # down pen
        self.u_t_seq = pd.DataFrame(columns=['high', 'low', 'date_start', 'date_end'])  # up pen after include
        self.d_t_seq = pd.DataFrame(columns=['high', 'low', 'date_start', 'date_end'])  # down pen after include
        self.u_p_seq = []
        self.d_p_seq = []
        self.ana_seq = None
        self.l_seq = []  # bar index of p_seq  Line_data
        self.l_signal_seq = []  # line siganl saving 1 2 3
        # high 2 low 2 is for high level desision
        self.c_seq_v1 = pd.DataFrame(columns=['high', 'low', 'date_start', 'date_end', 'high2', 'low2'])
        self.c_seq_v2 = pd.DataFrame(columns=['high', 'low', 'date_start', 'date_end', 'high2', 'low2'])
        self.c_seq_v3 = pd.DataFrame(columns=['high', 'low', 'date_start', 'date_end', 'high2', 'low2'])
        self.next_v2_num = 0
        self.next_v3_num = 0
        self.c_tmp_seq = pd.DataFrame(columns=['high', 'low', 'date_start', 'date_end', 'ud'])
        self.c_out_count = 0
        self.c_end = False

        self.temp_pen_u = None
        self.temp_pen_d = None
        # 走势
        self.x_trend_seq = pd.DataFrame(columns=['high', 'low', 'date', 'date_end'])
        self.t_trend_seq = pd.DataFrame(columns=['high', 'low', 'date', 'date_end'])
        self.l_trend_seq = pd.DataFrame(columns=['high', 'low', 'date_start', 'date_end', 'ud'])
        self.b_new_area, self.b_new_line = 0, 0
        self.p_trend_seq = []
        self.last_temp_x_trend = None
        self.last_trend_index = 0
        self.p_trend_idx = 0
        self.c_trend_seq = pd.DataFrame(columns=['high', 'low', 'date_start', 'date_end', 'high2', 'low2'])
        self.c_trend_end = False
        self.c_trend_tmp_seq = pd.DataFrame(columns=['high', 'low', 'date_start', 'date_end', 'ud'])
        self.c_trend_out_count = 0
        self.b_new_trend_line, self.b_new_trend_area = 0, 0

    def update(self, datas_1min):
        b_new_area, b_new_line, b_new_area_v1, b_new_area_v2 = 0, 0, 0, 0
        self.x_seq = self.x_seq.append(datas_1min, ignore_index=True)
        t_num = len(self.t_seq)
        self.t_seq = self.t_seq.append(datas_1min, ignore_index=True) \
            if t_num < 2 else compare_include(self.t_seq, datas_1min)
        t_num_after, p_num = len(self.t_seq), len(self.p_seq)
        if t_num_after >= 3:
            get_p_seq(get_p_value, self.p_seq, self.t_seq, t_num_after)
        p_num_after, y_num = len(self.p_seq), len(self.y_seq)
        if p_num_after > 1 and p_num_after - p_num == 1:
            assert (t_num_after - p_num_after == 2)
            p_val = self.p_seq[-2]
            if p_val != 0:
                self.get_y_seq(p_val, p_num_after, y_num)
        y_num_after, l_num, u_num, d_num = len(self.y_seq), len(self.l_seq), len(self.u_seq), len(self.d_seq)
        if y_num_after > y_num and y_num_after > 2:  # 仅在画出新的一笔之后判断 至少有两笔才判断
            assert y_num_after - y_num == 1
            b_pen_direction = 0 if self.p_seq[self.y_seq[0]] == -1 else 1  # 0 第一个是上笔，1 下笔
            temp_df_ud = self.get_u_d_seq(b_pen_direction, y_num_after)
            u_num_after, d_num_after = len(self.u_seq), len(self.d_seq)
            b_up_down = 1 if (y_num_after - 1 + b_pen_direction) % 2 == 0 else 0
            # 倒数第二笔为上笔
            if b_up_down:
                self.u_t_seq = get_pen_t_data(self.u_t_seq, temp_df_ud, b_up_down)
            else:
                self.d_t_seq = get_pen_t_data(self.d_t_seq, temp_df_ud, b_up_down)
            u_t_num_after, d_t_num_after, u_p_num, d_p_num = len(self.u_t_seq), len(self.d_t_seq), len(
                self.u_p_seq), len(self.d_p_seq)
            if b_up_down:
                if u_t_num_after >= 3:
                    u_p_seq = get_p_seq(get_p_value_du, self.u_p_seq, self.u_t_seq, u_t_num_after)
            else:
                if d_t_num_after >= 3:
                    d_p_seq = get_p_seq(get_p_value_du, self.d_p_seq, self.d_t_seq, d_t_num_after)
            # print('-------------------calculate L Signal Data:------------------------')
            u_p_num_after, d_p_num_after = len(self.u_p_seq), len(self.d_p_seq)
            l_signal = self.get_l_signal(b_up_down, u_num_after, u_p_num, u_p_num_after,
                                         d_num_after, d_p_num, d_p_num_after)
            # print('-------------------calculate L Data:------------------------')
            if l_signal:
                temp_l_node = self.get_temp_node(l_signal, b_up_down)
                self.get_l_seq(l_num, l_signal, temp_l_node, b_up_down)
        l_num_after, c_num = len(self.l_seq), len(self.c_seq_v1)
        if l_num_after - l_num == 1 and l_num_after >= 7:
            # print('-------------------calculate C Signal Data:------------------------')
            self.get_c_seq_v1(l_num_after, c_num)
        b_new_line = 1 if l_num_after - l_num == 1 else 0

        c_num_after = len(self.c_seq_v1)
        c_num_v2 = len(self.c_seq_v2)
        b_new_area_v1 = 1 if c_num_after - c_num == 1 else 0

        if c_num_after - c_num == 1 and c_num_after > 1:
            # print('-------------------calculate C_v2:------------------------')
            ok, temp_df = self.get_update_solo(self.c_seq_v1.iloc[-2:-1], 1)
            if ok:
                self.c_seq_v2 = self.c_seq_v2.append(temp_df)
                self.next_v2_num = 0  # 表示，对于下一个中枢，他前面有多少没有被使用过的中枢
            elif self.next_v2_num >= 1 and c_num_after > 2:
                ok, temp_df = self.get_update_double(self.c_seq_v1.iloc[-3:-1], 1)
                if ok:
                    self.c_seq_v2 = self.c_seq_v2.append(temp_df)
                    self.next_v2_num = 0  # 表示，对于下一个中枢，他前面有多少没有被使用过的中枢
                elif self.next_v2_num >= 2 and c_num_after > 3:
                    ok, temp_df = self.get_update_trible(self.c_seq_v1.iloc[-4:-1], 1)
                    if ok:
                        self.c_seq_v2 = self.c_seq_v2.append(temp_df)
                        self.next_v2_num = 0
            if not ok:
                self.next_v2_num = self.next_v2_num + 1
        c_num_v2_after = len(self.c_seq_v2)
        if c_num_v2_after - c_num_v2 == 1:
            b_new_area_v2 = 1
        if c_num_v2_after - c_num_v2 == 1 and c_num_v2_after > 1:
            # print('-------------------calculate C_v3:------------------------')
            ok, temp_df = self.get_update_solo(self.c_seq_v2.iloc[-2:-1], 2)
            if ok:
                self.c_seq_v3 = self.c_seq_v3.append(temp_df)
                self.next_v3_num = 0  # 表示，对于下一个中枢，他前面有多少没有被使用过的中枢
            elif self.next_v3_num >= 1 and c_num_v2_after > 2:
                ok, temp_df = self.get_update_double(self.c_seq_v2.iloc[-3:-1], 2)
                if ok:
                    self.c_seq_v3 = self.c_seq_v3.append(temp_df)
                    self.next_v3_num = 0  # 表示，对于下一个中枢，他前面有多少没有被使用过的中枢
                elif self.next_v3_num >= 2 and c_num_v2_after > 3:
                    ok, temp_df = self.get_update_trible(self.c_seq_v2.iloc[-4:-1], 2)
                    if ok:
                        self.c_seq_v3 = self.c_seq_v3.append(temp_df)
                        self.next_v3_num = 0
            if not ok:
                self.next_v3_num = self.next_v3_num + 1
            else:
                # print('找到第{}个三级中枢, 线段条数为{}'.format(len(self.c_seq_v3), self.get_line_num(temp_df)))
                b_new_area = 1
                # print('此时的时间为{}'.format(datas_1min['date'].values[0]))
        self.b_new_line, self.b_new_area = b_new_line, b_new_area_v1
        return b_new_area, b_new_line, b_new_area_v1, b_new_area_v2

    def update_trend(self):
        self.trend_x_num_old = len(self.x_trend_seq)
        temp_x = self.x_seq.tail(1).values[0]
        # get trend bar
        if len(self.x_trend_seq) == 0:
            # print('x_trend 新建')
            trend_data = pd.DataFrame({'high': temp_x[0], 'low': temp_x[1], 'date': temp_x[2], 'date_end': temp_x[2]},
                                      index=[0], columns=['high', 'low', 'date', 'date_end'])
            self.x_trend_seq = self.x_trend_seq.append(trend_data, ignore_index=True)
        else:
            if self.b_new_area:
                # print('新区域，当前有{}个1级中枢'.format(len(self.c_seq_v1)))
                if len(self.c_seq_v1) > 1:
                    pre_trend_data = self.x_seq[(self.x_seq['date'] >= self.c_seq_v1.iloc[-2:-1]['date_end'].values[0])
                                                & (self.x_seq['date'] <= self.c_seq_v1.tail(1)['date_start'].values[0])]

                else:
                    pre_trend_data = self.x_seq[self.x_seq['date'] <= self.c_seq_v1.tail(1)['date_start'].values[0]]
                data_last_area_v1 = self.x_seq[(self.x_seq['date'] >= self.c_seq_v1.tail(1)['date_start'].values[0])
                                               & (self.x_seq['date'] <= self.c_seq_v1.tail(1)['date_end'].values[0])]
                trend_data_1 = self.get_df_from_trend_data(data_last_area_v1)
                trend_data_2 = self.get_df_from_trend_data(pre_trend_data)
                trend_data = pd.DataFrame(
                    {'high': temp_x[0], 'low': temp_x[1], 'date': temp_x[2], 'date_end': temp_x[2]},
                    index=[0], columns=['high', 'low', 'date', 'date_end'])
                if len(self.x_trend_seq) == 1:
                    self.x_trend_seq = trend_data_2
                elif len(self.x_trend_seq) > 1:
                    self.x_trend_seq = self.x_trend_seq.iloc[:-1].append(trend_data_2, ignore_index=True)
                self.x_trend_seq = self.x_trend_seq.append(trend_data_1, ignore_index=True)
                self.x_trend_seq = self.x_trend_seq.append(trend_data, ignore_index=True)
                # print('x_trend 数量{}'.format(len(self.x_trend_seq)))
            elif self.b_new_line and len(self.c_seq_v1) > 0:
                # print('新线段，当前有{}个1级中枢'.format(len(self.c_seq_v1)))
                data_last_area_v1 = self.x_seq[(self.x_seq['date'] >= self.c_seq_v1.tail(1)['date_start'].values[0])
                                               & (self.x_seq['date'] <= self.c_seq_v1.tail(1)['date_end'].values[0])]
                if len(data_last_area_v1) == 0:
                    print('date:{}'.format(self.c_seq_v1.tail(1)['date_start'].values[0]))
                    print('date:{}'.format(self.c_seq_v1.tail(1)['date_end'].values[0]))
                pre_trend_data = self.x_seq[self.x_seq['date'] >= self.c_seq_v1.tail(1)['date_end'].values[0]]
                trend_data_1 = self.get_df_from_trend_data(data_last_area_v1)
                trend_data_2 = self.get_df_from_trend_data(pre_trend_data)
                self.x_trend_seq = self.x_trend_seq.iloc[:-2].append(trend_data_1, ignore_index=True)
                self.x_trend_seq = self.x_trend_seq.append(trend_data_2, ignore_index=True)
                # print('x_trend 数量{}'.format(len(self.x_trend_seq)))
                pass
            else:
                pre_trend_data = self.x_seq[self.x_seq['date'] >= self.x_trend_seq.tail(1)['date'].values[0]]
                trend_data = self.get_df_from_trend_data(pre_trend_data)
                self.x_trend_seq = self.x_trend_seq.iloc[:-1].append(trend_data, ignore_index=True)
        # t_trend bar
        self.trend_x_num_new = len(self.x_trend_seq)
        t_trend_num = len(self.t_trend_seq)
        if self.trend_x_num_new > 2:
            if t_trend_num == 0:
                self.t_trend_seq = self.x_trend_seq.iloc[:-2]
                # print('open t_trend num {}'.format(t_trend_num))
            else:
                if self.trend_x_num_new - self.trend_x_num_old > 0:
                    # print('before t_trend num {}'.format(t_trend_num))
                    if t_trend_num >= 2:
                        # print('first append t_trend num {}'.format(t_trend_num))
                        self.t_trend_seq = compare_include_trend(self.t_trend_seq, self.x_trend_seq.iloc[-4:-3])
                    else:
                        assert t_trend_num == 1, t_trend_num
                        self.t_trend_seq = self.t_trend_seq.append(self.x_trend_seq.iloc[-4:-3])
                        high, low = self.t_trend_seq['high'].values, self.t_trend_seq['low'].values
                        if high[1] >= high[0] and low[1] <= low[0]:
                            # print('first 2 drop head 1')
                            self.t_trend_seq.iloc[1:2, 2] = self.t_trend_seq.head(1)['date'].values[0]
                            self.t_trend_seq = self.t_trend_seq.drop(self.t_trend_seq.head(1).index, inplace=False)
                        elif high[1] <= high[0] and low[1] >= low[0]:
                            # print('first 2 drop tail 1')
                            self.t_trend_seq.iloc[0:1, 3] = self.t_trend_seq.tail(1)['date_end'].values[0]
                            self.t_trend_seq = self.t_trend_seq.drop(self.t_trend_seq.tail(1).index, inplace=False)
                    if len(self.t_trend_seq) >= 2:
                        # print('second append t_trend num {}'.format(len(self.t_trend_seq)))
                        self.t_trend_seq = compare_include_trend(self.t_trend_seq, self.x_trend_seq.iloc[-3:-2])
                    else:
                        assert len(self.t_trend_seq) == 1, len(self.t_trend_seq)
                        self.t_trend_seq = self.t_trend_seq.append(self.x_trend_seq.iloc[-3:-2])
                        high, low = self.t_trend_seq['high'].values, self.t_trend_seq['low'].values
                        if high[1] > high[0] and low[1] < low[0]:
                            # print('first 2 drop head 2')
                            self.t_trend_seq.iloc[1:2, 2] = self.t_trend_seq.head(1)['date'].values[0]
                            self.t_trend_seq = self.t_trend_seq.drop(self.t_trend_seq.head(1).index, inplace=False)
                        elif high[1] < high[0] and low[1] > low[0]:
                            # print('first 2 drop tail 2')
                            self.t_trend_seq.iloc[0:1, 3] = self.t_trend_seq.tail(1)['date_end'].values[0]
                            self.t_trend_seq = self.t_trend_seq.drop(self.t_trend_seq.tail(1).index, inplace=False)
                    # print('t_trend num {}'.format(len(self.t_trend_seq)))
        t_trend_num_after = len(self.t_trend_seq)
        # get p
        p_trend_num = len(self.p_trend_seq)
        if len(self.t_trend_seq) >= 3 and self.trend_x_num_new - self.trend_x_num_old > 0:
            #self.trend_x_num_new - self.trend_x_num_old > 0 保证只有在新加入两个bar时候才进行顶底分判断
            p_val = get_p_value(self.t_trend_seq.iloc[-3:-2],
                                self.t_trend_seq.iloc[-2:-1],
                                self.t_trend_seq.iloc[-1:])
            # print('p判断，当前t数量为{}'.format(t_trend_num_after))
            if p_trend_num == 0:
                # print('首次获取p')
                if t_trend_num_after > 3:
                    assert t_trend_num_after == 4, 't:{}'.format(t_trend_num_after)
                    p_val_1 = get_p_value(self.t_trend_seq.iloc[-4:-3],
                                          self.t_trend_seq.iloc[-3:-2],
                                          self.t_trend_seq.iloc[-2:-1])
                    self.p_trend_seq.append(p_val_1)
                self.p_trend_seq.append(p_val)
            else:
                # print('非首次获取p')
                if t_trend_num_after - t_trend_num > 0 and t_trend_num_after >= 4:
                    assert t_trend_num == p_trend_num + 2, 't:{}, p:{}'.format(t_trend_num, p_trend_num)
                    if t_trend_num_after - p_trend_num == 4:
                        p_val_1 = get_p_value(self.t_trend_seq.iloc[-4:-3],
                                              self.t_trend_seq.iloc[-3:-2],
                                              self.t_trend_seq.iloc[-2:-1])
                        self.p_trend_seq.append(p_val_1)
                    else:
                        pass
                    self.p_trend_seq.append(p_val)
                else:
                    # print('t更新')
                    self.p_trend_seq[-1] = p_val
        l_trend_num = len(self.l_trend_seq)
        self.get_l_trend(p_trend_num)
        l_trend_num_after, c_trend_num = len(self.l_trend_seq), len(self.c_trend_seq)
        self.b_new_trend_line = 1 if l_trend_num_after - l_trend_num > 0 else 0

        if l_trend_num_after - l_trend_num > 0 and l_trend_num_after >= 6:
            # assert  l_trend_num_after - l_trend_num == 1, 'adding more than 1 lines in one time'
            self.get_c_trend_seq()
        c_trend_num_after = len(self.c_trend_seq)
        self.b_new_trend_area = 1 if c_trend_num_after - c_trend_num > 0 else 0






    def get_l_trend(self, p_trend_num):
        p_trend_num_after = len(self.p_trend_seq)
        temp_index = self.p_trend_idx
        b_add = False
        # 移除最后的不稳定项
        l_trend_num = len(self.l_trend_seq)
        if l_trend_num > 1:
            self.l_trend_seq = self.l_trend_seq.iloc[:-1]
            # print('移除最后的不稳定项')
        if p_trend_num_after > temp_index + 1:
            # print('p 更新')
            for j in range(temp_index, p_trend_num_after-1):
                self.p_trend_idx = self.p_trend_idx + 1
                # print('old:{}, new:{} ,j:{} '.format(self.p_trend_idx, p_trend_num_after, j))
                temp_p = self.p_trend_seq[j]
                if temp_p == 1:
                    b_last_up_down = 1
                    temp_x_trend = self.x_trend_seq[
                        self.x_trend_seq['date'] == self.t_trend_seq.iloc[j + 1:j + 2]['date'].values[0]]
                    trend_end_value = temp_x_trend['high'].values[0]
                    trend_end_time = temp_x_trend['date_end'].values[0]
                    trend_index = len(self.c_seq_v1[self.c_seq_v1['date_end'] <= trend_end_time])
                    if len(self.l_trend_seq) == 0:
                        trend_start_value = self.x_trend_seq.head(1)['low'].values[0]
                        area_num = trend_index
                        trend_start_time = self.x_trend_seq.head(1)['date_end'].values[0]
                    else:
                        trend_start_value = self.last_temp_x_trend['low'].values[0]
                        trend_start_time = self.last_temp_x_trend['date_end'].values[0]
                        area_num = trend_index - self.last_trend_index
                    pass
                elif temp_p == -1:
                    b_last_up_down = -1
                    temp_x_trend = self.x_trend_seq[
                        self.x_trend_seq['date'] == self.t_trend_seq.iloc[j + 1:j + 2]['date'].values[0]]
                    trend_end_value = temp_x_trend['low'].values[0]
                    trend_end_time = temp_x_trend['date_end'].values[0]
                    trend_index = len(self.c_seq_v1[self.c_seq_v1['date_end'] <= trend_end_time])
                    if len(self.l_trend_seq) == 0:
                        trend_start_value = self.x_trend_seq.head(1)['high'].values[0]
                        area_num = trend_index
                        trend_start_time = self.x_trend_seq.head(1)['date_end'].values[0]

                    else:
                        trend_start_value = self.last_temp_x_trend['high'].values[0]
                        trend_start_time = self.last_temp_x_trend['date_end'].values[0]
                        area_num = trend_index - self.last_trend_index
                    pass
                if temp_p != 0:
                    high = trend_start_value if temp_p == -1 else trend_end_value
                    low = trend_end_value if temp_p == -1 else trend_start_value
                    temp_df = pd.DataFrame({'high': high, 'low': low, 'date_start': trend_start_time, 'date_end': trend_end_time,
                                            'ud': b_last_up_down},
                                           index=[0], columns=['high', 'low', 'date_start', 'date_end', 'ud'])
                    self.l_trend_seq = self.l_trend_seq.append(temp_df)
                    # print('adding trend lines, line num:{}'.format(len(self.l_trend_seq)))
                    self.last_temp_x_trend = temp_x_trend
                    self.last_trend_index = trend_index
                    b_add = True
        if l_trend_num > 1 or b_add:
            self.adding_final_l_trend()

    def adding_final_l_trend(self):
        # add 不稳定项
        final_up_down = -self.l_trend_seq.tail(1)['ud'].values[0]
        if final_up_down == 1:
            trend_start_value = self.last_temp_x_trend['high'].values[0]
            trend_end_value = self.x_trend_seq.tail(1)['low'].values[0]
        elif final_up_down == -1:
            trend_start_value = self.last_temp_x_trend['low'].values[0]
            trend_end_value = self.x_trend_seq.tail(1)['high'].values[0]
        area_num = len(self.c_seq_v1) - self.last_trend_index
        trend_start_time = self.last_temp_x_trend['date_end'].values[0]
        trend_end_time = self.x_trend_seq.tail(1)['date_end'].values[0]
        high = trend_start_value if final_up_down == -1 else trend_end_value
        low = trend_end_value if final_up_down == -1 else trend_start_value
        temp_df = pd.DataFrame({'high': high, 'low': low, 'date_start': trend_start_time, 'date_end': trend_end_time,
                                'ud': final_up_down},
                               index=[0], columns=['high', 'low', 'date_start', 'date_end', 'ud'])
        self.l_trend_seq = self.l_trend_seq.append(temp_df)
        # print('添加不稳定项,after num l is {}'.format(len(self.l_trend_seq)))

    def get_df_from_trend_data(self, pre_trend_data):
        high = np.max(np.array(pre_trend_data['high'].values))
        low = np.min(np.array(pre_trend_data['low'].values))
        trend_data = pd.DataFrame({'high': high, 'low': low,
                                   'date': pre_trend_data.head(1)['date'].values[0],
                                   'date_end': pre_trend_data.tail(1)['date'].values[0]},
                                  index=[0], columns=['high', 'low', 'date', 'date_end'])
        return trend_data

    def get_y_seq(self, p_val, p_num_after, y_num):
        current_p_index = p_num_after - 2
        # temp_corner = t_seq[current_p_index + 1:current_p_index + 1 + 1]
        if y_num == 0:
            # print('原来无笔，画一笔起点')
            self.y_seq.append(current_p_index)
        elif y_num > 0:
            # print('p_bar 间隔 为 %d, %d' % (self.y_seq[-1], current_p_index))
            # print('p_bar 时间 为 {}, {}'.format(self.t_seq[self.y_seq[-1] + 1:self.y_seq[-1] + 2]['date'].values[0],
            #                                  self.t_seq[current_p_index + 1:current_p_index + 2]['date'].values[0]))
            if self.p_seq[self.y_seq[-1]] == p_val:
                if len(self.y_seq) > 2:
                    t1_ = self.t_seq[self.y_seq[-2] + 1:self.y_seq[-2] + 2]
                    t2_ = self.t_seq[self.y_seq[-1] + 1:self.y_seq[-1] + 2]
                    t_now_ = self.t_seq[current_p_index + 1:current_p_index + 2]
                    t1, t2, t_now = 0, 0, 0
                    if p_val == -1:
                        t1 = t1_['low'].values[0]
                        t2 = t2_['low'].values[0]
                        t_now = t_now_['low'].values[0]
                    elif p_val == 1:
                        t1 = t1_['high'].values[0]
                        t2 = t2_['high'].values[0]
                        t_now = t_now_['high'].values[0]
                    # print('t1:{},t2:{},t_now:{}'.format(t1, t2, t_now))
                    if (t1 - t2) * (t2 - t_now) < 0:
                        pass
                        # print('延申反向，不延申')
                    else:
                        # print('更新笔起点')
                        self.y_seq[-1] = current_p_index
                else:
                    # print('更新笔起点')
                    self.y_seq[-1] = current_p_index
            elif current_p_index - self.y_seq[-1] > 3:
                high1, high2, low1, low2 = 1, 1, 0, 0
                last_t = self.t_seq[self.y_seq[-1] + 1:self.y_seq[-1] + 2]
                new_t = self.t_seq[current_p_index + 1:current_p_index + 2]
                if p_val == -1:
                    high1 = last_t['low'].values[0]
                    low1 = new_t['low'].values[0]
                    high2 = last_t['high'].values[0]
                    low2 = new_t['high'].values[0]
                elif p_val == 1:
                    low1 = last_t['high'].values[0]
                    high1 = new_t['high'].values[0]
                    low2 = last_t['low'].values[0]
                    high2 = new_t['low'].values[0]
                # print('high1:{},high2:{},low1:{},low2:{}'.format(high1, high2, low1, low2))
                if high1 > low1 and high2 > low2:
                    # print('画下一个节点')
                    self.y_seq.append(current_p_index)
                else:
                    pass
                    # print('顶底数值反向，不增加节点')
            else:
                pass
                # print('无法画笔,节点间距太小')

    def get_u_d_seq(self, b_pen_direction, y_num_after):
        idx_final2 = y_num_after - 2
        t_start = self.t_seq[self.y_seq[idx_final2 - 1] + 1:self.y_seq[idx_final2 - 1] + 2]
        t_end = self.t_seq[self.y_seq[idx_final2] + 1:self.y_seq[idx_final2] + 2]
        b_up_down = 1 if (y_num_after - 1 + b_pen_direction) % 2 == 0 else 0
        if b_up_down:
            # 若为上笔
            high = t_end['high'].values[0]
            low = t_start['low'].values[0]
        else:
            high = t_start['high'].values[0]
            low = t_end['low'].values[0]
        date_start = t_start['date'].values[0]
        date_end = t_end['date'].values[0]
        temp_df = pd.DataFrame({'high': high, 'low': low, 'date_start': date_start, 'date_end': date_end},
                               index=[0], columns=['high', 'low', 'date_start', 'date_end'])
        # print('high:{}-{}low:{}-{},start:{},end:{}'.format(t_start['high'].values[0],
        #                                                    t_end['high'].values[0],
        #                                                    t_start['low'].values[0],
        #                                                    t_end['low'].values[0],
        #                                                    date_start, date_end))
        if b_up_down:
            # print('当前为上笔')
            self.u_seq = self.u_seq.append(temp_df, ignore_index=True)
        else:
            # print('当前为下笔')
            self.d_seq = self.d_seq.append(temp_df, ignore_index=True)
        return temp_df

    def get_l_signal(self, b_up_down, u_num_after, u_p_num, u_p_num_after,
                     d_num_after, d_p_num, d_p_num_after):
        l_signal = 0
        if b_up_down:
            # print('上笔信号')
            if u_num_after >= 3:
                # print_pd_data(self.u_seq.tail(1))
                if self.temp_pen_u is not None:  # 判断顶分二型临时节点是否存在
                    # print('存在临时节点')
                    temp_high = self.u_seq[-1:]['high'].values[0]
                    temp_low = self.d_seq[-2:-1]['low'].values[0]
                    if self.temp_pen_u['low'].values[0] > temp_low:  # 判断是否存在正向穿越，即是否存在下笔low值高于临时笔
                        # print('底分二型取消')
                        self.temp_pen_u = None
                    elif self.temp_pen_u['high'].values[0] < temp_high:  # 判断是否反向穿越，即对底分，是否存在上笔high值高于临时笔
                        # print('底分二型')
                        l_signal = 3
                else:
                    u_last3 = self.u_seq.tail(3)
                    low_3 = u_last3['low'].values
                    high_3 = u_last3['high'].values
                    if low_3[1] < low_3[0] and low_3[1] < low_3[2] and high_3[1] > low_3[0]:
                        if high_3[2] > high_3[1]:  # 判断第6笔high值是否超越第4笔
                            # print('底分二型一次定位')
                            l_signal = 2
                        else:
                            # print('底分二型临时节点')
                            l_signal = 0
                            self.temp_pen_u = self.u_seq[-2:-1]
                            # 增加临时笔
                    else:
                        if u_p_num_after > 1 and self.u_p_seq[-2] == -1 and u_p_num_after - u_p_num == 1:
                            # print_pd_data(self.u_p_seq.tail(1))
                            # print('融合后为底分')
                            l_signal = 1
                            self.temp_pen_u = None
                        else:
                            l_signal = 0
        else:
            # print('下笔信号')
            if d_num_after >= 3:
                # print_pd_data(self.d_seq.tail(1))
                if self.temp_pen_d is not None:  # 判断顶分二型临时节点是否存在
                    # print('存在临时节点')
                    temp_high = self.u_seq[-2:-1]['high'].values[0]
                    temp_low = self.d_seq[-1:]['low'].values[0]
                    if self.temp_pen_d['high'].values[0] < temp_high:  # 判断是否存在正向穿越，即是否存在下笔low值高于临时笔
                        # print('顶分二型取消')
                        self.temp_pen_d = None
                    elif self.temp_pen_d['low'].values[0] > temp_low:  # 判断是否反向穿越，即对底分，是否存在上笔high值高于临时笔
                        # print('顶分二型')
                        l_signal = 3
                else:
                    d_last3 = self.d_seq.tail(3)
                    low_3 = d_last3['low'].values
                    high_3 = d_last3['high'].values
                    if high_3[1] > high_3[0] and high_3[1] > high_3[2] and low_3[1] < high_3[0]:
                        if low_3[2] < low_3[1]:  # 判断第6笔high值是否超越第4笔
                            l_signal = 2
                            # print('顶分二型一次定位')
                        else:
                            l_signal = 0
                            self.temp_pen_d = self.d_seq[-2:-1]
                            # print('顶分二型临时节点')
                            # 增加临时笔
                    else:
                        if d_p_num_after > 1 and self.d_p_seq[-2] == 1 and d_p_num_after - d_p_num == 1:
                            # print_pd_data(self.d_t_seq.tail(1))
                            # print('融合后为顶分')
                            l_signal = 1
                            self.temp_pen_d = None
                        else:
                            l_signal = 0
        return l_signal

    def get_temp_node(self, l_signal, b_up_down):
        temp_l_node = None
        if l_signal == 1:
            temp_l_node = self.u_t_seq[-3:-2]['date_start'].values[0] \
                if b_up_down else self.d_t_seq[-3:-2]['date_start'].values[0]
            # print('当前节点为 {}'.format(temp_l_node))
        elif l_signal == 2:
            temp_l_node = self.u_seq[-2:-1]['date_start'].values[0] \
                if b_up_down else self.d_seq[-2:-1]['date_start'].values[0]
        elif l_signal == 3:
            if b_up_down:
                temp_l_node = self.temp_pen_u['date_start'].values[0]
                self.temp_pen_u = None
            else:
                temp_l_node = self.temp_pen_d['date_start'].values[0]
                self.temp_pen_d = None
        return temp_l_node

    def get_jump_value(self, temp_l_node, b_up_down):
        b_jump = 0
        if b_up_down:
            # print('判断底角跳空')
            if len(self.l_signal_seq) == 0 or self.l_signal_seq[-1] == 1:
                pen_2 = self.u_t_seq[self.u_t_seq['date_start'] == temp_l_node]
                index = pen_2.index.values[0]
                pen_1 = self.u_t_seq[index - 1:index]
                # print('pen1 low value:{},pen2 high value:{} '.format(pen_1['low'].values[0],
                #                                                      pen_2['high'].values[0]))
                if pen_2['high'].values[0] < pen_1['low'].values[0]:
                    b_jump = 1
                else:
                    b_jump = 0
                # print('时间从 {} 到 {}'.format(pen_1['date_start'].values[0], pen_2['date_start'].values[0]))
            else:
                # print('前一节点signal为{}'.format(self.l_signal_seq[-1]))
                b_jump = 0
        else:
            # print('判断顶角跳空')
            if len(self.l_signal_seq) == 0 or self.l_signal_seq[-1] == 1:
                pen_2 = self.d_t_seq[self.d_t_seq['date_start'] == temp_l_node]
                index = pen_2.index.values[0]
                pen_1 = self.d_t_seq[index - 1:index]
                # print('pen1 high value:{},pen2 low value:{} '.format(pen_1['high'].values[0],
                #                                                      pen_2['low'].values[0]))
                if pen_2['low'].values[0] > pen_1['high'].values[0]:
                    b_jump = 1
                else:
                    b_jump = 0
                # print('时间从 {} 到 {}'.format(pen_1['date_start'].values[0], pen_2['date_start'].values[0]))
            else:
                # print('前一节点signal为{}'.format(self.l_signal_seq[-1]))
                b_jump = 0
        return b_jump

    def get_l_direction(self, last_date):
        # 以last_date为起点的方向，b_last_up_down 为1 说明上线段，0下线段
        if last_date in self.u_t_seq['date_start'].values or last_date in self.u_seq['date_start'].values:
            b_last_up_down = 1
        elif last_date in self.d_t_seq['date_start'].values or last_date in self.d_seq['date_start'].values:
            b_last_up_down = 0
        else:
            b_last_up_down = -1
        assert b_last_up_down != -1
        return b_last_up_down

    def get_l_seq(self, l_num, l_signal, temp_l_node, b_up_down):
        if l_num == 0:
            if l_signal == 1:
                # 判断节点是否存在跳空
                b_jump = self.get_jump_value(temp_l_node, b_up_down)
                if not b_jump:
                    # print('第一个线段节点')
                    self.l_seq.append(temp_l_node)
                    self.l_signal_seq.append(l_signal)
                else:
                    pass
                    # print('第一个线段节点跳空，未载入')
            else:
                pass
                # print('第一个线段节点信号不为1，忽略')
        elif l_num > 0:
            last_date = self.l_seq[-1]
            t_index_start = self.t_seq[self.t_seq['date'] == last_date].index.values[0]
            t_index_end = self.t_seq[self.t_seq['date'] == temp_l_node].index.values[0]
            # print('last_date:{},now_date:{}'.format(last_date, temp_l_node))
            if t_index_start < t_index_end:
                distance = 0
                if t_index_start - 1 in self.y_seq and t_index_end - 1 in self.y_seq:
                    distance = self.y_seq.index(t_index_end - 1) - self.y_seq.index(t_index_start - 1)
                else:
                    pass
                    # print('笔没有在笔数据中，报错')
                if distance >= 3:
                    b_last_up_down = self.get_l_direction(last_date)
                    b_last_jump = self.get_jump_value(last_date, b_last_up_down)
                    if b_last_up_down == b_up_down:
                        if b_last_jump:
                            if self.verify_line_update(temp_l_node, last_date):
                                # print('前一线段节点有跳跃，重置线段起点')
                                self.l_seq[-1] = temp_l_node
                                self.l_signal_seq[-1] = l_signal
                            else:
                                pass
                                # print('数值与线段方向相反，线段起点更新失败')
                        else:
                            pass
                            # print('笔顶底分与线段方向相反，线段起点固定，不增加节点')
                    else:
                        # print('增加线段终点')
                        self.l_seq.append(temp_l_node)
                        self.l_signal_seq.append(l_signal)
                else:
                    pass
                    # print('线段信号频次太快，构成线段笔太少，不操作')

    def verify_line_update(self, new_date, old_date):
        b_up_down = self.get_l_direction(old_date)
        if b_up_down:
            # 由于当前是向上线段，说明前一线段是向下的
            old_pen = self.u_t_seq[self.u_t_seq['date_start'] == old_date]
            if len(old_pen) == 0:
                old_pen = self.u_seq[self.u_seq['date_start'] == old_date]
            new_pen = self.u_t_seq[self.u_t_seq['date_start'] == new_date]
            if len(new_pen) == 0:
                new_pen = self.u_seq[self.u_seq['date_start'] == new_date]
            old_low, new_low = old_pen['low'].values[0], new_pen['low'].values[0]
            if new_low <= old_low:
                return 1
            else:
                return 0
        else:
            # 由于当前是向上线段，说明前一线段是向下的
            old_pen = self.d_t_seq[self.d_t_seq['date_start'] == old_date]
            if len(old_pen) == 0:
                old_pen = self.d_seq[self.d_seq['date_start'] == old_date]
            new_pen = self.d_t_seq[self.d_t_seq['date_start'] == new_date]
            if len(new_pen) == 0:
                new_pen = self.d_seq[self.d_seq['date_start'] == new_date]
            old_high, new_high = old_pen['high'].values[0], new_pen['high'].values[0]
            if new_high >= old_high:
                return 1
            else:
                return 0

    def get_temp_l_data(self, idx):
        start_date = self.l_seq[idx]
        end_date = self.l_seq[idx + 1]
        b_last_up_down = self.get_l_direction(start_date)
        if b_last_up_down:
            # print('第{}线段为，上升线段'.format(idx + 1))
            start = self.u_t_seq[self.u_t_seq['date_start'] == start_date]
            if len(start) == 0 or self.l_signal_seq[idx] != 1:
                start = self.u_seq[self.u_seq['date_start'] == start_date]
            end = self.d_t_seq[self.d_t_seq['date_start'] == end_date]
            if len(end) == 0 or self.l_signal_seq[idx] != 1:
                end = self.d_seq[self.d_seq['date_start'] == end_date]
            high = end['high'].values[0]
            low = start['low'].values[0]
        else:
            # print('第{}线段为，下降线段'.format(idx + 1))
            start = self.d_t_seq[self.d_t_seq['date_start'] == start_date]
            if len(start) == 0 or self.l_signal_seq[idx] != 1:
                start = self.d_seq[self.d_seq['date_start'] == start_date]
            end = self.u_t_seq[self.u_t_seq['date_start'] == end_date]
            if len(end) == 0 or self.l_signal_seq[idx] != 1:
                end = self.u_seq[self.u_seq['date_start'] == end_date]
            high = start['high'].values[0]
            low = end['low'].values[0]
        temp_df = pd.DataFrame({'high': high, 'low': low, 'date_start': start_date, 'date_end': end_date,
                                'ud': b_last_up_down},
                               index=[0], columns=['high', 'low', 'date_start', 'date_end', 'ud'])
        return temp_df

    def verify_range(self, line, line_4):
        c = self.c_seq_v1.tail(1)
        high1, high2 = line['high'].values[0], c['high'].values[0]
        low1, low2 = line['low'].values[0], c['low'].values[0]
        high4, low4 = line_4['high'].values[0], line_4['low'].values[0]
        b_extra_update = 1 if not (high4 < self.c_seq_v1.tail(1)['low'].values[0] or
                                   low4 > self.c_seq_v1.tail(1)['high'].values[0]) else 0

        # print('high1,high2 {}.{}'.format(high1, high2))
        # print('low1,low2 {}.{}'.format(low1, low2))
        if high1 <= high2 and low1 >= low2:
            # print('line is in area')
            return 1
        elif low1 > high2 or high1 < low2:
            # print('line is out of area')
            return 0
        elif b_extra_update:
            # print('line is cross with area')
            return 2
        else:
            # 既不具备成为临时节点，又不属于中枢外线段
            return 3

    def verify_trend_range(self, line, line_4):
        c = self.c_trend_seq.tail(1)
        high1, high2 = line['high'].values[0], c['high'].values[0]
        low1, low2 = line['low'].values[0], c['low'].values[0]
        high4, low4 = line_4['high'].values[0], line_4['low'].values[0]
        b_extra_update = 1 if not (high4 < self.c_trend_seq.tail(1)['low'].values[0] or
                                   low4 > self.c_trend_seq.tail(1)['high'].values[0]) else 0
        if high1 <= high2 and low1 >= low2:
            # print('line is in area')
            return 1
        elif low1 > high2 or high1 < low2:
            # print('line is out of area')
            return 0
        elif b_extra_update:
            # print('line is cross with area')
            return 2
        else:
            # 既不具备成为临时节点，又不属于中枢外线段
            return 3


    def get_c_seq_v1(self, l_num_after, c_num):
        i = l_num_after - 7
        line_0 = self.get_temp_l_data(i) #中枢前线段
        line1 = self.get_temp_l_data(i + 1)
        line3 = self.get_temp_l_data(i + 3)
        line_4 = self.get_temp_l_data(i + 4)# 中枢后线段
        if c_num == 0 or self.c_end:
            # print('找起点')
            self.get_c_start(line1, line3, line_0, line_4)
        else:
            signal = self.verify_range(line3, line_4)
            # b_extra_update 在更新结尾时，需要考虑用于被更新为结尾之后一条线段是否处于中枢区间内
            # print('area 信号判断')
            if signal == 1:
                # print('area signal 1')
                if line3['high'].values[0] > self.c_seq_v1.tail(1)['high2'].values[0]:
                    self.c_seq_v1.iloc[-1, 4] = line3['high'].values[0]
                if line3['low'].values[0] < self.c_seq_v1.tail(1)['low2'].values[0]:
                    self.c_seq_v1.iloc[-1, 5] = line3['low'].values[0]
                self.c_seq_v1.iloc[-1, 3] = line3['date_end'].values[0]
                self.c_out_count = 0
                if len(self.c_tmp_seq) > 0:
                    self.c_tmp_update()
            elif signal == 2:
                # print('area signal 2')
                if len(self.c_tmp_seq) > 0:
                    if self.c_tmp_seq.tail(1)['high'].values[0] > self.c_seq_v1.tail(1)['high2'].values[0]:
                        self.c_seq_v1.iloc[-1, 4] = self.c_tmp_seq.tail(1)['high'].values[0]
                    if self.c_tmp_seq.tail(1)['low'].values[0] < self.c_seq_v1.tail(1)['low2'].values[0]:
                        self.c_seq_v1.iloc[-1, 5] = self.c_tmp_seq.tail(1)['low'].values[0]
                    self.c_seq_v1.iloc[-1, 3] = self.c_tmp_seq.tail(1)['date_end'].values[0]
                    self.c_tmp_update()
                self.c_tmp_seq = self.c_tmp_seq.append(line3)
                self.c_out_count = 0
            elif signal == 0:
                # print('area signal 0')
                self.c_out_count = self.c_out_count + 1
                if self.c_out_count >= 3:
                    # print('中枢结束于{}'.format(get_time(self.c_seq_v1.tail(1)['date_end'])))
                    self.c_end = True
                    self.c_out_count = 0
                    self.c_tmp_update()
                    if not self.c_seq_v1.tail(1)['date_end'].values[0] == line1['date_start'].values[0]:
                        # print('找新的起点')
                        self.get_c_start(line1, line3, line_0, line_4)
            else:
                #signal = 3
                self.c_out_count = 0

    def get_c_trend_seq(self):
        if len(self.l_trend_seq) > 5:
            line_0 = self.l_trend_seq.iloc[-6:-5]  # 中枢前线段
            line1 = self.l_trend_seq.iloc[-5:-4]
            line3 = self.l_trend_seq.iloc[-3:-2]
            line_4 = self.l_trend_seq.iloc[-2:-1]  # 中枢后线段
            if len(self.c_trend_seq) == 0 or self.c_trend_end:
                # print('找起点')
                self.get_c_trend_start(line1, line3, line_0, line_4)
            else:
                signal = self.verify_trend_range(line3, line_4)
                # b_extra_update 在更新结尾时，需要考虑用于被更新为结尾之后一条线段是否处于中枢区间内
                # print('area 信号判断')
                if signal == 1:
                    # print('area signal 1')
                    if line3['high'].values[0] > self.c_trend_seq.tail(1)['high2'].values[0]:
                        self.c_trend_seq.iloc[-1, 4] = line3['high'].values[0]
                    if line3['low'].values[0] < self.c_trend_seq.tail(1)['low2'].values[0]:
                        self.c_trend_seq.iloc[-1, 5] = line3['low'].values[0]
                    self.c_trend_seq.iloc[-1, 3] = line3['date_end'].values[0]
                    self.c_trend_out_count = 0
                    if len(self.c_trend_tmp_seq) > 0:
                        self.c_trend_tmp_update()
                elif signal == 2:
                    # print('area signal 2')
                    if len(self.c_trend_tmp_seq) > 0:
                        if self.c_trend_tmp_seq.tail(1)['high'].values[0] > self.c_trend_seq.tail(1)['high2'].values[0]:
                            self.c_trend_seq.iloc[-1, 4] = self.c_trend_tmp_seq.tail(1)['high'].values[0]
                        if self.c_trend_tmp_seq.tail(1)['low'].values[0] < self.c_trend_seq.tail(1)['low2'].values[0]:
                            self.c_trend_seq.iloc[-1, 5] = self.c_trend_tmp_seq.tail(1)['low'].values[0]
                        self.c_trend_seq.iloc[-1, 3] = self.c_trend_tmp_seq.tail(1)['date_end'].values[0]
                        self.c_trend_tmp_update()
                    self.c_trend_tmp_seq = self.c_trend_tmp_seq.append(line3)
                    self.c_trend_out_count = 0
                elif signal == 0:
                    # print('area signal 0')
                    self.c_trend_out_count = self.c_trend_out_count + 1
                    if self.c_trend_out_count >= 3:
                        # print('中枢结束于{}'.format(get_time(self.c_seq_v1.tail(1)['date_end'])))
                        self.c_trend_end = True
                        self.c_trend_out_count = 0
                        self.c_trend_tmp_update()
                        if not self.c_trend_seq.tail(1)['date_end'].values[0] == line1['date_start'].values[0]:
                            # print('找新的起点')
                            self.get_c_trend_start(line1, line3, line_0, line_4)
                else:
                    # signal = 3
                    self.c_trend_out_count = 0

    def c_tmp_update(self):
        self.c_tmp_seq = self.c_tmp_seq.drop(self.c_tmp_seq.index, inplace=False)

    def c_trend_tmp_update(self):
        self.c_trend_tmp_seq = self.c_trend_tmp_seq.drop(self.c_trend_tmp_seq.index, inplace=False)

    def get_c_trend_start(self, line1, line3, line_0, line_4):
        high1, high2 = line1['high'].values[0], line3['high'].values[0]
        low1, low2 = line1['low'].values[0], line3['low'].values[0]
        if (bool(line1['ud'].values[0]) and high2 < low1) or \
                (not bool(line1['ud'].values[0]) and high1 < low2):
            pass
            # print('不构成中枢')
        else:
            # print('建立中枢')
            high0, high4 = line_0['high'].values[0], line_4['high'].values[0]
            low0, low4 = line_0['low'].values[0], line_4['low'].values[0]
            if not (high0 < max(low1, low2) or low0 > min(high1, high2)) \
                    and not (high4 < max(low1, low2) or low4 > min(high1, high2)):
                tmp_dic = {'high': min(high1, high2), 'low': max(low1, low2),
                           'date_start': line1['date_start'].values[0],
                           'date_end': line3['date_end'].values[0],
                           'high2': max(high1, high2), 'low2': min(low1, low2)}
                temp_df = pd.DataFrame(tmp_dic, index=[0],
                                       columns=['high', 'low', 'date_start', 'date_end', 'high2', 'low2'])
                self.c_trend_seq = self.c_trend_seq.append(temp_df)
                self.c_trend_end = False

    def get_c_start(self, line1, line3, line_0, line_4):
        high1, high2 = line1['high'].values[0], line3['high'].values[0]
        low1, low2 = line1['low'].values[0], line3['low'].values[0]
        if (bool(line1['ud'].values[0]) and high2 < low1) or \
                (not bool(line1['ud'].values[0]) and high1 < low2):
            pass
            # print('不构成中枢')
        else:
            # print('建立中枢')
            high0, high4 = line_0['high'].values[0], line_4['high'].values[0]
            low0, low4 = line_0['low'].values[0], line_4['low'].values[0]
            if not (high0 < max(low1, low2) or low0 > min(high1, high2)) \
                    and not (high4 < max(low1, low2) or low4 > min(high1, high2)):
                tmp_dic = {'high': min(high1, high2), 'low': max(low1, low2),
                           'date_start': line1['date_start'].values[0],
                           'date_end': line3['date_end'].values[0],
                           'high2': max(high1, high2), 'low2': min(low1, low2)}
                temp_df = pd.DataFrame(tmp_dic, index=[0],
                                       columns=['high', 'low', 'date_start', 'date_end', 'high2', 'low2'])
                self.c_seq_v1 = self.c_seq_v1.append(temp_df)
                self.c_end = False

    def get_update_solo(self, df, rank):
        if self.get_line_num(df) >= 3 * (2 ** rank):
            return 1, df.copy()
        else:
            return 0, None

    def get_update_double(self, df, rank):
        assert len(df) == 2
        if self.get_line_num(df.head(1)) + self.get_line_num(df.tail(1)) >= 3 * (2 ** rank):
            high, low = df['high2'].values, df['low2'].values
            if high[0] > high[1] > low[0] or high[1] > high[0] > low[1]:
                tmp_dic = {'high': max(df['high'].values), 'low': min(df['low'].values),
                           'date_start': df.head(1)['date_start'].values[0],
                           'date_end': df.tail(1)['date_end'].values[0],
                           'high2': max(high), 'low2': min(low)}
                temp_df = pd.DataFrame(tmp_dic, index=[0],
                                       columns=['high', 'low', 'date_start', 'date_end', 'high2', 'low2'])
                return 1, temp_df
        return 0, None

    def get_update_trible(self, df, rank):
        assert len(df) == 3
        if self.get_line_num(df.head(1)) \
                + self.get_line_num(df.tail(1))\
                + self.get_line_num(df.iloc[-2:-1]) >= 3 * (2 ** rank):
            high, low = df['high2'].values, df['low2'].values
            if high[0] > high[1] > low[0] or high[1] > high[0] > low[1] and \
                    (high[1] > high[2] > low[1] or high[2] > high[1] > low[2]):
                tmp_dic = {'high': max(df['high'].values), 'low': min(df['low'].values),
                           'date_start': df.head(1)['date_start'].values[0],
                           'date_end': df.tail(1)['date_end'].values[0],
                           'high2': max(high), 'low2': min(low)}
                temp_df = pd.DataFrame(tmp_dic, index=[0],
                                       columns=['high', 'low', 'date_start', 'date_end', 'high2', 'low2'])
                return 1, temp_df
        return 0, None

    def get_line_num(self, df):
        t1 = df['date_start'].values[0]
        t2 = df['date_end'].values[0]

        t1, t2 = df['date_start'].values[0], df['date_end'].values[0]
        idx1, idx2 = self.l_seq.index(t1), self.l_seq.index(t2)
        n_line = idx2 - idx1
        return n_line

    def get_first_line(self, datas_30min):
        self.x_seq = self.x_seq.append(datas_30min, ignore_index=True)
        t_num = len(self.t_seq)
        self.t_seq = self.t_seq.append(datas_30min, ignore_index=True) \
            if t_num < 2 else compare_include(self.t_seq, datas_30min)
        t_num_after, p_num = len(self.t_seq), len(self.p_seq)
        if t_num_after >= 3:
            get_p_seq(get_p_value, self.p_seq, self.t_seq, t_num_after)
        p_num_after, y_num = len(self.p_seq), len(self.y_seq)
        if p_num_after > 1 and p_num_after - p_num == 1:
            assert (t_num_after - p_num_after == 2)
            p_val = self.p_seq[-2]
            if p_val != 0:
                self.get_y_seq(p_val, p_num_after, y_num)
        y_num_after, l_num, u_num, d_num = len(self.y_seq), len(self.l_seq), len(self.u_seq), len(self.d_seq)
        if y_num_after > y_num and y_num_after > 2:  # 仅在画出新的一笔之后判断 至少有两笔才判断
            assert y_num_after - y_num == 1
            b_pen_direction = 0 if self.p_seq[self.y_seq[0]] == -1 else 1  # 0 第一个是上笔，1 下笔
            temp_df_ud = self.get_u_d_seq(b_pen_direction, y_num_after)
            u_num_after, d_num_after = len(self.u_seq), len(self.d_seq)
            b_up_down = 1 if (y_num_after - 1 + b_pen_direction) % 2 == 0 else 0
            # 倒数第二笔为上笔
            if b_up_down:
                self.u_t_seq = get_pen_t_data(self.u_t_seq, temp_df_ud, b_up_down)
            else:
                self.d_t_seq = get_pen_t_data(self.d_t_seq, temp_df_ud, b_up_down)
            u_t_num_after, d_t_num_after, u_p_num, d_p_num = len(self.u_t_seq), len(self.d_t_seq), len(
                self.u_p_seq), len(self.d_p_seq)
            if b_up_down:
                if u_t_num_after >= 3:
                    u_p_seq = get_p_seq(get_p_value_du, self.u_p_seq, self.u_t_seq, u_t_num_after)
            else:
                if d_t_num_after >= 3:
                    d_p_seq = get_p_seq(get_p_value_du, self.d_p_seq, self.d_t_seq, d_t_num_after)
            # print('-------------------calculate L Signal Data:------------------------')
            u_p_num_after, d_p_num_after = len(self.u_p_seq), len(self.d_p_seq)
            l_signal = self.get_l_signal(b_up_down, u_num_after, u_p_num, u_p_num_after,
                                         d_num_after, d_p_num, d_p_num_after)
            # print('-------------------calculate L Data:------------------------')
            if l_signal:
                temp_l_node = self.get_temp_node(l_signal, b_up_down)
                self.get_l_seq(l_num, l_signal, temp_l_node, b_up_down)