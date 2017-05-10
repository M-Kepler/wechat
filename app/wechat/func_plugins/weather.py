#  !/usr/bin/env python
#  -*- coding: utf-8 -*-
#  XXX  爬虫 + API = 临时的方案
#  后续修改一下, 就用那个彩云的api

from flask import current_app
import hashlib
import urllib.request
import hmac, time, requests, re, json
from . import wechat_custom

def day_of_week(offset=0):
    """获取星期几"""
    day_of_week = int(time.strftime('%w')) + offset
    days = [u'周日', u'周一', u'周二', u'周三', u'周四', u'周五', u'周六',
            u'周日', u'周一']
    prefix = [u'今天', u'明天', u'后天']
    return prefix[offset] + days[day_of_week]

def download(url):
    try:
        html = urllib.request.urlopen(url)
        html = html.read()
    except Exception as e:
        current_app.logger.Warning("获取信息失败")
    return html

def get(openid):
    # all全部的天气数据
    all_url = 'https://free-api.heweather.com/v5/weather?city=CN101300507&key=5c043b56de9f4371b0c7f8bee8f5b75e'
    # 3天预报
    forecast_url = 'https://free-api.heweather.com/v5/forecast?city=CN101300507&key=5c043b56de9f4371b0c7f8bee8f5b75e'
    #生活指数
    sugg_url = 'https://free-api.heweather.com/v5/suggestion?city=CN101300507&key=5c043b56de9f4371b0c7f8bee8f5b75e'
    # 天气图标
    photo_url = 'https://cdn.heweather.com/cond_icon/100.png'
    #  彩云天气
    caiyun_url ='http://www.caiyunapp.com/fcgi-bin/v1/api.py?lonlat=110.429369,25.310815&format=json&product=minutes_prec&token=96Ly7wgKGq6FhllM&random=0.8600497214532319'

    #  彩云天气-降雨情况 -----------
    caiyun_res = requests.get(caiyun_url)
    caiyun_data = json.loads(caiyun_res.text)
    rain_summary = caiyun_data['summary']

    #天气情况的内容提取------------开始
    weather_res = download(forecast_url)
    html = weather_res.decode('utf-8')

    max_tmp = re.findall('max":"(.*?)"', html)[0]  #最高温度
    min_tmp = re.findall('min":"(.*?)"', html)[0]  #最低温度
    photo = re.findall('code_d":"(.*?)"', html)[0] #天气图片
    txt_d = re.findall('txt_d":"(.*?)"', html)[0] #天气情况
    dir = re.findall('dir":"(.*?)"', html)[0]  # 风向
    sc = re.findall('sc":"(.*?)"', html)[0]  # 风力
    wind = "%s - %s" %(sc, dir)

    weather_data = u"温度：%s℃ - %s℃   %s  %s\n" % (min_tmp, max_tmp,txt_d, wind)

    #生活指数等内容的提取-----------开始
    life_res = download(sugg_url)
    html = life_res.decode('utf-8')
    brf = re.findall('brf":"(.*?)"', html)
    txt = re.findall('txt":"(.*?)"', html)

    comf_brf = brf[0]#舒适度指数
    comf_txt = txt[0]
    comf = comf_brf + '\n' + comf_txt

    drsg_brf = brf[3]#穿衣
    drsg_txt = txt[3]
    drsg = drsg_brf + '\n' + drsg_txt

    flu_brf = brf[4]#感冒
    flu_txt = txt[4]
    flu = flu_brf+ '\n' + flu_txt

    trav_brf = brf[6]#出行指数
    trav_txt = txt[6]
    trav = trav_brf + '\n' + trav_txt

    life_data = weather_data + '\n' + u"舒适度：%s\n\n穿衣指数：%s\n\n出行指数：%s" % (comf, drsg, trav)

    content = [{
        'title' : rain_summary,
        'description' : life_data,
        'url':'http://www.caiyunapp.com/h5/?lonlat=110.411377,25.321474'
        }]

    wechat_custom.send_news(openid, content)

