import requests
import json
from kafka import KafkaProducer
import scrapy
class WallaPopStreamer():

    def __init__(self, lat, lon, pages, server,queue):

        self.base_url = "https://api.wallapop.com/api/v3/general/wall?"
        self.headers = {
                "User-Agent":"Mozilla/3.0",
                "Accept-Language":"en-EN,en;q=0.8,en-US;q=0.5,en;q=0.3",
                "Referer":"https://en.wallapop.com/search?latitude=lat=lon",
                "Timestamp": "",
                "X-Signature": "="
        }

        self.server = server 
        self.queue = queue 
        self.lat = lat 
        self.lon = lon
        self.producer = KafkaProducer(bootstrap_servers=self.server, value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        self.item_url = "https://en.wallapop.com/item/"
        self.pages = pages
    def __del__(self):
        self.producer.close()

    def get_item_page(self,j):
        item_title = j["web_slug"]
        print(item_title)
        item_url = self.item_url+item_title
        r = requests.get(url=item_url)
        rc = str(r.content.decode('utf8'))

        return rc

    def get_postalcode(self,rc):
        
        get_postalcode = '//div[@class="card-product-detail-location"]/text()'
        
        res = scrapy.Selector(text=rc).xpath(get_postalcode).extract()[0].strip()[:-1]
        return res
    
    def get_item_rating(self,rc):

        get_itemrate = '//div[@class="card-profile-rating"]/@data-score'

        res = scrapy.Selector(text=rc).xpath(get_itemrate).extract()[0].strip()
        return res
        
    def get_item_rating_num(self,rc):

        get_itemrate = '//span[@class="recived-reviews-count"]/text()'
        res = scrapy.Selector(text=rc).xpath(get_itemrate).extract()[0]
        return res
    def parse_items(self, r):
        j = json.loads(r)
        for item in j["search_objects"]:
            item_page = self.get_item_page(item)
            postalcode=self.get_postalcode(item_page)
            itemrating = self.get_item_rating(item_page)
            ratenum = self.get_item_rating_num(item_page)
            item["rating"] = itemrating
            item["postalcode"] = postalcode
            item["ratenum"] = ratenum
            self.producer.send(topic=self.queue,value=item)
    
    def parse_page(self):
        url = self.base_url + "latitude="+self.lat+"&longitude="+self.lon+"&filters_source=quick_filters&language=en_EN"
        r = requests.get(url = url, headers = self.headers)
        self.parse_items(r.content)
        nextpage = r.headers["X-NextPage"]
        if self.pages > 0:
            self.pages = self.pages - 1
            self.parse_next_page(nextpage)

    def parse_next_page(self, nextpage):
        next_url = self.base_url + nextpage
        r = requests.get(url=next_url, headers = self.headers)
        self.parse_items(r.content)
        nextpage = r.headers["X-NextPage"]
        if self.pages > 0:
            self.pages = self.pages - 1
            self.parse_next_page(nextpage)

    def start(self):
        self.parse_page()



lat = ""
lon = ""
server = "localhost:9092"
queue = "wallapop"
wallapopstreamer = WallaPopStreamer(lat,lon,3,server, queue)
wallapopstreamer.start()
