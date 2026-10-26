# GPU가 없는 컨테이너에서 CuPy의 설치 상태와 API 존재 여부만 확인한다. GPU 계산은 하지 않는다.
import sys, traceback
import numpy as np
try:
    import cupy as cp
except Exception as e:
    print('import cupy 실패:', type(e).__name__, e); sys.exit(1)
print('cupy', cp.__version__, '| numpy', np.__version__)
for name in ('get_array_module', 'asarray', 'asnumpy', 'percentile', 'searchsorted', 'arange', 'repeat', 'sin', 'cos', 'arcsin', 'radians', 'sqrt', 'concatenate'):
    print('cupy.%-18s 있음: %s' % (name, hasattr(cp, name)))
print('cupy.random.default_rng 있음:', hasattr(cp.random, 'default_rng'))
print('cupy.random.Generator.integers 있음:', hasattr(cp.random, 'Generator') and hasattr(cp.random.Generator, 'integers'))
# gpu-bench-v1.py가 부르는 이름이 이 CuPy 버전에 있는지(호출이 아니라 이름의 존재만 본다)
names = ['cuda.Device', 'cuda.runtime.memGetInfo', 'cuda.runtime.getDeviceProperties', 'cuda.runtime.runtimeGetVersion',
         'cuda.runtime.driverGetVersion', 'cuda.runtime.getDeviceCount', 'get_default_memory_pool', 'cuda.memory.OutOfMemoryError',
         'cuda.MemoryPool', 'cuda.set_allocator']
for dotted in names:
    o = cp; ok = True
    for part in dotted.split('.'):
        if hasattr(o, part): o = getattr(o, part)
        else: ok = False; break
    print('cupy.%-34s 있음: %s' % (dotted, ok))
for meth in ('used_bytes', 'total_bytes', 'free_all_blocks', 'set_limit', 'get_limit'):
    print('MemoryPool.%-16s 있음: %s' % (meth, hasattr(cp.cuda.MemoryPool, meth)))
print('Device.synchronize 있음:', hasattr(cp.cuda.Device, 'synchronize'))
print('cupy.get_array_module(numpy 배열) ->', cp.get_array_module(np.zeros(2)).__name__)
for label, fn in (('cupy.cuda.runtime.getDeviceCount()', lambda: cp.cuda.runtime.getDeviceCount()),
                  ('cupy.arange(3)', lambda: cp.arange(3)),
                  ('cupy.random.default_rng(1).integers(0, 5, 3)', lambda: cp.random.default_rng(1).integers(0, 5, 3))):
    try:
        print('%-48s -> %r' % (label, fn()))
    except Exception as e:
        print('%-48s -> 예외 %s: %s' % (label, type(e).__name__, str(e).splitlines()[0][:160]))
