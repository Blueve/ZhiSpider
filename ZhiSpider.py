#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import sys
import time
import json
import logging
import sqlite3

import yaml
import requests
import lxml
import lxml.html
from lxml import etree

from ZhiQuestions import ZhiQuestions
from ZhiAnswers import ZhiAnswers

# 设置Logging的基本格式末默认选项
logging.basicConfig(level=logging.INFO,
					format='[%(asctime)s][%(levelname)s]%(message)s',
					datefmt='%Y-%m-%d %H:%M:%S')

class ZhiSpider(object):

	def __init__(self):
		self.configs = self._getConfigs()
		self.rules = self._getRules()

		self.session = requests.session()
		self._setHeader()

		self.login()

		self.fpExcept = open(self.configs['EXCEPTIONS'], 'wb')

		# 创建数据库
		self.db = sqlite3.connect(self.configs['DB']['NAME'])
		self.dbCursor = self.db.cursor()

		# 爬问题列表
		self.questionSpider = ZhiQuestions(self)
		# 爬答案
		self.answerSpider = ZhiAnswers(self)


	def __del__(self):
		self.fpExcept.close()
		self.dbCursor.close()
		self.db.close()

	# 读取配置文件
	def _getConfigs(self):
		with open('Config.yaml', 'rb') as fp:
			configs = yaml.load(fp)
		return configs

	# 读取规则文件
	def _getRules(self):
		with open('Rule.yaml', 'rb') as fp:
			rules = yaml.load(fp)
		return rules

	# 设置HTTP头
	def _setHeader(self):
		self.session.headers.update(self.configs['HEADERS']['INIT'])

	# 登陆知乎
	def login(self):
		# 构造登陆表单并提交
		loginPost = {
			'email': self.configs['AUTH']['EMAIL'],
			'password': self.configs['AUTH']['PASSWORD'],
			'_xsrf': self._getXsrf(),
			'rememberme': 'y',
		}
		self.session.post(self.configs['URL']['LOGIN'], loginPost)
		# 验证登陆状态 若登陆失败则退出
		response = self.session.get(self.configs['URL']['HOME'])
		html = etree.HTML(response.content)
		assert len(html.xpath(self.rules['LOGIN']['TEST'])) == 1, "Failed to login status_code %d" % (response.status_code,)

	# 获取xsrf token
	def _getXsrf(self):
		return self.session.cookies.get('_xsrf')

	# 获取当前时间
	def _getTime(self):
		return time.strftime('%Y-%m-%d-%H%M%S',time.localtime(time.time()))

	# 抓取问题列表
	def getQuestions(self):
		self.questionSpider.start()

	def getAnswers(self):
		self.answerSpider.start()




if __name__ == '__main__':
	# 创建一个爬虫
	spider = ZhiSpider()
	spider.getAnswers()
