#!/usr/bin/python2.5
#_*_ encoding: utf-8 _*_

import urllib
import urllib2
from BeautifulSoup import BeautifulSoup
import re
import os


class BBSCrawling:
	''' crawl university bbs sites '''
	
	def __init__(self):
		''' Define Global info '''
		self.URL_ROOT = 'http://bbs.sjtu.edu.cn'
		self.url_login = self.URL_ROOT + '/bbslogin?id=guest'
	
	def get_boards(self):
		''' GET board list '''
		url_boards = self.URL_ROOT + '/bbsall'
		req = urllib2.Request(url_boards)
		response = urllib2.urlopen( req )
		content_boards = unicode(response.read(), 'gbk', 'ignore').encode('utf-8', 'ignore')
		
		''' parse html '''
		soup = BeautifulSoup(content_boards)
		self.boards = []
		for board in soup.findAll('tr'):
			try:
				board_id = int(board.contents[0].string.strip())
				board_screen_name = board.contents[1].contents[0].string.strip()
				board_category = board.contents[2].contents[0].string.strip()
				board_name = board.contents[3].contents[0].string.strip()
				board_admin = board.contents[4].contents[0].string.strip()
			
				self.boards.append({
					'id': board_id,
					'screen_name': board_screen_name,
					'category': board_category,
					'name': board_name,
					'admin': board_admin
				})
			except:
				continue
		
	
	def get_topics_by_board_screen_name(self, board_screen_name):
		''' GET topics info '''
		page_num = 0
		while True :
			try:
				url_board = self.URL_ROOT + '/bbstdoc,board,' + board_screen_name + \
							',page,' + str(page_num) + '.html'
				req = urllib2.Request(url_board)
				response = urllib2.urlopen(req)
				content_topics = unicode(response.read(), 'gbk', 'ignore').encode('utf-8', 'ignore')
				
				self.get_topic_info_by_content(board_screen_name, content_topics)
				
				''' Define the Stop position '''
				keyword = '下一页'
				if content_topics.find(keyword) < 0:
					break
				
				''' increase page count '''
				page_num = page_num + 1
			
			except urllib2.HTTPError, e:
				print 'Error code:', e.code
				break
	
	def get_topic_info_by_content(self, board_screen_name, content_topics):
		''' parse html '''
		soup = BeautifulSoup(content_topics)
		self.topics = []
		for topic in soup.findAll('tr'):
			try:
				topic_id = int(topic.contents[0].string.strip())
				#topic_status = topic.contents[1].string.strip()
				topic_author = topic.contents[2].contents[0].string.strip()
				topic_datetime = topic.contents[3].string.strip()
				topic_title = topic.contents[4].contents[0].string.strip()
				topic_url = topic.contents[4].a['href']
				topic_reid = int(re.search('reid\,(\d+)', topic_url).group(1))
				
				self.topics.append({
					'id': topic_id,
					#'status': topic_status,
					'author': topic_author,
					'title': topic_title,
					'board_screen_name': board_screen_name,
					'reid': topic_reid
				})
				
				#test
				print topic_id, topic_author, topic_datetime, topic_title
				print topic_reid
				
			except:
				continue
	
	def get_threads_by_reid(self, reid, board_screen_name):
		#get thread list
		print 'THREAD ROOT ID: ', reid
		
		url_threads = self.URL_ROOT + '/bbstcon?board=' + board_screen_name + \
					'&reid=' + str(reid) + '&file=M.' + str(reid) + '.A&showall=true'
		req = urllib2.Request(url_threads)
		response = urllib2.urlopen( req )
		content_threads = unicode(response.read(), 'gbk', 'ignore').encode('utf-8', 'ignore')
		
		''' parse html '''
		soup = BeautifulSoup(content_threads)
		self.threads = []
		for thread in soup.findAll('pre'):
			thread_author = thread.contents[5].string.strip()
			thread_content = thread.contents[6].string.strip()
			thread_url = thread.a['href']
			thread_id = int(re.search('M\.(\d+)', thread_url).group(1))
			
			self.threads.append({
				'id': thread_id,
				'author': thread_author,
				'content': thread_content,
				'board_screen_name': board_screen_name,
				'root_id': reid
			})
			
			#test
			print thread_id, thread_author
			print thread_content
			print


if __name__ == '__main__':
	s = BBSCrawling()
	s.get_boards()
	
	'''
	count = 0
	for board in s.boards:
		#removable following 4 lines
		count = count + 1
		if count > 1:
			break
		flag = 0
		s.get_topics_by_board_screen_name(board['screen_name'])
	'''
	
	s.get_threads_by_reid(1301638709, 'IS')