# ！/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/5/31 10:21
# @Author   : Run (18817363043@163.com)
# @File     : map_bin.py
# @Software : PyCharm


"""
Notes:
    1. 补充更多的颜色风格
"""


import re
import math
import pandas as pd
from pyecharts.chart import Chart
import pyecharts.utils as utils
from pyecharts_javascripthon.compat import TranslatorCompatAPI


class Map_Bin(Chart):
    """
    <<< 方格热力图 >>>
    背景是地图，根据指定指标的数值大小决定小方格内颜色深浅；
    """

    def __init__(self, title="", subtitle="", **kwargs):
        """

        :param title:
        :param subtitle:
        :param kwargs:
        """

        super(Map_Bin, self).__init__(title, subtitle, **kwargs)

        # 用于存放一些自定义的设置
        self.my_option = {}

        # python2javascript翻译器（返回的是javascript函数的字符串）
        self.translator = TranslatorCompatAPI.translate_function

    def add_data(self,
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

        '''样式库'''
        lightness_color_dict = {
            'pink': ["#ffffff", "#FFD2F7", "#FFADEB", "#FF8BE3", "#FF66DD", "#FF36D0", "#FF01C7"],
            'blue': ["#ffffff", "#b4e0f3", "#70b4eb", "#1482e5", "#1c3fbf", "#070093", "#060058"],
            'orange': ["#ffffff", "#F5E1CA", "#F5CBA3", "#F5B37C", "#F59F53", "#F58928", "#F57708"]
        }
        self.my_option['lightness_color'] = lightness_color_dict[lightness_color]
        #
        mapStyle_dict = {
            'color': {},
            'gray': {
                "styleJson": [{
                    'featureType': 'water',
                    'elementType': 'all',
                    'stylers': {
                        'color': '#d1d1d1'
                    }
                }, {
                    'featureType': 'land',
                    'elementType': 'all',
                    'stylers': {
                        'color': '#f3f3f3'
                    }
                }, {
                    'featureType': 'railway',
                    'elementType': 'all',
                    'stylers': {
                        'visibility': 'off'
                    }
                }, {
                    'featureType': 'highway',
                    'elementType': 'all',
                    'stylers': {
                        'color': '#999999'
                    }
                }, {
                    'featureType': 'highway',
                    'elementType': 'labels',
                    'stylers': {
                        'visibility': 'off'
                    }
                }, {
                    'featureType': 'arterial',
                    'elementType': 'geometry',
                    'stylers': {
                        'color': '#fefefe'
                    }
                }, {
                    'featureType': 'arterial',
                    'elementType': 'geometry.fill',
                    'stylers': {
                        'color': '#fefefe'
                    }
                }, {
                    'featureType': 'poi',
                    'elementType': 'all',
                    'stylers': {
                        'visibility': 'off'
                    }
                }, {
                    'featureType': 'green',
                    'elementType': 'all',
                    'stylers': {
                        'visibility': 'off'
                    }
                }, {
                    'featureType': 'subway',
                    'elementType': 'all',
                    'stylers': {
                        'visibility': 'off'
                    }
                }, {
                    'featureType': 'manmade',
                    'elementType': 'all',
                    'stylers': {
                        'color': '#d1d1d1'
                    }
                }, {
                    'featureType': 'local',
                    'elementType': 'all',
                    'stylers': {
                        'color': '#d1d1d1'
                    }
                }, {
                    'featureType': 'arterial',
                    'elementType': 'labels',
                    'stylers': {
                        'visibility': 'off'
                    }
                }, {
                    'featureType': 'boundary',
                    'elementType': 'all',
                    'stylers': {
                        'color': '#fefefe'
                    }
                }, {
                    'featureType': 'building',
                    'elementType': 'all',
                    'stylers': {
                        'color': '#d1d1d1'
                    }
                }, {
                    'featureType': 'label',
                    'elementType': 'labels.text.fill',
                    'stylers': {
                        'color': 'rgba(0,0,0,0)'
                    }
                }]
            }
        }
        #
        checkpoint_symbol_dict = {
            'circle': 'circle',
            'rect': 'rect',
            'roundRect': 'roundRect',
            'triangle': 'triangle',
            'diamond': 'diamond',
            'pin': 'pin',
            'arrow': 'arrow',
            'cardinal': 'image://https://unicorn-rel.oss-cn-beijing.aliyuncs.com/media/img/algorithm/favicon.ico'
        }
        checkpoint_symbol = checkpoint_symbol_dict[checkpoint_symbol]

        self.my_option['time_line_col'] = time_line_col
        self.my_option['search_box'] = search_box

        def renderItem(params, api):
            pointLeftBottom = api.coord([api.value(1), api.value(2)])
            pointRightTop = api.coord([api.value(1) + api.value(3), api.value(2) + api.value(4)])
            results = {
                'type': 'rect',
                'shape': {
                    'x': pointLeftBottom[0],
                    'y': pointLeftBottom[1],
                    'width': pointRightTop[0] - pointLeftBottom[0],
                    'height': pointRightTop[1] - pointLeftBottom[1]
                },
                'style': api.style({
                    'stroke': 'rgba(0,0,0,0.1)'
                }),
                'styleEmphasis': api.styleEmphasis()
            }
            return results

        # 数据去重
        data_df = data_df.drop_duplicates().reset_index(drop=True)

        if time_line_col is None:
            '''没有时间轴'''

            # 调整数据列顺序
            ignore_col_list = [name_col, lgt_col, lat_col, width_col, height_col, lightness_col]
            ignore_list = data_df.columns[ignore_col_list].tolist()
            binmap_columns_list = data_df.columns.tolist()
            short_columns_list = [x for x in binmap_columns_list if x not in ignore_list]
            binmap_columns_list = ignore_list + short_columns_list  # 调换顺序后的新表头
            self.my_option['binmap_columns_list'] = binmap_columns_list
            data_df = data_df[binmap_columns_list]

            # 确定各维度范围
            lgt_max = data_df.iloc[:, 1].max()
            lgt_min = data_df.iloc[:, 1].min()
            lat_max = data_df.iloc[:, 2].max()
            lat_min = data_df.iloc[:, 2].min()
            lightness_max = data_df.iloc[:, 5].max()
            lightness_min = data_df.iloc[:, 5].min()
            lightness_range = lightness_max - lightness_min
            lightness_max = math.ceil(lightness_max + 0.05 * lightness_range)
            lightness_min = math.floor(lightness_min - 0.05 * lightness_range)

            # 确定地图中心点
            if center is None:
                center = [(lgt_max + lgt_min) / 2, (lat_max + lat_min) / 2]
            # bmap
            self._option['bmap'] = {
                'center': center,
                'zoom': zoom,
                'roam': True,
                'mapStyle': mapStyle_dict[mapStyle]
            }

            # toolbox（默认不显示工具箱）
            try:
                if 'is_toolbox_show' not in kwargs:
                    self._option.pop('toolbox')
                elif not kwargs['is_toolbox_show']:
                    self._option.pop('toolbox')
                else:
                    pass
            except:
                pass

            # visualMap
            self._option['visualMap'] = [
                {
                    'text': [binmap_columns_list[5]],
                    'type': 'continuous',
                    'seriesIndex': [0],
                    'dimension': 5,
                    'min': lightness_min,
                    'max': lightness_max,
                    'left': 10,
                    'top': "50%",
                    'textGap': 30,
                    'textStyle': {
                        'color': '#333'
                    },
                    "backgroundColor": "#f4f4f4",
                    "borderColor": "#e3e3e3",
                    "borderWidth": 2,
                    "contentColor": "#5793f3",
                    'calculable': True,
                    'precision': 0.1,
                    'inRange': {
                        "color": lightness_color_dict[lightness_color],
                        'opacity': 0.6
                    }
                }
            ]

            # tooltip
            def tooltip_formatter(params):
                value = params.value
                results_str = '<div style="border-bottom: 1px solid rgba(255,255,255,.3); ' \
                              'font-size: 18px;padding-bottom: 7px;margin-bottom: 7px">' + \
                              value[0] + '</div>'
                for i in range(5, len(value)):
                    results_str += binmap_columns_list[i] + '：' + value[i] + '<br>'
                return results_str

            #
            self._option['tooltip'] = [{}]  # 如果不加这个，方格的tooltip无法正常显示

            # series
            self._option['series'] = [{
                'type': 'custom',
                'coordinateSystem': 'bmap',
                'data': data_df.values.tolist(),
                'renderItem': renderItem,
                'animation': False,
                'itemStyle': {
                    'emphasis': {
                        'color': 'yellow'
                    }
                },
                "tooltip": {
                    'padding': 10,
                    'backgroundColor': "rgba(50,50,50,0.7)",
                    'borderColor': '#777',
                    'borderWidth': 1,
                    'formatter': tooltip_formatter
                }
                # 'encode': {
                #     'tooltip': [0, 1, 2]
                # }
            }]


            # if search_box:
            #     # 只有搜索框、没有时间轴
            #     pass
            # else:
            #     # 搜索框和时间轴都不要
            #     pass

        else:
            '''带有时间轴'''

            # title = self._option.get('title')

            self._option = {
                'baseOption': {
                    "timeline": {
                        "show": True,
                        "bottom": 0,
                        "left": "10%",
                        "axisType": "category",
                        "autoPlay": True,
                        "playInterval": 1000,
                        "loop": True,
                        "symbol": "emptyCircle",
                        "symbolSize": 10,
                        "rewind": False,  # 表示是否反向传播
                        "label": {
                            "normal": {
                                "show": True,
                                "interval": 'auto'
                            },
                        },
                        "tooltip": {
                            "show": False
                        },
                        "checkpointStyle": {
                            "symbol": checkpoint_symbol,
                            "symbolSize": 15,
                            "color": lightness_color_dict[lightness_color][-1],
                            "borderWidth": 2,
                            "borderColor": lightness_color_dict[lightness_color][2]
                        }
                    },
                    "tooltip": [{}],
                    "bmap": {
                        "zoom": zoom,
                        "roam": True,
                        'mapStyle': mapStyle_dict[mapStyle]
                    }
                },
                'options': []
            }

            # 调整数据列顺序
            ignore_col_list = [name_col, lgt_col, lat_col, width_col, height_col, lightness_col, time_line_col]
            ignore_list = data_df.columns[ignore_col_list].tolist()
            binmap_columns_list = data_df.columns.tolist()
            short_columns_list = [x for x in binmap_columns_list if x not in ignore_list]
            binmap_columns_list = ignore_list + short_columns_list  # 调换顺序后的新表头
            self.my_option['binmap_columns_list'] = binmap_columns_list
            data_df = data_df[binmap_columns_list]

            # 整理时间轴顺序
            time_line = data_df.iloc[:, 6].unique().tolist()
            time_line.sort()
            if time_line_order is None:
                time_line_order = time_line
            else:
                if set(time_line_order) != set(time_line):
                    raise Exception("时间轴顺序和时间轴列的值不一致！")
            # 全体数据的lightness的范围
            lightness_max = data_df.iloc[:, 5].max()
            lightness_min = data_df.iloc[:, 5].min()
            lightness_range = lightness_max - lightness_min
            lightness_max = math.ceil(lightness_max + 0.05 * lightness_range)
            lightness_min = math.floor(lightness_min - 0.05 * lightness_range)

            # tooltip
            def tooltip_formatter_with_timeline(params):
                value = params.value
                results_str = '<div style="border-bottom: 1px solid rgba(255,255,255,.3); ' \
                              'font-size: 18px;padding-bottom: 7px;margin-bottom: 7px">' + \
                              value[0] + '</div>' + binmap_columns_list[5] + '：' + value[5] + '<br>'
                for i in range(7, len(value)):
                    results_str += binmap_columns_list[i] + '：' + value[i] + '<br>'
                return results_str

            # 整理分组数据
            for time_point in time_line_order:
                temp_data_df = data_df[data_df.iloc[:, 6] == time_point]

                if not lightness_range_fixed:
                    lightness_max = temp_data_df.iloc[:, 5].max()
                    lightness_min = temp_data_df.iloc[:, 5].min()
                    lightness_range = lightness_max - lightness_min
                    lightness_max = math.ceil(lightness_max + 0.05 * lightness_range)
                    lightness_min = math.floor(lightness_min - 0.05 * lightness_range)

                # 确定地图中心点（以第一个时间点的中心为地图中心，播放时间轴时不变动该中心位置）
                if center is None:
                    lgt_max = temp_data_df.iloc[:, 1].max()
                    lgt_min = temp_data_df.iloc[:, 1].min()
                    lat_max = temp_data_df.iloc[:, 2].max()
                    lat_min = temp_data_df.iloc[:, 2].min()
                    center = [(lgt_max + lgt_min) / 2, (lat_max + lat_min) / 2]

                self._option['options'].append({
                    "series": [
                        {
                            'type': 'custom',
                            'coordinateSystem': 'bmap',
                            'data': temp_data_df.values.tolist(),
                            'renderItem': renderItem,
                            'animation': False,
                            'itemStyle': {
                                'emphasis': {
                                    'color': 'yellow'
                                }
                            },
                            "tooltip": {
                                'padding': 10,
                                'backgroundColor': "rgba(50,50,50,0.7)",
                                'borderColor': '#777',
                                'borderWidth': 1,
                                'formatter': tooltip_formatter_with_timeline
                            }
                        }
                    ],
                    "visualMap": [
                        {
                            "text": [binmap_columns_list[5]],
                            "max": lightness_max,
                            "min": lightness_min,
                            'type': 'continuous',
                            'seriesIndex': [0],
                            'dimension': 5,
                            'left': 10,
                            'top': "50%",
                            'textGap': 30,
                            'textStyle': {
                                'color': '#333'
                            },
                            "backgroundColor": "#f4f4f4",
                            "borderColor": "#e3e3e3",
                            "borderWidth": 2,
                            "contentColor": "#5793f3",
                            'calculable': True,
                            'precision': 0.1,
                            'inRange': {
                                "color": lightness_color_dict[lightness_color],
                                'opacity': 0.6
                            }
                        }
                    ]
                })

            # bmap设置地图中心点
            self._option['baseOption']['bmap']['center'] = center

            # timeline
            self._option['baseOption']['timeline']['data'] = time_line_order
            self._option['baseOption']['timeline']['label']['normal']['formatter'] = '{value}' + binmap_columns_list[6]

            if search_box:
                # 既有搜索框、也有时间轴
                pass
            else:
                # 只有时间轴、没有搜索框
                pass

    def render(self, path="render.html", template_name="simple_chart.html", object_name="chart", **kwargs):
        """
        将图表保存成html文件，默认占满屏幕
        :param path:
        :param template_name:
        :param object_name:
        :param kwargs:
        :return:
        """

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
        cont = cont[: pos1] + "var binmap_columns_list = {0};\n".format(self.my_option['binmap_columns_list']) + cont[pos1:]

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

        if self.my_option['search_box']:
            # 添加搜索框和按钮
            pos5 = re.search('<div id="{0}"(.*?)></div>'.format(myChart_id), cont).span()[1] + 1
            cont = cont[: pos5] + '<div id="left-panel" style="height: 654px;position: absolute;left: 20px;top: 20px;overflow: hidden;pointer-events: none;">\n    <div id="searchbox" class="clearfix" style="border-radius: 2px;width: 425px;position: relative;z-index: 5;zoom: 1;">\n        <div id="searchbox-container" style="position: relative;z-index: 2;pointer-events: auto;width: 200px;float: left;box-sizing: border-box;box-shadow: 1px 2px 1px rgba(0, 0, 0, .15);">\n            <div id="sole-searchbox-content" class="searchbox-content" style="position: relative;width: 200px;border-radius: 2px 0 0 2px;background: #fff;">\n                <input id="sole-input" class="searchbox-content-common" placeholder="以名称定位方格、点" style="position: relative;height: 38px;box-sizing: border-box;border: 0;padding: 9px 0;border-left: 10px solid transparent;border-right: 27px solid transparent;border-radius: 2px 0 0 2px;line-height: 20px;font-size: 16px;color: #333;box-sizing: border-box;float: left; width: 200px;height: 38px;"\n                    type="text" name="word" autocomplete="off" maxlength="256">\n            </div>\n        </div>\n    </div>\n    <button id="search-button" onclick="search()" style="width: 50px;height: 38px;float: left;pointer-events: auto;background: url(http://webmap1.bdimg.com/wolfman/static/common/images/new/searchbox_f175577.png) no-repeat -3px -76px ' + self.my_option['lightness_color'][3] + ';border: 0;padding: 0;cursor: pointer;border-radius: 0 2px 2px 0;box-shadow: 1px 2px 1px rgba(0, 0, 0, .15);"></button>\n</div>\n' + cont[pos5:]

            if self.my_option['time_line_col'] is None:
                search_function_str = 'function search() {\n    let search_text = document.getElementById("sole-input").value;\n    let data = option_%s["series"][0]["data"];\n    let flag = false;\n    for (var i = 0; i < data.length; i++) {\n        if (search_text == data[i][0].toString()) {\n            console.log(data[i]);\n            var pt = new BMap.Point((data[i][1] + data[i][3] / 2).toFixed(6), (data[i][2] + data[i][4] / 2).toFixed(6));\n            infoContent = "麻烦你用力<br>去吻碎<br>这相反故事";\n            var infoWindow = new BMap.InfoWindow(infoContent, infoOpts); // 创建信息窗口对象\n            bmap.openInfoWindow(infoWindow, pt); //开启信息窗口\n            flag = true;\n            break;\n        }\n    }\n    if (!flag) {\n        console.log("can\'t find");\n        alert("而事到如今\\n终于明白\\n我图里没你");\n    }\n}\n' % myChart_id
            else:
                search_function_str = 'function search() {\n    let search_text = document.getElementById("sole-input").value;\n    let current_index = myChart_%s.getOption()["timeline"][0]["currentIndex"];\n    let data = option_%s["options"][current_index]["series"][0]["data"];\n    let flag = false;\n    for (var i = 0; i < data.length; i++) {\n        if (search_text == data[i][0].toString()) {\n            console.log(data[i]);\n            var pt = new BMap.Point((data[i][1] + data[i][3] / 2).toFixed(6), (data[i][2] + data[i][4] / 2).toFixed(6));\n            infoContent = "麻烦你用力<br>去吻碎<br>这相反故事";\n            var infoWindow = new BMap.InfoWindow(infoContent, infoOpts); // 创建信息窗口对象\n            bmap.openInfoWindow(infoWindow, pt); //开启信息窗口\n            flag = true;\n            break;\n        }\n    }\n    if (!flag) {\n        console.log("can\'t find");\n        alert("而事到如今\\n终于明白\\n我图里没你");\n    }\n}\n' % (myChart_id, myChart_id)

            # 获取地图实例、添加信息窗模板
            pos6 = re.search("myChart\w*.setOption(.*?);", cont).span()[1] + 1
            temp_str = "var bmap = myChart_{0}.getModel().getComponent('bmap').getBMap();\n".format(myChart_id)
            temp_str += 'var infoOpts = {\n    width: 50, // 信息窗口宽度\n    height: 50, // 信息窗口高度\n    // title: "信息", // 信息窗口标题\n    enableMessage: true //设置允许信息窗发送短息\n};\n'
            temp_str += search_function_str
            cont = cont[: pos6] + temp_str + cont[pos6: ]


        # 保存修改后的html文件
        utils.write_utf8_html_file(path, cont)
