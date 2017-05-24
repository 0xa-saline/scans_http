# 对scans.io中获取的80端口的http信息进行处理

# 0.获取文件
https://scans.io/study/sonar.http

# 1.先对文件进行分割处理

zcat 2017-03-30-1490885671-http_get_80.json.gz  | split -l 200000


# 2.对单个文件进行读取入库
提取状态码，标题等基本信息
    fuck = json.dumps(data)
    parser = HTMLParser.HTMLParser()
    httpdata = base64.b64decode(data.get('data'))
    httpstatus = re.findall('HTTP/1.(.*?)\r\n',httpdata, re.IGNORECASE)
    httptitle = re.findall('<title>(.*?)</title>',httpdata, re.IGNORECASE)
    httpdomain = re.findall('Cookie:.*domain=(.*?);',httpdata, re.IGNORECASE)
    httplocal = re.findall('Location: (.*?)',httpdata, re.IGNORECASE)
    charset = re.findall('charset=(.*?)',httpdata, re.IGNORECASE)
    
#3 .更多细节参考
http://0cx.cc/deal_with_scans_http.jspx
