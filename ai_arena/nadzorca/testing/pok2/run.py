import os
current_dir = os.path.dirname(os.path.abspath(__file__))
grand_dir = os.path.dirname(os.path.dirname(current_dir))
os.sys.path.insert(0, grand_dir) 
import nadzorca

print 'TEST pok'

judge_path = current_dir + "/pok_judge"
bot_path = current_dir + "/cpp_pok_bot"
bot_lang = 'CPP'
bot2_path = current_dir + "/cpp_pok_bot"
bot2_lang = 'CPP'
results = nadzorca.play(judge_file=judge_path, judge_lang='CPP', players=[(bot_path, bot_lang), (bot2_path, bot2_lang)], time_limit=10, memory_limit=1000000)

#print results

passed = True
judge_info = ''
for item in results['logs']['judge']:
    judge_info = judge_info + item
bot1_info = ''
for item in results['logs'][0]:
    bot1_info = bot1_info + item
bot2_info = ''
for item in results['logs'][1]:
    bot2_info = bot2_info + item

print "judge info:\n" + judge_info

#print "bot1 info:\n" + bot1_info

#print "bot2 info:\n" + bot2_info

if results['exit_status'] != 10:
    passed = False
    print "exit status: " + str(results['exit_status']) + " instead of 10"

print "results: " + str(results['results'])

if passed:
    print "PASS"
else:
    print "FAIL"
