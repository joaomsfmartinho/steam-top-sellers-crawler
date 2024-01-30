import re
import json
import scrapy
from scrapy import Selector
from ..items import SteamStoreItem


def write_header_to_logs():
    with open("games.csv", "w") as f:
        f.write("game_name, game_url, img_url, release_date, platform, rating, price, discount_price, discount_rate\n")
        f.close()


def append_game_to_logs(game: SteamStoreItem):
    with open("games.csv", "a") as f:
        f.write(
            f"{game['game_name']}, {game['game_url']}, {game['img_url']}, {game['release_date']}, {game['platforms']}, {game['rating']}, {game['price']}, {game['discount_price']}, {game['discount_rate']}\n")
        f.close()


class BestSellersSpider(scrapy.Spider):
    name = "best_sellers"
    allowed_domains = ["store.steampowered.com"]
    start_urls = ["https://store.steampowered.com/search/?filter=topsellers"]

    pagination_start_index = 0

    COUNT = 50

    # Write header to csv file
    write_header_to_logs()

    def start_requests(self):
        """ Handle dynamic loading of the page """
        yield scrapy.Request(
            method='GET',
            url=f'https://store.steampowered.com/search/results/?query&start={self.pagination_start_index}&count={self.COUNT}&dynamic_data=&sort_by=_ASC&supportedlang=english&snr=1_7_7_7000_7&filter=topsellers&infinite=1',
            headers={
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'text/javascript, text/html, application/xml, text/xml, */*',
                'Content-Type': 'application/json'
            },
            callback=self.parse,
            meta={
                'start': self.pagination_start_index
            }
        )

    def remove_tabs(self, string):
        return string.strip().replace(",", "")

    def remove_tags(self, review_summary):
        cleaned_review_summary = ""
        try:
            cleaned_review_summary = re.sub('<[^<]+?>', '', review_summary)
        except:
            cleaned_review_summary = review_summary
        return cleaned_review_summary

    def remove_html(self, review_summary):
        cleaned_review_summary = ""
        try:
            cleaned_review_summary = self.remove_tags(review_summary)
        except:
            cleaned_review_summary = "No reviews yet"
        return cleaned_review_summary

    def clean_discount_rate(self, discount_rate):
        cleaned_discount_rate = ""
        try:
            cleaned_discount_rate = discount_rate.replace("-", "0")
        except:
            cleaned_discount_rate = "No discount"
        return cleaned_discount_rate

    def clean_discount_price(self, discount_price):
        if discount_price is None:
            return "No discount"
        return discount_price

    def parse(self, response):
        resp = json.loads(response.body)
        steam_item = SteamStoreItem()
        html = resp.get('results_html')
        if html is None:
            return

        with open("games.html", "w") as f:
            f.write(html)
            f.close()

        html_selector = Selector(text=html)
        games = html_selector.xpath("//a[contains(@class, 'search_result_row')]")
        for game in games:
            steam_item["game_url"] = game.xpath(".//@href").get()
            steam_item["img_url"] = game.xpath(".//div[@class='col search_capsule']/img/@src").get()
            steam_item["game_name"] = game.xpath(".//span[@class='title']/text()").get()
            steam_item["release_date"] = self.remove_tabs(
                game.xpath(".//div[contains(@class, 'col search_released')]/text()").get())
            steam_item["platforms"] = (
                game.xpath(
                    ".//div[@class='col search_name ellipsis']/div/span[contains(@class, 'platform_img') or contains(@class, 'vr')]/@class").getall())
            steam_item["rating"] = self.remove_html(
                game.xpath(".//span[contains(@class, 'search_review_summary')]//@data-tooltip-html").get())
            steam_item["price"] = game.xpath(".//div[@class='discount_original_price']/text()").get()
            steam_item["discount_price"] = self.clean_discount_price(game.xpath(".//div[contains(@class, 'discount_final_price')]/text()").get())
            steam_item["discount_rate"] = self.clean_discount_rate(
                game.xpath(".//div[contains(@class, 'discount_pct')]/text()").get())
            # Remove platform _img from platforms and transform win to Win, mac to Mac, linux to Linux, vr_supported to VR
            steam_item["platforms"] = [platform.replace("platform_img", "").replace("vr_supported", "VR").capitalize()
                                       for platform in steam_item["platforms"]]

            # Append game to csv file
            append_game_to_logs(steam_item)
            yield steam_item

            # Handle dynamic loading
            if self.pagination_start_index < resp.get('total_count'):
                self.pagination_start_index += self.COUNT
                yield scrapy.Request(
                    method='GET',
                    url=f'https://store.steampowered.com/search/results/?query&start={self.pagination_start_index}&count={self.COUNT}&dynamic_data=&sort_by=_ASC&supportedlang=english&snr=1_7_7_7000_7&filter=topsellers&infinite=1',
                    headers={
                        'X-Requested-With': 'XMLHttpRequest',
                        'Accept': 'text/javascript, text/html, application/xml, text/xml, */*',
                        'Content-Type': 'application/json'
                    },
                    callback=self.parse,
                )