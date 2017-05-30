## 对scans.io中获取的80端口的http信息进行处理

### 0x00.获取文件
https://scans.io/study/sonar.http

### 0x01.先对文件进行分割处理
```
zcat 2017-03-30-1490885671-http_get_80.json.gz  | split -l 200000
```

### 0x02.对单个文件进行读取入库
提取状态码，标题等基本信息
```
    fuck = json.dumps(data)
    parser = HTMLParser.HTMLParser()
    httpdata = base64.b64decode(data.get('data'))
    httpstatus = re.findall('HTTP/1.(.*?)\r\n',httpdata, re.IGNORECASE)
    httptitle = re.findall('<title>(.*?)</title>',httpdata, re.IGNORECASE)
    httpdomain = re.findall('Cookie:.*domain=(.*?);',httpdata, re.IGNORECASE)
    httplocal = re.findall('Location: (.*?)',httpdata, re.IGNORECASE)
    charset = re.findall('charset=(.*?)',httpdata, re.IGNORECASE)
```

### 0x03 .更多细节参考
http://0cx.cc/deal_with_scans_http.jspx



## 扫描常见http端口

可以访问的就提取状态码，容器类型，标题，headers等常见的信息
```
    try:
        socket.setdefaulttimeout(timeout/2)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((str(host),int(port)))
        print_warm('[*] portscan %s %s' %(str(host),str(port)))
        result = "{scheme}://"+str(host)+":"+str(port)
    except Exception,e:
        sock.close()
        return False
```

同样提取常见有用的信息
```
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
```

**how to run**
```
python main.py 192.168.1.1-192.168.200.254
```
