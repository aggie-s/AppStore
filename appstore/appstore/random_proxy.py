import re
import random
import base64
import logging


class RandomProxyMiddleware(object):

    def __init__(self, settings):
        self.proxy_list = settings.get('PROXY_LIST')
        fin = open(self.proxy_list)

        self.proxies = {}
        for line in fin.readlines():
            parts = re.match('(\w+:\/\/)(\w+:\w+@)?(.+)', line)

            if parts is None:
                break
            # Cut trailing @
            if parts.group(2) is None:
                user_pass = ''
            else:
                user_pass = parts.group(2)[:-1]

            self.proxies[parts.group(1) + parts.group(3)] = user_pass

        fin.close()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        # Don't overwrite with a random one (server-side state for IP)
        if 'proxy' in request.meta:
            return

        proxy_address = random.choice(self.proxies.keys())
        proxy_user_pass = self.proxies[proxy_address]
        print "***Proxy Address: %s***" % proxy_address
        request.meta['proxy'] = proxy_address
        if proxy_user_pass:
            basic_auth = 'Basic ' + base64.encodestring(proxy_user_pass)
            request.headers['Proxy-Authorization'] = basic_auth

    def process_exception(self, request, exception, spider):
        proxy = request.meta['proxy']
        logger = logging.getLogger()
        logger.warning('Removing failed proxy <%s>, %d proxies left' % (
            proxy, len(self.proxies)))
        try:
            del self.proxies[proxy]
        except ValueError:
            pass
