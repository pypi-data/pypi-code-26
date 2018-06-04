# -*- coding: utf-8 -*-

import re
import pandas as pd
from pyecharts_plus import Map_Bin
import pyecharts.utils as utils


class Map_Bin_Scatter(Map_Bin):
    """
    <<< 散点图的变种 >>>
    背景是地图，中间层是方格热力图，

    注意：
        1. 添加数据时，必须先添加方格热力图，后添加散点图 （待提高）
        2. 一张图里只能有一条时间轴，方格热力图的时间轴不可以和散点图的热力图共存 （不可提高）
        3. 无论在方格热力图还是在散点图中指定了添加搜索框功能，该搜索功能既可以用于搜索方格也可以用于搜索散点
    """



    def __init__(self, title="", subtitle="", **kwargs):
        """

        :param title:
        :param subtitle:
        :param kwargs:
        """

        super(Map_Bin_Scatter, self).__init__(title, subtitle, **kwargs)

        self.my_option['binmap'] = False
        self.my_option['scatter'] = False
        self.my_option['search_box'] = False

    def add_binmap(self,
                    data_df,
                    name_col=0, lgt_col=1, lat_col=2, width_col=3, height_col=4, lightness_col=5,
                    lightness_range_fixed=True, lightness_color='pink',
                    time_line_col=None, time_line_order=None, checkpoint_symbol='circle',
                    search_box=True,
                    center=None, zoom=11, mapStyle='color',
                    **kwargs):
        """

        :param data_df: 数据中除了必须要有的6列外，还可以附带其他信息列，会在tooltip中一并展示出来
        :param name_col: 名称列位于DataFrame中的列数，方格的名称会在tooltip中第一行加粗显示（最好是唯一标识，因为搜索框内查找到第一个相同名称后就会停止）
        :param lgt_col: 经度列位于DataFrame中的列数，该经度是指方格左下角的经度（中国位于东半球北半球）
        :param lat_col: 纬度列位于DataFrame中的列数，该经度是指方格左下角的纬度
        :param width_col: 宽度列位于DataFrame中的列数，方格横向宽度换算成经度
        :param height_col: 高度列位于DataFrame中的列数，方格纵向高度换算成纬度
        :param lightness_col: visualMap数值列位于DataFrame中的列数，用于指示方格颜色深浅，该列的表头会作为visualMap组件的标题
        :param lightness_range_fixed: visualMap拖动条的范围是否固定，默认为True,固定
        :param lightness_color: 方格热力值颜色的风格，默认为粉色系，目前可选择
            pink: 粉色系
            blue: 蓝色系
            orange: 橙色系
        :param time_line_col: 时间列位于DataFrame中的列数，该列表头会作为timeline组件中label的后缀（用于展示方格热力图随时间的变化，默认没有时间轴）
        :param time_line_order: 指示时间轴的顺序，数据类型为list，应当和time_line_col内的值是一致的（这里手动指定，主要是因为如果是汉字等，比如“第一季度”“第二季度”，程序是难以自行比较时间上的先后顺序的）
        :param checkpoint_symbol: 默认为圆形，目前可选择
            circle: 圆形
            rect:
            roundRect:
            triangle:
            diamond:
            pin:
            arrow:
            cardinal: 杉树
        :param search_box: 数据类型为Bool（通过名称搜索方格的位置，默认为True带有搜索框）
        :param center: 地图初始加载时的中心点坐标，可以不指定，默认为所有方格所在区域的中心点
        :param zoom: 地图初始加载时的缩放程度
        :param mapStyle: 地图显示风格，默认为彩色的，目前可选择
            color: 彩色
            gray: 灰色
        :param kwargs: 用于传入一些Chart类指定的参数
        :return:
        """

        self.add_data(data_df,
                 name_col, lgt_col, lat_col, width_col, height_col, lightness_col,
                 lightness_range_fixed, lightness_color,
                 time_line_col, time_line_order, checkpoint_symbol,
                 search_box,
                 center, zoom, mapStyle,
                 **kwargs)

        self.my_option['binmap'] = True
        self.my_option['binmap_time_line_col'] = time_line_col
        self.my_option['search_box'] = self.my_option['search_box'] or search_box
        try:
            del self.my_option['time_line_col']  # self.add_data()中添加的，将其去除
        except:
            pass

    def add_scatter(self,
                    data_df,
                    name_col=0, lgt_col=1, lat_col=2, legend_col=3,
                    time_line_col=None, time_line_order=None, checkpoint_symbol='circle',
                    search_box=True):
        """

        :param data_df:
        :param name_col:
        :param lgt_col:
        :param lat_col:
        :param legend_col:
        :param time_line_col:
        :param time_line_order:
        :param checkpoint_symbol:
        :param search_box:
        :return:
        """

        self.my_option['scatter'] = True
        self.my_option['scatter_time_line_col'] = time_line_col
        self.my_option['search_box'] = self.my_option['search_box'] or search_box

        # 时间轴冲突性检测
        if self.my_option['binmap_time_line_col'] is not None and self.my_option['scatter_time_line_col'] is not None:
            raise Exception("timeline contradict!")

        # 没有时间轴
        if self.my_option['binmap_time_line_col'] is None and self.my_option['scatter_time_line_col'] is None:
            # 调整数据列顺序
            ignore_col_list = [lgt_col, lat_col, name_col, legend_col]
            ignore_list = data_df.columns[ignore_col_list].tolist()
            scatter_columns_list = data_df.columns.tolist()
            short_columns_list = [x for x in scatter_columns_list if x not in ignore_list]
            scatter_columns_list = ignore_list + short_columns_list  # 调换顺序后的新表头
            self.my_option['scatter_columns_list'] = scatter_columns_list
            data_df = data_df[scatter_columns_list]

            # tooltip
            def scatter_tooltip_formatter(params):
                value = params.value
                results_str = '<div style="border-bottom: 1px solid rgba(255,255,255,.3); ' \
                              'font-size: 18px;padding-bottom: 7px;margin-bottom: 7px">' + \
                              value[2] + '</div>'
                for i in range(4, len(value)):
                    results_str += scatter_columns_list[i] + '：' + value[i] + '<br>'
                return results_str

            # legend
            legends_list = data_df.iloc[:, 3].unique().tolist()
            self.my_option['scatter_group_num'] = len(legends_list)
            self._option['legend'] = {
                "data": legends_list,
                "left": 'center',
                "top": '5%',
                "borderColor": '#ccc',
                "borderWidth": 2,
            }
            # 整理分组数据
            for legend in legends_list:
                temp_data_df = data_df[data_df.iloc[:, 3] == legend]
                self._option['series'].append({
                    "name": legend,
                    "type": 'scatter',
                    "coordinateSystem": 'bmap',
                    "data": temp_data_df.values.tolist(),
                    "symbol": 'pin',
                    "symbolSize": 35,
                    "zlevel": 10,
                    # "itemStyle": {
                    #     "normal": {
                    #         "color": 'red'  # 标志颜色
                    #     },
                    # },
                    "itemStyle": {
                        "normal": {
                            "shadowBlur": 10,
                            "shadowColor": "rgba(0, 0, 0, 0.5)",
                            "shadowOffsetX": 0,
                            "opacity": 0.8,
                            "shadowOffsetY": 0
                        }
                    },
                    "tooltip": {
                        "trigger": 'item',
                        "formatter": scatter_tooltip_formatter
                    }
                })

        # 时间轴加在方格热力图上
        if self.my_option['binmap_time_line_col'] is not None:
            # 调整数据列顺序
            ignore_col_list = [lgt_col, lat_col, name_col, legend_col]
            ignore_list = data_df.columns[ignore_col_list].tolist()
            scatter_columns_list = data_df.columns.tolist()
            short_columns_list = [x for x in scatter_columns_list if x not in ignore_list]
            scatter_columns_list = ignore_list + short_columns_list  # 调换顺序后的新表头
            self.my_option['scatter_columns_list'] = scatter_columns_list
            data_df = data_df[scatter_columns_list]

            # tooltip
            def scatter_tooltip_formatter(params):
                value = params.value
                results_str = '<div style="border-bottom: 1px solid rgba(255,255,255,.3); ' \
                              'font-size: 18px;padding-bottom: 7px;margin-bottom: 7px">' + \
                              value[2] + '</div>'
                for i in range(4, len(value)):
                    results_str += scatter_columns_list[i] + '：' + value[i] + '<br>'
                return results_str

            # legend
            legends_list = data_df.iloc[:, 3].unique().tolist()
            self.my_option['scatter_group_num'] = len(legends_list)
            self._option['baseOption']['legend'] = {
                "data": legends_list,
                "left": 'center',
                "top": '5%',
                "borderColor": '#ccc',
                "borderWidth": 2,
            }
            # 整理分组数据
            temp_series = []
            for legend in legends_list:
                temp_data_df = data_df[data_df.iloc[:, 3] == legend]
                temp_series.append({
                    "name": legend,
                    "type": 'scatter',
                    "coordinateSystem": 'bmap',
                    "data": temp_data_df.values.tolist(),
                    "symbol": 'pin',
                    "symbolSize": 35,
                    "zlevel": 10,
                    # "itemStyle": {
                    #     "normal": {
                    #         "color": 'red'  # 标志颜色
                    #     },
                    # },
                    "itemStyle": {
                        "normal": {
                            "shadowBlur": 10,
                            "shadowColor": "rgba(0, 0, 0, 0.5)",
                            "shadowOffsetX": 0,
                            "opacity": 0.8,
                            "shadowOffsetY": 0
                        }
                    },
                    "tooltip": {
                        "trigger": 'item',
                        "formatter": scatter_tooltip_formatter
                    }
                })
            for temp_option in self._option["options"]:
                temp_option["series"] += temp_series


    def render(self, path="render.html", template_name="simple_chart.html", object_name="chart", **kwargs):
        """
        将图表保存成html文件，默认占满屏幕
        :param path:
        :param template_name:
        :param object_name:
        :param kwargs:
        :return:
        """

        # 这里仍然调用Chart类的render函数，在此基础上修改
        super(Map_Bin, self).render(path, "simple_chart.html", "chart", **kwargs)
        with open(path, 'r', encoding="utf-8") as file:
            cont = file.read()

        # 查找myChart的id
        temp_start, temp_end = re.search("myChart_(.*?).setOption", cont).span()
        myChart_id = cont[temp_start: temp_end].replace('myChart_', '').replace('.setOption', '')

        # 导入百度接口和bmap.js
        try:
            pos1 = re.search("<body>\n\s*<div id=", cont).span()[0] + 7
            cont = cont[: pos1] + """<script type="text/javascript" src="http://api.map.baidu.com/api?v=2.0&ak=ZUONbpqGBsYGXNIYHicvbAbM"></script>\n<script type="text/javascript" src="http://echarts.baidu.com/gallery/vendors/echarts/extension/bmap.min.js"></script>\n""" + cont[pos1:]
        except:
            pass

        # 使tooltip可以正常显示
        pos1 = re.search("myChart\w*.setOption(.*?);", cont).span()[1] + 1
        cont = cont[: pos1] + "var binmap_columns_list = {0};\nvar scatter_columns_list={1};\n".format(self.my_option['binmap_columns_list'], self.my_option['scatter_columns_list']) + cont[pos1:]

        # 使图表全屏显示
        try:
            pos2 = re.search("<html>", cont).span()[1] - 1
            cont = cont[: pos2] + ' style="height: 100%"' + cont[pos2:]
            pos2 = re.search("<body>", cont).span()[1] - 1
            cont = cont[: pos2] + ' style="height: 100%; margin: 0"' + cont[pos2:]
            pos3, pos4 = re.search('style="width:.*?;height:.*?;"', cont).span()
            cont = cont[: pos3] + ' style="width: 100%; height: 100%;"' + cont[pos4:]
        except:
            pass

        # 有搜索框
        if self.my_option['search_box']:
            # 添加搜索框和按钮
            pos5 = re.search('<div id="{0}"(.*?)></div>'.format(myChart_id), cont).span()[1] + 1
            cont = cont[: pos5] + '<div id="left-panel" style="height: 654px;position: absolute;left: 20px;top: 20px;overflow: hidden;pointer-events: none;">\n    <div id="searchbox" class="clearfix" style="border-radius: 2px;width: 425px;position: relative;z-index: 5;zoom: 1;">\n        <div id="searchbox-container" style="position: relative;z-index: 2;pointer-events: auto;width: 200px;float: left;box-sizing: border-box;box-shadow: 1px 2px 1px rgba(0, 0, 0, .15);">\n            <div id="sole-searchbox-content" class="searchbox-content" style="position: relative;width: 200px;border-radius: 2px 0 0 2px;background: #fff;">\n                <input id="sole-input" class="searchbox-content-common" placeholder="以名称定位方格、点" style="position: relative;height: 38px;box-sizing: border-box;border: 0;padding: 9px 0;border-left: 10px solid transparent;border-right: 27px solid transparent;border-radius: 2px 0 0 2px;line-height: 20px;font-size: 16px;color: #333;box-sizing: border-box;float: left; width: 200px;height: 38px;"\n                    type="text" name="word" autocomplete="off" maxlength="256">\n            </div>\n        </div>\n    </div>\n    <button id="search-button" onclick="search()" style="width: 50px;height: 38px;float: left;pointer-events: auto;background: url(http://webmap1.bdimg.com/wolfman/static/common/images/new/searchbox_f175577.png) no-repeat -3px -76px ' + self.my_option['lightness_color'][3] + ';border: 0;padding: 0;cursor: pointer;border-radius: 0 2px 2px 0;box-shadow: 1px 2px 1px rgba(0, 0, 0, .15);"></button>\n</div>\n' + cont[pos5:]

            # 没有时间轴
            if self.my_option['binmap_time_line_col'] is None and self.my_option['scatter_time_line_col'] is None:
                search_function_str = 'function search() {\n    let search_text = document.getElementById("sole-input").value;\n    let data = option_%s["series"];\n    for (var i = 0; i < data[0]["data"].length; i++) {\n        if (search_text == data[0]["data"][i][0].toString()) {\n            console.log(data[i]);\n            var pt = new BMap.Point((data[0]["data"][i][1] + data[0]["data"][i][3] / 2).toFixed(6), (data[0]["data"][i][2] + data[0]["data"][i][4] / 2).toFixed(6));\n            infoContent = "麻烦你用力<br>去吻碎<br>这相反故事";\n            var infoWindow = new BMap.InfoWindow(infoContent, infoOpts); // 创建信息窗口对象\n            bmap.openInfoWindow(infoWindow, pt); //开启信息窗口\n            return;\n        }\n    }\n    for (var i = 1; i < data.length; i++) {\n\t\tfor (var j = 0; j < data[i]["data"].length; j++) {\n\t\t\tif (search_text == data[i]["data"][j][2].toString()) {\n\t\t\t\tconsole.log(data[i]);\n\t\t\t\tvar pt = new BMap.Point(data[i]["data"][j][0].toFixed(6), data[i]["data"][j][1].toFixed(6));\n\t\t\t\tinfoContent = "麻烦你用力<br>去吻碎<br>这相反故事";\n\t\t\t\tvar infoWindow = new BMap.InfoWindow(infoContent, infoOpts); // 创建信息窗口对象\n\t\t\t\tbmap.openInfoWindow(infoWindow, pt); //开启信息窗口\n\t\t\t\treturn;\n\t\t\t}\n\t\t}\n\t}\n\tconsole.log("can\'t find");\n\talert("而事到如今\\n终于明白\\n我图里没你");\n}\n' % myChart_id
            # 时间轴加在热力图上
            if self.my_option['binmap_time_line_col'] is not None and self.my_option['scatter_time_line_col'] is None:
                search_function_str = 'function search() {\n\tlet search_text = document.getElementById("sole-input").value;\n    let current_index = myChart_%s.getOption()["timeline"][0]["currentIndex"];\n\tlet data = option_%s["options"][current_index]["series"];\n\tfor (var i = 0; i < data[0]["data"].length; i++) {\n        if (search_text == data[0]["data"][i][0].toString()) {\n            console.log(data[i]);\n            var pt = new BMap.Point((data[0]["data"][i][1] + data[0]["data"][i][3] / 2).toFixed(6), (data[0]["data"][i][2] + data[0]["data"][i][4] / 2).toFixed(6));\n            infoContent = "麻烦你用力<br>去吻碎<br>这相反故事";\n            var infoWindow = new BMap.InfoWindow(infoContent, infoOpts); // 创建信息窗口对象\n            bmap.openInfoWindow(infoWindow, pt); //开启信息窗口\n            return;\n        }\n    }\n    for (var i = 1; i < data.length; i++) {\n\t\tfor (var j = 0; j < data[i]["data"].length; j++) {\n\t\t\tif (search_text == data[i]["data"][j][2].toString()) {\n\t\t\t\tconsole.log(data[i]);\n\t\t\t\tvar pt = new BMap.Point(data[i]["data"][j][0].toFixed(6), data[i]["data"][j][1].toFixed(6));\n\t\t\t\tinfoContent = "麻烦你用力<br>去吻碎<br>这相反故事";\n\t\t\t\tvar infoWindow = new BMap.InfoWindow(infoContent, infoOpts); // 创建信息窗口对象\n\t\t\t\tbmap.openInfoWindow(infoWindow, pt); //开启信息窗口\n\t\t\t\treturn;\n\t\t\t}\n\t\t}\n\t}\n\tconsole.log("can\'t find");\n\talert("而事到如今\\n终于明白\\n我图里没你");\n}' % (myChart_id, myChart_id)
            # 时间轴加在散点图上
            if self.my_option['binmap_time_line_col'] is None and self.my_option['scatter_time_line_col'] is not None:
                pass

            # 获取地图实例、添加信息窗模板
            pos6 = re.search("myChart\w*.setOption(.*?);", cont).span()[1] + 1
            temp_str = "var bmap = myChart_{0}.getModel().getComponent('bmap').getBMap();\n".format(myChart_id)
            temp_str += 'var infoOpts = {\n    width: 50, // 信息窗口宽度\n    height: 50, // 信息窗口高度\n    // title: "信息", // 信息窗口标题\n    enableMessage: true //设置允许信息窗发送短息\n};\n'
            temp_str += search_function_str
            cont = cont[: pos6] + temp_str + cont[pos6:]


        # 保存修改后的html文件
        utils.write_utf8_html_file(path, cont)






