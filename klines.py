import pyecharts.options as opts
from pyecharts.charts import Kline, Candlestick
import datetime
import requests
import math

kline_cnt = 24*30

def ts2datetime(ts):
    return datetime.datetime.fromtimestamp(ts/1000).strftime('%Y-%m-%d %H:%M:%S')

interval_base = {'s':1,'m':60,'h':60*60,'d':60*60*24,'w':60*60*24*7,'M':60*60*24*30}
max_kline_range = 1000 * 60 * 60 * 24 * 365

def get_ohlcv_list(symbol='BTCUSDT', interval='1h', start_time=None, end_time=None):
    symbol = symbol.upper()
    ibase = interval[-1]
    try:
        icnt = int(interval[:-1])
    except Exception as e:
        print("invalid interval:"+interval)
        return []
    if ibase not in interval_base:
        print("invalid interval:"+interval)
        return []
    #注意：start_time和end_time都是时间戳格式，单位是毫秒，不是秒
    default_end_time = datetime.datetime.utcnow().timestamp()*1000
    default_start_time = default_end_time - 60*60*24*5*1000
    now_flag = False
    if start_time is None:
        start_time = default_start_time
    if end_time is None:
        now_flag = True
        end_time = default_end_time
    interval_time = interval_base[ibase]*icnt*1000
    #计算时间差
    global kline_cnt
    time_diff = end_time - start_time
    if time_diff > max_kline_range:
        time_diff = max_kline_range
        start_time = end_time - time_diff
    kline_cnt = math.ceil(time_diff/interval_time)
    if kline_cnt > 1000:
        kline_cnt = 1000
        time_diff = kline_cnt * interval_time
        start_time = end_time - time_diff
    url = 'https://api.binance.com/api/v3/klines?symbol='+ symbol +'&interval='+interval+'&startTime='+str(int(start_time))+'&endTime='+str(int(end_time))
    # 获取最近五天的BTCUSDT 30分钟K线数据
    #url = 'https://api.binance.com/api/v3/klines?symbol='+ symbol +'&interval=1h&limit=' + str(kline_cnt)
    r = requests.get(url)
    ohlcv_list = r.json()
    return ohlcv_list

def draw_klines(symbol, interval='1h', start_time=None, end_time=None, indicators=[]):
    ohlcv_list = get_ohlcv_list(symbol, interval, start_time, end_time)
    filename_html = 'html/'+symbol+'.html'
    last_price = ohlcv_list[-1][4]
    x_data = []
    y_data = []
    current_utc_yyyymmddhhmmss = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    for i in range(len(ohlcv_list)):
        x_data.append(ts2datetime(ohlcv_list[i][0]))
        y_data.append([ohlcv_list[i][1],ohlcv_list[i][4],ohlcv_list[i][2],ohlcv_list[i][3]])
    
    #将链式调用分开写，方便调试
    kline = Kline(init_opts=opts.InitOpts(width="350px", height="550px",))
    kline.add_xaxis(xaxis_data=x_data)
    yaxis_itemstyle_opts=opts.ItemStyleOpts(
            color0="#ec0000",
            #color0="#00da3c",
            color="#303030",
            border_color0="#8A0000",
            #border_color0="#008F28",
            border_color="#000000",
        )
    kline.add_yaxis(
        series_name="",
        y_axis=y_data,
        itemstyle_opts=yaxis_itemstyle_opts,
        )
    yaxis_splitarea_opts = opts.SplitAreaOpts(is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1))
    title_opts = opts.TitleOpts(title=symbol+":"+str(last_price) + "\n"+current_utc_yyyymmddhhmmss+" UTC\nby AI纪元", pos_left="0"),
    kline.set_global_opts(
        xaxis_opts = opts.AxisOpts(is_scale=True),
        yaxis_opts = opts.AxisOpts(is_scale=True,splitarea_opts = yaxis_splitarea_opts),
        datazoom_opts = [opts.DataZoomOpts(pos_bottom="-2%")], 
        title_opts = title_opts
        )
    kline.render(filename_html)
    return filename_html
    # c=Candlestick(init_opts=opts.InitOpts(width="350px", height="550px",)).add_xaxis(xaxis_data=x_data).add_yaxis(
    #     series_name="",
    #     y_axis=y_data,
    #     itemstyle_opts=opts.ItemStyleOpts(
    #         color0="#ec0000",
    #         #color0="#00da3c",
    #         color="#303030",
    #         border_color0="#8A0000",
    #         #border_color0="#008F28",
    #         border_color="#000000",
    #     ),
    # ).add_xaxis(xaxis_data=x_data
    # ).set_global_opts(
    #     xaxis_opts=opts.AxisOpts(is_scale=True),
    #     yaxis_opts=opts.AxisOpts(
    #         is_scale=True,
    #         splitarea_opts=opts.SplitAreaOpts(
    #             is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
    #         ),
    #     ),
    #     datazoom_opts=[opts.DataZoomOpts(pos_bottom="-2%")], 
    #     title_opts=opts.TitleOpts(title=symbol+":"+str(last_price) + "\n"+current_utc_yyyymmddhhmmss+" UTC\nby AI纪元", pos_left="0"),
    # )
    # c.render(filename_html)
    # return filename_html