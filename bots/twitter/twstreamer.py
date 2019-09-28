from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from kafka import KafkaProducer
import json

class TwitterKafka():
    def __init__(self, server, queue):
        self.server = server
        self.queue = queue

        self.producer = KafkaProducer(bootstrap_servers=server)

    def send(self,data):
        self.producer.send(topic=self.queue,value=data.encode('utf-8'))
        self.producer.close()

class StdOutListener(StreamListener):
    def on_data(self, data):

        streamer = TwitterKafka("localhost:9092", "twitter")
        streamer.send(data)
        return True
    def on_error(self, status):
        print (status)

class TwitterStreamer():

    def __init__(self,access_token, access_token_secret, consumer_key, 
                    consumer_secret):
        self.atoken = access_token
        self.tokensecret = access_token_secret
        self.consumerkey = consumer_key
        self.consumersecret = consumer_secret

        self.geobox = None

        self.twlistener = StdOutListener()
        self.stream = None

        self.enable_listener()

    def enable_listener(self):
        l = StdOutListener()
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.stream = Stream(auth, l)

    def set_location(self,geobox):
        self.geobox = geobox
    
    def start_streaming(self):
        self.stream.filter(locations=self.geobox)


access_token = "-"
access_token_secret =  ""
consumer_key =  ""
consumer_secret =  ""
GEOBOX_SAMPLE = [-1.253769,47.217684,-1.060379,70.621771]

twstreamer = TwitterStreamer(access_token, access_token_secret, 
                        consumer_key, consumer_secret)
twstreamer.set_location(GEOBOX_SAMPLE)

twstreamer.start_streaming()




