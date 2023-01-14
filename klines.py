import pyecharts.options as opts
from pyecharts.charts import Kline, Candlestick
import datetime
import requests

kline_cnt = 24*5

def ts2datetime(ts):
    return datetime.datetime.fromtimestamp(ts/1000).strftime('%Y-%m-%d %H:%M:%S')

def get_ohlcv_list(symbol='BTCUSDT'):
    symbol = symbol.upper()
    # 获取最近五天的BTCUSDT 30分钟K线数据
    url = 'https://api.binance.com/api/v3/klines?symbol='+ symbol +'&interval=1h&limit=' + str(kline_cnt)
    #url = 'https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=72'
    r = requests.get(url)
    ohlcv_list = r.json()
    return ohlcv_list

def draw_klines(symbol):
    ohlcv_list = get_ohlcv_list(symbol)
    filename_html = 'html/'+symbol+'.html'
    last_price = ohlcv_list[-1][4]
    x_data = []
    y_data = []
    current_utc_yyyymmddhhmmss = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    for i in range(len(ohlcv_list)):
        x_data.append(ts2datetime(ohlcv_list[i][0]))
        y_data.append([ohlcv_list[i][1],ohlcv_list[i][4],ohlcv_list[i][2],ohlcv_list[i][3]])
    c=Candlestick(init_opts=opts.InitOpts(width="1000px", height="600px")).add_xaxis(xaxis_data=x_data).add_yaxis(
        series_name="",
        y_axis=y_data,
        itemstyle_opts=opts.ItemStyleOpts(
            color="#ec0000",
            color0="#00da3c",
            border_color="#8A0000",
            border_color0="#008F28",
        ),
    ).add_xaxis(xaxis_data=x_data
    ).set_global_opts(
        xaxis_opts=opts.AxisOpts(is_scale=True),
        yaxis_opts=opts.AxisOpts(
            is_scale=True,
            splitarea_opts=opts.SplitAreaOpts(
                is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
            ),
        ),
        #datazoom_opts=[opts.DataZoomOpts(pos_bottom="-2%")],by AI纪元 
        title_opts=opts.TitleOpts(title=symbol+":"+str(last_price) + "\n"+current_utc_yyyymmddhhmmss+" UTC\nby AI纪元", pos_left="0"),
    )
    c.render(filename_html)
    return filename_html