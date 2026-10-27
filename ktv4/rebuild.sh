cd /home/claude/book4
python3 build.py color > /tmp/b4c.log 2>&1
python3 build.py bw > /tmp/b4b.log 2>&1
python3 -c "
import sys,runpy
sys.setrecursionlimit(20000)
sys.argv=['a','build/book.html']
runpy.run_path('scripts/audit-v1.py',run_name='__main__')
" > /tmp/b4a.log 2>&1
echo done > /tmp/b4done
