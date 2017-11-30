# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 16:32:38 2017
"""

#%%
import os
from bs4 import BeautifulSoup
import requests
import urllib.request
import urllib.parse
import socket
from multiprocessing.dummy import Pool
import json
import time
import xlsxwriter
#----------------------------------------------------------#
headers={
'Referer':'https://www.lagou.com/jobs/list_Python?',
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
}

###
###（1）获取代理IP
###
def getProxies():
    url = 'http://www.xicidaili.com/nn/'
    web_data = requests.get(url, headers=headers)
    soup = BeautifulSoup(web_data.text, 'lxml')
    ips = soup.find_all('tr')
    global proxy_addr
    proxy_addr = []
    for i in range(1, len(ips)):
        ip_info = ips[i]
        tds = ip_info.find_all('td')
        if not tds[5].text.lower().startswith("https"):
            proxy_addr.append(tds[5].text.lower()+'://' + tds[1].text + ':' + tds[2].text)
    return proxy_addr



def testProxy(curr_ip):
  '''
  功能：利用百度首页，逐个验证代理IP的有效性
  @curr_ip：当前被验证的IP
  '''
  socket.setdefaulttimeout(5)  #设置全局超时时间
  tarURL = "https://www.baidu.com/"  #测试网址
  try:
      proxy_support = {"http":curr_ip}
      res = requests.get(tarURL, headers=headers, proxies=proxy_support)
      if not res.status_code == 200:
          print(res.status_code)
  except Exception as er:
      print("验证代理IP("+curr_ip+")时发生错误："+str(er))
  return proxy_support 
 


def mulTestProxies(proxies_ip):
  '''
  功能：构建多进程验证所有代理IP
  @proxies_ip：代理IP池
  '''
  pool = Pool(processes=4)  #开启四个进程
  proxies_addr = pool.map(testProxy,proxies_ip)
  pool.close()
  pool.join()  #等待进程池中的worker进程执行完毕
  return proxies_addr
#----------------------------------------------------------#


###
###（2）爬取数据
###
def getInfoDict(url,page,pos_words_one,proxy_addr_one):
  '''
  功能：获取单页职位数据，返回数据字典
  @url：目标URL
  @page：爬取第几页
  @pos_words_one：搜索关键词（单个）
  @proxy_addr_one：使用的代理IP（单个）
  '''
  global pos_dict
  page = 1
  if page==1:
      tORf = "true"
  else:
      tORf = "false"
  mydata = {"first": tORf,"pn": page,"kd": pos_words_one}
  try:
      response = requests.post(url, data=mydata, headers=headers, proxies=proxy_addr_one, timeout=5)
      pos_dict = json.loads(response.text)  #将str转成dict
  except urllib.error.URLError  as er:
      if hasattr(er,"code"):
          print("获取职位信息json对象时发生URLError错误，错误代码：")
          print(er.code)
      if hasattr(er,"reason"):
          print("获取职位信息json对象时发生URLError错误，错误原因：")
          print(er.reason)
  return pos_dict


def getInfoList(pos_dict): 
  '''
  功能：将getInfoDict()返回的数据字典转换为数据列表
  @pos_dict：职位信息数据字典
  '''
  pos_list = []  #职位信息列表
  jcontent = pos_dict["content"]["positionResult"]["result"]    
  for i in jcontent:        
      one_info = []  #一个职位的相关信息      
      one_info.append(i["companyFullName"])        
      one_info.append(i['companySize'])        
      one_info.append(i['positionName'])        
      one_info.append(i['education'])        
      one_info.append(i['financeStage'])        
      one_info.append(i['salary'])        
      one_info.append(i['city'])        
      one_info.append(i['district'])        
      one_info.append(i['positionAdvantage'])        
      one_info.append(i['workYear'])        
      pos_list.append(one_info)
  return pos_list


def getPosInfo(pos_words,city_words,proxy_addr):
  '''
  功能：基于函数getInfoDict()与getInfoList()，循环遍历每一页获取最终所有职位信息列表
  @pos_words：职位关键词（多个）
  @city_words：限制城市关键词（多个）
  @proxy_addr：使用的代理IP池（多个）
  '''
  posInfo_result = []    
  title = ['公司全名', '公司规模', '职位名称', '教育程度', '融资情况', "薪资水平", "城市", "区域", "优势", "工作经验"]    
  posInfo_result.append(title)  
  for i in range(len(city_words)):
      #i = 0
      key_city = urllib.request.quote(city_words[i])
      #筛选关键词设置：gj=应届毕业生&xl=大专&jd=成长型&hy=移动互联网&px=new&city=广州
      url = "https://www.lagou.com/jobs/positionAjax.json?city="+key_city+"&needAddtionalResult=false"
      for j in range(len(pos_words)):
          #j = 0
          page=1
          while page<3:  #每个关键词搜索拉钩显示30页，在此只爬取3页
              pos_words_one = pos_words[j]
              #k = 1 
              proxy_addr_one = proxy_addr[page]
              #page += 1 
              time.sleep(3)
              pos_info = getInfoDict(url,page,pos_words_one,proxy_addr_one)  #获取单页信息列表
              pos_infoList = getInfoList(pos_info)
              posInfo_result += pos_infoList  #累加所有页面信息       
              page += 1   
  return posInfo_result
#----------------------------------------------------------#


###
###(3)存储数据
###
def wXlsConcent(export_path,posInfo_result):
  '''
  功能：将最终结果写入本地excel文件中
  @export_path：导出路径
  @posInfo_result：爬取的数据列表
  '''
  # 打开最终写入的文件
  wb1 = xlsxwriter.Workbook(export_path)
  # 创建一个sheet工作对象
  ws = wb1.add_worksheet()
  try:
      for i in range(len(posInfo_result)):
          for j in range(len(posInfo_result[i])):
              data = posInfo_result[i][j]
              ws.write(i,j,data)
      print("Done!")
  except Exception as er:
      print('写入“'+export_path+'”文件时出现错误：')
      print(er)
  finally:
      if wb1:
          wb1.close()
#----------------------------------------------------------#


###
###(4)定义main()函数
###
def main():
  '''
  功能：主函数，调用相关函数，最终输出路径（与py文件同级目录）下的positionInfo.xls文件    
  '''
  #---（1）获取代理IP池
  proxies = getProxies()  #获取原始代理IP
  proxy_addr = mulTestProxies(proxies) #多线程测试原始代理IP
#  ---（2）爬取数据
  search_key = ["数据挖掘"]  #设置职位关键词（可以设置多个）
  city_word = ["广州"]  #设置搜索地区(可以设置多个)
  posInfo_result = getPosInfo(search_key,city_word,proxy_addr) #爬取职位信息
#  ---（3）存储数据
  export_path = os.path.join(".", "positionInfo.xls") #设置导出路径
  with open(export_path,"wb") as f:
      wXlsConcent(f,posInfo_result)  #写入到excel中   

        
if __name__ == "__main__":
  main()
