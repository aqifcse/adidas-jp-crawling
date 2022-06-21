# adidas-jp-crawiling

```
git clone https://github.com/aqifcse/adidas-jp-crawiling.git

```

```
cd adidas-jp-crawiling

```

```
virtualenv venv

```

```
source venv/bin/activate

```

```
pip install -r requirements.txt

```

To crawl all the product urls and save the urls to urls.txt file please give the following command

```
python product-urls-crawler.py
```

To crawl the required data of the product urls stored in urls.txt simply give the following command -

```
python single-product-crawling.py
```

That's it the data will be stored in product-details.xlsx file. Enjoy!!!