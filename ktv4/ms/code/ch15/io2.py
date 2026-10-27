# -*- coding: utf-8 -*-
"""2장 계산 공용 읽기 함수. 자료 두 개는 pip 패키지 pyleoclim 1.3.0 안의 예제 자료 사본이다.
GISP2: pyleoclim/data/GISP2_d18O.csv  (열: 깊이 m, d18O 퍼밀, 나이 yr BP). NOAA 의 'GISP2 Ice Core 110,000 Year Oxygen Isotope Data'
        (Grootes & Stuiver 1997 인용, 시간 범위 110,977 ~ -37 BP)와 같은 범위이다. 이 파일이 그 NOAA 파일의 사본이라는 것은 범위와 열로 추정한 것이며 원본과 대조하지 못했다.
EDC: pyleoclim/data/edc3deuttemp2007.csv (열: 나이, 중수소, 온도). NOAA 의 edc3deuttemp2007 (Jouzel 등 2007, EDC3 시간 눈금) 사본으로 추정. 원본과 대조하지 못했다.
EDC 파일은 줄바꿈이 CR 이어서 edc3deuttemp2007-clean.csv 로 줄바꿈만 고친 사본을 둔다.
"""
import os
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
def gisp2():
    g = pd.read_csv(os.path.join(HERE, 'gisp2-d18o-pyleoclim.csv'))
    g.columns = ['depth', 'd18o', 'age']
    return g.dropna().reset_index(drop=True)
def edc():
    e = pd.read_csv(os.path.join(HERE, 'edc3deuttemp2007-clean.csv'))
    e.columns = ['age', 'dD', 'T']
    return e.dropna().reset_index(drop=True)
