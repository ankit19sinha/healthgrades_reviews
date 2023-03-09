# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class HealthgradesItem(scrapy.Item):
    # define the fields for your item here like:
    unique_id = scrapy.Field()
    provider_name = scrapy.Field()
    provider_spec = scrapy.Field()
    provider_addresses = scrapy.Field()
    provider_ph_numbers = scrapy.Field()
    commenter_name = scrapy.Field()
    commenter_date = scrapy.Field()
    rating = scrapy.Field()
    review = scrapy.Field()