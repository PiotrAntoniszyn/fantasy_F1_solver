import pandas as pd
import sasoptpy as so
from IPython import get_ipython
import streamlit as st
import os

st.write("""
# Fantasy F1 Solver

Upload CSV file...
""")

model = so.Model(name="single_race")

f1_data = pd.read_csv(r"C:\Users\ppark\Desktop\F1_data.csv",index_col=0)
picks = f1_data.index.to_list()


squad = model.add_variables(picks,name='squad',vartype=so.binary)
drs_boost = model.add_variables(picks,name='drs_boost',vartype=so.binary)


driver_count = so.expr_sum(squad[p] for p in picks[0:20])
team_count = so.expr_sum(squad[p] for p in picks[20:])



model.add_constraint(driver_count==5, name='driver_count')
model.add_constraint(team_count==2, name='team_count')
model.add_constraint(so.expr_sum(drs_boost[p] for p in picks[0:20])==1, name='drs_boost_count_driver')
model.add_constraint(so.expr_sum(drs_boost[p] for p in picks[20:])==0, name='drs_boost_count_constructor')


budget = 100.0
price = so.expr_sum(f1_data.loc[p,'Price']*squad[p] for p in picks)


model.add_constraint(price <=budget, name='budget_limit')


total_points = so.expr_sum(f1_data.loc[p,'xP_f1'] * (squad[p] + drs_boost[p]) for p in picks)


model.set_objective(-total_points,sense='N', name='total_xp')
model.export_mps('single_race.mps')

command = 'cbc single_race.mps solve solu solution.txt >/dev/null 2>&1'
os.system('{command}')


for v in model.get_variables():
    v.set_value(0)


with open(r"C:\Users\ppark\Desktop\solution.txt", 'r') as f:
    for line in f:
        if 'objective value' in line:
            continue
        words = line.split()
        var = model.get_variable(words[1])
        var.set_value(float(words[2]))



race_picks = []
for p in picks:
    if squad[p].get_value()>0.5:
        lp = f1_data.loc[p]
        print(lp['Name'])
        is_drs_boost = 1 if drs_boost[p].get_value() > 0.5 else 0
        race_picks.append([
            lp['Name'],lp['type'],lp['Price'],round(lp['xP_f1'],2),is_drs_boost
        ])
race_picks_df =pd.DataFrame(race_picks, columns = ['name','type','price','xP','drs_boost'])


race_picks_df



total_xp = round(so.expr_sum((squad[p]+drs_boost[p])*f1_data.loc[p,'xP_f1'] for p in picks).get_value(),3)



total_price = price.get_value()


total_price
total_xp




