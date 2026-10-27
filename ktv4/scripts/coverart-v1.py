# 4권 표지 임시 그림: 세계 지도(람베르트 정적방위 투영, Natural Earth). 생성 그림이 아니라 지도 자료로만 그린다.
import geopandas as gpd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
crs = '+proj=laea +lat_0=25 +lon_0=40 +datum=WGS84'
land = gpd.read_file('geodata/ne_50m_land.geojson').to_crs(crs)
lakes = gpd.read_file('geodata/ne_10m_lakes.geojson').to_crs(crs)
fig = plt.figure(figsize=(10, 9.7), dpi=200); ax = fig.add_axes([0, 0, 1, 1]); fig.patch.set_facecolor('#0f2a3f'); ax.set_facecolor('#0f2a3f')
land.plot(ax=ax, color='#c7ae80', edgecolor='#e6dcc2', linewidth=0.3)
lakes.plot(ax=ax, color='#0f2a3f', edgecolor='#e6dcc2', linewidth=0.2)
R = 1.02e7
ax.set_xlim(-R, R); ax.set_ylim(-R*0.97, R*0.97); ax.set_aspect('equal'); ax.axis('off')
fig.savefig('cover/art-c-v1.jpg', facecolor=fig.get_facecolor(), pil_kwargs={'quality': 92})
