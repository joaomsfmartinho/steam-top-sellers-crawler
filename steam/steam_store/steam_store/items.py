# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import re
import scrapy
from scrapy.loader.processors import TakeFirst, MapCompose, Join


def remove_tags(review_summary):
    cleaned_review_summary = ""
    try:
        cleaned_review_summary = re.sub('<[^<]+?>', '', review_summary)
    except:
        cleaned_review_summary = review_summary
    return cleaned_review_summary


def remove_html(review_summary):
    cleaned_review_summary = ""
    try:
        cleaned_review_summary = remove_tags(review_summary)
    except:
        cleaned_review_summary = "No reviews yet"
    return cleaned_review_summary


def get_platforms(platform):
    cleaned_platforms = []
    try:
        cleaned_platforms.append(platform.replace("platform_img ", "").replace("vr_supported", "VR").capitalize())
    except:
        pass
    return cleaned_platforms


def clean_discount_rate(discount_rate):
    if discount_rate is None:
        return "No discount"

    return discount_rate.replace("-", "")


def clean_discount_price(discount_price):
    if discount_price is None:
        return "No discount"
    return discount_price


def clean_price(price):
    if price is None:
        return "Free"
    return price


class SteamStoreItem(scrapy.Item):
    game_url = scrapy.Field(
        output_processor=TakeFirst()
    )
    img_url = scrapy.Field(
        output_processor=TakeFirst()
    )
    game_name = scrapy.Field(
        output_processor=TakeFirst()
    )
    release_date = scrapy.Field(
        output_processor=TakeFirst()
    )
    platforms = scrapy.Field(
        input_processor=MapCompose(get_platforms),
        output_processor=Join("; ")
    )
    rating = scrapy.Field(
        input_processor=MapCompose(remove_html),
        output_processor=TakeFirst()
    )
    price = scrapy.Field(
        input_processor=MapCompose(clean_price),
        output_processor=TakeFirst()
    )
    discount_price = scrapy.Field(
        input_processor=MapCompose(clean_discount_price),
        output_processor=TakeFirst()
    )
    discount_rate = scrapy.Field(
        input_processor=MapCompose(clean_discount_rate),
        output_processor=TakeFirst()
    )
