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

### Configure Cloudflare R2

Create an R2 API token with Object Read & Write access to the blog resource
bucket. The scraper uploads objects below `archive/blog/<author>/<filename>` and
writes public URLs below `https://res.227wiki.eu.org/archive/blog`.

#### Sample .env

```
R2_ACCOUNT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
R2_ACCESS_KEY_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
R2_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
R2_BUCKET_NAME=archive

# Optional overrides
BLOG_RESOURCE_BASE_URL=https://res.227wiki.eu.org/archive/blog
R2_BLOG_PREFIX=archive/blog
# R2_ENDPOINT=https://<account-id>.r2.cloudflarestorage.com
```

`BLOG_RESOURCE_BASE_URL` is the single public URL setting. `R2_BLOG_PREFIX` is
the object-key prefix inside the configured bucket; it is not included twice by
the URL builder.

### Test URL mapping and R2 signing

```
python -m unittest discover -s tests
```

To validate the configured credentials and bucket without uploading, deleting,
or changing any object, run:

```
python validate_r2.py
```

GitHub Actions also provides a read-only `Validate R2 Migration` workflow. A
push to the `codex/r2-action-validation` branch runs the unit tests and the same
R2 bucket check, but never runs the scraper or pushes generated posts to the
blog repository.

### Get blogs

```
python main.py
```

### Migrate legacy AList URLs

The migration command is a dry-run unless `--write` is supplied. It only maps
recognized `/d/Backup/Blog/<author>/<filename>` URLs and reports malformed
legacy values without changing them.

```
python migrate_legacy_blog_urls.py . ../blog/source/_posts \
  ../blog/_config.Acrylic.yml ../blog/_config.anzhiyu.yml

python migrate_legacy_blog_urls.py --write . ../blog/source/_posts \
  ../blog/_config.Acrylic.yml ../blog/_config.anzhiyu.yml
```

# License

GPL V3.0
