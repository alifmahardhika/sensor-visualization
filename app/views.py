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

    except Exception as e:
        print(e)

    cur.close()
    conn.close()
    try:
        load_template = request.path.split('/')[-1]

        # SPECIAL PAGE CASES
        if(load_template == "temperature-table.html"):
            return(table_render(request, sqlresult))
        if(load_template == "temperature-chart.html"):
            return render(request, "temperature-chart.html")

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

    objlist = []
    for a in jsonData:
        objlist.append(json.loads(query_to_Json(a)))
    return TemplateResponse(request, 'temperature-table.html', {'data': objlist})


@login_required(login_url="/login/")
def temperature_json(request):
    labels = []
    data = []

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

    except Exception as e:
        print(e)

    cur.close()
    conn.close()

    for a in sqlresult:
        labels.append(json.loads(query_to_Json(a))['time_stamp'])
        data.append(json.loads(query_to_Json(a))['temperature'])

    for v in labels:
        print(v)

    return JsonResponse(data={
        'labels': labels,
        'data': data,
    })
