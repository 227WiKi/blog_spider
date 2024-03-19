# 22/7 Spider
------

# About

A spider to get all the articles and images from 22/7 members' blogs and convert them into markdown files that can be used in hexo.

Preview of markdown files in [22/7 WiKi blog](https://github.com/227WiKi/blog)

**All the markdown files can be found in this repo, check them by searching in the folders, most of the file names are renamed by md5, please check the file name at the link suffix on the [22/7 WiKi blog](https://github.com/227WiKi/blog)**

Updated from [227-blog-generator](https://github.com/zzzhxxx/227-blog-generator)

> [!Important]
> Due to the change of the domain, the script is no longer suitable to grab the latest contents. The new version will be a general spider to grab the contents from the official blog.

# Updates

- [x] 天城サリー
- [x] 河瀬詩
- [x] 宮瀬玲奈
- [x] 西條和
- [x] 白沢かなえ
- [x] 涼花萌
- [x] 雨夜音
- [x] 清井美那
- [x] 麻丘真央
- [x] 望月りの
- [x] 相川奈央
- [x] 椎名桜月
- [x] 四条月
- [x] 月城咲舞


# Require
- Python >= 3.8
- requests
- BeautifulSoup
# Usage
create the folder named by members' names and a folder called images inside it.

``python -m spider_[replace with member's name].py``

> You may need to change the number of pages the program crawls at a time, which may cause the program to crash.

# License

GPL V3.0
