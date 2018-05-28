# coding=utf-8
import requests
import re
from pydawn.file_utils import open_file_in_utf8
import matplotlib
from matplotlib.collections import PatchCollection
from matplotlib.font_manager import FontProperties
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import time
import os
import numpy as np
import sys
from pypinyin import lazy_pinyin

reload(sys)
sys.setdefaultencoding('utf-8')

location_cache = "location_cache.txt"
base_dir = os.path.dirname(__file__).replace("\\", "/")
font = FontProperties(fname="%s/fonts/simsun.ttc" % base_dir, size=14)


def load_coordinate_cache():
    location_coord = {}
    if os.path.exists(location_cache):
        for line in open_file_in_utf8(location_cache):
            line = line.strip()
            location = line.split("|")[0].strip().encode("utf-8")
            posx = line.split("|")[1].split(" ")[0]
            posy = line.split("|")[1].split(" ")[1]
            location_coord[location] = (float(posx), float(posy))
    return location_coord


def get_coordinate(location):
    url_format = "http://api.map.baidu.com/geocoder/v2/?output=json&ak=SjDhGSaC0GTQfhL7ezS9Qb0MoTWk49hO&address=%s"
    url = url_format % location
    response = requests.get(url)
    answer = response.json()
    try:
        x, y = answer['result']['location']['lng'], answer['result']['location']['lat']
        print "get coordinate for %s(%s,%s)" % (location, x, y)
        return x, y
    except:
        print 'query location %s fail, %s' % (location, answer)
        return None, None


def get_coordinates(location_list_file):
    location_coord = load_coordinate_cache()
    location_cache_file = open(location_cache, "a+")
    for line in open_file_in_utf8(location_list_file):
        city = line.strip()
        if city in location_coord:
            continue

        x, y = get_coordinate(city)
        if x is None:
            continue
        location_cache_file.write("%s|%f %f\n" % (city, x, y))
        location_cache_file.flush()
    location_cache_file.close()


def draw_cn_map(location_file):
    plt.figure(figsize=(16, 8))
    m = Basemap(llcrnrlon=77, llcrnrlat=14, urcrnrlon=140, urcrnrlat=51, projection='lcc', lat_1=33, lat_2=45, lon_0=100)
    m.drawcoastlines()
    m.drawcountries(linewidth=1.5)

    base_dir = os.path.dirname(__file__).replace("\\", "/")

    m.readshapefile('%s/CHN_adm_shp/CHN_adm1' % base_dir, 'states', drawbounds=True)
    ax = plt.gca()
    for nshape, seg in enumerate(m.states):
        poly = Polygon(seg, facecolor='#96CDCD')
        ax.add_patch(poly)

    m.readshapefile('%s/TWN_adm_shp/TWN_adm0' % base_dir, 'taiwan', drawbounds=True)
    for nshape, seg in enumerate(m.taiwan):
        poly = Polygon(seg, facecolor='#96CDCD')
        ax.add_patch(poly)

    location_coord = {}
    location_cache = "location_cache.txt"

    fail_cache = "fail_cache.txt"
    fail_list = []
    if os.path.exists(fail_cache):
        for line in open(fail_cache):
            line = line.strip()
            fail_list.append(line)

    if os.path.exists(location_cache):
        for line in open(location_cache):
            line = line.strip()
            location = line.split("|")[0].strip()
            posx = line.split("|")[1].split(" ")[0]
            posy = line.split("|")[1].split(" ")[1]
            location_coord[location] = (float(posx), float(posy))

    location_cache_file = open(location_cache, "a+")
    fail_cache_file = open(fail_cache, "a+")

    for line in open(location_file):
        location = re.split(",\s;", line)[0]
        location = location.replace(";", "").strip()
        if location in location_coord:
            x, y = location_coord[location]
        else:
            if location in fail_list:
                continue
            x, y = get_coordinate(location)
            if x is None:
                fail_cache_file.write(location+"\n")
                continue

            print "query location: %s, x:%d, y:%d" % (location, x, y)
            location_cache_file.write("%s|%f %f\n" % (location, x, y))
            location_cache_file.flush()

            x, y = m(x, y)

        m.plot(x, y, marker='o', color='r', markersize=3, alpha=0.8, zorder=10)

    province = []
    for shapedict in m.states_info:
        statename = shapedict['NL_NAME_1']
        p = statename.split('|')
        if len(p) > 1:
            s = p[1]
        else:
            s = p[0]

        if s not in province:
            province.append(s)

    for shapedict in m.taiwan_info:
        s = shapedict['NAME_CHINE']
        if s not in province:
            province.append(s)

    province.append(u"黑龙江")
    font = FontProperties(fname="%s/fonts/simsun.ttc" % base_dir, size=14)
    for pro in province:
        print "pro", pro
        try:
            if pro == u"海南" or pro == u"河南":
                pro = pro + u"省"
            if pro in location_coord:
                x, y = location_coord[pro]
            else:
                if pro in fail_list:
                    continue

                x, y = get_coordinate(pro)
                location_cache_file.write("%s|%f %f\n" % (location, x, y))
                location_cache_file.flush()
                x, y = m(x, y)

            plt.text(x, y, pro, fontsize=8, color='#000000', zorder=100, fontproperties=font)
            print "add text %s" % pro
        except:
            pass

    fail_cache_file.close()
    location_cache_file.close()
    plt.show()


def draw_label(x, y, width, height, ax, color, text):
    rect_pos = np.zeros(shape=(4, 2))
    rect_pos[0][0] = x
    rect_pos[0][1] = y

    rect_pos[1][0] = x
    rect_pos[1][1] = y - height

    rect_pos[2][0] = x + width
    rect_pos[2][1] = y - height

    rect_pos[3][0] = x + width
    rect_pos[3][1] = y

    patches = []
    polygon = Polygon(rect_pos, True)
    patches.append(polygon)
    p = PatchCollection(patches, cmap=matplotlib.cm.jet, alpha=0.4, facecolors=color, edgecolors="#000000")
    ax.add_collection(p)

    text_margin = 10000
    top_margin = 1000
    plt.text(x+width+text_margin, y-top_margin, text, fontsize=14, color='#000000', zorder=100, fontproperties=font, ha='left', va="top")


def draw_cities(city_list, save_path):
    location_coord = load_coordinate_cache()

    coords = []
    for city in city_list:
        x, y = location_coord[city]
        coords.append((x, y))

    padding = 0.05
    llcrnrlon = min(coords,key=lambda x:x[0])[0] * (1-padding)
    urcrnrlon = max(coords, key=lambda x: x[0])[0] * (1+padding)
    llcrnrlat = min(coords, key=lambda x: x[1])[1] * (1-padding)
    urcrnrlat = max(coords, key=lambda x: x[1])[1] * (1+padding)

    mid_lon = (llcrnrlon+urcrnrlon) / 2
    mid_lat = (llcrnrlat+urcrnrlat) / 2

    show_label = True
    start = time.clock()

    plt.figure(figsize=(20, 20))
    m = Basemap(llcrnrlon=llcrnrlon, urcrnrlon=urcrnrlon, llcrnrlat=llcrnrlat, urcrnrlat=urcrnrlat, projection='lcc', lon_0=mid_lon, lat_0=mid_lat)

    m.readshapefile("CHN_adm_shp\\CHN_adm2", 'states', drawbounds=False)
    m.drawcoastlines(color="w", zorder=-1)

    ax = plt.gca()
    # ax.spines['top'].set_visible(False)
    # ax.spines['bottom'].set_visible(False)
    # ax.spines['left'].set_visible(False)
    # ax.spines['right'].set_visible(False)


    color1 = "#ffff00"
    color2 = "#def9de"
    color3 = "#bbfbba"
    color4 = "#9eeb1a"
    color5 = "#00FF00"

    for info, shp in zip(m.states_info, m.states):
        province = info['NAME_1']
        city = info['NAME_2']
        city_name = info["NL_NAME_2"].split("|")[0].encode("utf-8")
        if city_name in city_list:
            color = 'g'
            poly = Polygon(shp, facecolor=color, edgecolor='#000000', lw=1)
            ax.add_patch(poly)

            if show_label:
                x, y = location_coord[city_name]
                x, y = m(x, y)
                # print city_name, x, y
                city_name = city_name.replace(u"襄樊", u"襄阳")
                plt.text(x, y, city_name, fontsize=10, color='#000000', zorder=100, fontproperties=font, ha='center')

    # draw arrow
    '''
    x, y = location_coord["arrow"]
    x, y = m(x, y)
    plt.text(x, y, "N", fontsize=14, color='#000000', zorder=100, fontproperties=font, ha='center')

    x_offset = 25000
    y_offset = 70000
    height = 50000

    left_angle = np.zeros(shape=(3, 2))
    left_angle[0][0] = x
    left_angle[0][1] = y

    left_angle[1][0] = x - x_offset
    left_angle[1][1] = y - y_offset

    left_angle[2][0] = x
    left_angle[2][1] = y - height

    left_patches = []
    left_polygon = Polygon(left_angle, True)
    left_patches.append(left_polygon)

    left_p = PatchCollection(left_patches, cmap=matplotlib.cm.jet, alpha=0.4, facecolors="#000000",
                             edgecolors="#000000")
    ax.add_collection(left_p)

    right_angle = np.zeros(shape=(3, 2))
    right_angle[0][0] = x
    right_angle[0][1] = y

    right_angle[1][0] = x + x_offset
    right_angle[1][1] = y - y_offset

    right_angle[2][0] = x
    right_angle[2][1] = y - height

    right_patches = []
    right_polygon = Polygon(right_angle, True, color="w")
    right_patches.append(right_polygon)

    right_p = PatchCollection(right_patches, cmap=matplotlib.cm.jet, alpha=0.4, facecolors="w", edgecolors="#000000")
    ax.add_collection(right_p)

    # draw label
    width = 50000
    height = 20000
    location = location_coord["label"]
    x = float(location.split(",")[0])
    y = float(location.split(",")[1])
    x, y = m(x, y)

    margin = 10000
    draw_label(x, y, width, height, ax, color1, "<0.2")
    draw_label(x, y - (height + margin), width, height, ax, color2, "0.2～0.4")
    draw_label(x, y - (height + margin) * 2, width, height, ax, color3, "0.4～0.6")
    draw_label(x, y - (height + margin) * 3, width, height, ax, color4, "0.6～0.8")
    draw_label(x, y - (height + margin) * 4, width, height, ax, color5, ">0.8")
    '''

    end = time.clock()
    print(end - start)
    plt.savefig(save_path)
    plt.show()


if __name__ == '__main__':
    # get_coordinates("cities.txt")
    city_list = []
    for city in open_file_in_utf8("cities.txt"):
        city_list.append(city.strip().encode("utf-8"))
    draw_cities(city_list, "cities.png")
