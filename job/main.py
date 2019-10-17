# encoding: utf-8
from scrapy import cmdline
from scrapy.cmdline import execute

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# execute(["scrapy", "crawl", "enterprise","-a","word=苏州金螳螂建筑装饰股份有限公司"])
# execute(["scrapy", "crawl", "zhilian"])
execute(["scrapy", "crawl", "boss"])
# execute(["scrapy", "crawl", "liepin"])