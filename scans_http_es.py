#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import time
import json
import base64
import HTMLParser
from datetime import datetime
from elasticsearch import Elasticsearch

es = Elasticsearch([{'host':'192.168.199.117','port':9200}])

#es.indices.create(index='httpinfo')


def push(data):
    fuck = json.dumps(data)
    parser = HTMLParser.HTMLParser()
    httpdata = base64.b64decode(data.get('data'))
    httpstatus = re.findall('HTTP/1.(.*?)\r\n',httpdata, re.IGNORECASE)
    httptitle = re.findall('<title>(.*?)</title>',httpdata, re.IGNORECASE)
    httpdomain = re.findall('Cookie:.*domain=(.*?);',httpdata, re.IGNORECASE)
    httplocal = re.findall('Location: (.*?)',httpdata, re.IGNORECASE)
    charset = re.findall('charset=(.*?)',httpdata, re.IGNORECASE)
    status = httpstatus[0].split(' ')[1] if httpstatus else '200'
    charsets = charset[0] if charset else ''
    domain = httpdomain[0] if httpdomain else ''
    local = httplocal[0] if httplocal else ''

    if charsets:
    	charts = charsets[0]
    else:
    	charts = 'gb2312'

    try:
    	stitle = httptitle[0].decode(charts, 'ignore').encode('utf-8', 'ignore') if httptitle else ''
    except:
    	stitle = httptitle[0].decode('utf-8', 'ignore').encode('utf-8', 'ignore') if httptitle else ''

    if '&#' in stitle :
    	try:
    		title = parser.unescape(str(stitle))
    	except Exception as e:
    		title = stitle
    else:
    	title = stitle

    try:
    	title = title.decode(charts, 'ignore').encode('utf-8', 'ignore')
    except Exception as e:
    	title = title

    mydict = {"status":status, "title":title,"ip":data.get('ip'),"port":data.get('port'),"domain":domain,"Location":local,"content":data.get('data'),"gettimestamp":data.get('timestamp'),"addtimestamp":datetime.now()}
    
    es.index(index="httpinfo",doc_type="httpdata",body=mydict)
    print status,title,data.get('ip'),data.get('port')

def deal_with(file):
	with open('./'+file, 'rb') as f:
		for line in f:
			#利用eval把str转换成dict
			push(eval(line))

def start():
	import os
	#扫描当前目录下的文件
	lst=os.listdir(os.getcwd())
	for files in lst:
		try:
			deal_with(files)
		except  Exception as e:
			print files,str(e)
			pass

if __name__ == '__main__':
	start()
