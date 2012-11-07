#!/usr/bin/python
#_*_ encoding:UTF-8 _*_

# The spider of BBC healthcare channel.
# Author: zzq889 <zzq889@gmail.com>

import urllib, urllib2, os, re, simplejson

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
RESULT_ROOT = os.path.join(PROJECT_ROOT, 'result')
BBC_ROOT = 'http://www.bbc.co.uk'
FORM_URL = '/apps/ifl/health/first_aid/quizengine/'

def get_questions_in_serial(init_page_url, quiz_name):
	#fetch quiz by url
	QUIZ_ROOT = os.path.join(RESULT_ROOT, quiz_name)
	if not os.path.exists(QUIZ_ROOT):
		os.mkdir(QUIZ_ROOT)
	
	page_count = 1
	quest_count = 1
	
	init_page = getter(init_page_url)
	first_page_name = str(quest_count) + '.html'
	save(os.path.join(QUIZ_ROOT, first_page_name), init_page)
	form = parse_form(init_page)
	
	while True:
		page_count = page_count + 1
		
		if form:
			postdata = urllib.urlencode(form)
			result = sender(BBC_ROOT + FORM_URL, postdata)
			
			if page_count % 2:
				quest_count = quest_count + 1
				filename = str(quest_count) + '.html'
				save(os.path.join(QUIZ_ROOT, filename), result)
			else:
				filename = str(quest_count) + '_answer_a.html'
				save(os.path.join(QUIZ_ROOT, filename), result)
			
			form = parse_form(result)
		
		else:
			break

def parse_form(html):
	#find & parse the form
	form_prog = re.compile(r'<form.*\<\/form\>', re.S)
	form_match = form_prog.search(html)
	
	if form_match:
		form = form_match.group(0)
		action_prog = re.compile(r'action=\"(.+?)\"')
		action = action_prog.search(form).group(1)
		
		if action == FORM_URL:
			# parse each input element
			i_prog = re.compile(r'<input.+?\/?\>', re.S)
			i_name_prog = re.compile(r'name=\"(.+?)\"')
			i_type_prog = re.compile(r'type=\"(.+?)\"')
			i_value_prog = re.compile(r'value=\"(.+?)\"', re.S)
		
			form_data = {}
			for i_element in i_prog.findall(form):
				# Get all element data for post
				i_name = i_name_prog.search(i_element)
				i_type = i_type_prog.search(i_element).group(1)
				i_value = i_value_prog.search(i_element)
				if i_type == 'hidden':
					form_data[i_name.group(1)] = i_value.group(1)
				elif i_type == 'radio':
					form_data[i_name.group(1)] = 'a'
		
			return form_data
			
		else:
			print '-------------------'
			print 'Finished.'
	
	else:
		return False

def answer_each_question(quiz_dir, page_num, html):
	#find & parse the form
	form_prog = re.compile(r'<form.*\<\/form\>', re.S)
	form_match = form_prog.search(html)
	
	if form_match:
		form = form_match.group(0)
		action_prog = re.compile(r'action=\"(.+?)\"')
		action = action_prog.search(form).group(1)
		
		if action == FORM_URL:
			# parse each input element
			i_prog = re.compile(r'<input.+?\/?\>', re.S)
			i_name_prog = re.compile(r'name=\"(.+?)\"')
			i_type_prog = re.compile(r'type=\"(.+?)\"')
			i_value_prog = re.compile(r'value=\"(.+?)\"', re.S)
			
			form_data = {}
			radio_name = None
			radio_set = []
			
			for i_element in i_prog.findall(form):
				# Get all element data for post
				i_name = i_name_prog.search(i_element)
				i_type = i_type_prog.search(i_element).group(1)
				i_value = i_value_prog.search(i_element)
				if i_type == 'hidden':
					form_data[i_name.group(1)] = i_value.group(1)
				elif i_type == 'radio':
					radio_name = i_name.group(1)
					radio_set.append(i_value.group(1))
			
			for ans in radio_set:
				form_data[radio_name] = ans
				result = sender(BBC_ROOT + FORM_URL, urllib.urlencode(form_data))
				filename = str(page_num) + '_answer_' + ans + '.html'
				save(os.path.join(quiz_dir, filename), result)
				print filename
				
		
		else:
			print '-------------------'
			print 'Finished.'
		
	else:
		return False


def getter(url):
	result = urllib2.urlopen(url)
	html = result.read()
	return html

def sender(url, postdata):
	req = urllib2.Request(
		url = url, 
		data = postdata
	)
	result = urllib2.urlopen(req)
	html = result.read()
	return html


def read_from_file(filepath):
	f = open(filepath, 'r')
	text = f.read()
	f.close()
	return text

def save(filepath, text):
	if text:
		f = open(filepath, 'w')
		f.write(text)
		print filepath
		f.close()


def first_process():
	html_quiz_index = read_from_file(os.path.join(PROJECT_ROOT, 'quiz_index.html'))
	entry_prog = re.compile(r'href=\"(.+?)\"')
	for quiz_url in entry_prog.findall(html_quiz_index):
		quiz_name = re.search(r'quiz=(\w+)\&', quiz_url).group(1)
		get_questions_in_serial(BBC_ROOT + quiz_url, quiz_name)

def second_process():
	html_quiz_index = read_from_file(os.path.join(PROJECT_ROOT, 'quiz2.html'))
	entry_prog = re.compile(r'href=\"(.+?)\"')
	for quiz_url in entry_prog.findall(html_quiz_index):
		quiz_name = re.search(r'quiz=(\w+)\&', quiz_url).group(1)
		quiz_dir = os.path.join(RESULT_ROOT, quiz_name)
		filelist = os.listdir(quiz_dir)
		filelist = [ x[:-5] for x in filelist if x[:-5].isdigit() ]
		filelist.pop()
		for question_num in filelist:
			question_path = os.path.join(quiz_dir, question_num + '.html')
			question_page = read_from_file(question_path)
			answer_each_question(quiz_dir, question_num, question_page)
			

if __name__ == '__main__':
	#first_process()
	#second_process()