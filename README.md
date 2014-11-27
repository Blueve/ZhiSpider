ZhiSpider
=========

知蛛 — 抓取知乎的问题及答案的爬虫，采用SQLite存储

- 配置说明

  - Mac OSX

  1.
  '''
  sudo pip install requests
  '''

  1.
  '''
  sudo pip install pyyaml
  '''
  1.
  '''
  sudo apt-get install libxml2-dev libxslt-dev python-dev
  '''

  1.
  '''
  sudo pip install lxml
  '''

  - Ubuntu

  1.
  '''
  sudo pip install requests
  '''

  1.
  '''
  sudo pip install pyyaml
  '''

  1.
  '''
  STATIC_DEPS=true sudo pip install lxml
  '''

 - 使用

   1.
   修改Config.yaml文件中的知乎账号部分信息，填入可以使用的账号

   2.
   执行
   '''
   python Setup.py
   '''

   3.
   参考ZhiSpider.py的__main__部分，开启功能，并执行
   '''
   python ZhiSpider.py
   '''