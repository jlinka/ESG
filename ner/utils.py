#_*_ coding:utf-8 _*_
import logging, sys, argparse

def str2bool(v):
	# copy from StackOverflow
	if v.lower() in ('yes', 'true', 't', 'y', '1'):
		return True
	elif v.lower() in ('no', 'false', 'f', 'n', '0'):
		return False
	else:
		raise argparse.ArgumentTypeError('Boolean value expected.')


def get_entity(tag_seq, char_seq):
	PER = get_PER_entity(tag_seq, char_seq)
	LOC = get_LOC_entity(tag_seq, char_seq)
	ORG = get_ORG_entity(tag_seq, char_seq)
	return PER, LOC, ORG

def get_entity2(tag_seq, char_seq):
	company = get_company_entity(tag_seq, char_seq)
	person = get_person_entity(tag_seq, char_seq)
	# meeting = get_meeting_entity(tag_seq, char_seq)
	# return company, person, meeting
	return company, person

def get_entity_in_esg(tag_seq, char_seq):
	company = get_company_entity(tag_seq, char_seq)
	person = get_person_entity(tag_seq, char_seq)
	location = get_person_entity(tag_seq, char_seq)
	time = get_person_entity(tag_seq, char_seq)

	# meeting = get_meeting_entity(tag_seq, char_seq)
	# return company, person, meeting
	return company, person, location, time

def get_entity3(tag_seq, char_seq):
	company = get_company_entity(tag_seq, char_seq)
	person = get_person_entity(tag_seq, char_seq)
	meeting = get_meeting_entity(tag_seq, char_seq)
	return company, person, meeting

def get_PER_entity(tag_seq, char_seq):
	length = len(char_seq)
	PER = []
	for i, (char, tag) in enumerate(zip(char_seq, tag_seq)):
		if tag == 'B-PER':
			if 'per' in locals().keys():
				PER.append(per)
				del per
			per = char
			if i+1 == length:
				PER.append(per)
		if tag == 'I-PER':
			per += char
			if i+1 == length:
				PER.append(per)
		if tag not in ['I-PER', 'B-PER']:
			if 'per' in locals().keys():
				PER.append(per)
				del per
			continue
	return PER


def get_LOC_entity(tag_seq, char_seq):
	length = len(char_seq)
	LOC = []
	for i, (char, tag) in enumerate(zip(char_seq, tag_seq)):
		if tag == 'B-LOC':
			if 'loc' in locals().keys():
				LOC.append(loc)
				del loc
			loc = char
			if i+1 == length:
				LOC.append(loc)
		if tag == 'I-LOC':
			loc += char
			if i+1 == length:
				LOC.append(loc)
		if tag not in ['I-LOC', 'B-LOC']:
			if 'loc' in locals().keys():
				LOC.append(loc)
				del loc
			continue
	return LOC


def get_ORG_entity(tag_seq, char_seq):
	length = len(char_seq)
	ORG = []
	for i, (char, tag) in enumerate(zip(char_seq, tag_seq)):
		if tag == 'B-ORG':
			if 'org' in locals().keys():
				ORG.append(org)
				del org
			org = char
			if i+1 == length:
				ORG.append(org)
		if tag == 'I-ORG':
			org += char
			if i+1 == length:
				ORG.append(org)
		if tag not in ['I-ORG', 'B-ORG']:
			if 'org' in locals().keys():
				ORG.append(org)
				del org
			continue
	return ORG


def get_entity_in_esg(tag_seq, char_seq):
	"""
	esg项目代码
	:param tag_seq:
	:param char_seq:
	:return:
	"""
	company = get_company_entity(tag_seq, char_seq)
	person = get_person_entity(tag_seq, char_seq)
	location = get_location_entity(tag_seq, char_seq)
	time = get_time_entity(tag_seq, char_seq)

	return company, person, location, time


def get_company_entity(tag_seq, char_seq):
	length = len(char_seq)
	ORG = []
	for i, (char, tag) in enumerate(zip(char_seq, tag_seq)):
		if tag == 'B-company_name':
			if 'org' in locals().keys():
				ORG.append(org)
				del org
			org = char
			if i+1 == length:
				ORG.append(org)
		if tag == 'I-company_name':
			if 'org' not in locals().keys():
				continue
			org += char
			if i+1 == length:
				ORG.append(org)
		if tag not in ['I-company_name', 'B-company_name']:
			if 'org' in locals().keys():
				ORG.append(org)
				del org
			continue
	return ORG

def get_person_entity(tag_seq, char_seq):
	length = len(char_seq)
	ORG = []
	for i, (char, tag) in enumerate(zip(char_seq, tag_seq)):
		if tag == 'B-person_name':
			if 'org' in locals().keys():
				ORG.append(org)
				del org
			org = char
			if i+1 == length:
				ORG.append(org)
		if tag == 'I-person_name':
			if 'org' not in locals().keys():
				continue
			org += char
			if i+1 == length:
				ORG.append(org)
		if tag not in ['I-person_name', 'B-person_name']:
			if 'org' in locals().keys():
				ORG.append(org)
				del org
			continue
	return ORG


def get_location_entity(tag_seq, char_seq):
	length = len(char_seq)
	ORG = []
	for i, (char, tag) in enumerate(zip(char_seq, tag_seq)):
		if tag == 'B-location':
			if 'org' in locals().keys():
				ORG.append(org)
				del org
			org = char
			if i+1 == length:
				ORG.append(org)
		if tag == 'I-location':
			if 'org' not in locals().keys():
				continue
			org += char
			if i+1 == length:
				ORG.append(org)
		if tag not in ['I-location', 'B-location']:
			if 'org' in locals().keys():
				ORG.append(org)
				del org
			continue
	return ORG


def get_time_entity(tag_seq, char_seq):
	length = len(char_seq)
	ORG = []
	for i, (char, tag) in enumerate(zip(char_seq, tag_seq)):
		if tag == 'B-time':
			if 'org' in locals().keys():
				ORG.append(org)
				del org
			org = char
			if i+1 == length:
				ORG.append(org)
		if tag == 'I-time':
			if 'org' not in locals().keys():
				continue
			org += char
			if i+1 == length:
				ORG.append(org)
		if tag not in ['I-time', 'B-time']:
			if 'org' in locals().keys():
				ORG.append(org)
				del org
			continue
	return ORG

def get_meeting_entity(tag_seq, char_seq):
	length = len(char_seq)
	ORG = []
	for i, (char, tag) in enumerate(zip(char_seq, tag_seq)):
		if tag == 'B-meeting':
			if 'org' in locals().keys():
				ORG.append(org)
				del org
			org = char
			if i+1 == length:
				ORG.append(org)
		if tag == 'I-meeting':
			if 'org' not in locals().keys():
				continue
			org += char
			if i+1 == length:
				ORG.append(org)
		if tag not in ['I-meeting', 'B-meeting']:
			if 'org' in locals().keys():
				ORG.append(org)
				del org
			continue
	return ORG

def get_logger(filename):
	logger = logging.getLogger('logger')
	logger.setLevel(logging.DEBUG)
	logging.basicConfig(format='%(message)s', level=logging.DEBUG)
	handler = logging.FileHandler(filename)
	handler.setLevel(logging.DEBUG)
	handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s: %(message)s'))
	logging.getLogger().addHandler(handler)
	return logger
