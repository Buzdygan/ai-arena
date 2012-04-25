import os
current_dir = os.path.dirname(os.path.abspath(__file__))
grand_dir = os.path.dirname(os.path.dirname(current_dir))
os.sys.path.insert(0, grand_dir) 
import nadzorca

print 'TEST bot_logs'

judge_path = current_dir + "/bot_logs_judge"
bot_path = current_dir + "/bot_logs_bot"
results = nadzorca.play(judge_file=judge_path, players=[bot_path, bot_path], time_limit=1, memory_limit=100000)

passed = True
bot1_info = ''
for item in results['logs'][0]:
    bot1_info = bot1_info + item
bot2_info = ''
for item in results['logs'][1]:
    bot2_info = bot2_info + item

if bot1_info != '1122334455':
    passed = False
    print "bot1 info: " + bot1_info + " instead of 1122334455"

if bot2_info != '11223344':
    passed = False
    print "bot2 info: " + bot2_info + " instead of 11223344"

if results['exit_status'] != 0:
    passed = False
    print "exit status: " + str(results['exit_status']) + " instead of 0"

if results['results'] != [1, 0]:
    passed = False
    print "results: " + str(results['results']) + " instead of [1, 0]"

if passed:
    print "PASS"
else:
    print "FAIL"
