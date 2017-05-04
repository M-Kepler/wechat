# !/usr/bin/env python
# _*_ coding:utf-8

# -*- coding: utf-8 -*-


from wechatpy import parse_message, create_reply
from wechatpy.replies import TextReply, ArticlesReply
from wechatpy.utils import check_signature
from wechatpy.exceptions import InvalidSignatureException
from webcore.weatherservices import cityweather
from isay9685.models import CityWeahter
import json
import time
from datetime import datetime

def replyWeather(cityname, msg):
    reply = None
    dateid = time.strftime("%Y%m%d")
    timeid = time.strftime("%H")
    cWeahter = CityWeahter.objects.filter(dateid=dateid, timeid=timeid, cityname=cityname)
    if cWeahter:
        weatherstr = cWeahter[0].wheather
    else:
        weatherstr = cityweather.getcityweather(cityname)
        cw = CityWeahter(dateid=dateid, timeid=timeid, cityname=cityname, wheather=weatherstr, createtime=datetime.now())
        cw.save()
    # weatherstr = '''{"error":0,"status":"success","date":"2015-06-15","results":[{"currentCity":"合肥","pm25":"126","index":[{"title":"穿衣","zs":"热","tipt":"穿衣指数","des":"天气热，建议着短裙、短裤、短薄外套、T恤等夏季服装。"},{"title":"洗车","zs":"不宜","tipt":"洗车指数","des":"不宜洗车，未来24小时内有雨，如果在此期间洗车，雨水和路上的泥水可能会再次弄脏您的爱车。"},{"title":"旅游","zs":"适宜","tipt":"旅游指数","des":"温度适宜，又有较弱降水和微风作伴，会给您的旅行带来意想不到的景象，适宜旅游，可不要错过机会呦！"},{"title":"感冒","zs":"较易发","tipt":"感冒指数","des":"相对今天出现了较大幅度降温，较易发生感冒，体质较弱的朋友请注意适当防护。"},{"title":"运动","zs":"较不宜","tipt":"运动指数","des":"有降水，推荐您在室内进行健身休闲运动；若坚持户外运动，须注意携带雨具并注意避雨防滑。"},{"title":"紫外线强度","zs":"弱","tipt":"紫外线强度指数","des":"紫外线强度较弱，建议出门前涂擦SPF在12-15之间、PA+的防晒护肤品。"}],"weather_data":[{"date":"周一 06月15日 (实时：27℃)","dayPictureUrl":"http://api.map.baidu.com/images/weather/day/xiaoyu.png","nightPictureUrl":"http://api.map.baidu.com/images/weather/night/zhongyu.png","weather":"小雨转中雨","wind":"南风微风","temperature":"28 ~ 22℃"},{"date":"周二","dayPictureUrl":"http://api.map.baidu.com/images/weather/day/dayu.png","nightPictureUrl":"http://api.map.baidu.com/images/weather/night/xiaoyu.png","weather":"大雨转小雨","wind":"北风微风","temperature":"26 ~ 21℃"},{"date":"周三","dayPictureUrl":"http://api.map.baidu.com/images/weather/day/xiaoyu.png","nightPictureUrl":"http://api.map.baidu.com/images/weather/night/yin.png","weather":"小雨转阴","wind":"北风微风","temperature":"24 ~ 20℃"},{"date":"周四","dayPictureUrl":"http://api.map.baidu.com/images/weather/day/duoyun.png","nightPictureUrl":"http://api.map.baidu.com/images/weather/night/duoyun.png","weather":"多云","wind":"东北风3-4级","temperature":"28 ~ 20℃"}]}]} '''
    weatherjson = json.loads(weatherstr)
    if weatherjson and weatherjson.get('error') == 0:
        date = weatherjson.get('date')
        result = weatherjson.get('results')[0]
        currentCity = result.get('currentCity')
        pm25 = result.get('pm25')
        wheathernowdatas = result.get('weather_data')[0]
        weathermsg = repr(wheathernowdatas)
        reply = ArticlesReply(message=msg)
        # simply use dict as article
        reply.add_article({
            'title': wheathernowdatas.get('date'),
        })
        reply.add_article({
            'title':
             u'%s %s %s' % (wheathernowdatas.get('weather') , wheathernowdatas.get('temperature') , wheathernowdatas.get('wind')) \
             + '\r\n'\
             + '\r\n'\
             + currentCity + u' PM2.5: ' + pm25  ,
            'url': 'http://isay9685.duapp.com'
        })
        reply.add_article({
            'title':  u'白天',
            'image': wheathernowdatas.get('dayPictureUrl'),
        })
        reply.add_article({
            'title':  u'晚上',
            'image': wheathernowdatas.get('nightPictureUrl'),
        })
    return reply
