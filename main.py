import os
import glob
import gpxpy
import gpxpy.gpx
from datetime import datetime, timedelta


def procXml(gpxPath):
    fileDir, fileName = os.path.split(gpxPath)
    fileName = 'update_'+fileName
    jsonDir = os.path.join(fileDir, 'update')
    if not os.path.exists(jsonDir):
        os.mkdir(jsonDir)

    # -----------------------------
    newGpxPath = os.path.join(jsonDir, fileName)

    # ----------------------
    # 读取文件
    gpx_file = open(gpxPath, 'r', encoding='UTF-8')
    gpx = gpxpy.parse(gpx_file)
    t1 = gpx.tracks[0].segments[0].points[0].time
    last_t = t1
    over24Flag = True
    delta_t = timedelta(seconds=0)  # 不移动
    # .total_seconds()
    # 第一次处理，将所有时间变为同一天
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

    if (final_t-t1 > timedelta(hours=12)):
        print('时间大于12h，对时间进行压缩')
        totol_t = final_t-t1
        scale_t = timedelta(hours=11, minutes=55)/totol_t

        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    delta_t = scale_t*(point.time-t1)
                    print(f'delta_t:{delta_t}')
                    point.time = t1+delta_t

    # print('Created GPX:', gpx.to_xml())
    with open(newGpxPath, 'w', encoding='UTF-8') as f:
        f.write(gpx.to_xml())


def main():
    # if len(sys.argv) < 2:
    #     print('Specify the gpx file path')
    #     return

    gpsDir = './gps'
    abspath = os.path.abspath(gpsDir)
    fileList = glob.glob(gpsDir+'/*.gpx')
    for p in fileList:
        if os.path.isfile(p):
            gpxPath = os.path.abspath(p)
            procXml(gpxPath)

            # print('Processing'+str(gpxPath))
            # try:
            #     procXml(gpxPath)
            #     print('Coresponding JSON file was generated.')
            # except:
            #     print('=====Somthing was wrong！=====')


if __name__ == '__main__':
    main()
