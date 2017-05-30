#! /usr/bin/env python
#-*- coding: utf-8 -*-
import socket,ssl,re
import pymongo
import requests
from logger import *
from datetime import datetime
from threadpool import ThreadPool
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

timeout = 10

db_info = dict(
    host="127.0.0.1",
    port=27017
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


portlist = ['80','81','85','89','443','7001','7002','8000','8001','8080','8081','8002','8003','8010','8443','8888','9200','9300','27017','27018']

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


def scan_port(host,port):
    headers = {'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20'}
    try:
        socket.setdefaulttimeout(timeout/2)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((str(host),int(port)))
        print_warm('[*] portscan %s %s' %(str(host),str(port)))
        result = "{scheme}://"+str(host)+":"+str(port)
        try:
            response = requests.get(result.format(scheme='http'),headers=headers,timeout=timeout/2,verify=False)
            if response.status_code:
                if ('<title>400' in response.content or '<TITLE>400' in response.content) and ('HTTP request was sent to HTTPS port' in response.content or 'HTTPS scheme to access this URL' in response.content):
                    res = requests.get(result.format(scheme='https'),headers=headers,timeout=timeout/2,verify=False)
                    getresult = {'url':result.format(scheme='https'),'result':res}
                elif ':443' in result:
                    getresult = {'url':result.format(scheme='https'),'result':response}
                else:
                    getresult = {'url':result.format(scheme='http'),'result':response}
                return getresult
        except:
            response = requests.get(result.format(scheme='https'),headers=headers,timeout=timeout/2,verify=False)
            if response.status_code:
                getresult = {'url':result.format(scheme='http'),'result':response}
                return getresult
        else:
            return 'NULL'
    except Exception,e:
        sock.close()
        return False


def get_ip_list(ip):
    ip_list = []
    iptonum = lambda x:sum([256**j*int(i) for j,i in enumerate(x.split('.')[::-1])])
    numtoip = lambda x: '.'.join([str(x/(256**i)%256) for i in range(3,-1,-1)])
    if '-' in ip:
        ip_range = ip.split('-')
        ip_start = long(iptonum(ip_range[0]))
        ip_end = long(iptonum(ip_range[1]))
        ip_count = ip_end - ip_start
        if ip_count >= 0 and ip_count <= 65536:
            for ip_num in range(ip_start,ip_end+1):
                ip_list.append(numtoip(ip_num))
        else:
            print '-h wrong format'
    elif '.ini' in ip:
        ip_config = open(ip,'r')
        for ip in ip_config:
            ip_list.extend(get_ip_list(ip.strip()))
        ip_config.close()
    else:
        ip_split=ip.split('.')
        net = len(ip_split)
        if net == 2:
            for b in range(1,255):
                for c in range(1,255):
                    ip = "%s.%s.%d.%d"%(ip_split[0],ip_split[1],b,c)
                    ip_list.append(ip)
        elif net == 3:
            for c in range(1,255):
                ip = "%s.%s.%s.%d"%(ip_split[0],ip_split[1],ip_split[2],c)
                ip_list.append(ip)
        elif net ==4:
            ip_list.append(ip)
        else:
            print "-h wrong format"
    return ip_list

def check(host):
    for port in portlist:
        result = scan_port(host,port)
        if result and result is not 'NULL':
            print_debug(result.get('url'))
            res = result.get('result')
            server = res.headers.get('Server')
            local = res.headers.get('Location')
            httptitle = re.findall('<title>(.*?)</title>',res.content,re.IGNORECASE)
            r = re.search('<meta[^\r\n]+charset=[\'"]*([^\r\n\'">]+)', res.content, re.IGNORECASE)
            if r:
                charset = r.group(1).lower()
            else:
                charset = 'utf-8'

            title = httptitle[0] if httptitle else ''

            mydict = {"url":result.get('url'),"server":server,"title":str(title).decode(charset, 'ignore').encode('utf-8', 'ignore'),"status":res.status_code,"ip":host,"port":port,"headers":res.headers,"content":str(res.content).decode(charset, 'ignore').encode('utf-8', 'ignore'),"timestamp":datetime.now()}
            mongodbid = mongodb.insert(mydict)
            
            print server,str(title).decode(charset, 'ignore').encode('utf-8', 'ignore'),mongodbid

if __name__ == "__main__":
    
    import sys
    if len(sys.argv)==2:
        ip_list = get_ip_list(sys.argv[1])
        tp = ThreadPool(50)
        for ip in ip_list:
            tp.push(check, str(ip))
        tp.wait()
        tp.busy()
    else:
        print "*"*50
        print "** python %s 192.168.1.1-192.168.5.1 **" % (sys.argv[0])
        print "*"*50
    
