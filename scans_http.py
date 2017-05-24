#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import time
import json
import base64
import pymongo
import HTMLParser

db_info = dict(
    host="127.0.0.1",
    port=27017
    #username = '',
    #password = '',

)

class Mongodb(object):
    def __init__(self, db_info):
        self.db_info = db_info
        self.client = pymongo.MongoClient(db_info.get('host'), db_info.get('port'))
        self.db = self.client["info"]
        self.collection = self.db["httpdata"]

    def insert(self, values):
        ret = self.collection.insert(values)
        return ret

mongodb = Mongodb(db_info)

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
    	charts = charsets
    else:
    	charts = 'gb2312'

    try:
    	stitle = httptitle[0].decode('gb2312') if httptitle else ''
    except:
    	stitle = httptitle[0].decode('utf-8','ignore').encode("utf-8") if httptitle else ''

    if '&#' in stitle :
    	try:
    		title = parser.unescape(str(stitle))
    	except Exception as e:
    		print stitle,str(e)
    		title = stitle
    else:
    	title = stitle

    try:
    	title = title.decode(charts)
    except Exception as e:
    	title = title

    mydict = {"status":status, "title":title,"ip":data.get('ip'),"port":data.get('port'),"domain":domain,"Location":local,"content":data.get('data'),"timestamp":data.get('timestamp')}
    mongodbid = mongodb.insert(mydict)
    print status,title,data.get('ip'),data.get('port')#,mongodbid


def deal_with(file):
	with open(file, 'rb') as f:
		for line in f:
			#利用eval把str转换成dict
			push(eval(line))

def start():
	import os
	#扫描当前目录下的文件
	lst=os.listdir(os.getcwd())
	for files in lst:
		deal_with(files)

if __name__ == '__main__':
	start()
