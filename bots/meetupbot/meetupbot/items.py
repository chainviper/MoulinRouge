# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MeetupbotItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    event_title = scrapy.Field()
    event_desc = scrapy.Field()
    event_id = scrapy.Field()
    group_name = scrapy.Field()
    event_address = scrapy.Field()
    event_location = scrapy.Field()
    event_timestmap = scrapy.Field()
    event_date = scrapy.Field()
    event_time = scrapy.Field()
    coords = scrapy.Field()
    event_hour_end = scrapy.Field()
    event_price = scrapy.Field()
    event_attendees = scrapy.Field()
    event_url = scrapy.Field()
    #name = scrapy.Field()
