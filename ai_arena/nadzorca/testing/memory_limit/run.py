import os
current_dir = os.path.dirname(os.path.abspath(__file__))
grand_dir = os.path.dirname(os.path.dirname(current_dir))
os.sys.path.insert(0, grand_dir) 
import nadzorca

print 'TEST memory_limit'

judge_path = current_dir + "/memory_limit_judge"
bot_path = current_dir + "/memory_limit_bot"
results = nadzorca.play(judge_file=judge_path, judge_lang='CPP', players=[(bot_path, 'CPP'), (bot_path, 'CPP')], time_limit=100, memory_limit=10000)

#print results

passed = True

if results['results'] != [0, 0]:
    passed = False
    print "results: " + str(results['results']) + " instead of [1, 0]"

if passed:
    print "PASS"
else:
    print "FAIL"
