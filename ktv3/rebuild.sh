cd /home/claude/book3
python3 build.py color > /tmp/b3c.log 2>&1
python3 build.py bw > /tmp/b3b.log 2>&1
python3 -c "
import sys,runpy
sys.setrecursionlimit(20000)
sys.argv=['a','build/book.html']
runpy.run_path('scripts/audit-v1.py',run_name='__main__')
" > /tmp/b3a.log 2>&1
echo done > /tmp/b3done
