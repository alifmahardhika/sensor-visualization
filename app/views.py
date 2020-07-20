# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse, JsonResponse
from django import template
import json
import mariadb
from django.template.response import TemplateResponse
import calendar
from datetime import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# =========set up file dbconfig.txt dengan format host,user,pass,dbname ========
DB_HOST = ''
DB_USER = ''
DB_PASS = ''
DB_NAME = ''
# =========================================


@login_required(login_url="/login/")
def index(request):
    return render(request, "index.html")


def query_to_Json(query_result):
    obj_dict = {
        "mac_address": query_result[1],
        "time_stamp": query_result[2],
        "temperature":  query_result[3],
        "id": query_result[0]
    }
    jsoned = json.dumps(obj_dict)
    return jsoned


def set_DB_config():
    getDBConfig()
    try:
        conn = mariadb.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
        )
        print("\n=========================Database connection to " +
              DB_HOST + " SUCCESS===================================\n")
        return conn
    except mariadb.Error as e:
        print("\n=========================Database connection to " +
              DB_HOST + " FAILEDS===================================\n")
        print(e)
        return None


@login_required(login_url="/login/")
def pages(request):
    context = {}
    conn = set_DB_config()
    if conn == None:
        html_template = loader.get_template('error-500.html')
        return HttpResponse(html_template.render(context, request))
    cur = conn.cursor()
    try:
        insert_query = 'select * from temperature_records'
        cur.execute(insert_query)
        sqlresult = cur.fetchall()

    except Exception as e:
        print(e)

    cur.close()
    conn.close()
    try:
        load_template = request.path.split('/')[-1]

        # SPECIAL PAGE CASES
        if(load_template == "history.html"):
            return(table_render(request, sqlresult))
        if(load_template == "summary.html"):
            date_filter = ''
            try:
                date_filter = request.GET["date-filter"]
            except Exception as e:
                print(e)
            return render(request, "summary.html", {'date_filter': date_filter})

        html_template = loader.get_template(load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('error-404.html')
        return HttpResponse(html_template.render(context, request))

    except:

        html_template = loader.get_template('error-500.html')
        return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def table_render(request, jsonData):
    date_filter = ''
    objlist = []
    print(request.GET.get('page'))

    try:
        date_filter = request.GET["date-filter"]
        if (date_filter != ''):
            a = date_filter.split('-')
            a[1] = calendar.month_abbr[int(a[1])]
            date_filter = a[2] + '-' + a[1] + '-' + a[0]
        # VALIDATE DATE FILTER INPUT
        try:
            d = datetime.strptime(date_filter, '%d-%b-%Y')
        except Exception as e:
            # INVALID INPUT nanti return error page
            print(e)

        if(request.GET["date-filter"] != ''):
            for a in jsonData:
                queried = json.loads(query_to_Json(a))
                datedata = queried[
                    'time_stamp'].split(' ')
                if(datedata[0] == date_filter):
                    objlist.append(queried)
        print('here')
        paginator = Paginator(objlist, 10)
        print(paginator.num_pages)
        page = request.GET.get('page', 1)
        try:
            data = paginator.page(page)
        except PageNotAnInteger:
            data = paginator.page(1)
        except EmptyPage:
            data = paginator.page(paginator.num_pages)

        return TemplateResponse(request, 'history.html', {'data': data, 'date': request.GET["date-filter"]})
    except Exception as e:
        print(e)

    for a in jsonData:
        objlist.append(json.loads(query_to_Json(a)))
    return TemplateResponse(request, 'history.html', {'data': objlist, 'date': request.GET["date-filter"]})


@ login_required(login_url="/login/")
def temperature_json(request):
    conn = set_DB_config()
    cur = conn.cursor()
    time_stamp = []
    temperature = []

    try:
        insert_query = 'select * from temperature_records'
        cur.execute(insert_query)
        sqlresult = cur.fetchall()

    except Exception as e:
        print(e)

    cur.close()
    conn.close()

    data_id = '0'
    try:
        query_process(request, sqlresult, time_stamp, temperature, data_id)
    except Exception as e:
        print(e)
        return JsonResponse(data={
        })

    if (data_id == '0'):
        data_id = 'All'

    return JsonResponse(data={
        'time_stamp': time_stamp,
        'temperature': temperature,
        'min': min(temperature),
        'max': max(temperature),
        'avg': float("{:.2f}".format(sum(temperature)/len(temperature))),
        'num': len(temperature),
        'date_req': data_id
    })


def query_process(request, sqlresult, time_stamp, temperature, data_id):
    date_filter = request.GET["date-filter"]
    if (date_filter != ''):
        a = date_filter.split('-')
        a[1] = calendar.month_abbr[int(a[1])]
        date_filter = a[2] + '-' + a[1] + '-' + a[0]
        # VALIDATE DATE FILTER INPUT
        try:
            d = datetime.strptime(date_filter, '%d-%b-%Y')
        except Exception as e:
            # INVALID INPUT nanti return error page
            print(e)

        # ===================================start querying=========================
        for a in sqlresult:
            datef = json.loads(query_to_Json(a))['time_stamp'][:12]
            if (datef[0:11] == date_filter):
                time_stamp.append(json.loads(query_to_Json(a))
                                  ['time_stamp'][:17])
                temperature.append(json.loads(query_to_Json(a))['temperature'])
        data_id = date_filter
    else:
        for a in sqlresult:
            time_stamp.append(json.loads(query_to_Json(a))['time_stamp'][:17])
            temperature.append(json.loads(query_to_Json(a))['temperature'])


'''
==================================================
get db credentials dari file db config
==================================================
'''


def getDBConfig():
    f = open("dbconfig.txt", "r")
    config = f.readline().split(',')
    global DB_HOST
    global DB_USER
    global DB_PASS
    global DB_NAME
    DB_HOST = config[0]
    DB_USER = config[1]
    DB_PASS = config[2]
    DB_NAME = config[3]
    f.close()
