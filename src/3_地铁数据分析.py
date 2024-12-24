import jieba
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Geo, Bar, Pie, Scatter
from wordcloud import WordCloud


# 设置列名与数据对齐
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
# 显示10行
pd.set_option('display.max_rows', 10)


def read_data():
    """
    读取地铁数据文件
    """
    try:
        df = pd.read_csv('../data/subway.csv', header=None, names=['city', 'line', 'station'], encoding='utf8')
        return df
    except FileNotFoundError:
        print("数据文件未找到，请检查文件路径是否正确。")
        return None


def remove_duplicate_stations(df):
    """
    去除重复换乘站的地铁数据
    """
    return df.groupby(['city', 'station']).count().reset_index()


def all_np(arr):
    """
    统计单字频率
    """
    arr = np.array(arr)
    key = np.unique(arr)
    result = {}
    for k in key:
        mask = (arr == k)
        arr_new = arr[mask]
        v = arr_new.size
        result[k] = v
    return result


def create_map(df_city):
    """
    绘制地图展示已开通地铁城市分布情况
    """
    c = (
        Geo()
     .add_schema(maptype="china")
     .add("", [list(z) for z in zip(df_city['city'], df_city['line'])], type_="effectScatter", symbol_size=15)
     .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
     .set_global_opts(
            title_opts=opts.TitleOpts(title="已开通地铁城市分布情况", pos_left="center", pos_top="0",
                                      title_textstyle_opts=opts.TextStyleOpts(color="#fff")),
            visualmap_opts=opts.VisualMapOpts(is_show=True, min_=0, max_=25, range_text=["", ""],
                                              textstyle_opts=opts.TextStyleOpts(color="#fff"), pos_left="left",
                                              pos_bottom="bottom"),
            graphic_opts=[
                opts.GraphicGroup(
                    graphic_item=opts.GraphicItem(
                        left="center", top="center", bounding="raw", z=100
                    )
                )
            ]
        )
    )
    c.render("../res/已开通地铁城市分布情况.html")


def create_line_chart(df_city):
    """
    生成城市地铁线路数量分布情况柱状图
    """
    if df_city.empty:
        print("数据为空，无法绘制城市地铁线路数量分布情况柱状图，请检查数据。")
        return
    title_len = df_city['line']
    bins = [0, 5, 10, 15, 20, 25]
    level = ['0-5', '5-10', '10-15', '15-20', '20以上']
    len_stage = pd.cut(title_len, bins=bins, labels=level).value_counts().sort_index()
    bar = (
        Bar()
     .add_xaxis(list(len_stage.index))
     .add_yaxis("", list(len_stage.values))
     .set_global_opts(
            title_opts=opts.TitleOpts(title="各城市地铁线路数量分布", pos_left="center", pos_top="18"),
            xaxis_opts=opts.AxisOpts(name="线路数量区间"),
            yaxis_opts=opts.AxisOpts(name="城市数量"),
            graphic_opts=[
                opts.GraphicGroup(
                    graphic_item=opts.GraphicItem(
                        left="center", top="center", bounding="raw", z=100
                    )
                )
            ]
        )
    )
    bar.render("../res/各城市地铁线路数量分布.html")


def create_wordcloud(df_station):
    """
    生成地铁名词云
    """
    text = ''
    for line in df_station['station']:
        text += ' '.join(jieba.cut(line, cut_all=False))
        text += ' '

    wc = WordCloud(
        background_color='white',
        font_path='STXINGKA.TTF',
        max_words=1000,
        max_font_size=150,
        min_font_size=15,
        prefer_horizontal=1,
        random_state=50,
    )
    wc.generate(text)
    process_word = WordCloud.process_text(wc, text)
    sort = sorted(process_word.items(), key=lambda e: e[1], reverse=True)
    print(sort[:50])
    plt.imshow(wc)
    plt.axis('off')
    wc.to_file("../res/地铁名词云.jpg")
    print('生成词云成功!')


def create_word_frequency_chart(word_message):
    """
    生成柱状图展示中国地铁站最爱用的字
    """
    if not word_message:
        print("数据为空，无法生成柱状图展示中国地铁站最爱用的字，请检查数据。")
        return
    bar = (
        Bar()
     .add_xaxis([j[0] for j in word_message])
     .add_yaxis("", [j[1] for j in word_message])
     .set_global_opts(
            title_opts=opts.TitleOpts(title="中国地铁站最爱用的字", pos_left="center", pos_top="18"),
            xaxis_opts=opts.AxisOpts(name="汉字"),
            yaxis_opts=opts.AxisOpts(name="出现次数"),
            graphic_opts=[
                opts.GraphicGroup(
                    graphic_item=opts.GraphicItem(
                        left="center", top="center", bounding="raw", z=100
                    )
                )
            ]
        )
    )
    bar.render("../res/中国地铁站最爱用的字.html")


def create_door_chart(df2):
    """
    生成柱状图展示地铁站最爱用“门”命名的城市
    """
    if df2.empty:
        print("数据为空，无法生成柱状图展示地铁站最爱用“门”命名的城市，请检查数据。")
        return
    bar = (
        Bar()
     .add_xaxis([j for j in df2['city'][:5]])
     .add_yaxis("", [j for j in df2['line'][:5]])
     .set_global_opts(
            title_opts=opts.TitleOpts(title="地铁站最爱用门命名的城市", pos_left="center", pos_top="18"),
            yaxis_opts=opts.AxisOpts(max_=40),
            xaxis_opts=opts.AxisOpts(name="城市"),
            graphic_opts=[
                opts.GraphicGroup(
                    graphic_item=opts.GraphicItem(
                        left="center", top="center", bounding="raw", z=100
                    )
                )
            ]
        )
    )
    bar.render("../res/地铁站最爱用门命名的城市.html")


def create_city_line_station_trend_charts(city, df):
    """
    生成各城市特定线路站点数量分布可视化（柱状图）
    """
    df_city_data = df[df['city'] == city]
    if df_city_data.empty:
        print(f"{city} 数据为空，无法生成各城市特定线路站点数量分布可视化，请检查数据。")
        return
    station_count = df_city_data['line'].value_counts()
    line_data = list(station_count[:32].index)
    bar = (
        Bar()
     .add_xaxis(line_data)
     .add_yaxis("", list(station_count[:32]))
     .set_global_opts(
            title_opts=opts.TitleOpts(title=f"{city}各线路站点数量的分布趋势", pos_left="center", pos_top="18"),
            xaxis_opts=opts.AxisOpts(name="线路"),
            yaxis_opts=opts.AxisOpts(name="站点数量"),
            graphic_opts=[
                opts.GraphicGroup(
                    graphic_item=opts.GraphicItem(
                        left="center", top="center", bounding="raw", z=100
                    )
                )
            ]
        )
    )
    bar.render("../res/" + f"{city}各线路站点数量的分布趋势.html")


def create_city_station_count_pie_chart(df):
    """
    生成各个城市的站点数量的饼状图分布
    """
    df_station_count = remove_duplicate_stations(df).groupby(['city']).count().reset_index().sort_values(by='station',
                                                                                                      ascending=False)
    if df_station_count.empty:
        print("数据为空，无法生成各个城市的站点数量的饼状图分布，请检查数据。")
        return
    df_station_count['city_label'] = df_station_count['city'] + '(站点数' + df_station_count['station'].astype(str) + ')'
    pie_station = (
        Pie()
     .add("", [list(z) for z in zip(df_station_count['city_label'], df_station_count['station'])])
     .set_global_opts(
            title_opts=opts.TitleOpts(title="各个城市的站点数量的饼状图分布", pos_left="center", pos_top="18"),
            legend_opts=opts.LegendOpts(orient="vertical", pos_left="left", pos_top="middle"),
            graphic_opts=[
                opts.GraphicGroup(
                    graphic_item=opts.GraphicItem(
                        left="center", top="center", bounding="raw", z=100
                    )
                )
            ]
        )
     .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {d}%"))
    )
    pie_station.render("../res/各个城市的站点数量的饼状图分布.html")


def create_city_station_count_scatter_chart(df):
    """
    生成各个城市的站点数量的散点图分布
    """
    df_station_count = remove_duplicate_stations(df).groupby(['city']).count().reset_index().sort_values(by='station',
                                                                                                      ascending=False)
    if df_station_count.empty:
        print("数据为空，无法生成各个城市的站点数量的散点图分布，请检查数据。")
        return
    scatter = (
        Scatter()
     .add_xaxis(list(df_station_count['city']))
     .add_yaxis("", list(df_station_count['station']))
     .set_global_opts(
            title_opts=opts.TitleOpts(title="各个城市的站点数量的散点图分布", pos_left="center", pos_top="18"),
            xaxis_opts=opts.AxisOpts(name="城市"),
            yaxis_opts=opts.AxisOpts(name="站点数量"),
            graphic_opts=[
                opts.GraphicGroup(
                    graphic_item=opts.GraphicItem(
                        left="center", top="center", bounding="raw", z=100
                    )
                )
            ]
        )
    )
    scatter.render("../res/各个城市的站点数量的散点图分布.html")


def create_transit_station_count_chart(df):
    """
    生成全国各城市总的换乘站点数量（2换乘、3换乘、4换乘等）分布统计（柱状图）
    """
    df_1 = remove_duplicate_stations(df)
    df_1 = df_1[df_1['line'] > 1]
    if df_1.empty:
        print("数据为空，无法生成全国各城市总的换乘站点数量（2换乘、3换乘、4换乘等）分布统计，请检查数据。")
        return
    tran_sit = df_1.groupby('line').count().reset_index()
    bar_tran_sit = (
        Bar()
     .add_xaxis(list( tran_sit['line']))
     .add_yaxis("", list( tran_sit['station']))
     .set_global_opts(
            title_opts=opts.TitleOpts(title="全国各城市总的换乘站点数量（2换乘、3换乘、4换乘等）分布统计", pos_left="center",
                                      pos_top="18"),
            xaxis_opts=opts.AxisOpts(name="站点可换乘等级"),
            yaxis_opts=opts.AxisOpts(name="站点数量"),
            graphic_opts=[
                opts.GraphicGroup(
                    graphic_item=opts.GraphicItem(
                        left="center", top="center", bounding="raw", z=100
                    )
                )
            ]
        )
    )
    bar_tran_sit.render("../res/全国各城市总的换乘站点数量（2换乘、3换乘、4换乘等）分布统计.html")


if __name__ == "__main__":
    df = read_data()
    if df is not None:
        # 各个城市地铁线路情况
        df_line = df.groupby(['city', 'line']).count().reset_index()

        # 各个城市地铁线路数
        df_city = df_line.groupby(['city']).count().reset_index().sort_values(by='line', ascending=False)

        # 绘制地图
        create_map(df_city)

        # 去除重复换乘站的地铁数据
        df_station = remove_duplicate_stations(df)

        # 生成地铁名词云
        create_wordcloud(df_station)

        words = []
        for line in df['station']:
            for char in line:
                words.append(char)
        word = all_np(words)
        word_message = sorted(word.items(), key=lambda x: x[1], reverse=True)[:10]
        # 生成柱状图展示中国地铁站最爱用的字
        create_word_frequency_chart(word_message)

        # 对地铁站名字包含“门”的数据进行处理和可视化
        df1_door = df_station[df_station['station'].str.contains('门')]
        df2_door = df1_door.groupby(['city']).count().reset_index().sort_values(by='line', ascending=False)
        create_door_chart(df2_door)

        # 各城市特定线路站点数量分布可视化（以下为示例，多个城市重复代码，可考虑进一步优化封装）
        cities = ['北京', '天津']
        for city in cities:
            create_city_line_station_trend_charts(city, df)

        # 各个城市的站点数量的饼状图分布
        create_city_station_count_pie_chart(df)

        # 各个城市的站点数量的散点图分布
        create_city_station_count_scatter_chart(df)

        # 全国各城市总的换乘站点数量（2换乘、3换乘、4换乘等）分布统计（柱状图）
        create_transit_station_count_chart(df)