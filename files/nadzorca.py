#!/usr/bin/puthon
# Filename: nadzorca.py

import subprocess
import shlex
import os

class Game:
	memory_limit = 50  # Memory limit in MB
	time_limit = 600	# Time limit in seconds
	judge_path = None	# The binary file of the judge 
	
	def __init__(self, mem_limit=None, t_limit=None, j_path=None):
		if mem_limit:
			self.memory_limit = mem_limit
		if t_limit:
			self.time_limit = t_limit
		if j_path:
			self.judge_path = j_path

	def set_limits(self, mem_limit=None, t_limit=None):
		if mem_limit:
			self.memory_limit = mem_limit
		if t_limit:
			self.time_limit = t_limit
	
	def set_judge(self, j):
		self.judge_path = j

class Bot:
	filepath = None

	def __init__(self, fpath=None):
		if fpath:
			self.filepath = fpath

	def set_filepath(self, fpath):
		self.filepath = fpath

"""
	ListOfBots is a list of objects of class Bot.
	Bots are meant to know where is theirs executable file is located.

	Game, according to the description above knows its limits and the judge, 
	which is an executable file
"""
def play(list_of_bots, game):
	judge_process = subprocess.Popen(
			args=game.judge_path,
			stdin=subprocess.PIPE,
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE
			)
	while True:
		l = judge_process.stdout.readline()
		if not l:
			break
		else:
			print l

	bots_process_list = []
	mem_lim = "ulimit -v %d" % (game.memory_limit)
	time_lim = "ulimit -t %d" % (game.time_limit)
	for bot in list_of_bots:
		arg_to_execute = "ulimit -v %d -t %d ; ./%s" % (game.memory_limit * 1024, game.time_limit, bot.filepath)
		bot_process = subprocess.Popen(
				args = arg_to_execute,
				stdin = subprocess.PIPE,
				stdout = subprocess.PIPE,
				stderr = subprocess.PIPE,
				shell=True,
				)
		bot_process_out = bot_process.stdout.read()
		print bot_process_out
		bots_process_list.append(bot_process)

		"""
			komunikacja od Botow idzie do sedziego
			Komunikacja od sedziego trzeba sparsowac i rozeslac do odpowiednich ziomow
		"""
