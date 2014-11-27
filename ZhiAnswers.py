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

class ZhiAnswers(object):

	def __init__(self, spider):
		self.configs = spider.configs
		self.rules = spider.rules['ANSWER']

		self.spider = spider
		self.session = spider.session
		self.dbCursor = spider.dbCursor

		self.count = 0

	def start(self):
		while True:
			# 读取数据库队列 每次读取N个问题
			self.dbCursor.execute('SELECT id, url FROM Question WHERE visited = 0 LIMIT ? OFFSET 0', (self.rules['QUEUE']['LIMIT'],))
			queue = self.dbCursor.fetchall()
			# 全部爬取完毕后退出
			if len(queue) == 0:
				break
			# 从队列中依次爬取
			for item in queue:
				id = item[0]
				url = item[1]
				logging.info('Visit %s' % (url,))
				# 访问指定的问题并解析该页面
				while True:
					try:
						response = self.session.get(url, timeout = 5.05)
					except requests.exceptions.Timeout:
						logging.warning('Timeout')
						time.sleep(20)
						continue
					except requests.exceptions.ConnectionError:
						logging.warning('Connection Error')
						self.spider.login()
						continue

					statusCode = response.status_code
					if statusCode >= 500:
						time.sleep(10)
						continue
					elif statusCode >= 400:
						logging.warning("Cant't fetch page.")
						time.sleep(10)
						break

					self._parseHtml(response.content)
					break
				# 更新磁盘队列状态
				self._updateQueueItem(id)
				# 更新到数据库
				self.spider.db.commit()
				time.sleep(1)

	# 解析HTML页面
	def _parseHtml(self, content):
		html = etree.HTML(content)
		tags = html.xpath(self.rules['XPATH']['TAGS'])

		answers = html.xpath(self.rules['XPATH']['ANSWERS'])
		count = 0
		for answer in answers:
			try:
				aid = int(answer.xpath('@data-aid')[0])
				content = etree.tostring(answer.xpath(self.rules['XPATH']['CONTENT'])[0], method='text', encoding="unicode")
			except Exception:
				logging.warning('Answer invalid.')
				continue
			# 判别匿名用户情况
			authorNode = answer.xpath(self.rules['XPATH']['AUTHOR'])
			if len(authorNode) == 0:
				author = answer.xpath(self.rules['XPATH']['AUTHOR_ANONYMOUS'])[0].text
			else:
				author = answer.xpath(self.rules['XPATH']['AUTHOR_SHOW'])[0].text
			date = answer.xpath(self.rules['XPATH']['DATE'])[0].text.split(' ')[-1]

			# 判断自己的回答的情况
			voteNode = answer.xpath(self.rules['XPATH']['VOTE_MY'])
			if len(voteNode) == 0:
				voteNode = answer.xpath(self.rules['XPATH']['VOTE_OTHER'])[0]
				vote = int(voteNode.xpath('@data-votecount')[0])
			else:
				vote = int(voteNode[0].text)

			# 只收集有限的答案
			if vote > int(self.rules['VOTELIMIT']) or count < int(self.rules['MAX']):
				tagsNode = answer.xpath(self.rules['XPATH']['TAGS'])
				tags = ''
				for tag in tagsNode:
					tags += tag.text + ','
				self._insertNew(aid, content, vote, author, date, tags)
				count += 1
				logging.info('id %s |vote %d' % (aid, vote))
			else:
				break


		logging.info('Page parsed. Total: %d' % (self.count,))

 
 	# 往数据库中插入新的数据
 	def _insertNew(self, id, content, vote, author, date, tags):
 		try:
 			self.dbCursor.execute('INSERT INTO Answer values (?, ?, ?, ?, ?, ?)', (id, content, vote, author, date, tags))
 			self.count += 1
 		except sqlite3.IntegrityError as e:
 			logging.warning('Already Exist.')

 	def _updateQueueItem(self, id):
 		self.dbCursor.execute('UPDATE Question SET visited = 1 WHERE id = ?', (id,))




