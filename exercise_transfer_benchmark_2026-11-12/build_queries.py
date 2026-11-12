"""Construct the two prespecified, source-derived searches."""
from pathlib import Path
ROOT = Path(__file__).resolve().parent
population = '(depress* OR dysthymi* OR "seasonal affective disorder")'
exercise = '(sport* OR exercis* OR aerobic* OR running OR jogging OR walk* OR hiking OR swim* OR aquatic* OR yoga OR "tai-chi" OR "tai chi" OR "tai ji" OR qigong OR "qi gong" OR cycling OR bicycl* OR ((physical OR strength*) AND (activit* OR educat* OR fitness OR train*)) OR "physical medicine" OR ((resistance OR weight*) AND (train* OR lift*)) OR "physical exertion")'
trial = '(random* OR trial* OR groups OR control* OR placebo* OR factorial* OR crossover* OR (cross AND over*) OR ((singl* OR doubl* OR trebl* OR tripl*) AND (blind* OR mask* OR dummy)) OR assign* OR allocat* OR volunteer* OR "treatment effectiveness evaluation" OR "mental health program evaluation")'
compact_exercise = '(exercis* OR "physical activit*" OR sport* OR aerobic* OR walk* OR running OR jogging OR swim* OR cycling OR bicycl* OR yoga OR "tai chi" OR "tai-chi" OR "tai ji" OR qigong OR "qi gong" OR "resistance train*" OR "strength train*" OR "weight lift*")'
strategies = {'A_fuller_source_concepts': f'{population} AND {exercise} AND {trial}',
              'B_compact_three_concepts': f'(depress* OR dysthymi*) AND {compact_exercise} AND (random* OR trial* OR placebo* OR control*)'}
for name, text in strategies.items():
    (ROOT / 'queries' / (name + '.oql')).write_text('get works where date <= (2023-06-03) and title-abstract-keywords has (' + text + ')\n')
