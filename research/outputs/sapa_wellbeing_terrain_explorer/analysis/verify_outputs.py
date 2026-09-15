import json, csv
from pathlib import Path
p=Path(__file__).resolve().parent/'research/outputs/sapa_wellbeing_terrain_explorer'
b=json.loads((p/'wellbeing_surface_bundle.json').read_text())
assert b['source']['respondents']==23679 and b['support']['k']==10
assert set(b['axes'])=={'Agreeableness','Conscientiousness','Extraversion','Emotional Stability','Openness'}
rows=list(csv.DictReader((p/'wellbeing_surface_aggregate.csv').open()))
assert rows and all(int(r['N'])>=10 for r in rows)
h=(p/'sapa_wellbeing_terrain_explorer.html').read_text()
assert 'Observed / marginal' in h and 'Conditional 5D model' in h and 'Plotly' in h
print(json.dumps({'ok':True,'aggregate_rows':len(rows),'terrain_N':b['source']['terrain_N'],'html_bytes':(p/'sapa_wellbeing_terrain_explorer.html').stat().st_size}))
