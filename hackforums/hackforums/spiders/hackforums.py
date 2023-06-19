import scrapy
import sqlite3
from datetime import datetime
from scrapy.shell import inspect_response

class HackforumsSpider(scrapy.Spider):
    name = "hackforums"
    allowed_domains = ["hackforums.net"]

    # Check if DB exists before running the scraper
    if os.path.isfile("../hackforums.db"):
        db = sqlite3.connect('../hackforums.db')
    else:
        print("ERROR: DB doesn't exist")
        exit()

    def start_requests(self):
        url = 'https://hackforums.net/forumdisplay.php?fid=299&page=1&sortby=views'
        yield scrapy.Request(url=url, callback=self.parse)
    

    # Get all pages to crawl in a domain
    def parse(self, response):
        
        # Print progress
        page = response.css('div.pagination').css('span.pagination_current::text').get()
        nPages = response.css('div.pagination').css('a.pagination_last::text').get()
        print("Scraping page %s/%s" % (page, nPages), end="\r")

        # Get all posts in page
        descriptions = response.css('div.mobile-link-truncate')
        viewList = response.css('span.mobile-hide::text').getall()
        raw_replies = response.css('td.mobile-remove').css('a::text').getall()
        
        # Map timestamps of last post
        lastPosts = []
        for lastPost in response.css('span.lastpost.smalltext'):
            try:
                # If existing timestamp
                lastPosts.append(float(lastPost.css('.smart-time').attrib['data-timestamp']))
            except:
                # Translate to timestamp
                lastPosts.append(datetime.timestamp(datetime.strptime(lastPost.css('::text').getall()[0], '%m-%d-%Y, %I:%M %p')))

        # Get only num replies from raw_replies
        replyList = []
        for i in raw_replies:
            try:
                replyList.append(int(i.replace(",", "")))
            except:
                pass

        # Populate sqlite with scraped data
        for i, desc in enumerate(descriptions):

            # Get values from each post
            tid = int(desc.css('span.subject_new').css('a').attrib['href'].split('tid=')[-1])
            name = desc.css('span.subject_new').css('a::text').get()
            # Not a real user
            if len(desc.css('div.author.smalltext').css('span')) < 3:
                creatorName = "Guest"
                creatorUid = 000
            else:
                creatorName = desc.css('div.author.smalltext').css('span::text').get()
                creatorUid = int(desc.css('div.author.smalltext').css('a').attrib['href'].split('uid=')[-1])
            postUrl = 'https://hackforums.net/%s' % desc.css('span.subject_new').css('a').attrib['href']
            views = int(viewList[i].replace(",", ""))
            replies = replyList[i]
            lastPost = str(lastPosts[i])
            try:
                nPage = int(desc.css('div.mobile-link-truncate').css('div.author.smalltext').css('span.smalltext').css('a::text')[-1].get())
            except:
                nPage = 1

            # Create post
            values = [
                tid,
                name,
                "creation",
                creatorName,
                creatorUid,
                postUrl,
                views,
                lastPost,
                "originalPost",
                "img",
                "no data",
                replies,
                1,
                nPage
            ]

            try:
                self.db.execute("INSERT INTO posts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", values)
                self.db.commit()
            except:
                #! Handle errors
                pass

        # Next page of forum to be scraped
        try:
            next = response.css('div.pagination').css('a.pagination_next').attrib['href']
            yield scrapy.Request(url='https://hackforums.net/%s' % next, callback=self.parse)
        except:
            self.db.close()
        