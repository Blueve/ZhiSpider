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

# 设置Logging的基本格式末默认选项
logging.basicConfig(level=logging.INFO,
					format='[%(asctime)s][%(levelname)s]%(message)s',
					datefmt='%Y-%m-%d %H:%M:%S')

class ZhiSpiderSetup(object):

	def __init__(self):
		logging.info('Database installing...')
		with open('Config.yaml', 'rb') as fp:
			configs = yaml.load(fp)

		db = sqlite3.connect(configs['DB']['NAME'])
		self.dbCursor = db.cursor()

		#self._createQuestionTable()
		self._createAnswerTable()

		db.commit()
		self.dbCursor.close()
		db.close()
		logging.info('Done!')

	def _createQuestionTable(self):
		logging.info('Create table [Question]...')
		self.dbCursor.execute('CREATE TABLE Question('\
								'id INT PRIMARY KEY NOT NULL,'\
								'title NVARCHAR(255), '\
								'url VARCHAR(255),'\
								'author NVARCHAR(255),'\
								'date DATE,'\
								'visited BOOLEAN'\
								')')

	def _createAnswerTable(self):
		logging.info('Create table [Answer]...')
		self.dbCursor.execute('CREATE TABLE Answer('\
								'id INT PRIMARY KEY NOT NULL,'\
								'content NTEXT,'\
								'vote INT,'\
								'author NVARCHAR,'\
								'date DATE,'\
								'tags NTEXT'\
								')')


if __name__ == '__main__':
	# 安装
	ZhiSpiderSetup()