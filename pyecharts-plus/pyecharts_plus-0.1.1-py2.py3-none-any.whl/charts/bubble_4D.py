# -*- coding: utf-8 -*-

import re
import math
import pandas as pd
from pyecharts.chart import Chart
from pyecharts.charts.scatter import Scatter
from pyecharts.conf import CURRENT_CONFIG
import pyecharts.engine as engine
import pyecharts.constants as constants
import pyecharts.utils as utils


class Bubble_4D(Scatter):
    """
    <<< 多维信息气泡图 >>>
    直角坐标系上的散点图（Scatter）的变种，用来展现数据的 x，y 之间的关系，并分别通过圆形的大小、阴影深浅展示另两个维度的信息。
    """

    def __init__(self, title="", subtitle="", **kwargs):
        """

        notes:
            1. 考虑增加参数`theme`，指定使用某套预设的主题，如背景色、数据组颜色等

        :param title:
        :param subtitle:
        :param kwargs:
        """

        super(Bubble_4D, self).__init__(title, subtitle, **kwargs)

        self._option["backgroundColor"] = "#404a59"  # 为图表更改默认的背景色
        # 直角坐标系内绘图网格
        self._option['grid'] = {
                                   'x': '10%',
                                   'x2': 150,
                                   'y': '18%',
                                   'y2': '10%'
                               }
        # 预设足够的色彩，防止不同的数据组重色
        self._option['color'] = ['#AC4343', '#8E323D', '#0CAAF3', '#2788FF', '#3B4CD0', '#745CD9', '#1C6FD4', '#077F9D',
                                 '#8DBD5E', '#45B194', '#7A574A', '#1A8C82', '#DC5FDA', '#AC62C7', '#584389', '#B4665C',
                                 '#E4B324', '#FFA324', '#C85948']

        # 用于存放一些自定义的设置
        self.my_option = {}
        self.my_option['color'] = ['#AC4343', '#8E323D', '#0CAAF3', '#2788FF', '#3B4CD0', '#745CD9', '#1C6FD4', '#077F9D',
                                 '#8DBD5E', '#45B194', '#7A574A', '#1A8C82', '#DC5FDA', '#AC62C7', '#584389', '#B4665C',
                                 '#E4B324', '#FFA324', '#C85948']

    def add_data(self, data_df,
                 x_col=0, y_col=1, size_col=2, lightness_col=3, name_col=4, legend_col=None,
                 tooltip_show='full',
                 **kwargs):
        """
        :param data_df:
        :param x_col:
        :param y_col:
        :param size_col:
        :param lightness_col:
        :param name_col: 单点名称所在的列
        :param legend_col: 表示图例分组所在的列
        :param tooltip_show: tooltip提示信息内是否展示名称列及四个数据维度，默认为'full'
            'full': 全部展示
            'part': 不展示4个数据维度及legend列
        :param kwargs:
        :return:
        """

        # 数据去重
        data_df = data_df.drop_duplicates().reset_index(drop=True)

        # 确定各维度范围
        x_max = data_df.iloc[:, x_col].max()
        x_min = data_df.iloc[:, x_col].min()
        x_range = x_max - x_min
        x_max = math.ceil(x_max + 0.05 * x_range)
        x_min = math.floor(x_min - 0.05 * x_range)
        #
        # y_max = data_df.iloc[:, y_col].max()
        # y_min = data_df.iloc[:, y_col].min()
        # y_range = y_max - y_min
        # y_max = math.ceil(y_max + 0.05 * y_range)
        # y_min = math.floor(y_min - 0.05 * y_range)
        #
        size_max = data_df.iloc[:, size_col].max()
        size_min = data_df.iloc[:, size_col].min()
        size_range = size_max - size_min
        size_max = math.ceil(size_max + 0.05 * size_range)
        size_min = math.floor(size_min - 0.05 * size_range)
        #
        lightness_max = data_df.iloc[:, lightness_col].max()
        lightness_min = data_df.iloc[:, lightness_col].min()
        lightness_range = lightness_max - lightness_min
        lightness_max = math.ceil(lightness_max + 0.05 * lightness_range)
        lightness_min = math.floor(lightness_min - 0.05 * lightness_range)

        # 调整数据列顺序
        if legend_col is None:
            ignore_col_list = [x_col, y_col, size_col, lightness_col, name_col]
        else:
            ignore_col_list = [x_col, y_col, size_col, lightness_col, name_col, legend_col]
        ignore_list = data_df.columns[ignore_col_list].tolist()
        columns_list = data_df.columns.tolist()
        short_columns_list = [x for x in columns_list if x not in ignore_list]
        columns_list = ignore_list + short_columns_list  # 调换顺序后的新表头
        self.my_option['columns_list'] = columns_list
        data_df = data_df[columns_list]

        # xAxis
        self._option['xAxis'] = [{
            'name': columns_list[0],
            'show': True,
            'inverse': False,
            'type': 'value',
            'min': x_min,
            'max': x_max,
            'nameLocation': 'end',
            'nameGap': 20,
            'nameTextStyle': {
                'color': '#fff',
                'fontSize': 16
            },
            'splitLine': {
                'show': False
            },
            'axisLine': {
                'lineStyle': {
                    'color': '#eee'
                }
            }
        }]
        # yAxis
        self._option['yAxis'] = [{
            'name': columns_list[1],
            'show': True,
            'inverse': False,
            'type': 'value',
            'nameLocation': 'end',
            'nameGap': 20,
            'nameTextStyle': {
                'color': '#fff',
                'fontSize': 16
            },
            'splitLine': {
                'show': False
            },
            'axisLine': {
                'lineStyle': {
                    'color': '#eee'
                }
            }
        }]

        # tooltip
        def tooltip_formatter1(params):
            value = params.value
            results_str = '<div style="border-bottom: 1px solid rgba(255,255,255,.3); ' \
                          'font-size: 18px;padding-bottom: 7px;margin-bottom: 7px">' + \
                          value[4] + '</div>'
            for i in range(len(value)):
                if i != 4:
                    results_str += columns_list[i] + '：' + value[i] + '<br>'
            return results_str
        #
        def tooltip_formatter2(params):
            value = params.value
            results_str = '<div style="border-bottom: 1px solid rgba(255,255,255,.3); ' \
                          'font-size: 18px;padding-bottom: 7px;margin-bottom: 7px">' + \
                          value[4] + '</div>'
            for i in range(5, len(value)):
                results_str += columns_list[i] + '：' + value[i] + '<br>'
            return results_str
        #
        def tooltip_formatter3(params):
            value = params.value
            results_str = '<div style="border-bottom: 1px solid rgba(255,255,255,.3); ' \
                          'font-size: 18px;padding-bottom: 7px;margin-bottom: 7px">' + \
                          value[4] + '</div>'
            for i in range(6, len(value)):
                results_str += columns_list[i] + '：' + value[i] + '<br>'
            return results_str
        #
        self._option['tooltip'] = {
            'padding': 10,
            'backgroundColor': '#222',
            'borderColor': '#777',
            'borderWidth': 1
        }
        if tooltip_show == 'full':
            self._option['tooltip']['formatter'] = tooltip_formatter1
        elif tooltip_show == 'part':
            if legend_col is None:
                self._option['tooltip']['formatter'] = tooltip_formatter2
            else:
                self._option['tooltip']['formatter'] = tooltip_formatter3
        else:
            raise Exception("please correct [tooltip_show]")


        # # 这种手段似乎重置了预设颜色，所以再次进行设置
        # self._option['color'] = self.my_option['color']

        if legend_col is None:
            self._option['series'] = [{
                    'data': data_df.values.tolist(),
                    'type': 'scatter',
                    'itemStyle': {
                        'normal': {
                            'opacity': 0.8,
                            'shadowBlur': 10,
                            'shadowOffsetX': 0,
                            'shadowOffsetY': 0,
                            'shadowColor': 'rgba(0, 0, 0, 0.5)'
                        }
                    }
                }]
        else:
            legends = data_df.iloc[:, legend_col].unique().tolist()
            # legend
            self._option['legend'] = [{
                'data': legends,
                'textStyle': {
                    'color': '#fff',
                    'fontSize': 16
                }
            }]
            # series
            self._option['series'] = []
            for legend in legends:
                self._option['series'].append({
                    'name': legend,
                    'data': data_df[data_df.iloc[:, 5] == legend].values.tolist(),
                    'type': 'scatter',
                    'itemStyle': {
                        'normal': {
                            'opacity': 0.8,
                            'shadowBlur': 10,
                            'shadowOffsetX': 0,
                            'shadowOffsetY': 0,
                            'shadowColor': 'rgba(0, 0, 0, 0.5)'
                        }
                    }
                })

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
                'text': ['圆形大小：{0}'.format(columns_list[2])],
                'textGap': 30,
                'textStyle': {
                    'color': '#fff'
                },
                'left': 'right',
                'top': '15%',
                'dimension': size_col,
                'min': size_min,
                'max': size_max,
                'calculable': True,
                'precision': 0.1,
                'inRange': {
                    'symbolSize': [10, 100]
                },
                'outOfRange': {
                    'symbolSize': [10, 100],  # 如果去掉这一行，不在选择范围内的圆形会缩至最小
                    'color': ['rgba(255,255,255,.2)']  # 拖动条上选中范围外颜色变成灰色
                },
                # 设置拖动条的样式
                'controller': {
                    'inRange': {
                        'color': ['#c23531']
                    },
                    'outOfRange': {
                        'color': ['#444']
                    }
                }
            },
            {
                'text': ['颜色明暗：{0}'.format(columns_list[3])],
                'textGap': 30,
                'textStyle': {
                    'color': '#fff'
                },
                'left': 'right',
                'bottom': '15%',
                'dimension': lightness_col,
                'min': lightness_min,
                'max': lightness_max,
                'calculable': True,
                'precision': 0.1,
                'inRange': {
                    'colorLightness': [1, 0.5]
                },
                'outOfRange': {
                    'color': ['rgba(255,255,255,.2)']
                },
                'controller': {
                    'inRange': {
                        'color': ['#c23531']
                    },
                    'outOfRange': {
                        'color': ['#444']
                    }
                }
            }
        ]

    def _repr_html_(self):
        """
        渲染配置项并将图形显示在 notebook 中
        覆盖基类中的该函数，通过读取'notebook.html'文件后，向模板中增加变量的方式，来设置tooltip提示信息

        chart/page => charts
        chart.js_dependencies => require_config => config_items, libraries
        :return A unicode string.
        """
        if CURRENT_CONFIG.jupyter_presentation != constants.DEFAULT_HTML:
            return None

        require_config = CURRENT_CONFIG.produce_require_configuration(
            self.js_dependencies
        )
        config_items = require_config["config_items"]
        libraries = require_config["libraries"]
        env = engine.create_default_environment(constants.DEFAULT_HTML)
        # return env.render_chart_to_notebook(
        #     charts=(self,), config_items=config_items, libraries=libraries
        # )
        cont = env.render_chart_to_notebook(
                charts=(self,), config_items=config_items, libraries=libraries
            )
        tooltip_script = """<script>\nvar columns_list = {0};\n</script>""".format(self.my_option['columns_list'])
        cont += tooltip_script
        # print(cont)

        return cont

    def render(self, path="render.html", template_name="simple_chart.html", object_name="chart", **kwargs):
        """
        将图表保存成html文件，默认占满屏幕
        :param path:
        :param template_name:
        :param object_name:
        :param kwargs:
        :return:
        """

        # 调用父类的方法生成html文件
        super(Bubble_4D, self).render(path, "simple_chart.html", "chart", **kwargs)
        with open(path, 'r', encoding="utf-8") as file:
            cont = file.read()

        # 修改html文件使tooltip可以正常显示
        pos1 = re.search("myChart\w*.setOption(.*?);", cont).span()[1] +1
        cont = cont[: pos1] + "var columns_list = {0};\n".format(self.my_option['columns_list']) + cont[pos1:]

        # 修改html文件使图表全屏显示
        try:
            pos2 = re.search("<html>", cont).span()[1] - 1
            cont = cont[: pos2] + ' style="height: 100%"' + cont[pos2: ]
            pos2 = re.search("<body>", cont).span()[1] - 1
            cont = cont[: pos2] + ' style="height: 100%; margin: 0"' + cont[pos2:]
            pos3, pos4 = re.search('style="width:.*?;height:.*?;"', cont).span()
            cont = cont[: pos3] + ' style="width: 100%; height: 100%;"' + cont[pos4:]
        except:
            pass

        # 保存修改后的html文件
        utils.write_utf8_html_file(path, cont)

