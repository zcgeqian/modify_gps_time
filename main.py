import os
import sys
import glob
import gpxpy
import gpxpy.gpx
import argparse
from datetime import datetime, timedelta



def procXml(gpxPath,time_s):
    fileDir, fileName = os.path.split(gpxPath)
    fileName = 'update_'+fileName
    newDir = os.path.join(fileDir, 'update')
    if not os.path.exists(newDir):
        os.mkdir(newDir)

    # -----------------------------
    newGpxPath = os.path.join(newDir, fileName)
    # ----------------------
    # 读取文件
    gpx_file = open(gpxPath, 'r', encoding='UTF-8')
    gpx = gpxpy.parse(gpx_file)
    if time_s is not None:
        time_s = gpx.tracks[0].segments[0].points[0].time
    last_t = time_s
    over24Flag = True
    delta_t = timedelta(seconds=0)  # 不移动
    # .total_seconds()
    # 第一次处理,将隔天数据累加起来
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                # print('Point at ({0},{1}) -> {2}'.format(point.latitude, point.longitude, point.elevation))
                # print(f'当前点时间：{point.time}')
                cur_t = point.time
                if (cur_t.day != t1.day and cur_t.day != last_t.day):  # 日期变化,需要向前一定时间
                    delta_t = delta_t + last_t-cur_t + \
                        timedelta(minutes=3)  # 向前移动的时间段，隔天累加移动时间

                point.adjust_time(delta_t)
                if (delta_t != timedelta(seconds=0)):
                    print(f'修改后时间：{point.time}，时间差：{delta_t}')
                last_t = cur_t
                final_t = point.time
    

    if (final_t-time_s > timedelta(hours=12)):
        print(f'运动时间为{final_t-time_s},大于12h，对时间进行压缩')
        totol_t = final_t-time_s
        scale_t = timedelta(hours=11, minutes=55)/totol_t

        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    delta_t = scale_t*(point.time-time_s)
                    print(f'delta_t:{delta_t}')
                    point.time = time_s+delta_t

    # print('Created GPX:', gpx.to_xml())
    with open(newGpxPath, 'w', encoding='UTF-8') as f:
        f.write(gpx.to_xml())


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("-f",help='gpx file name',type=str)
    parser.add_argument("-d",help="gpx file dir name",type=str)
    parser.add_argument("-t",help="how many hours before the current time",type=int)

    args=parser.parse_args()

    if args.d:  fileList = glob.glob(args.d+'/*.gpx')
    
    if args.f:  fileList=[args.f]

    if args.t:
        time_s=datetime.now()-timedelta(hours=args.t)
    else: time_s=None

    for p in fileList:
        if os.path.isfile(p):
            gpxPath = os.path.abspath(p)
           
            print('Processing '+str(p))
            try:
                procXml(gpxPath,time_s)
                print('===time changed gpx file was generated.===')
            except:
                print('=====Somthing was wrong！=====')

        else:
            print('the input file was not found!')


if __name__ == '__main__':
    main()
