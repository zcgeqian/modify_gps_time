import os
import sys
import glob
import gpxpy
import gpxpy.gpx
import argparse
from datetime import datetime, timedelta, timezone


def procXml(gpxPath, time_new):
    fileDir, fileName = os.path.split(gpxPath)
    fileName = 'update_'+fileName
    newDir = os.path.join(fileDir, 'update')
    if not os.path.exists(newDir):
        os.mkdir(newDir)

    newGpxPath = os.path.join(newDir, fileName)
    # ----------------------
    gpx_file = open(gpxPath, 'r', encoding='UTF-8')
    gpx = gpxpy.parse(gpx_file)
    gpx.description='朝出品'
    gpx.keywords='朝出品'
    gpx.tracks[0].name='朝出品'
    time_s = gpx.tracks[0].segments[0].points[0].time
    last_t = time_s

    delta_t = timedelta(seconds=0)
    cyc_time = timedelta(seconds=0)
    # .total_seconds()
    # 第一次处理,将隔天数据累加起来
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                # print('Point at ({0},{1}) -> {2}'.format(point.latitude, point.longitude, point.elevation))
                # print(f'当前点时间：{point.time}')
                cur_t = point.time
                if (cur_t.day != time_s.day and cur_t.day != last_t.day):  # 日期变化
                     # 向前移动的时间段，隔天累加移动时间
                    delta_t = delta_t + last_t-cur_t + timedelta(minutes=3)

                point.adjust_time(delta_t)
                # if (delta_t != timedelta(seconds=0)):
                #     print(f'修改后时间：{point.time}，时间差：{delta_t}')
                # # compute cyc_time
                if (cur_t-last_t > timedelta(seconds=60)):
                    pass
                else:
                    cyc_time += (cur_t-last_t)

                last_t = cur_t

    print(f'运动时间为：{cyc_time}')

    if (cyc_time > timedelta(hours=12)):
        print(f'运动时间为{cyc_time},大于12h，对时间进行压缩')
        scale_t = timedelta(hours=11, minutes=30)/cyc_time

        cyc_time = timedelta(seconds=0)
        last_t = gpx.tracks[0].segments[0].points[0].time
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    delta_t = scale_t*(point.time-time_s)
                    # print(f'delta_t:{delta_t}')
                    point.time = time_s+delta_t
                    cur_t = point.time
                    if (cur_t-last_t <= timedelta(seconds=60)):
                        cyc_time += (cur_t-last_t)
                    last_t = cur_t
        print(f'更新后运动时间为：{cyc_time}')
    
    if time_new is not None:
        gpx.name=str(time_new.date())+' 骑行'
        time_s=gpx.tracks[0].segments[0].points[0].time
        delta_t=time_new-time_s
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    point.adjust_time(delta_t)
                    print(point.time)

    # print('Created GPX:', gpx.to_xml())
    with open(newGpxPath, 'w', encoding='UTF-8') as f:
        f.write(gpx.to_xml())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", help='gpx file name', type=str)
    parser.add_argument("-d", help="gpx file dir name", type=str)
    parser.add_argument("-t", help="how many hours before the current time", type=int)

    args = parser.parse_args()

    if args.d:
        fileList = glob.glob(args.d+'/*.gpx')

    if args.f:
        fileList = [args.f]

    if args.t:
        time_new = datetime.now(timezone.utc)-timedelta(hours=args.t)
    else:
        time_new = None

    for p in fileList:
        if os.path.isfile(p):
            gpxPath = os.path.abspath(p)
            print('Processing '+str(p))
            try:
                procXml(gpxPath, time_new)
                print('===time changed gpx file was generated.===')
            except:
                print('=====Somthing was wrong！=====')
        else:
            print('the input file was not found!')


if __name__ == '__main__':
    main()
