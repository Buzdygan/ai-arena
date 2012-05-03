import os
current_dir = os.path.dirname(os.path.abspath(__file__))
grand_dir = os.path.dirname(os.path.dirname(current_dir))
os.sys.path.insert(0, grand_dir) 
import nadzorca

print 'TEST timeout'

judge_path = current_dir + "/timeout_judge"
bot_path = current_dir + "/timeout_bot"
results = nadzorca.play(judge_file=judge_path, players=[bot_path, bot_path], time_limit=1, memory_limit=100000)

passed = True
judge_info = ''
for item in results['logs']['judge']:
    judge_info = judge_info + item

if judge_info != '1122DEAD_BOT':
    passed = False
    print "judge info: " + judge_info + " instead of 1122DEAD_BOT"

if results['exit_status'] != 0:
    passed = False
    print "exit status: " + str(results['exit_status']) + " instead of 0"

if passed:
    print "PASS"
else:
    print "FAIL"
