import scrapy
from scrapy.http import FormRequest
import requests
import re
import gender_guesser.detector as gender
import json
from datetime import datetime
import time
from time import gmtime, strftime
from geopy.geocoders import Nominatim
from dateutil import parser

import timestring
class QuotesSpider(scrapy.Spider):
    name = "eventbrite"

    

    def start_requests(self):
        urls = [
            'https://www.eventbrite.com/d/france--paris/all-events/'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        events = '//a[@class="eds-media-card-content__action-link"]/@href'

        events_content = response.xpath(events).extract()

        for e in events_content:
            print(e)
            print("\n")
            yield scrapy.Request(url=e, callback=self.parse_event)

        next_page = '//a[@aria-label="Go to next page"]/@href'
        next_page_content = response.xpath(next_page).extract()
        next_url = "https://eventbrite.com/" +next_page_content[0]
        print(next_url)

    
    def get_start_date(self, response):
        body = response.body.decode("utf8")
        start = "'event_date': \""
        end = '",'
        result = re.search(''+start+'(.*)'+end+'', body)
        return result.group(1)
    def parse_event(self, response):

        price = '//div[@class="js-display-price"]/text()'
        title = '//h1[@class="listing-hero-title"]/text()'
        location = '//div[@class="event-details__data"]/p/text()'
        group_name = '//a[@class="js-d-scroll-to listing-organizer-name text-default"]/text()'
        desc = '//div[@class="structured-content-rich-text structured-content__module l-align-left l-mar-vert-6 l-sm-mar-vert-4 text-body-medium"]/p/text()'
        
        price_content = response.xpath(price).extract()
        title_content = response.xpath(title).extract()[0]
        location_content = response.xpath(location).extract()
        desc_content = response.xpath(desc).extract()
        desc_content = ' '.join(desc_content)
        group_name_content =  response.xpath(group_name).extract()[0].strip().lower()[3:]
        event_url = response.url
        try:
            if price_content:
                price = price_content[0].strip().lower()
        
                if "free" in price:
                    price = 0
                else:
                    price = price[0:4]
                    if "," in price:
                        price = price.split(',')
                        price = price[0]
                    if "'" in price:
                        price = price.split("'")
                        price = price[0]
                        price = int(''.join(filter(str.isdigit, price)))
            else:
                price = 0
        except:
            price = 0
        
        address = location_content[1] + ","+ location_content[2]
        start_date = self.get_start_date(response)
        parsing_date = strftime("%Y-%m-%d %H:%M:%S", gmtime())

        try:
            geolocator = Nominatim(user_agent="eventbrite")

            coords = geolocator.geocode(address)

            coords = [coords.latitude, coords.longitude]
        except:
            coords = []
        event_object = {
            "title": title_content,
            "organizer": group_name_content,
            "price": price,
            "address" : address,
            "start_date" : start_date,
            "coords" : coords,
            "parsing_date" : parsing_date,
            "content" : desc_content,
            "event_url" : event_url
        }
        yield event_object
        print("\n")
        
