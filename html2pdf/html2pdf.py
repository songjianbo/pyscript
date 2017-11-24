# -*- coding: utf-8 -*-
"""
Created on Fri Oct 20 09:29:41 2017
"""

#%%
import os  
import re  
import time  
import logging  
import pdfkit  
import requests  
from bs4 import BeautifulSoup  
from PyPDF2 import PdfFileMerger  


headers = {'User-Agent':
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36'}


html_template = """ 
<!DOCTYPE html> 
<html lang="en"> 
<head> 
    <meta charset="UTF-8"> 
</head> 
<body> 
{content} 
</body> 
</html> 

"""  

def func(m):
#    print('1111:'+m.group(1))
#    print('2222:'+m.group(2))
#    print('3333:'+m.group(3))
#    print('4444:'+m.group(4))
#    print('5555:'+m.group(5))
#    print('6666:'+m.group(6))
    if m.group(5).startswith("https"):  
        rtn = m.group(1) + m.group(2) + m.group(3) + m.group(4) +\
        m.group(2) + m.group(6)
        return rtn  
    else:
        return ""


# body中的img标签的src路径需要改变  
pattern = "(<img .*?data-src=\")(.*?)(\")( src=\")(.*?)(\")"
re_img = re.compile(pattern)


def parse_url_to_html(url, name):  
    """ 
    解析URL，返回HTML内容 
    :param url:解析的url 
    :param name: 保存的html文件名 
    :return: html 
    """  
    try:  
        response = requests.get(url,headers=headers)  
        soup = BeautifulSoup(response.content, 'html.parser')  
        # 正文  
        body = soup.find_all(class_="x-wiki-content")[0]
#        print(body)
        # 标题  
        title = soup.find('h4').get_text()  

        # 标题加入到正文的最前面，居中显示  
        center_tag = soup.new_tag("center")  
        title_tag = soup.new_tag('h1')  
        title_tag.string = title  
        center_tag.insert(0, title_tag)  
        body.insert(0, center_tag)  
        html = str(body)
        html = re_img.sub(func, html)
        html = html_template.format(content=html)  
        html = html.encode("utf-8")  
        with open(name, 'wb') as f:  
            f.write(html)  
        return name  

    except Exception as e:  

        logging.error("解析错误", exc_info=True)  


def get_url_list():  
    """ 
    获取所有URL目录列表 
    :return: 
    """  
    response = requests.get("http://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000",headers=headers)  
    print("状态码:"+str(response.status_code))
    soup = BeautifulSoup(response.content, "html.parser")  
    menu_tag = soup.find_all(class_="x-wiki-index-item")  
    urls = []  
    for li in menu_tag:  
        url = "http://www.liaoxuefeng.com" + li.get('href')  
        urls.append(url)
    return urls[:3]  


def save_pdf(htmls, file_name):  
    """ 
    把所有html文件保存到pdf文件 
    :param htmls:  html文件列表 
    :param file_name: pdf文件名 
    :return: 
    """  
    options = {  
        'page-size': 'Letter',  
        'margin-top': '0.75in',  
        'margin-right': '0.75in',  
        'margin-bottom': '0.75in',  
        'margin-left': '0.75in',  
        'encoding': "UTF-8",  
        'custom-header': [  
            ('Accept-Encoding', 'gzip')  
        ],  
        'cookie': [  
            ('cookie-name1', 'cookie-value1'),  
            ('cookie-name2', 'cookie-value2'),  
        ],  
        'outline-depth': 10,  
    }  
    pdfkit.from_file(htmls, file_name)  


def main():  
    start = time.time()  
    file_name = "liaoxuefeng_Python3_tutorial"  
    urls = get_url_list()
    for index, url in enumerate(urls):
        parse_url_to_html(url, str(index) + ".html")
    htmls =[]  
    pdfs =[]
    for i in range(len(urls)):  
        htmls.append(str(i)+'.html')  
        pdfs.append(file_name+str(i)+'.pdf')  

        save_pdf(str(i)+'.html', file_name+str(i)+'.pdf')  

        print("转换完成第"+str(i)+'个html')

    merger = PdfFileMerger()  
    for pdf in pdfs:
        merger.append(open(pdf, 'rb'))
        print("合并完成第"+str(pdfs.index(pdf))+'个pdf'+pdf)

    if len(pdfs)>0:
        with open("Python_all.pdf", "wb") as output:
            merger.write(output)
        print("输出PDF成功！")
    

    

#    for html in htmls:  
#        os.remove(html)  
#        print("删除临时文件"+html)

#    for pdf in pdfs:  
#        os.remove(pdf)  
#        print("删除临时文件"+pdf)

    total_time = time.time() - start  
    print("总共耗时：%f 秒" % total_time)

if __name__ == '__main__':  
    main()