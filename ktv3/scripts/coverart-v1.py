# 3권 표지 임시 그림: 유라시아 동서 지도 (Natural Earth 땅·호수·강). 생성 그림이 아니라 지도 자료로만 그린다.
import geopandas as gpd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from shapely.geometry import box
bb = box(25, 20, 135, 62)
land = gpd.read_file('geodata/ne_50m_land.geojson').clip(bb)
lakes = gpd.read_file('geodata/ne_10m_lakes.geojson').clip(bb)
riv = gpd.read_file('geodata/ne_10m_rivers_lake_centerlines.geojson').clip(bb)
fig = plt.figure(figsize=(10, 9.7), dpi=200); ax = fig.add_axes([0, 0, 1, 1]); fig.patch.set_facecolor('#0f2a3f'); ax.set_facecolor('#0f2a3f')
land.plot(ax=ax, color='#c7ae80', edgecolor='#e6dcc2', linewidth=0.4)
lakes.plot(ax=ax, color='#0f2a3f', edgecolor='#e6dcc2', linewidth=0.3)
riv.plot(ax=ax, color='#0f2a3f', linewidth=0.5)
ax.set_xlim(25, 135); ax.set_ylim(20, 62); ax.set_aspect(1/0.62); ax.axis('off')
fig.savefig('cover/art-c-v1.jpg', facecolor=fig.get_facecolor(), pil_kwargs={'quality': 92})
