# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SteamStoreItem(scrapy.Item):
    game_url = scrapy.Field()
    img_url = scrapy.Field()
    game_name = scrapy.Field()
    release_date = scrapy.Field()
    platforms = scrapy.Field()
    rating = scrapy.Field()
    price = scrapy.Field()
    discount_price = scrapy.Field()
    discount_rate = scrapy.Field()
