from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from time import sleep
from re import findall
from tools import fRead,fWrite,counter,savePic
from random import randint

driver = webdriver.Chrome(r'../../chromedriver.exe')
options = Options()
options.page_load_strategy = 'none'
prefs = {"profile.managed_default_content_settings.images":2}
options.add_experimental_option("prefs",prefs)
driver = webdriver.Chrome(options=options)

hForBili={
    'accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
'accept-encoding':'gzip, deflate, br',
'accept-language':'zh-CN,zh;q=0.9',
'cache-control':'no-cache',
'pragma':'no-cache',
'referer':'https://www.bilibili.com/',
'sec-ch-ua':'"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
'sec-ch-ua-mobile':'?0',
'sec-ch-ua-platform':'"Windows"',
'sec-fetch-dest':'image',
'sec-fetch-mode':'no-cors',
'sec-fetch-site':'cross-site',
'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
}
#初始化counter
count1,count2={},{}
c=counter(count1,1)
cX=counter(count2,0)

#取出
if fRead("result"):
    result=eval(fRead("result"))
    print(result)
else:
    result={}
#取出urls字典
assert fRead("urls")
#加载
sleep(randint(100,300)/100)
urls=eval(fRead("urls"))
#建立字典result={urlkey:{url: ,hraderUrl: ,logoUrl: ,video:{title:[link,picSrc],title:[link,picSrc],,,,,共6个}}}链接不带http，www
for keys in urls:
    #检查重复
    print("开始",keys)
    if keys in result:
        continue
    #打开页面
    url=urls[keys]
    try:driver.get(url)
    except: 
        pass
    #头图
    times=1
    while times<4:
        headerUrl,logoUrl='',''
        for i in range(200):
            try:
                logoUrl0=driver.find_element(by=By.XPATH, value='//*[@id="banner_link"]/div/a')
                logoUrl=findall(r'//web\.archive\.org/web/.{13,15}/\w{4,5}://(.*\..*\..*\.[pngwebjpg]{2,5})"',logoUrl0.get_attribute("style"))[0]
                cX.success('logo')
            except:
                cX.fail('logo')
            try:
                headerUrl0=driver.find_element(by=By.XPATH,value='/html/body/div[5]/div[1]/div[2]').get_attribute('style')
                headerUrl=findall(r'//web\.archive\.org/web/.{13,15}/\w{4,5}://(.*\..*\..*\.[pngwebjpg]{2,5})"',headerUrl0)[0]
                cX.success('header')
            except:
                cX.fail('header')
            if headerUrl and logoUrl:
                print("[O]logo&header成功")
                break
            sleep(0.1)
        else:
            try:driver.refresh()
            except: pass
            times+=1
            continue
        break
    
    times=1
    while times<4:
        #推荐视频 8个
        result[keys]={"video":{}}
        try:
            video=WebDriverWait(driver, timeout=15).until(lambda d: d.find_element(by=By.XPATH, value='//*[@id="chief_recommend"]/div[2]').find_elements(by=By.TAG_NAME,value='div'))
        except:
            video=[]
            c.fail('video')
            times+=1
            try:driver.refresh()
            except: pass
            print('刷新')
            #刷新，如果没有加载完成
            continue
        #视频循环
        
        vnum=0
        for item in video:
            if vnum >7:break
            print('video',vnum)   
            try:
                a=item.find_element(by=By.TAG_NAME,value="a")
                link=a.get_attribute("href")
                title=a.get_attribute("title")
                vnum+=1
            except:
                continue
            try:
                picSrc0=a.find_element(by=By.TAG_NAME,value="img").get_attribute("src")
                picSrc=findall(r'\w{4,5}://(.*\..*\..*\.[pngwebjpg]{2,5})@',picSrc0)[0]
            except:
                picSrc=''
            result[keys]["video"][title]=[link,picSrc]
            c.savePic(picSrc,"%s%.7scover"%(keys,title),hForBili)   
        c.success('video')
        break
    #广告栏也要
    result[keys].update({'panel':{}})
    for panelNum in range(1,5):
        try:
            panel0=driver.find_element(by=By.XPATH,value='//*[@id="chief_recommend"]/div[1]/div/div/ul[1]/li[%i]' % panelNum)
            panel1=driver.find_element(by=By.XPATH,value='//*[@id="chief_recommend"]/div[1]/div/div/ul[2]/a[%i]' % panelNum)
            c.success('panel')
        except:
            c.fail('panel')
            continue
        #图片src+链接
        try:
            a=panel0.find_element(by=By.TAG_NAME,value='a')
            adPage=a.get_attribute('href')
            adImg=a.find_element(by=By.TAG_NAME,value='img').get_attribute('src').replace('https://','').replace('http://','')
            c.savePic(adImg,"%s_%spannel"%(keys,panelNum),hForBili)
            c.success('pannel图链')
        except:
            c.fail('pannel图链')
            adPage,adImg='',''
        #标题
        try:
            panelTitle=panel1.text
            c.success('pannelTitle')
        except:
            c.fail('pannelTitle')
            panelTitle=str(panelNum)
        result[keys]['panel'][panelTitle]=[adPage,adImg]
    #logo图

    result[keys].update({"url":url,"headerUrl":headerUrl,"logoUrl":logoUrl,})
    c.savePic(headerUrl,"%sheader"%keys,hForBili)
    c.savePic(logoUrl,"%slogo"%keys,hForBili)
    c.show()
    cX.show()
    
    fWrite(str(result),"result")
        
driver.quit()
