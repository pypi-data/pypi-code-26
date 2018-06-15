import requests
import json
import base64
import os
import time
from PIL import Image


def _resize_img(filepath,max_size=512000):
    filesize = os.path.getsize(filepath)
    im = Image.open(filepath)
    src_w = im.size[0]
    src_h = im.size[1]
    dst_w = 500
    dst_h = (src_h/src_w) * 500
    dst_size = dst_w , dst_h
    im.thumbnail(dst_size)
    im.save(filepath)
    return filepath

def _getInfo(filename='', mode=0):
    url = 'https://www.yuanfudao.com/tutor-ybc-course-api/faceInfo.php'
    filepath = os.path.abspath(filename)
    filepath = _resize_img(filepath)
    b64img= base64.b64encode(open(filepath, 'rb').read()).rstrip().decode('utf-8')
    data = {}
    data['b64img'] = b64img
    data['mode'] = mode
    r = requests.post(url, data=data)
    res = r.json()
    if res['ret'] == 0 and res['data']:
        res = res['data']['face_list'][0]
        res_dict = {
        'age':res['age'],
        'gender':res['gender'],
        'beauty':res['beauty'],
        'glass':res['glass']
        }
        return res_dict
    else:
        return -1

def gender1(filename=''):
    if not filename:
        return -1
    res = _getInfo(filename)
    if res == -1:
        return '图片中找不到人哦~'
    return res['gender']

def gender(filename=''):
    if not filename:
        return -1
    res = _getInfo(filename)
    if res == -1:
        return '图片中找不到人哦~'
    return '男' if res['gender']>90 else '女'

def age(filename=''):
    if not filename:
        return -1
    res = _getInfo(filename)
    if res == -1:
        return '图片中找不到人哦~'
    return res['age']

def glass1(filename=''):
    if not filename:
        return -1
    res = _getInfo(filename)
    if res == -1:
        return '图片中找不到人哦~'
    return bool(res['glass'])

def glass(filename=''):
    if not filename:
        return -1
    res = _getInfo(filename)
    if res == -1:
        return '图片中找不到人哦~'
    return res['glass']

def beauty(filename=''):
    if not filename:
        return -1
    res = _getInfo(filename)
    if res == -1:
        return '图片中找不到人哦~'
    return res['beauty']

'''识别图片中一张人脸信息'''
def info(filename='', mode=0):
    if not filename:
        return -1
    filepath = os.path.abspath(filename)
    filepath = _resize_img(filepath)

    url = 'https://www.yuanfudao.com/tutor-ybc-course-api/faceInfo.php'
    filepath = os.path.abspath(filename)
    b64img= base64.b64encode(open(filepath, 'rb').read()).rstrip().decode('utf-8')
    data = {}
    data['b64img'] = b64img
    data['mode'] = mode
    r = requests.post(url, data=data)
    res = r.json()
    if res['ret'] == 0 and res['data']:
        res = res['data']['face_list'][0]
        res_dict = {
        'age':res['age'],
        'gender':res['gender'],
        'beauty':res['beauty'],
        'glass':res['glass']
        }
        gender =  '男性' if res_dict['gender'] >= 50 else '女性'
        glass = '戴' if res_dict['glass'] else '不戴'
        res_str = '{gender}，{age}岁左右，{glass}眼镜，颜值打分：{beauty}分'.format(gender=gender,age=res_dict['age'],glass=glass,beauty=res_dict['beauty'])
        return res_str
    else:
        return '图片中找不到人哦~'

'''返回图片中所有人脸信息'''
def info_all(filename='', mode=0):
    if not filename:
        return -1
    url = 'https://www.yuanfudao.com/tutor-ybc-course-api/faceInfo.php'
    filepath = os.path.abspath(filename)
    b64img= base64.b64encode(open(filepath, 'rb').read()).rstrip().decode('utf-8')
    data = {}
    data['b64img'] = b64img
    data['mode'] = mode
    r = requests.post(url, data=data)
    res = r.json()
    if res['ret'] == 0 and res['data']:
        res = res['data']['face_list']
        res_str = '图片中总共发现{face_len}张人脸：'.format(face_len=len(res))+os.linesep
        i = 1
        for val in res :
            gender =  '男性' if val['gender'] >= 50 else '女性'
            glass = '戴' if val['glass'] else '不戴'
            res_str += '第{i}个人脸信息：{gender}，{age}岁左右，{glass}眼镜，颜值打分：{beauty}分'.format(gender=gender,age=val['age'],glass=glass,beauty=val['beauty'],i=i)
            res_str += os.linesep
            i += 1
        return res_str
    else:
        return '图片中找不到人哦~'

def ps(filename='', decoration=21):
    '''变装'''
    if not filename:
        return -1
    if decoration < 1:
        decoration = 1
    if decoration > 22:
        decoration = 22
    filepath = os.path.abspath(filename)
    filepath = _resize_img(filepath)
    url = 'https://www.yuanfudao.com/tutor-ybc-course-api/faceDecoration.php'

    b64img= base64.b64encode(open(filepath, 'rb').read()).rstrip().decode('utf-8')
    data = {}
    data['b64img'] = b64img
    data['decoration'] = decoration
    r = requests.post(url, data=data)
    res = r.json()
    if res['ret'] == 0 and res['data']:
        new_file = os.path.splitext(filename)[0] + '_' + str(int(time.time())) +'.'+os.path.splitext(filename)[1]
        with open(new_file,'wb') as f:
            f.write(base64.b64decode(res['data']['image']))
        return new_file
    else:
        return -1


def mofa(filename='', model=16):

    '''人脸融合'''
    if not filename:
        return -1

    if model < 1:
        model = 1
    if model > 50:
        model = 50

    filepath = os.path.abspath(filename)
    filepath = _resize_img(filepath)
    url = 'https://www.yuanfudao.com/tutor-ybc-course-api/faceMerge.php'

    b64img= base64.b64encode(open(filepath, 'rb').read()).rstrip().decode('utf-8')
    data = {}
    data['b64img'] = b64img
    data['model'] = model
    r = requests.post(url, data=data)

    res = r.json()
    if res['ret'] == 0 and res['data']:
        new_file = os.path.splitext(filename)[0] + '_' + str(int(time.time())) +'.png'
        with open(new_file,'wb') as f:
            f.write(base64.b64decode(res['data']['image']))
        return _resize_img(new_file)
    else:
        return -1

def main():
    # pass
    # import ybc_box as box
    print(info('1.jpg'))
    # filename = camera()
    # res = age(filename)
    # print(res)
    # res = gender(filename)
    # print(res)
    # res = glass(filename)
    # print(res)
    # res = beauty(filename)
    # print(res)
    # res = info('2.jpg')
    # print(res)
    # res = info_all('3.jpg')
    # print(res)
    # res = age('5.jpg')
    # print(res)
    # res = gender('5.jpg')
    # print(res)
    # res = glass('5.jpg')
    # print(res)
    # res = beauty('5.jpg')
    # print(res)


if __name__ == '__main__':
    main()
