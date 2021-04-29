# this file is used to circle run python command
import os

if __name__ == '__main__':
    names = ['2009-12-30', '2010-06-30', '2010-12-30',
            '2011-06-30', '2011-12-30', '2012-06-25', '2012-12-25',
            '2013-06-25', '2013-12-30', '2014-06-30', '2014-12-30',
            '2015-06-30']
    for name in names:
        command_str = 'python C:\\Users\Administrator\Desktop\chanhuice\quant\chan_ts\demo_update_data_tushare.py --python_head C:\\Users\Administrator\Desktop\chanhuice\quant\chan_ts --stock_list C:\\Users\Administrator\Desktop\chanhuice\quant\chan_ts\data\hs300\hs_{}.csv --end_time {}-00:00'.format(name, name)
        print(command_str)
        os.system(command_str)
        command_str = 'python C:\\Users\Administrator\Desktop\chanhuice\quant\chan_ts\demo_update_data_tushare.py --python_head C:\\Users\Administrator\Desktop\chanhuice\quant\chan_ts --stock_list C:\\Users\Administrator\Desktop\chanhuice\quant\chan_ts\data\hs300\hs_{}.csv --end_time 2020-07-20-00:00'.format(name)
        print(command_str)
        os.system(command_str)
        # time.sleep(60 * 60 * 24)