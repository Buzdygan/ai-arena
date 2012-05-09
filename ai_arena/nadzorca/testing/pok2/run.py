import os
current_dir = os.path.dirname(os.path.abspath(__file__))
grand_dir = os.path.dirname(os.path.dirname(current_dir))
os.sys.path.insert(0, grand_dir) 
import nadzorca

print 'TEST pok'

judge_path = current_dir + "/pok_judge"
bot_path = current_dir + "/pok_bot"
results = nadzorca.play(judge_file=judge_path, players=[bot_path, bot_path], time_limit=10000, memory_limit=1000000)

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

if results['exit_status'] != 0:
    passed = False
    print "exit status: " + str(results['exit_status']) + " instead of 0"

print "results: " + str(results['results'])

if passed:
    print "PASS"
else:
    print "FAIL"
