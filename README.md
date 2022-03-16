# XWeatherAPI

源项目地址：<https://gitee.com/ayo_yo/xweather>

本 `API` 基于 `Flask` ，仅供 [XWeather](https://gitee.com/ayo_yo/xweather) 使用

## 使用方法

### 天气

URL: <https://api.2fanbaby.cn/weather/城市>

参数介绍

仅一个参数，城市的中文名，无需带行政单位，例如：北京

<https://api.2fanbaby.cn/weather/北京>

---

### 获取当前城市

URL: <https://api.2fanbaby.cn/getcity?x=0&y=0>

目前仅支持获取市级地址，直辖市可获取县区级，因为目前采用的免费API不支持获取普通县域一下的服务。

参数介绍

两个参数，一个`x`为经度，`y`为维度，支持浮点数，可通过`GET`和`POST`方式提交
