# encoding: utf-8
from scrapy import cmdline
from scrapy.cmdline import execute

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# execute(["scrapy", "crawl", "enterprise","-a","word=百度"])
execute(["scrapy", "crawl", "zhilian"])