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

# 设置Logging的基本格式末默认选项
logging.basicConfig(level=logging.INFO,
					format='[%(asctime)s][%(levelname)s]%(message)s',
					datefmt='%Y-%m-%d %H:%M:%S')

class ZhiQuestions(object):

	def __init__(self, spider):
		self.configs = spider.configs
		self.rules = spider.rules['QUESTION']

		self.spider = spider
		self.session = spider.session
		self.dbCursor = spider.dbCursor

		self.count = 0

	def start(self):
		startPage = self.session.get(self.rules['URL'])
		assert startPage.status_code == 200, "Can't fetch questions."
		# 解析首页
		start = self._parseHtml(startPage.content)
		# 继续解析
		self._modHeader()
		offset = 20
		while True:
			xsrf = self._getXsrf()
			post = {
				'start': start,
				'offset': offset,
				'_xsrf': xsrf
			}

			try:
				response = self.session.post(self.rules['URL'], post, timeout=10)
			except requests.exceptions.Timeout:
				logging.warning('Timeout')
				time.sleep(20)
				continue
			except requests.exceptions.ConnectionError:
				logging.warning('Connection Error')
				self.spider.login()
				continue

			statusCode = response.status_code
			#logging.info('Status: %d' % (statusCode,))
			if statusCode >= 500:
				time.sleep(10)
				continue
			elif statusCode >= 400:
				logging.error("Failed to get AJAX data, start %d, offset %d" % start, offset)
				sys.exit(-1)

			start = self._parseJson(response.content)
			offset += 20
			time.sleep(1)

	# 解析HTML页面
	def _parseHtml(self, content):
		html = etree.HTML(content)
		items = html.xpath(self.rules['XPATH']['PAGE'])

		#logging.info('Questions Number: %d' % (len(items),))

		self._parse(items)

		logging.info('Page parsed.')
		lastId = int(items[-1].xpath('@id')[0].split('-')[-1])
		return lastId

	def _parseJson(self, content):
		message = json.loads(content)['msg']
		number = int(message[0])
		try:
			html = lxml.html.document_fromstring(message[1])
		except lxml.etree.XMLSyntaxError as e:
			self.spider.fpExcept.write('%s\n' % (message,))
			logging.error('%s' % (e.message,))
			sys.exit(-2)
		items = html.xpath(self.rules['XPATH']['JSON'])

		#logging.info('Questions Number: %d' % (number,))
		self._parse(items)

		lastId = int(items[-1].xpath('@id')[0].split('-')[-1])

		logging.info('Page parsed. Total: %d' % (self.count,))

		return lastId

	def _parse(self, items):
		for item in items:
			# 形式为 "logitem-{id}"
			qId = int(item.xpath('@id')[0].split('-')[-1])
			qTitle = item.xpath(self.rules['XPATH']['TITLE'])[0]
			qUrl = '%s%s' % (self.rules['HOME'], qTitle.xpath('@href')[0])
			qTitle = qTitle.text
			qAuthor = item.xpath(self.rules['XPATH']['AUTHOR'])[0].text
			qTime = item.xpath(self.rules['XPATH']['DATE'])[0].text
			self._insertNew(qId, qTitle, qUrl, qAuthor, qTime)

		# 更新到数据库
		self.spider.db.commit()


	def _modHeader(self):
		self.session.headers.update(self.configs['HEADERS']['MOD'])

	def _getXsrf(self):
		return self.session.cookies.get('_xsrf')
 
 	# 往数据库中插入新的数据
 	def _insertNew(self, id, title, url, author, time):
 		try:
 			self.dbCursor.execute('INSERT INTO Question values (?, ?, ?, ?, ?)', (id, title, url, author, time))
 			self.count += 1
 		except sqlite3.IntegrityError as e:
 			logging.warning('Already Exist.')




