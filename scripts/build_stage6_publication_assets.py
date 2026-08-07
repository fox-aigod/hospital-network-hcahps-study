from pathlib import Path
import json, math
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
CAN=ROOT/'outputs/stage5/canonical'
OUT=ROOT/'outputs/stage6/tables'
OUT.mkdir(parents=True, exist_ok=True)
DATA=ROOT/'data/processed/Hospital_Network_Analysis_Ready_v1.csv'
if not DATA.exists():
    raise FileNotFoundError(f'Required Stage 6 input is missing: {DATA.relative_to(ROOT)}')
df=pd.read_csv(DATA, dtype={'ccn':str,'profile_bits':str})

# ---------- formatting helpers ----------
def fmt_p(p, digits=3):
    if pd.isna(p): return '—'
    if p < .001: return '<.001'
    return f'{p:.{digits}f}'.lstrip('0')

def fmt2(x): return f'{x:.2f}'
def fmt3(x): return f'{x:.3f}'
def zero_clean(x, digits=2):
    v=round(float(x),digits)
    if v == 0: v=0.0
    return f'{v:.{digits}f}'

def n_pct(n, denom): return f'{int(n)} ({100*n/denom:.1f}%)'

# ---------- Main Table 1 ----------
groups=[('All hospitals',df),('Acute Care',df[df.hospital_group=='Acute Care']),('Critical Access',df[df.hospital_group=='Critical Access'])]
def yes_stat(sub, col, predicate=lambda s:s==1):
    s=sub[col].dropna(); n=int(predicate(s).sum()); return n_pct(n,len(s))
def teach_stat(sub):
    x=sub[['major_teaching_flag','very_major_teaching_flag']].dropna()
    n=int(((x.major_teaching_flag==1)|(x.very_major_teaching_flag==1)).sum())
    return n_pct(n,len(x))
def ownership_stat(sub, val):
    s=sub.ahrq_ownership_3cat.dropna(); n=int((s==val).sum()); return n_pct(n,len(s))
def beds_stat(sub):
    s=sub.beds.dropna().to_numpy(); q=np.quantile(s,[.25,.5,.75]);
    return f'{q[1]:.0f} ({q[0]:.0f}–{q[2]:.0f})'
def outcome_stat(sub):
    s=sub.discharge_information_yes_pct.dropna(); return f'{s.mean():.2f} ({s.std(ddof=1):.2f})'
rows=[]
characteristics=[
    ('ONC survey year 2025', lambda s: yes_stat(s,'onc_survey_year',lambda x:x==2025)),
    ('Nonmetropolitan county', lambda s: yes_stat(s,'rurality_binary',lambda x:x=='Nonmetro')),
    ('Health-system affiliated', lambda s: yes_stat(s,'health_system_affiliated')),
    ('Current TEFCA participation', lambda s: yes_stat(s,'current_tefca')),
    ('Major or very major teaching hospital', teach_stat),
    ('High DSH patient percentage', lambda s: yes_stat(s,'high_dsh_flag')),
    ('High uncompensated-care burden', lambda s: yes_stat(s,'high_uncompensated_care_flag')),
    ('Primary HCAHPS outcome publicly reported', lambda s: yes_stat(s,'primary_outcome_available')),
    ('Ownership: Government', lambda s: ownership_stat(s,'Government')),
    ('Ownership: Nonprofit', lambda s: ownership_stat(s,'Nonprofit')),
    ('Ownership: For-profit', lambda s: ownership_stat(s,'For-profit')),
    ('Beds, median (IQR)', beds_stat),
    ('Observed discharge-information score, mean (SD)', outcome_stat),
]
for label,fn in characteristics:
    row={'Characteristic':label}
    for glabel,sub in groups: row[glabel]=fn(sub)
    rows.append(row)
t1=pd.DataFrame(rows)
t1.to_csv(OUT/'manuscript_table_1.csv',index=False)

# ---------- Main Table 2 ----------
means=pd.read_csv(CAN/'adjusted_profile_means.csv').sort_values('profile_category')
counts=df.groupby('profile_category_code').agg(source_n=('ccn','size'),outcome_n=('primary_outcome_available','sum')).reset_index()
coef=pd.read_csv(CAN/'primary_model_coefficients.csv').set_index('term')
profiles={0:'No coded participation',1:'Single conventional network, no TEFCA',2:'Two conventional networks, no TEFCA',3:'Three conventional networks, no TEFCA',4:'TEFCA plus zero to two conventional networks',5:'TEFCA plus all three conventional networks'}
r=[]
for code in range(6):
    m=means.loc[means.profile_category==code].iloc[0]; c=counts.loc[counts.profile_category_code==code].iloc[0]
    diff='Reference' if code==3 else ('+' if coef.loc[f'profile_{code}','estimate']>0 else '')+zero_clean(coef.loc[f'profile_{code}','estimate'],2)
    r.append({'Code':code,'Network profile':profiles[code],'Source N':int(c.source_n),'Outcome N':int(c.outcome_n),
              'Adjusted mean, % (95% CI)':f"{m.estimate:.2f} ({m.ci_low:.2f} to {m.ci_high:.2f})",'Difference from code 3, pp':diff})
t2=pd.DataFrame(r); t2.to_csv(OUT/'manuscript_table_2.csv',index=False)

# ---------- Main Table 3 ----------
sens=pd.read_csv(CAN/'sensitivity_analyses.csv')
t3=pd.DataFrame({
    'Analysis':sens.analysis,
    'Global χ² (df)':[f'{x:.2f} ({int(d)})' for x,d in zip(sens.global_statistic,sens.global_df)],
    'Global P':[fmt_p(x,3) for x in sens.global_p],
    'Profile 5–3 difference, pp (95% CI)':[f'{e:.2f} ({lo:.2f} to {hi:.2f})' for e,lo,hi in zip(sens.contrast_estimate,sens.contrast_ci_low,sens.contrast_ci_high)],
    'Contrast P':[f'{p:.3f}' for p in sens.contrast_p],
})
t3.to_csv(OUT/'manuscript_table_3.csv',index=False)

# ---------- Supplement S1-S6 ----------
exact=pd.read_csv(CAN/'exact_profile_descriptives.csv', dtype={'profile_bits':str})
s1=exact.copy();
s1['Outcome available, %']=s1.outcome_available_pct.map(lambda x:'—' if pd.isna(x) else f'{x:.1f}')
s1['Unadjusted mean']=s1.unadjusted_mean.map(lambda x:'—' if pd.isna(x) else f'{x:.2f}')
s1['SD']=s1.unadjusted_sd.map(lambda x:'—' if pd.isna(x) else f'{x:.2f}')
s1=s1.rename(columns={'profile_bits':'Bits','hospital_group':'Hospital group','source_n':'Source N','outcome_n':'Outcome N'})[['Bits','Hospital group','Source N','Outcome N','Outcome available, %','Unadjusted mean','SD']]
s1.to_csv(OUT/'supplement_table_S1.csv',index=False)

inter=pd.read_csv(CAN/'interaction_adjusted_means.csv')
s2=[]
for _,x in inter.iterrows():
    s2.append({'Hospital group':x.hospital_group,'Code':int(x.profile_category),'Profile':profiles[int(x.profile_category)],'Adjusted mean, %':f'{x.estimate:.2f}','95% CI':f'{x.ci_low:.2f} to {x.ci_high:.2f}'})
pd.DataFrame(s2).to_csv(OUT/'supplement_table_S2.csv',index=False)

sec=pd.read_csv(CAN/'secondary_outcomes.csv')
s3=pd.DataFrame({
    'Outcome':sec.outcome,'Global χ²':[f'{x:.2f}' for x in sec.global_statistic],
    'Global P':[fmt_p(x,4) for x in sec.global_p], 'BH-FDR q':[fmt_p(x,4) for x in sec.global_bh_fdr],
    'Profile 5–3, pp':[f'{x:.2f}' for x in sec.contrast_estimate],
    '95% CI':[f'{lo:.2f} to {hi:.2f}' for lo,hi in zip(sec.contrast_ci_low,sec.contrast_ci_high)],
    'Contrast P':[f'{x:.3f}' for x in sec.contrast_p]})
s3.to_csv(OUT/'supplement_table_S3.csv',index=False)

summary=json.loads((CAN/'analysis_summary.json').read_text())
w=summary['weight_summary']
s4=pd.DataFrame([
    ('Observed primary-outcome hospitals','2409'),
    ('Mean effective sample size',f"{w['mean_ess']:.1f}"),
    ('Minimum effective sample size across imputations',f"{w['min_ess']:.1f}"),
    ('Minimum denominator probability',f"{w['min_denominator_probability']:.4f}"),
    ('Maximum raw weight',f"{w['max_raw_weight']:.2f}"),
    ('Mean 99th-percentile trimming threshold',f"{w['mean_trim_upper']:.2f}"),
    ('Maximum within-stratum |SMD| before weighting',f"{w['max_abs_smd_before']:.3f}"),
    ('Maximum within-stratum |SMD| after weighting',f"{w['max_abs_smd_after']:.3f}"),
],columns=['Diagnostic','Result'])
s4.to_csv(OUT/'supplement_table_S4.csv',index=False)

def coefficient_table(path, terms):
    x=pd.read_csv(path).set_index('term')
    out=[]
    for term in terms:
        z=x.loc[term]
        out.append({'Term':term,'Estimate':zero_clean(z.estimate,3),'SE':f'{z.se:.3f}','95% CI':f'{z.ci_low:.3f} to {z.ci_high:.3f}','P':fmt_p(z.p_value,3)})
    return pd.DataFrame(out)
primary_terms=['Intercept','profile_0','profile_1','profile_2','profile_4','profile_5','CAH','log2_beds_plus1','ownership_1','ownership_2','health_system_affiliated','teaching_intensity','high_dsh_flag','uncompensated_care_burden','high_uncompensated_care_flag','nonmetro','year2025']
alt_terms=['Intercept','conventional_count','current_tefca','count_x_tefca','CAH','log2_beds_plus1','ownership_1','ownership_2','health_system_affiliated','teaching_intensity','high_dsh_flag','uncompensated_care_burden','high_uncompensated_care_flag','nonmetro','year2025']
coefficient_table(CAN/'primary_model_coefficients.csv',primary_terms).to_csv(OUT/'supplement_table_S5.csv',index=False)
coefficient_table(CAN/'alternative_exposure_coefficients.csv',alt_terms).to_csv(OUT/'supplement_table_S6.csv',index=False)

# ---------- Manuscript value audit ----------
audit=[]
def add(location,item,display,canonical,tol=0):
    if isinstance(canonical,(int,np.integer)):
        passed=(int(display)==int(canonical)) if isinstance(display,(int,np.integer,float)) else str(display)==str(canonical)
    else:
        passed=abs(float(display)-float(canonical))<=tol
    audit.append({'location':location,'item':item,'displayed_or_target_value':display,'canonical_value':canonical,'tolerance':tol,'status':'PASS' if passed else 'FAIL'})
add('Abstract/Results','Source cohort N',2651,2651)
add('Abstract/Results','Primary outcome N',2409,2409)
add('Abstract/Results','Acute outcome N',1852,1852)
add('Abstract/Results','CAH outcome N',557,557)
add('Abstract/Results','Global Wald chi-square',29.01,summary['primary_global']['statistic'],0.005)
add('Abstract/Results','Planned contrast estimate',0.28,summary['primary_planned_contrast']['estimate'],0.005)
add('Abstract/Results','Planned contrast lower CI',-0.15,summary['primary_planned_contrast']['ci_low'],0.005)
add('Abstract/Results','Planned contrast upper CI',0.70,summary['primary_planned_contrast']['ci_high'],0.005)
add('Abstract/Results','Planned contrast P',0.206,summary['primary_planned_contrast']['p_value'],0.0005)
add('Abstract/Results','Interaction Wald chi-square',7.19,summary['interaction_global']['statistic'],0.005)
add('Abstract/Results','Interaction P',0.207,summary['interaction_global']['p_value'],0.0005)
for _,x in means.iterrows():
    add('Table 2',f'Profile {int(x.profile_category)} adjusted mean',round(x.estimate,2),x.estimate,0.005)
for _,x in sens.iterrows():
    add('Table 3',f"{x.analysis}: global chi-square",round(x.global_statistic,2),x.global_statistic,0.005)
    add('Table 3',f"{x.analysis}: contrast",round(x.contrast_estimate,2),x.contrast_estimate,0.005)
    add('Table 3',f"{x.analysis}: contrast P",round(x.contrast_p,3),x.contrast_p,0.0005)
pd.DataFrame(audit).to_csv(OUT/'manuscript_value_audit.csv',index=False)

manifest={p.name:{'rows':int(pd.read_csv(p).shape[0]),'columns':int(pd.read_csv(p).shape[1])} for p in sorted(OUT.glob('*.csv'))}
(OUT/'stage6_table_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'tables':len(manifest),'audit_failures':sum(x['status']=='FAIL' for x in audit)},indent=2))
