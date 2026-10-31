cd /home/claude/book
python3 build.py color > /tmp/b1c.log 2>&1
python3 build.py bw > /tmp/b1b.log 2>&1
python3 -c "
import sys,runpy
sys.setrecursionlimit(20000)
sys.argv=['a','build/book.html']
runpy.run_path('scripts/audit-v1.py',run_name='__main__')
" > /tmp/b1a.log 2>&1
echo done > /tmp/b1done
