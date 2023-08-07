import requests
import io  
import sys  
import os
import time
import urllib
from bs4 import BeautifulSoup
import hashlib
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'}
url_base="https://blog.nanabunnonijyuuni.com/s/n227/diary/blog/list?ima=5649&page="
suffix="&ct=04&cd=blog"
page=0
url=url_base+str(page)
a=[]
title=[]
authors=[]
author_filename=[]
day=[]
des=[]
link=[]
cover=[]
image=[]
def get_inf():
    global title
    global authors
    global day
    global link
    global des
    global cover
    title=[]
    authors=[]
    day=[]
    des=[]
    link=[]
    url=url_base+str(page)+suffix
    data=requests.get(url,headers=headers)
    bs=BeautifulSoup(data.text,"html.parser")
    blog_title=bs.find_all('div',class_="blog-list__title")
    blog_descripiton=bs.find_all('div',class_="blog-list__txt")
    blog_link=bs.find_all('div',class_="blog-list__more")
    blog_thumb=bs.find_all('div',class_="blog-list__thumb")
    for i in blog_title:
        dates=i.find('p',class_="date").text
        day.insert(0,dates.replace(".","-"))
        name=i.find('p',class_="title").text
        title.insert(0,name)
        author=i.find('p',class_="name").text
        authors.insert(0,author)
    for i in blog_descripiton:
        desc=i.find('p',class_="txt").text
        desc=desc.replace("\n","")
        desc=desc.replace("\ufeff","")
        desc=desc.replace("\u3000"," ")
        desc=desc.replace("&nbsp"," ")
        des.insert(0,desc)
    for i in blog_link:
        l=i.find('a').get('href')
        link.insert(0,l)
    for i in blog_thumb:
        thumb=i.find("img").attrs["style"]
        if thumb == "background-image:url(/files/4/nanabunnonijyuuni/sp/img/blog/noimage.jpg);":
            cover.insert(0," ")
        if not(thumb == "background-image:url(/files/4/nanabunnonijyuuni/sp/img/blog/noimage.jpg);"):
            thumb =thumb.replace("background-image:url(","https://blog.nanabunnonijyuuni.com")
            thumb =thumb.replace(");"," ")
            cover.insert(0,thumb)
    # print(title, authors, day, link, des)
def get_img(i):
    filename = os.path.basename(i)
    print(i)
    try:
        request=urllib.request.Request(i,headers=headers)
        response=urllib.request.urlopen(request)
        with open(os.getcwd()+"/nagomi/images/"+filename, "wb+") as f:
            f.write(response.read())
    except:
        pass
def get_contents(links):
    global image
    data=requests.get(links,headers=headers)
    bs=BeautifulSoup(data.text,"html.parser")
    tweet =bs.find('div', class_="btnTweet")
    if tweet:
        bs.find('div', class_="btnTweet").decompose()
    blog_contents=bs.find('div',class_="blog_detail__main")
    img =blog_contents.find_all('img')
    if img:
        for i in img:
            l='https://blog.nanabunnonijyuuni.com'+i["src"]
            get_img(l)
            blog_contents=str(blog_contents).replace("</img>"," ")
            blog_contents=blog_contents.replace('<img src="' + i["src"] + '">',"![]("+get_link(l)+')')
        tr=BeautifulSoup(blog_contents,"html.parser")
        return tr.text
    else:
        return blog_contents.text

def get_link(links):
    filename = os.path.basename(links)
    l= 'https://files.zzzhxxx.top/img/' + filename
    return l
if __name__ == "__main__":
    for i in range(1):
        page=i
        get_inf()
        for j in range(len(title)):
            name="nagomi-"+day[j]+'-'+title[j]
            md=hashlib.md5(name.encode(encoding='UTF-8')).hexdigest()
            with open(os.getcwd()+"/nagomi/"+md+".md","w",encoding='utf-8') as f:
                f.write("---\n")
                f.write("title: "+title[j]+"\n")
                f.write("date: "+day[j]+"\n")
                f.write("tags: "+authors[j]+"\n")
                f.write("categories: \n- 成员博客\n- "+authors[j]+"\n")
                f.write("description: "+des[j]+"\n")
                if cover[j] != " ":
                        f.write("cover: "+get_link(cover[j])+"\n")
                f.write("---\n")
                f.write(get_contents(link[j])) 
    for i in cover:
        if i !=' ':
            get_img(i)
             

