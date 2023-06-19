from stem import Signal
from stem.control import Controller
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware


def new_tor_identity():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password='crypterPass')
        controller.signal(Signal.NEWNYM)


class ProxyMiddleware(HttpProxyMiddleware):
    def process_response(self, request, response, spider):
        # Get a new identity depending on the response
        if response.status != 200:
            new_tor_identity()
            return request
        return response


    def process_request(self, request, spider):
        # Set the Proxy

        # A new identity for each request
        # Comment out if you want to get a new Identity only through process_response
        new_tor_identity()

        request.meta['proxy'] = 'http://127.0.0.1:8118'
