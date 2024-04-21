import requests
import io  
import sys  
import os
import time
import urllib
from bs4 import BeautifulSoup
import hashlib
from tqdm import tqdm
import re
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'}
url="https://nanabunnonijyuuni-mobile.com/s/n110/diary/official_blog/list?page=0"
page=0
a=[]
title=[]
authors=[]
author_filename=[]
day=[]
des=[]
link=[]
cover=[]
image=[]
def name_map(name):
    if name == "天城サリー":
        return "sally"
    if name == "河瀬詩":
        return "uta"
    if name == "西條和":
        return "nagomi"
    if name == "涼花萌":
        return "moe"
    if name == "相川奈央":
        return "nao"
    if name == "麻丘真央":
        return "mao"
    if name == "椎名桜月":
        return "satsuki"
    if name == "四条月":
        return "luna"
    if name == "月城咲舞":
        return "emma"
    if name == "望月りの":
        return "rino"
def clear_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            clear_folder(file_path)
            os.rmdir(file_path)
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
def check_last_page():
    data=requests.get(url,headers=headers)
    bs=BeautifulSoup(data.text,"html.parser")
    blog_pages=bs.find_all('ul',class_="blog-list clearfix")
    if "記事がありません。" in str(blog_pages):
        return False
    else:
        return True    
def get_img(i,author):
    filename = os.path.basename(i)
    try:
        request=urllib.request.Request(i,headers=headers)
        response=urllib.request.urlopen(request)
        with open(os.getcwd()+"/"+author+"/images/"+filename, "wb+") as f:
            f.write(response.read())
    except:
        pass
def get_contents(links,author):
    global image
    data=requests.get(links,headers=headers)
    bs=BeautifulSoup(data.text,"html.parser")
    tweet =bs.find('div', class_="btnTweet")
    if tweet:
        bs.find('div', class_="btnTweet").decompose()
    blog_contents=bs.find('div',class_="blog_detail__main")
    tr = blog_contents
    p_tags = tr.find_all('p')
    for p_tag in p_tags:
        style_attr = p_tag.get('style')
        if style_attr:
            style_attr = re.sub(r'caret-color:[^;]+;', '', style_attr)
            style_attr = re.sub(r'color:[^;]+;', '', style_attr)
            p_tag['style'] = style_attr
        blog_contents = tr
    img = blog_contents.find_all('img')
    if img:
        for i in img:
            l='https://nanabunnonijyuuni-mobile.com'+i["src"]
            get_img(l,author)
            blog_contents=str(blog_contents).replace('src="'+i["src"]+'"','src="'+get_link(l,author)+'"')
        return blog_contents
    else:
        return str(blog_contents)
def get_link(links,folder):
    filename = os.path.basename(links)
    l= 'https://files.227wiki.eu.org/d/Backup/Blog/'+folder+ "/" + filename
    return l
def get_list():
    num=0
    global url
    while(check_last_page()):
        num = num + 1
        url = "https://nanabunnonijyuuni-mobile.com/s/n110/diary/official_blog/list?page="+str(num)
    return num
if __name__ == "__main__":
    for i in tqdm(range(get_list())):
        page=i
        url = "https://nanabunnonijyuuni-mobile.com/s/n110/diary/official_blog/list?page="+str(page)
        get_inf()
        for j in tqdm(range(len(title))):
            name=name_map(authors[j])+"-"+day[j]+'-'+title[j]
            md=hashlib.md5(name.encode(encoding='UTF-8')).hexdigest()
            if i == 0 and j == 0:
                with open(os.getcwd()+"/latest","r",encoding='utf-8') as f:
                    last=f.read()
                    if last == md:
                        f.close()
                        print("\n No new blog posts found. Exiting...")
                        sys.exit()
                    else:
                        needUpdate = True
                        clear_folder(os.getcwd()+"/updates")
                        f.close()
                if needUpdate:
                    with open(os.getcwd()+"/latest","w",encoding='utf-8') as f:
                        f.truncate(0)
                        f.write(md)
                        f.close()
            
            with open(os.getcwd()+"/"+name_map(authors[j])+"/"+md+".md","w",encoding='utf-8') as f:
                f.write("---\n")
                f.write("title: "+title[j]+"\n")
                f.write("date: "+day[j]+"\n")
                f.write("tags: "+authors[j]+"\n")
                f.write("categories: \n- 成员博客\n- "+authors[j]+"\n")
                f.write("description: "+des[j]+"\n")
                if cover[j] != " ":
                        f.write("cover: "+get_link(cover[j],name_map(authors[j]))+"\n")
                f.write("---\n")
                f.write(get_contents("https://nanabunnonijyuuni-mobile.com"+link[j],name_map(authors[j]))) 
            with open(os.getcwd()+"/"+name_map(authors[j])+"/"+md+".md", 'r', encoding='utf-8') as f1,open(os.getcwd()+"/updates/"+md+".md", "w", encoding="utf-8") as f2:
                content=f1.read()
                f2.write(content)
