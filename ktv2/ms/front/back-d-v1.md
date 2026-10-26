# 부록 C. z840에서 실행해야 채워지는 칸

이 책을 쓴 환경에는 GPU가 없고 논문 사이트에 접속할 수 없었다. 아래는 독자(또는 지은이)가 GPU와 네트워크가 있는 컴퓨터에서 실행해 채울 수 있는 칸이다.

{{T:실행 환경이 갖추어진 컴퓨터에서 채울 칸}}

| 장 | 실습 | 할 일 | 스크립트 |
|---|---|---|---|
| 2 | 2-1 | 논문 API 호출 실행, 응답과 이용 조건 확인 | `ms/code/ch02/apiclient.py` |
| 10 | 10-7b, 10-9 | GPU 시간과 메모리 측정, 12 GiB 교차점 확인 | `ms/code/ch10/gpu-bench-v1.py` |
| 11 | 11-7b | GPU 난수와 CPU 난수의 통계적 일치, 속도 | `ms/code/ch11/mc-bench-v1.py` |
| 12 | 12-4b | GPU 시뮬레이션 속도 | `ms/code/ch12/sim-bench-v1.py` |
| 13 | 13-12, 13-13 | 로컬 모델 호출, 실제 모델 출력에 점검기 적용 | `ms/code/ch13/llm-client-v1.py` |

10장의 측정 명령은 다음과 같다. CUDA 13 계열이면 `requirements-gpu-v1.txt`의 CuPy 패키지를 `cupy-cuda13x`로 바꾼다.

```
cd ms/code/ch10
python3 -m venv venv-gpu
source venv-gpu/bin/activate
pip install -r requirements-gpu-v1.txt
python gpu-bench-v1.py --xp cupy --tag z840
```
