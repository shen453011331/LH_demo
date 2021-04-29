# coding=gbk
import datetime
from chinese_calendar import is_workday
import time
import os
# �Ե�ǰʱ������жϣ���Ϊ��Ϣ������1��
# ��Ϊ�����գ��ҵ�ǰhourΪ�ǿ���ʱ�䣬����30����
# ��Ϊ�����գ��ҵ�ǰhourΪ����ʱ�䣬���г������к�����1h
import argparse
parser = argparse.ArgumentParser(description='Argument parser')
parser.add_argument('--python_path', dest='python_path', type=str, default='D:\LH\JoinQuant-Desktop-Py3\Python\python.exe', help='# stock code')
parser.add_argument('--python_head', dest='python_head', type=str, default='D:\clean\quant\chan', help='# stock code')
parser.add_argument('--stock_list', dest='stock_list', type=str, default='stock_list.csv', help='# stock code')

args = parser.parse_args()



if __name__ == '__main__':
    python_path = args.python_path
    python_head = args.python_head
    stock_list = args.stock_list
    last_time = None
    while 1:
        curr_time = datetime.datetime.now()
        if last_time is None:
            last_time = curr_time - datetime.timedelta(days=1)
        if is_workday(curr_time):
            print("�ǹ�����")
            if 9 <= curr_time.hour <=15:
                print('����ʱ��')
                if curr_time.minute == 0:
                    stock_file = os.path.join(python_head, stock_list)
                    filename = 'demo_update_data.py'
                    file_path = os.path.join(python_head, filename)
                    command_str = '{} {} --python_head {} --stock_list {}' \
                                  ' --end_time {}'.format(python_path , file_path, python_head,
                                                          stock_list, curr_time.strftime('%Y-%m-%d %H:%M'))
                    print(command_str)
                    print('���������� {}'.format(curr_time.strftime('%Y-%m-%d %H:%M')))
                    os.system(command_str)
                    print('�������')
                    filename = 'demo_update_signal.py'
                    file_path = os.path.join(python_head, filename)
                    command_str = '{} {} --python_head {} --stock_list {}' \
                                  ' --end_time {}'.format(python_path, file_path, python_head,
                                                          stock_list, curr_time.strftime('%Y-%m-%d %H:%M'))
                    print(command_str)
                    print('�����ź��� {}'.format(curr_time.strftime('%Y-%m-%d %H:%M')))
                    os.system(command_str)
                    print('�������')
                    filename = 'demo_output_signal.py'
                    file_path = os.path.join(python_head, filename)
                    command_str = '{} {} --python_head {} --stock_list {}' \
                                  ' --end_time {} --last_end_time {}'.format(python_path,
                                                                             file_path,
                                                                             python_head,
                                                                             stock_list,
                                                                             curr_time.strftime('%Y-%m-%d %H:%M'),
                                                                             last_time.strftime('%Y-%m-%d %H:%M'))
                    print(command_str)
                    os.system(command_str)
                else:
                    time.sleep(30)
            else:
                print('�ǿ���ʱ��')
                time.sleep(60 * 60)
        else:
            print("����Ϣ��")
            time.sleep(60*60*24)
        break
    last_time = curr_time