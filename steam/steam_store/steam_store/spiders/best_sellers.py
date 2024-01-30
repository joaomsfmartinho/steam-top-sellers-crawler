import re
import json
import scrapy
from scrapy import Selector
from ..items import SteamStoreItem
from scrapy.loader import ItemLoader


def write_header_to_logs():
    with open("games.csv", "w") as f:
        f.write("game_name, game_url, img_url, release_date, platform, rating, price, discount_price, discount_rate\n")
        f.close()


def append_game_to_logs(game):
    keys = game.keys()
    if "rating" not in keys:
        game["rating"] = "No rating"
    if "discount_price" not in keys:
        game["discount_price"] = "No discount"
    if "discount_rate" not in keys:
        game["discount_rate"] = "No discount"
    if "price" not in keys:
        game['price'] = game['discount_price']
    with open("games.csv", "a") as f:
        f.write(f"{game['game_name']}, {game['game_url']}, {game['img_url']}, {game['release_date']}, {game['platforms']}, {game['rating']}, {game['price']}, {game['discount_price']}, {game['discount_rate']}\n")
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
            loader = ItemLoader(item=SteamStoreItem(), selector=game, response=response)
            loader.add_xpath("game_url", ".//@href")
            loader.add_xpath("img_url", ".//div[@class='col search_capsule']/img/@src")
            loader.add_xpath("game_name", ".//span[@class='title']/text()")
            loader.add_xpath("release_date", ".//div[contains(@class, 'col search_released')]/text()")
            loader.add_xpath("platforms",
                             ".//div[@class='col search_name ellipsis']/div/span[contains(@class, 'platform_img') or contains(@class, 'vr')]/@class")
            loader.add_xpath("rating",
                             ".//span[contains(@class, 'search_review_summary')]//@data-tooltip-html")
            loader.add_xpath("price", ".//div[@class='discount_original_price']/text()")
            loader.add_xpath("discount_price", ".//div[contains(@class, 'discount_final_price')]/text()")
            loader.add_xpath("discount_rate", ".//div[contains(@class, 'discount_pct')]/text()")

            steam_item = loader.load_item()

            yield loader.load_item()

            # Log steam_item
            print(steam_item)

            append_game_to_logs(steam_item)

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
