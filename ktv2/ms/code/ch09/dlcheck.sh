#!/bin/bash
# 9-16: 공개 화산 자료 입수처에 셸(curl)로 접속해 내려받기가 되는지 시도한다. 우회하지 않고 결과만 적는다.
# 대조군으로 패키지 저장소(PyPI)도 함께 시도한다. 임시 폴더에 받고 끝나면 지운다.
TMP=$(mktemp -d)
date
try() {
  local url="$1"
  local out=$(curl -sS -m 30 -o "$TMP/f" -w "http=%{http_code} 받은바이트=%{size_download}" "$url" 2>&1 | tail -2 | tr '\n' ' ')
  echo "$url -> $out"
}
try "https://volcano.si.edu/"
try "https://volcano.si.edu/database/list_volcano_holocene_excel.cfm"
try "https://webservices.volcano.si.edu/geoserver/GVP-VOTW/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=GVP-VOTW:Smithsonian_VOTW_Holocene_Volcanoes&maxFeatures=5&outputFormat=csv"
try "https://webservices.volcano.si.edu/geoserver/GVP-VOTW/wfs?request=GetCapabilities"
try "https://doi.org/10.5479/si.GVP.VOTW5-2026.5.4"
try "https://www.ngdc.noaa.gov/hazel/view/about"
try "https://www.earthchem.org/"
try "https://pypi.org/simple/scipy/"
try "https://api.github.com/"
rm -rf "$TMP"
