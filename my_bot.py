# coding=utf-8

import time
import json
import os
import re
import sys
import requests
import getpass
import urllib

from http.server import BaseHTTPRequestHandler, HTTPServer
from time import gmtime, strftime, mktime

##download image url from the TRKD Chart service as chart.png
def downloadChartImage(chartURL):
    ##create header
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = {'User-Agent': user_agent}
    print('\nDownlading chart.png file from %s' % (chartURL))
    ##download image using Python3 urllib
    downloadResult = urllib.request.Request(chartURL, headers=headers)
    imgData = urllib.request.urlopen(downloadResult).read()
    ##write file
    fileName = './chart.png'
    with open(fileName, 'wb') as outfile:
        outfile.write(imgData)
        print('save chart.png file complete')


# Send HTTP request for all services
def doSendRequest(url, requestMsg, headers):
    result = None
    try:
        # send request
        result = requests.post(
            url, data=json.dumps(requestMsg), headers=headers)
        # handle error
        if result.status_code is not 200:
            print('Request fail')
            print('response status %s' % (result.status_code))
            if result.status_code == 500:  # if username or password or appid is wrong
                print('Error: %s' % (result.json()))
            result.raise_for_status()
    except requests.exceptions.RequestException as e:
        print('Exception!!!')
        print(e)
        sys.exit(1)
    print(type(result))
    return result


# Perform authentication
def CreateAuthorization(username, password, appid):
    token = None
    # create authentication request URL, message and header
    authenMsg = {'CreateServiceToken_Request_1': {
        'ApplicationID': appid, 'Username': username, 'Password': password}}
    authenURL = 'https://api.trkd.thomsonreuters.com/api/TokenManagement/TokenManagement.svc/REST/Anonymous/TokenManagement_1/CreateServiceToken_1'
    headers = {'content-type': 'application/json;charset=utf-8'}
    print('############### Sending Authentication request message to TRKD ###############')
    authenResult = doSendRequest(authenURL, authenMsg, headers)
    if authenResult is not None and authenResult.status_code == 200:
        print('Authen success')
        print('response status %s' % (authenResult.status_code))
        # get Token
        token = authenResult.json()['CreateServiceToken_Response_1']['Token']

    return token


# Perform Online Report request
def RetrieveOnlineReport(token, appid):
    # construct Online Report URL and header
    onlinereportURL = 'http://api.trkd.thomsonreuters.com/api/OnlineReports/OnlineReports.svc/REST/OnlineReports_1/GetSummaryByTopic_1'
    headers = {'content-type': 'application/json;charset=utf-8',
               'X-Trkd-Auth-ApplicationID': appid, 'X-Trkd-Auth-Token': token}
    # construct a Online Report request message
    onelinereportRequestMsg = {'GetSummaryByTopic_Request_1': {
        'Topic': 'OLRUTOPNEWS',
        'MaxCount': 20,
        'ReturnPrivateNetworkURL': False
    }
    }
    print('############### Sending News - Online Report request message to TRKD ###############')
    onlinereportResult = doSendRequest(
        onlinereportURL, onelinereportRequestMsg, headers)
    if onlinereportResult is not None and onlinereportResult.status_code == 200:
        print('Online Report response message: ')
        print(onlinereportResult.json())


def RetrievePriceFromTo(token, appid, ricName, date_from, date_to):

    #date_from = '2017-09-02'
    #date_to = '2017-12-02'
    #date_from += 'T00:00:00'
    #date_to += 'T23:59:00'

    # construct Online Report URL and header
    onlinereportURL = 'http://api.trkd.thomsonreuters.com/api/TimeSeries/TimeSeries.svc/REST/TimeSeries_1/GetInterdayTimeSeries_4'
    headers = {'Content-type': 'application/json;charset=utf-8',
               'X-Trkd-Auth-ApplicationID': appid, 'X-Trkd-Auth-Token': token}
    # construct a Online Report request message
    onelinereportRequestMsg = {
        "GetInterdayTimeSeries_Request_4": {
            "Symbol": ricName,
            #"StartTime": "2017-09-02T00:00:00",
            #"EndTime": "2017-12-02T23:59:00",
            "StartTime": date_from,
            "EndTime": date_to,
            "Interval": "DAILY"
        }
    }
    print('############### Sending News - Online Report request message to TRKD ###############')
    onlinereportResult = doSendRequest(
        onlinereportURL, onelinereportRequestMsg, headers)
    if onlinereportResult is not None and onlinereportResult.status_code == 200:
        print('Online Report response message: ')
        return onlinereportResult.json()


def GetPriceFromTo(ricName, date_from, date_to):
    token = CreateAuthorization('trkd-demo-wm@thomsonreuters.com', 'o3o4h91ac', 'trkddemoappwm')
    print('Token = %s' % (token))

    # if authentiacation success, continue subscribing Online Report
    if token is not None:
        appid = 'trkddemoappwm'
        price_data = RetrievePriceFromTo(token, appid, ricName, date_from, date_to)
        for i in list(((list(price_data.values())[0]).values()))[0]:
            print ('price : ', i[u'CLOSE'], '              datetime : ', i[u'TIMESTAMP'], '\n')
        #print (price_data)


def RetrievePriceLast(token, appid, ricName, num_bars):
    gamma = gmtime()
    seconds = mktime(gamma)

    alpha_to = strftime('%Y-%m-%d', gamma)
    beta_to = strftime('%H:%M:%S', gamma)

    date_to = alpha_to + 'T' + beta_to

    delta = gmtime(seconds - num_bars * 3600)

    alpha_from = strftime('%Y-%m-%d', delta)
    beta_from = strftime('%H:%M:%S', delta)

    date_from = alpha_from + 'T' + beta_from

    # construct Online Report URL and header
    onlinereportURL = 'http://api.trkd.thomsonreuters.com/api/TimeSeries/TimeSeries.svc/REST/TimeSeries_1/GetIntradayTimeSeries_4'
    headers = {'Content-type': 'application/json;charset=utf-8',
               'X-Trkd-Auth-ApplicationID': appid, 'X-Trkd-Auth-Token': token}
    # construct a Online Report request message
    onelinereportRequestMsg = {
        "GetIntradayTimeSeries_Request_4": {
            "Symbol": ricName,
            "StartTime": date_from,
            "EndTime": date_to,
            "Interval": "HOUR",
            "TrimResponse": True
        }
    }
    print('############### Sending News - Online Report request message to TRKD ###############')
    onlinereportResult = doSendRequest(onlinereportURL, onelinereportRequestMsg, headers)
    if onlinereportResult is not None and onlinereportResult.status_code == 200:
        print('Online Report response message: ')
        return onlinereportResult.json()


def GetPriceLast(ricName, num_bars):
    token = CreateAuthorization('trkd-demo-wm@thomsonreuters.com', 'o3o4h91ac', 'trkddemoappwm')
    print('Token = %s' % (token))

    # if authentiacation success, continue subscribing Online Report
    if token is not None:
        price_data = RetrievePriceLast(token, appid, ricName, num_bars)
        for i in list(((list(price_data.values())[0]).values()))[0]:
            print ('price : ', i[u'C'], '              datetime : ', i[u'T'], '\n')


def RetrieveExchange(token, appid, ricName):
    gamma = gmtime()
    seconds = mktime(gamma)
    num_bars = 1000
    alpha_to = strftime('%Y-%m-%d', gamma)
    beta_to = strftime('%H:%M:%S', gamma)

    date_to = alpha_to + 'T' + beta_to

    delta = gmtime(seconds - num_bars * 3600)

    alpha_from = strftime('%Y-%m-%d', delta)
    beta_from = strftime('%H:%M:%S', delta)

    date_from = alpha_from + 'T' + beta_from

    # construct Online Report URL and header
    onlinereportURL = 'http://api.trkd.thomsonreuters.com/api/TimeSeries/TimeSeries.svc/REST/TimeSeries_1/GetIntradayTimeSeries_4'
    headers = {'Content-type': 'application/json;charset=utf-8',
               'X-Trkd-Auth-ApplicationID': appid, 'X-Trkd-Auth-Token': token}
    # construct a Online Report request message
    onelinereportRequestMsg = {
        "GetIntradayTimeSeries_Request_4": {
            "Symbol": ricName,
            "StartTime": date_from,
            "EndTime": date_to,
            "Interval": "HOUR",
            "TrimResponse": True
        }
    }
    print('############### Sending News - Online Report request message to TRKD ###############')
    onlinereportResult = doSendRequest(onlinereportURL, onelinereportRequestMsg, headers)
    if onlinereportResult is not None and onlinereportResult.status_code == 200:
        print('Online Report response message: ')
        return onlinereportResult.json()


def GetExchange(name):
    ricName = name + 'RUB=R'
    token = CreateAuthorization('trkd-demo-wm@thomsonreuters.com', 'o3o4h91ac', 'trkddemoappwm')
    print('Token = %s' % (token))
    tmp = 0
    # if authentiacation success, continue subscribing Online Report
    if token is not None:
        appid = 'trkddemoappwm'
        price_data = RetrieveExchange(token, appid, ricName)
        tmp = ((list(((list(price_data.values())[0]).values()))[0])[-1])
        #for i in list(((list(price_data.values())[0]).values()))[0]:
        #    print ('price : ', i[u'C'], '              datetime : ', i[u'T'], '\n')
        print('price of ', name, ' : ', tmp['C'])
        return tmp['C']


def GetChartFromTo(ricName, date_from, date_to):
    token = CreateAuthorization(username, password, appid)
    print('Token = %s' % (token))

    ## if authentiacation success, continue subscribing Chart
    if token is not None:
        chartURL = RetrieveChartFromTo(token, appid, ricName, date_from, date_to)
        ## if chart request success, continue downloading Chart image
        if chartURL is not None:
            print('############### Downloading Chart file from TRKD ###############')
            downloadChartImage(chartURL)


## Perform Chart request
def RetrieveChartFromTo(token, appid, ricName, date_from, date_to):
    ##construct a Chart request message
    #ricName = 'APLE.K'

    date_from = '2017-09-02'
    date_to = '2017-12-02'
    date_from += 'T00:00:00'
    date_to += 'T23:59:00'

    chartRequestMsg = {'GetChart_Request_2': {'chartRequest': {
        'TimeSeries': {'TimeSeriesRequest_typehint': ['TimeSeriesRequest'],
                       'TimeSeriesRequest': [{'Symbol': ricName,
                                              'Reference': 'd1'}]},
        'Analyses': {'Analysis_typehint': ['Analysis', 'Analysis'],
                     'Analysis': [{'Reference': 'a1',
                                   'OHLC': {'Instrument1': {'Reference': 'd1'}}},
                                  {'Reference': 'a2',
                                   'Vol': {'Instrument1': {'Reference': 'd1'}}}]},
        'StandardTemplate': {
            'Interval': {'CommonType': 'Days', 'Multiplier': '1'},
            'ShowNonTradedPeriods': False,
            'ShowHolidays': False,
            'ShowGaps': True,
            'XAxis': {'Range': {'Fixed': {'First': date_from,
                                          'Last': date_to}}, 'Visible': True,
                      'Position': 'Bottom'},
            'Subchart': [{'YAxis': [{
                'Analysis': [{'Reference': 'a1'}],
                'Visible': True,
                'Position': 'Right',
                'Invert': False,
                'Logarithmic': False,
                'Display': {'Mode': 'Automatic'},
                'Range': {'Automatic': ''},
            }], 'Weight': 5.0}, {'YAxis': [{
                'Analysis': [{'Reference': 'a2'}],
                'Visible': True,
                'Position': 'Right',
                'Invert': False,
                'Logarithmic': False,
                'Display': {'Mode': 'Automatic'},
                'Range': {'Automatic': ''},
            }], 'Weight': 2.0}],
            'Title': {'Caption': {'Visible': True, 'Customized': False},
                      'Range': {'Visible': True}},
            'Legend': {
                'Visible': True,
                'Information': 'Long',
                'Layout': 'MultiLine',
                'Position': 'Overlaid',
            },
            'Instrument': 'Symbol',
            'Delimiter': '%',
            'GridLines': 'None',
            'YAxisMarkers': 'None',
            'YAxisTitles': 'All',
            'Brand': 'None',
        },
        'Scheme': {
            'Background': {
                'BackgroundMode': 'Solid',
                'StartColor': {'Named': 'White'},
                'EndColor': {'Named': 'White'},
                'HatchStyle': 'LargeGrid',
                'GradientMode': 'ForwardDiagonal',
                'ImageMode': 'Centered',
            },
            'Border': {'Color': {'RGB': '139;139;155'},
                       'DashStyle': 'Solid', 'Width': 1.0},
            'GridLines': {'Color': {'RGB': '139;139;155'},
                          'DashStyle': 'Dot', 'Width': 1.0},
            'Title': {'Caption': {
                'Color': {'Named': 'Black'},
                'Family': 'Arial',
                'Style': 'Bold',
                'Size': 12.0,
            }, 'Range': {
                'Color': {'Named': 'Black'},
                'Family': 'Arial',
                'Style': 'Regular',
                'Size': 8.25,
            }},
            'Legend': {
                'Color': {'Named': 'Black'},
                'Family': 'Arial',
                'Style': 'Regular',
                'Size': 8.25,
            },
            'XAxis': {'Major': {
                'Color': {'Named': 'Black'},
                'Family': 'Arial',
                'Style': 'Bold',
                'Size': 9.75,
            }, 'Minor': {
                'Color': {'Named': 'Black'},
                'Family': 'Arial',
                'Style': 'Regular',
                'Size': 8.25,
            }},
            'YAxis': {'Major': {
                'Color': {'Named': 'Black'},
                'Family': 'Arial',
                'Style': 'Bold',
                'Size': 9.75,
            }, 'Minor': {
                'Color': {'Named': 'Black'},
                'Family': 'Arial',
                'Style': 'Regular',
                'Size': 8.25,
            }, 'Title': {
                'Color': {'Named': 'Black'},
                'Family': 'Arial',
                'Style': 'Regular',
                'Size': 8.25,
            }},
            'Series': [
                {
                    'Color': {'Named': 'Black'},
                    'DashStyle': 'Solid',
                    'Width': 0.0,
                    'FillColor': {'Named': 'Black'},
                    'FillStyle': 'Percent20',
                },
                {
                    'Color': {'Named': 'Red'},
                    'DashStyle': 'Solid',
                    'Width': 0.0,
                    'FillColor': {'Named': 'Red'},
                    'FillStyle': 'Percent20',
                },
                {
                    'Color': {'RGB': '62;169;0'},
                    'DashStyle': 'Solid',
                    'Width': 0.0,
                    'FillColor': {'RGB': '62;169;0'},
                    'FillStyle': 'Percent20',
                },
                {
                    'Color': {'RGB': '156;38;115'},
                    'DashStyle': 'Solid',
                    'Width': 0.0,
                    'FillColor': {'RGB': '156;38;115'},
                    'FillStyle': 'Percent20',
                },
                {
                    'Color': {'RGB': '255;120;0'},
                    'DashStyle': 'Solid',
                    'Width': 0.0,
                    'FillColor': {'RGB': '255;120;0'},
                    'FillStyle': 'Percent20',
                },
                {
                    'Color': {'RGB': '25;108;229'},
                    'DashStyle': 'Solid',
                    'Width': 0.0,
                    'FillColor': {'RGB': '25;108;229'},
                    'FillStyle': 'Percent20',
                },
                {
                    'Color': {'RGB': '60;117;28'},
                    'DashStyle': 'Solid',
                    'Width': 0.0,
                    'FillColor': {'RGB': '60;117;28'},
                    'FillStyle': 'Percent20',
                },
                {
                    'Color': {'RGB': '230;176;18'},
                    'DashStyle': 'Solid',
                    'Width': 0.0,
                    'FillColor': {'RGB': '230;176;18'},
                    'FillStyle': 'Percent20',
                },
                {
                    'Color': {'RGB': '0;186;193'},
                    'DashStyle': 'Solid',
                    'Width': 0.0,
                    'FillColor': {'RGB': '0;186;193'},
                    'FillStyle': 'Percent20',
                },
                {
                    'Color': {'RGB': '255;178;127'},
                    'DashStyle': 'Solid',
                    'Width': 0.0,
                    'FillColor': {'RGB': '255;178;127'},
                    'FillStyle': 'Percent20',
                },
                {
                    'Color': {'RGB': '100;79;190'},
                    'DashStyle': 'Solid',
                    'Width': 0.0,
                    'FillColor': {'RGB': '100;79;190'},
                    'FillStyle': 'Percent20',
                },
                {
                    'Color': {'RGB': '209;36;33'},
                    'DashStyle': 'Solid',
                    'Width': 0.0,
                    'FillColor': {'RGB': '209;36;33'},
                    'FillStyle': 'Percent20',
                },
                {
                    'Color': {'RGB': '38;87;135'},
                    'DashStyle': 'Solid',
                    'Width': 0.0,
                    'FillColor': {'RGB': '38;87;135'},
                    'FillStyle': 'Percent20',
                },
                {
                    'Color': {'RGB': '94;176;176'},
                    'DashStyle': 'Solid',
                    'Width': 0.0,
                    'FillColor': {'RGB': '94;176;176'},
                    'FillStyle': 'Percent20',
                },
            ],
            'LevelLine': [{'Color': {'RGB': '0;0;153'}, 'DashStyle': 'Solid'
                              , 'Width': 1.0}, {'Color': {'RGB': '120;120;120'
                                                          }, 'DashStyle': 'Solid', 'Width': 1.0}],
        },
        'ImageType': 'PNG',
        'Width': 500,
        'Height': 400,
        'Culture': 'en-US',
        'ReturnPrivateNetworkURL': False,
    }}}
    ##construct Chart URL and header
    chartURL = 'http://api.trkd.thomsonreuters.com/api/Charts/Charts.svc/REST/Charts_1/GetChart_2'
    headers = {'content-type': 'application/json;charset=utf-8', 'X-Trkd-Auth-ApplicationID': appid,
               'X-Trkd-Auth-Token': token}

    print('############### Sending Chart request message to TRKD ###############')
    chartResult = doSendRequest(chartURL, chartRequestMsg, headers)
    if chartResult is not None and chartResult.status_code == 200:
        print('Time Series Interday response message: ')
        print(chartResult.json())
        ##print returned server, tag and image url
        server = chartResult.json()['GetChart_Response_2']['ChartImageResult']['Server']
        print('\nServer: %s' % (server))
        tag = chartResult.json()['GetChart_Response_2']['ChartImageResult']['Tag']
        print('Tag: %s' % (tag))
        imageUrl = chartResult.json()['GetChart_Response_2']['ChartImageResult']['Url']
        print('Url: %s' % (imageUrl))
        return imageUrl


def GetChartLast(ricName, num_bars):
    token = CreateAuthorization(username, password, appid)
    print('Token = %s' % (token))

    ## if authentiacation success, continue subscribing Chart
    if token is not None:
        chartURL = RetrieveChartLast(token, appid, ricName, num_bars)
        ## if chart request success, continue downloading Chart image
        if chartURL is not None:
            print('############### Downloading Chart file from TRKD ###############')
            downloadChartImage(chartURL)


## Perform Chart request
def RetrieveChartLast(token, appid, ricName, num_bars):
    ##construct a Chart request message

    gamma = gmtime()
    seconds = mktime(gamma)

    alpha_to = strftime('%Y-%m-%d', gamma)
    beta_to = strftime('%H:%M:%S', gamma)

    date_to = alpha_to + 'T' + beta_to

    delta = gmtime(seconds - num_bars * 3600)

    alpha_from = strftime('%Y-%m-%d', delta)
    beta_from = strftime('%H:%M:%S', delta)

    date_from = alpha_from + 'T' + beta_from

    chartRequestMsg = {'GetChart_Request_2': {'chartRequest': {
        'TimeSeries': {'TimeSeriesRequest_typehint': ['TimeSeriesRequest'],
                       'TimeSeriesRequest': [{'Symbol': ricName,
                                              'Reference': 'd1'}]},
        'Analyses': {'Analysis_typehint': ['Analysis', 'Analysis'],
                     'Analysis': [{'Reference': 'a1',
                                   'OHLC': {'Instrument1': {'Reference': 'd1'}}},
                                  {'Reference': 'a2',
                                   'Vol': {'Instrument1': {'Reference': 'd1'}}}]},
        'StandardTemplate': {
            'Interval': {'CommonType': 'Hours', 'Multiplier': '1'},
            'ShowNonTradedPeriods': False,
            'ShowHolidays': False,
            'ShowGaps': True,
            'XAxis': {'Range': {'Fixed': {'First': date_from,
                                          'Last': date_to}}, 'Visible': True,
                      'Position': 'Bottom'},
            'Subchart': [{'YAxis': [{
                'Analysis': [{'Reference': 'a1'}],
                'Visible': True,
                'Position': 'Right',
                'Invert': False,
                'Logarithmic': False,
                'Display': {'Mode': 'Automatic'},
                'Range': {'Automatic': ''},
            }], 'Weight': 5.0}, {'YAxis': [{
                'Analysis': [{'Reference': 'a2'}],
                'Visible': True,
                'Position': 'Right',
                'Invert': False,
                'Logarithmic': False,
                'Display': {'Mode': 'Automatic'},
                'Range': {'Automatic': ''},
            }], 'Weight': 2.0}],
            'Title': {'Caption': {'Visible': True, 'Customized': False},
                      'Range': {'Visible': True}},
            'Legend': {
                'Visible': True,
                'Information': 'Long',
                'Layout': 'MultiLine',
                'Position': 'Overlaid',
            },
            'Instrument': 'Symbol',
            'Delimiter': '%',
            'GridLines': 'None',
            'YAxisMarkers': 'None',
            'YAxisTitles': 'All',
            'Brand': 'None',
        },
        'Scheme': {
            'Background': {
                'BackgroundMode': 'Solid',
                'StartColor': {'Named': 'White'},
                'EndColor': {'Named': 'White'},
                'HatchStyle': 'LargeGrid',
                'GradientMode': 'ForwardDiagonal',
                'ImageMode': 'Centered',
            },
            'Border': {'Color': {'RGB': '139;139;155'},
                       'DashStyle': 'Solid', 'Width': 1.0},
            'GridLines': {'Color': {'RGB': '139;139;155'},
                          'DashStyle': 'Dot', 'Width': 1.0},
            'Title': {'Caption': {
                'Color': {'Named': 'Black'},
                'Family': 'Arial',
                'Style': 'Bold',
                'Size': 12.0,
            }, 'Range': {
                'Color': {'Named': 'Black'},
                'Family': 'Arial',
                'Style': 'Regular',
                'Size': 8.25,
            }},
            'Legend': {
                'Color': {'Named': 'Black'},
                'Family': 'Arial',
                'Style': 'Regular',
                'Size': 8.25,
            },
            'XAxis': {'Major': {
                'Color': {'Named': 'Black'},
                'Family': 'Arial',
                'Style': 'Bold',
                'Size': 9.75,
            }, 'Minor': {
                'Color': {'Named': 'Black'},
                'Family': 'Arial',
                'Style': 'Regular',
                'Size': 8.25,
            }},
            'YAxis': {'Major': {
                'Color': {'Named': 'Black'},
                'Family': 'Arial',
                'Style': 'Bold',
                'Size': 9.75,
            }, 'Minor': {
                'Color': {'Named': 'Black'},
                'Family': 'Arial',
                'Style': 'Regular',
                'Size': 8.25,
            }, 'Title': {
                'Color': {'Named': 'Black'},
                'Family': 'Arial',
                'Style': 'Regular',
                'Size': 8.25,
            }},
            'Series': [
                {
                    'Color': {'Named': 'Black'},
                    'DashStyle': 'Solid',
                    'Width': 0.0,
                    'FillColor': {'Named': 'Black'},
                    'FillStyle': 'Percent20',
                },
                {
                    'Color': {'Named': 'Red'},
                    'DashStyle': 'Solid',
                    'Width': 0.0,
                    'FillColor': {'Named': 'Red'},
                    'FillStyle': 'Percent20',
                },
                {
                    'Color': {'RGB': '62;169;0'},
                    'DashStyle': 'Solid',
                    'Width': 0.0,
                    'FillColor': {'RGB': '62;169;0'},
                    'FillStyle': 'Percent20',
                },
                {
                    'Color': {'RGB': '156;38;115'},
                    'DashStyle': 'Solid',
                    'Width': 0.0,
                    'FillColor': {'RGB': '156;38;115'},
                    'FillStyle': 'Percent20',
                },
                {
                    'Color': {'RGB': '255;120;0'},
                    'DashStyle': 'Solid',
                    'Width': 0.0,
                    'FillColor': {'RGB': '255;120;0'},
                    'FillStyle': 'Percent20',
                },
                {
                    'Color': {'RGB': '25;108;229'},
                    'DashStyle': 'Solid',
                    'Width': 0.0,
                    'FillColor': {'RGB': '25;108;229'},
                    'FillStyle': 'Percent20',
                },
                {
                    'Color': {'RGB': '60;117;28'},
                    'DashStyle': 'Solid',
                    'Width': 0.0,
                    'FillColor': {'RGB': '60;117;28'},
                    'FillStyle': 'Percent20',
                },
                {
                    'Color': {'RGB': '230;176;18'},
                    'DashStyle': 'Solid',
                    'Width': 0.0,
                    'FillColor': {'RGB': '230;176;18'},
                    'FillStyle': 'Percent20',
                },
                {
                    'Color': {'RGB': '0;186;193'},
                    'DashStyle': 'Solid',
                    'Width': 0.0,
                    'FillColor': {'RGB': '0;186;193'},
                    'FillStyle': 'Percent20',
                },
                {
                    'Color': {'RGB': '255;178;127'},
                    'DashStyle': 'Solid',
                    'Width': 0.0,
                    'FillColor': {'RGB': '255;178;127'},
                    'FillStyle': 'Percent20',
                },
                {
                    'Color': {'RGB': '100;79;190'},
                    'DashStyle': 'Solid',
                    'Width': 0.0,
                    'FillColor': {'RGB': '100;79;190'},
                    'FillStyle': 'Percent20',
                },
                {
                    'Color': {'RGB': '209;36;33'},
                    'DashStyle': 'Solid',
                    'Width': 0.0,
                    'FillColor': {'RGB': '209;36;33'},
                    'FillStyle': 'Percent20',
                },
                {
                    'Color': {'RGB': '38;87;135'},
                    'DashStyle': 'Solid',
                    'Width': 0.0,
                    'FillColor': {'RGB': '38;87;135'},
                    'FillStyle': 'Percent20',
                },
                {
                    'Color': {'RGB': '94;176;176'},
                    'DashStyle': 'Solid',
                    'Width': 0.0,
                    'FillColor': {'RGB': '94;176;176'},
                    'FillStyle': 'Percent20',
                },
            ],
            'LevelLine': [{'Color': {'RGB': '0;0;153'}, 'DashStyle': 'Solid'
                              , 'Width': 1.0}, {'Color': {'RGB': '120;120;120'
                                                          }, 'DashStyle': 'Solid', 'Width': 1.0}],
        },
        'ImageType': 'PNG',
        'Width': 500,
        'Height': 400,
        'Culture': 'en-US',
        'ReturnPrivateNetworkURL': False,
    }}}
    ##construct Chart URL and header
    chartURL = 'http://api.trkd.thomsonreuters.com/api/Charts/Charts.svc/REST/Charts_1/GetChart_2'
    headers = {'content-type': 'application/json;charset=utf-8', 'X-Trkd-Auth-ApplicationID': appid,
               'X-Trkd-Auth-Token': token}

    print('############### Sending Chart request message to TRKD ###############')
    chartResult = doSendRequest(chartURL, chartRequestMsg, headers)
    if chartResult is not None and chartResult.status_code == 200:
        print('Time Series Interday response message: ')
        print(chartResult.json())
        ##print returned server, tag and image url
        server = chartResult.json()['GetChart_Response_2']['ChartImageResult']['Server']
        print('\nServer: %s' % (server))
        tag = chartResult.json()['GetChart_Response_2']['ChartImageResult']['Tag']
        print('Tag: %s' % (tag))
        imageUrl = chartResult.json()['GetChart_Response_2']['ChartImageResult']['Url']
        print('Url: %s' % (imageUrl))
        return imageUrl

## ------------------------------------------ Main App ------------------------------------------ ##

# if __name__ == '__main__':
#     # Get username, password and applicationid
#     # username = input('Please input username: ')
#     username = 'trkd-demo-wm@thomsonreuters.com'
#     # use getpass.getpass to hide user inputted password
#     # password = getpass.getpass(prompt='Please input password: ')
#     password = 'o3o4h91ac'
#     # appid = input('Please input appid: ')
#     appid = 'trkddemoappwm'
#     ricName = 'GBPRUB=R'
#     date_from = '2017-09-02'
#     date_to = '2017-12-02'
#     date_from += 'T00:00:00'
#     date_to += 'T23:59:00'
#     num_bars = 400
#     name = 'AWG'

#     #GetPriceFromTo(ricName, date_from, date_to)
#     #GetChartFromTo(ricName, date_from, date_to)
#     #GetPriceLast(ricName, num_bars)
#     #GetChartLast(ricName, num_bars)
#     GetExchange(name)














def parse(message):
    m = re.match('.*intentName":"([a-zA-Z]+)"', message, flags=re.UNICODE)
    if m is not None:
        return m.group(1)

def parseArgGetChartFromTo(message):
    m = re.match('.*"security":"([a-zA-Z]+.[a-zA-Z]).*date_to":"(\d+-\d+-\d+)","date_from":\["(\d+-\d+-\d+)', message, flags=re.UNICODE)
    if m is not None:
        return ('.'.join(m.group(1).split(' ')), m.group(2), m.group(3))

def parseArgGetPriceFromTo(message):
    m = re.match('.*"text":"([a-zA-Z]+.[a-zA-Z]).*currency_to":"(\d+-\d+-\d+)","currency_from":\["(\d+-\d+-\d+)', message, flags=re.UNICODE)
    if m is not None:
        return (m.group(1), m.group(2), m.group(3))

def parseArgGetExchange(message):
    m = re.match('.*currency_from":"([a-zA-Z]+)"', message, flags=re.UNICODE)
    if m is not None:
        return m.group(1)

class DialogFlowHandler(BaseHTTPRequestHandler):

    def do_GET(s):
        s.send_response(200)
        s.end_headers()
        s.wfile.write('Test string')

    def do_POST(s):
        content_len = int(s.headers['Content-Length'])
        post_body = s.rfile.read(content_len)
        s.send_response(200)
        s.send_header('Content-type', 'application/json')
        s.end_headers()
        message = str(post_body)
        function = parse(message)
        response = 'Something bad happend at the back-end\n'
        if function == 'GetPriceFromTo':
            print(message)
            sec, frm, to = parseArgGetPriceFromTo(message);
            print(sec, frm, to)
            response = GetPriceFromTo(sec, frm + 'T00:00:00', to + 'T00:00:00')
        elif function == 'GetExchange':
            name = parseArgGetExchange(message)
            print(name)
            response = GetExchange(name)
        elif function == 'Chart':
            print(message)
            sec, frm, to = parseArgGetChartFromTo(message);
            print(sec, frm, to)
            response = GetChartFromTo(sec, frm + 'T00:00:00', to + 'T00:00:00')
        df_response = dict({
            'speech': response,
            'displayText': response,
            'data': {},
            'contextOut': [],
            'source': ''
        })
        s.wfile.write(bytes(json.dumps(df_response), 'utf-8'))
        
if __name__ == '__main__':
    print('debug')
    port = int(os.environ.get('PORT', 5000))
    server_class = HTTPServer
    httpd = server_class(('', port), DialogFlowHandler)
    print(time.asctime(), 'Server started on port %s' % port)
    try:
        print('iteration')
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close() 
