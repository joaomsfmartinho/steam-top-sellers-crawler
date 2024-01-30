# steam-top-sellers-crawler

A small project written in Python as part of the Advanced Web Scraping with Python course that crawls the Steam's top sellers and info related.

## How to run the Scrapy version

Do ``` cd /steam/steam_store ``` and then open a new terminal and execute ``` scrapy crawl best_sellers ```

## How to run the ScrapyRT version with Flask

Do ``` cd /steam/steam_store ``` and then open a new terminal and execute ``` scrapyrt -p 8080 ```. Then, open a new terminal and execute ``` python3 app.py ```. Finally, open your browser and go to ``` http://localhost:5000/ ``` and you will see the results.
