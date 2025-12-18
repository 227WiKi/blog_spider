# 22/7 Spider

## About

A spider to get all the articles and images from 22/7 members' blogs and convert them into markdown files that can be used in hexo.

Preview of markdown files in [22/7 WiKi blog](https://github.com/227WiKi/blog)

**All the markdown files can be found in this repo, check them by searching in the folders, most of the file names are renamed by md5, please check the file name at the link suffix on the [22/7 WiKi blog](https://github.com/227WiKi/blog)**

Updated from [227-blog-generator](https://github.com/zzzhxxx/227-blog-generator)

## Updates

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
- [x] 折本美玲
- [x] 北原実咲
- [x] 黒崎ありす
- [x] 橘茉奈
- [x] 桧山依子
- [x] 三雲遥加
- [x] 南伊織
- [x] 吉沢珠璃

## Require

- Python >= 3.8
- requests
- BeautifulSoup
- tqdm
- python-dotenv

## Usage

### Install requirements

```
pip install -r requirements.txt
```

### Setup OneDrive Account

1. Go to your Azure Dashboard and create an application
2. Fill in Client ID and Tenant ID into `.env`
3. Create a secret at Certificates & secrets for the application and fill the secrect into the `.env`
4. Go to API permissions and add permissions for `Files.ReadWrite.All`, `Sites.ReadWrite.All` with Application permissions
5. Press Grant admin consent for your orgniazation while the status shows green marks

#### Sample .env

```
AZURE_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
AZURE_TENANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

AZURE_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

SHAREPOINT_SITE_URL=https://<orginazation name>-my.sharepoint.com/personal/<username>_<domain>
```

### Test OneDrive connection

```
python test_onedrive.py
```

### Get blogs

```
python main.py
```

# License

GPL V3.0
