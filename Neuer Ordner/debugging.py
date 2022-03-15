from flask import Flask, request, render_template
from keybert import KeyBERT
from rdflib import Graph
from selenium import webdriver
from selenium.webdriver.common.by import By
import wikipedia
import pydotplus
from IPython.display import display
from rdflib.tools.rdf2dot import rdf2dot
import io
import PIL.Image as Image
import os
import multiprocessing
import time
import requests



def put(repository, data, context, auth=None):

    url = '{respository}/statements?context=<{context}>'.format(respository=repository, context=context)

    headers = {
        'Content-Type': 'application/x-turtle;charset=UTF-8, */*;q=0.5'
    }

    r = requests.put(url, data=data, headers=headers, auth=auth)

    if r.status_code != 204:
        raise requests.RequestException(r.text)


f = open("static/images/tbl.ttl", "r")
print(f.read())

repository = 'http://141.100.220.46:7200/repositories/isy_clara'
auth = ('student', 'student01')

data = open("static/images/tbl.ttl", "r")

context = 'http://data/IYS_Test.ttl'

put(repository, data, context, auth=auth)

