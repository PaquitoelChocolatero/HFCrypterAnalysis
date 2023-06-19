# HFCrypterAnalysis
Needed scripts to crawl and scrape Hackforums along with some analysis perfomed in the paper.

Below are the needed steps and cofiguration before running the crawler and how to do it.


## Preparing the environment
### Dependencies
Operating system
```bash
sudo pacman -S tor torsocks privoxy sqlite3 tesseract
```

Python
```bash
pip install -r requirements.txt
```

Playwright
```bash
# Once inside the virtual environment
playwright install
```

### Adding tor to python virtual environment
Add the following lines to start and end tor and privoxy service along the environment
```bash
# Add to the end of the activation file
sudo systemctl start tor
sudo systemctl start privoxy


# Add to the end of the deactivate function
sudo systemctl stop tor
sudo systemctl stop privoxy
```

### Privoxy config to use tor
```bash
# /etc/privoxy/config
forward-socks5t / 127.0.0.1:9050 .
keep-alive-timeout 600
default-server-timeout 600
socket-timeout 600
```

### Config tor
```bash
tor --hash-password <PASS>

# En /etc/tor/torrc
ControlPort 9051
HashedControlPassword <GENERATEDHASH>
```

### Test tor config
```bash
# Normal IP
curl http://ifconfig.me

# IP through tor
torify curl http://ifconfig.me
curl -x 127.0.0.1:8118 https://ifconfig.me
```
[Stealthy Crawling using Scrapy, Tor and Privoxy](https://www.khalidalnajjar.com/stealthy-crawling-using-scrapy-tor-and-privoxy/)<br>
[Tor installation and usage](https://wiki.archlinux.org/title/tor#Torsocks)

## Initialize the database
```bash
sqlite3 hackforums.db < create.sql
```


## Run crawler
The files are in path: /HFCrypterAnalysis/hackforums/hackforums/spiders

First run the crawler of the marketplace thread list
```bash
# Inside HFCrypterAnalysis/hackforums
scrapy crawl hackforums --nolog
```
[Antibot bypass for scrapy](https://scrapeops.io/python-scrapy-playbook/scrapy-403-unhandled-forbidden-error/)

Now you can run the scraper inside the threads, you need an account for this
```bash
# Inside HFCrypterAnalysis/hackforums
python3 hackforums/spiders/posts.py
```