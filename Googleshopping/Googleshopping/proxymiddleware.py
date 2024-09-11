import random

class ProxyMiddleware:
    def __init__(self, proxies):
        self.proxies = proxies

    @classmethod
    def from_crawler(cls, crawler, args, *kwargs):
        PROXY_RACK_DNS = ""
        username = ""
        password = ""
        proxies = [f'https://{username}:{password}@{PROXY_RACK_DNS}']  # Replace with your list of proxy URLs
        return cls(proxies)

    def process_request(self, request, spider):
        proxy = random.choice(self.proxies)
        request.meta['proxy'] = proxy