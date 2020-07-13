# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse
from django import template
import json
import mariadb
from django.template.response import TemplateResponse


@login_required(login_url="/login/")
def index(request):
    return render(request, "index.html")


def query_to_Json(query_result):
    obj_dict = {
        "mac_address": query_result[1],
        "time_stamp": query_result[2],
        "temperature":  query_result[3]
    }
    jsoned = json.dumps(obj_dict)
    return jsoned


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.

    # a = {
    #     "ID": 1,
    #     "Name": "John Smith",
    #     "IDNumber": "7606015012088"
    # }
    # print(json.dumps(a))

    try:
        conn = mariadb.connect(
            host="localhost",
            user="alif",
            password="alif",
            database="iotdb"
        )
        print("\n=========================Database connection to " +
              "localhost" + " SUCCESS===================================\n")
    except mariadb.Error as e:
        print(e)
    cur = conn.cursor()
    try:
        insert_query = 'select * from temperature_records'
        cur.execute(insert_query)
        sqlresult = cur.fetchall()
        # print("==================SQLRESULT====================:")
        # print(sqlresult[0])

    except Exception as e:
        print(e)

    cur.close()
    conn.close()
    try:
        load_template = request.path.split('/')[-1]
        if(load_template == "ui-tables.html"):
            return(table_render(request, sqlresult))
        print("==================not here===================:")

        html_template = loader.get_template(load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('error-404.html')
        return HttpResponse(html_template.render(context, request))

    except:

        html_template = loader.get_template('error-500.html')
        return HttpResponse(html_template.render(context, request))


def table_render(request, jsonData):

    objlist = []
    for a in jsonData:
        objlist.append(json.loads(query_to_Json(a)))
    for x in objlist:
        print(x)
    # label = []
    # data = []
    # for key in jsonData:
    #     label.append(key)
    # for value in jsonData:
    #     data.append(value)
    # print('============\n')
    # lbl = ''
    # for i in label:
    #     lbl = lbl + ', ' + i
    # dat = ''
    # for x in data:
    #     dat = dat + ', ' + x
    # print(lbl)
    # print(dat)
    return TemplateResponse(request, 'ui-tables.html', {'data': objlist})
    # html_template = loader.get_template(load_template)
    # myvar = {'myvar': a}
    # return HttpResponse(html_template.render(context, request), myvar)
    # print("==================here===================:")

    # return HttpResponse({'a': a}, 'templates/ui-tables.html', content_type="application/html")
