"""A super simplified interface to rFeed RSS feed generator"""
import sys
sys.path.append('') ##get import to look in the working dir

import datetime 
from .rfeed.rfeed import *

has_local_date = False
author_name = "Unknown Jerome"
site_link = "http://www.example.com/rss"

## I Expect to use this from within a shotglass site
try:
    from shotglass2.shotglass import get_site_config
    from shotglass2.takeabeltof.date_utils import local_datetime_now
    has_local_date = True
    site_config = get_site_config()
    author_name = site_config['SITE_NAME']
    site_link = 'http://' + site_config['HOST_NAME']
except ImportError:
    print('no shotglass package')
    

class FeedMe():
    """Setup the channel parmeters for the news feed prior to adding items
        params:
            title | <str>: Title for the feed
            
            link | <str>: a link to the host ('http://example.com/'). Defaults to the 
            site_settings 'HOST_NAME' if available.
            
            description | <str>: (optional) description of the feed
            
            language | <str>: (optional) language of feed
    """
    def __init__(self,**kwargs):
        self.title = kwargs.get('title',"World Greatest RSS Feed")
        self.link = kwargs.get('link',site_link)
        self.description = kwargs.get('description',"RSS 2.0 feed")
        self.language = kwargs.get('language',"en-US")
        self.lastBuildDate = self._now()
        self.items = []

    def _now(self):
        if has_local_date:
            return local_datetime_now()
        else:
            return datetime.datetime.now()
            
    def get_feed(self,items):
        """Generate the text of the RSS feed. Add the elements of items and return
        the formated xml of the news feed.
        
            params:
                **items** | <list>: Items is a list of dicts with the following keys;
                    title | <str>: The title of the article
                    
                    link | <str>: the url of the article
                    
                    description | <str>: Some descriptive text
                    
                    permalink | <str>: a link to the article ('http://example.com/get_the_story/')
                    
                    author | <str>: Name of author. Defaults to the host name if available.
                    
                    pubDate | <datetime>: date of article
                    
                    enclosure | <dict>: a dictionary of 3 elements that describe where to get more
                    content for the item. Includes 'url':url for content, 'length': len of enclosure, 'type': mimetype
                    
        """
        for item in items:
            #item is a dict like object
            enclosure = None
            if 'enclosure' in item and isinstance(item['enclosure'],dict):
                enc = item['enclosure']
                try:
                    enclosure = Enclosure(enc['url'],enc['length'],enc['type'])
                except:
                    pass
                
            self.items.append(Item(
                title = item.get('title',"An article"),
                link = item.get('link',self.link), 
                description = item.get('description',"This article has no description 8-("),
                author = item.get('author',author_name),
                guid = Guid(item.get('permalink',self.link)),
                pubDate = item.get('pubDate',self.lastBuildDate),
                enclosure = enclosure,
                )
            )
            
                
        # Return the feed as fully formed xml
        feed = Feed(
            title = self.title,
            link = self.link,
            description = self.description,
            language = self.language,
            lastBuildDate = self.lastBuildDate,
            items = self.items,
            )
            
        return feed.rss()
            
