import requests
import sys
from time import sleep
from random import randint
from re import findall

from tools import fRead,fWrite,counter

coun={}
cou=counter(coun,0)

urls={}#20180605 ：http://web.archive.org/web/20180605021923/https://www.bilibili.com/
keysite="bilibili.com"
year=2019
homepage='http://web.archive.org/web/%i0101000000*/%s'% (year,keysite)
ua={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}

#得到donation-identifier
if fRead('identifier'):
    diDict=eval(fRead('identifier'))
else:
    diDict={}
try:
    donationIdentifier=diDict[homepage]
except:
    r0=requests.get(homepage,headers=ua)
    donationIdentifier=findall(r'data-donationSourceData="ctx=\w{0,5};uid=(.{5,50})"',r0.text)
    diDict[homepage]=donationIdentifier

h = {
    'Accept':'*/*',
'Accept-Encoding':'gzip, deflate',
'Accept-Language':'zh-CN,zh;q=0.9',
'Cache-Control':'no-cache',
'Cookie':'donation-identifier='+donationIdentifier[0],
'Host':'web.archive.org',
'Pragma':'no-cache',
'Proxy-Connection':'keep-alive',
'Referer':homepage,
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}

    #是否有时日月
if not fRead("days"):
    #没有，下载日月
    r1=requests.get("http://web.archive.org/__wb/calendarcaptures/2?url=%s&date=%i&groupby=day"% (keysite,year),headers=h)
    fWrite(r1.text,"days")
    days=eval(r1.text)
else:
    days=eval(fRead("days"))
#检查错误
if  not days:
        print("days出错")
        sys.exit(0)
else:
    print(days['items'])
#下载时分秒
for item in days['items']:
    num1=year*10000+int(item[0]) #20180605
    #检查重复,
    if fRead("urls"):
        urls=eval(fRead("urls"))
        if num1 in list(urls.keys()):
            continue
    print("进行"+str(item[0]))
    times=1
    while times<=3:

        sleep(randint(100,300)/100)
        r2=requests.get("http://web.archive.org/__wb/calendarcaptures/2?url=%s&date=%i"%(keysite,num1),headers=h)
        print(r2.text)
        if r2.text:
            num2=num1*1000000+int(eval(r2.text)["items"][0][0]) #20180605021923
            urls[num1]="http://web.archive.org/web/%i/https://www.%s/"%(num2,keysite)
            cou.success('day')
            break
        else:
            cou.fail('day')
            print('空')
            times+=1
    else:
        days['items'].remove(item)
    fWrite(urls,"urls")

if not urls:
    print("urls出错")
    sys.exit(0)
else:
    print(urls)
    cou.show()


