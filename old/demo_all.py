# 由于之前tushare只下载了从09-06年的数据
# 故需要进行补充操作
# 1 将pkl生成csv，仅首次需要
# 2 将csv全部读取，且找到之前没有下载的部分，进行下载

import os
import pickle
import pandas as pd
if __name__ == '__main__':
    # names = ['2015-12-30', '2016-06-30', '2016-12-30',
    #         '2017-06-30', '2017-12-25', '2018-06-25', '2018-12-25',
    #         '2019-06-25', '2019-12-30']
    # for name in names:
    #     # new_stock_file = os.path.join('C:/Users/Administrator/Desktop/chanhuice/quant/chan_ts/data/', 'hs300', 'hs_{}.pkl'.format(name))
    #     # stock_file = os.path.join('C:/Users/Administrator/Desktop/chanhuice/quant/chan_ts/data/', 'hs300', 'hs_{}.csv'.format(name))
    #     # with open(new_stock_file, 'rb') as file:
    #     #     df = pickle.loads(file.read())
    #     #     df.to_csv(stock_file)
    #     # 先通过时间下载当前起始时间往前半年, 此时对于已存在的文件不需要进行更新，只需要对新出现的进行初始化下载
    #     command_str = 'python C:\\Users\Administrator\Desktop\chanhuice\quant\chan_ts\demo_update_data_tushare.py --python_head C:\\Users\Administrator\Desktop\chanhuice\quant\chan_ts --stock_list C:\\Users\Administrator\Desktop\chanhuice\quant\chan_ts\data\hs300\hs_{}.csv --end_time {}-00:00 --b_update 0'.format(name, name)
    #     print(command_str)
    #     os.system(command_str)
    # 再更新到最新时间
    command_str = 'python C:\\Users\Administrator\Desktop\chanhuice\quant\chan_ts\demo_update_data_tushare.py --python_head C:\\Users\Administrator\Desktop\chanhuice\quant\chan_ts --stock_list C:\\Users\Administrator\Desktop\chanhuice\quant\chan_ts\stock_15-19.csv --end_time 2020-07-20-00:00'
    print(command_str)
    os.system(command_str)