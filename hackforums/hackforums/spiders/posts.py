import os
import cv2
import scrapy
import sqlite3
import requests
import playwright
import pytesseract
from time import sleep
from datetime import datetime
from scrapy.crawler import CrawlerProcess
from scrapy.shell import inspect_response
from playwright.sync_api import sync_playwright

class PostsSpider(scrapy.Spider):
    name = "posts"
    allowed_domains = ["hackforums.net"]

    # Gather list of file to scrape
    start_urls = []
    for post in os.listdir("ABS PATH/downloaded-pages"):
        file = os.path.join("ABS PATH/downloaded-pages", post)

        # checking if it is a file
        if os.path.isfile(file):
            start_urls.append("file://%s" % file)

    # DB connection
    db = sqlite3.connect('../hackforums.db')
    cursor = db.cursor()

    def parse(self, response):

        # Status
        print("Files remaining: %s    " % len(os.listdir("ABS PATH/downloaded-pages")), end="\r")

        # Interactive shell
        # inspect_response(response, self)

        # Detect account blockage
        try:
            # Get individual comments
            comments = response.css('div.post.classic.clear')
        except:
            print("ERROR: Something went wrong in file: %s" % response.request.url.split("downloaded-pages/")[1])
            with open('../error.txt', 'a+') as errorFile:
                errorFile.write("%s\n" % response.request.url.split("downloaded-pages/")[1])
            return

        # Detect captcha
        if response.css('div#title').css('h1::text').get() == 'Site Challenge':
            print("ERROR: Something went wrong in file: %s" % response.request.url.split("downloaded-pages/")[1])
            with open('../error.txt', 'a+') as errorFile:
                errorFile.write("%s\n" % response.request.url.split("downloaded-pages/")[1])
            return

        # Go comment by comment
        for it, comment in enumerate(comments):

            # Get user info
            try:
                userUid = int(comment.css('div.post_author').css('div.author_information').css('a').attrib['href'].split('&uid=')[1])
            except:
                userUid = 000
            userName = comment.css('div.post_author').css('div.author_information').css('span::text').get()
            moto = comment.css('div.post_author').css('div.author_information').css('span.smalltext::text').get().strip()
            stats = comment.css('div.post_author').css('div.author_statistics').css('div.author_row').css('div::text').getall()
            stats = [el for el in stats if el != " "]

            if "Posts:" in stats:
                posts = int(stats[stats.index('Posts:')+1].replace(",", ""))
            else:
                posts = 1

            if "Threads:" in stats:
                threads = int(stats[stats.index('Threads:')+1].replace(",", ""))
            else:
                threads = 0

            if "Popularity:" in stats:
                popularity = int(comment.css('div.post_author').css('div.author_statistics').css('div.author_row').css('div.author_value').css('a').css('strong::text').getall()[3].replace(",", ""))
            else:
                popularity = 0

            if "B Rating:" in stats:
                goodreviews = int(comment.css('div.post_author').css('div.author_statistics').css('div.author_row').css('div.author_value').css('a').css('strong::text').getall()[0].replace(",", ""))
                neutralreviews = int(comment.css('div.post_author').css('div.author_statistics').css('div.author_row').css('div.author_value').css('a').css('strong::text').getall()[1].replace(",", ""))
                badreviews = int(comment.css('div.post_author').css('div.author_statistics').css('div.author_row').css('div.author_value').css('a').css('strong::text').getall()[2].replace(",", ""))
            else:
                goodreviews = 0
                neutralreviews = 0
                badreviews = 0

            # Insert user
            values = [
                userUid,
                userName,
                moto,
                posts,
                threads,
                popularity,
                goodreviews,
                neutralreviews,
                badreviews
            ]

            try:
                # Delete user if exists
                self.db.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", values)
                self.db.commit()
            except:
                #! Handle errors
                pass

            # Get comment info
            tid = response.css('div.breadcrumb').css('a').getall()[-1].split("tid=")[-1].split(">")[0][:-1]

            # Update post info
            if it == 0 and int(response.request.url.split("-")[2].split(".html")[0]) == 1:

                # Get content of comment in lines
                contents = comment.css('div.post_content').css('div.post_body::text').getall()
                contents = [el.strip() for el in contents]
                content = "\n".join(contents)

                try:
                    imagesSrc = ""
                    images = comment.css('img.mycode_img').getall()
                    for it, src in enumerate(images):
                        img = src.split('src="')[1].split('"')[0]
                        # Download image provided
                        image = requests.get(img, stream=True)
                        ext = image.headers['content-type'].split('/')[-1]

                        # Only download img extensions
                        if ext in ["jpeg", "png"]:
                            with open('../images/%s-%s.%s' % (tid, it, ext), 'wb') as imgFile:
                                for chunk in image.iter_content(1024): # iterate on stream using 1KB packets
                                    imgFile.write(chunk)
                        
                        imagesSrc += "%s\n" % img

                    # No OCR performed here because manual filter has to be done

                except:
                    imagesSrc = 'no img'

                # Grab creation timestamp
                try:
                    creation = datetime.timestamp(datetime.strptime(response.css('span.post_date::text').get(), '%m-%d-%Y, %I:%M %p '))
                except:
                    pass

                values = [content, imagesSrc, creation, tid]

                try:
                    self.db.execute("UPDATE posts SET originalPost = ?, imgUrl = ?, creation = ? WHERE tid = ?", values)
                    self.db.commit()
                except Exception as e:
                    #! Handle errors
                    print(e)
                    pass
            else:

                commentId = int(comment.attrib['id'].split('_')[1])
                postId = int(response.css('div.breadcrumb').css('a').getall()[-1].split("tid=")[-1].split(">")[0][:-1])
                try:
                    date = datetime.timestamp(datetime.strptime(response.css('span.post_date::text').get(), '%m-%d-%Y, %I:%M %p '))
                except:
                    date = 0

                # Get content of comment in lines
                contents = comment.css('div.post_content').css('div.post_body::text').getall()
                contents = [el.strip() for el in contents]
                content = "\n".join(contents)

                # Insert comment
                values = [
                    commentId,
                    userUid,
                    postId,
                    date,
                    content
                ]

                try:
                    # Delete comment if exists
                    self.db.execute("INSERT INTO comments VALUES (?, ?, ?, ?, ?)", values)
                    self.db.commit()
                except:
                    #! Handle errors
                    pass

        # Mark as done
        os.rename(response.request.url.split("file://")[1], response.request.url.split("file://")[1].split("downloaded-pages")[0] + "done" + response.request.url.split("file://")[1].split("downloaded-pages")[1])





if __name__ == "__main__":

    # Open database
    db = sqlite3.connect('../hackforums.db')
    cursor = db.cursor()

    # Get all initially crawled posts
    cursor.execute('SELECT * FROM posts;')

    # Get header for easier interaction
    header = list(map(lambda x: x[0], cursor.description))

    # Copy results
    posts = cursor.fetchall()

    # Launch playwright browser
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False, slow_mo=100, proxy={
            'server': 'http://127.0.0.1:8118'
        })
        page = browser.new_page()

        # Manual login
        page.goto('https://hackforums.net/member.php?action=login')
        sleep(30)

        with open('../timeout.txt', 'a+') as timeoutFile:
            # Loop through captured posts
            for it, post in enumerate(posts):

                commentPage = int(post[header.index('commentPage')])
                nPages = int(post[header.index('nPages')])

                # Skip completed posts
                if commentPage == -1:
                    continue


                while commentPage <= int(nPages):
                    # Print status
                    print("Downloading post %s/%s, page %s/%s      " % (it+1, len(posts), str(commentPage), nPages), end="\r")

                    # Download each posts page
                    # TODO detect captcha
                    url = "%s&page=%s" % (post[header.index('url')], str(commentPage))
                    try:
                        page.goto(url)
                    # If timeout continue with next post
                    except playwright._impl._api_types.TimeoutError:
                        print("\nERROR: Timeout in page: %s\n" % url)
                        timeoutFile.write("%s\n" % url)
                        commentPage += 1
                        continue

                    with open('../posts/%s-%s.html' % (post[header.index('tid')], str(commentPage)), 'w') as fd:
                        fd.write(page.content())

                    commentPage += 1

                # Mark as completed
                try:
                    db.execute("UPDATE posts SET commentPage = ? WHERE tid = ?", [-1, post[header.index('tid')]])
                    db.commit()
                except Exception as e:
                    #! Handle errors
                    print(e)
                    pass

    db.close()

    # Scrape local copy of page
    scraper = CrawlerProcess()
    scraper.crawl(PostsSpider)
    scraper.start()
