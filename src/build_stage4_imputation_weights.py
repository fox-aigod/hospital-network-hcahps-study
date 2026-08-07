"""Deterministic MICE and inverse-probability-of-observation weights."""
from __future__ import annotations
import csv, hashlib, json, warnings
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
import numpy as np
from joblib import Parallel, delayed
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import BayesianRidge, LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from .common import write_json

OWN={"Government":0,"Nonprofit":1,"For-profit":2}
TARGETS=[("health_system_affiliated","binary"),("log2_beds_plus1","continuous"),("ownership_code","categorical"),("teaching_intensity","continuous"),("high_dsh_flag","binary"),("uncompensated_care_burden","continuous"),("high_uncompensated_care_flag","binary")]
TARGET_SPECS=TARGETS
BAL=["CAH","profile_0","profile_1","profile_2","profile_4","profile_5","log2_beds_plus1","ownership_nonprofit","ownership_forprofit","health_system_affiliated","teaching_intensity","high_dsh_flag","uncompensated_care_burden","high_uncompensated_care_flag","nonmetro","year2025"]

def rows(path):
    with path.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def csvwrite(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
def num(x):
    try:return float(x)
    except:return np.nan
def integer(x):
    try:return int(float(x))
    except:return 0
def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()

class Ctx:
    def __init__(self,r):
        self.r=r;self.n=len(r);self.idx=np.arange(self.n)
        self.states=np.array([x["state"] for x in r],object);self.state_levels=sorted(set(self.states))
        self.profile=np.array([integer(x["profile_category_code"]) for x in r]);self.cah=np.array([x["hospital_group"]=="Critical Access" for x in r],int)
        self.year=np.array([x["onc_survey_year"]=="2025" for x in r],int);self.nonmetro=np.array([x["rurality_binary"]=="Nonmetro" for x in r],int);self.rucc=np.array([integer(x["rucc_2023"]) for x in r])
        self.y=np.array([num(x["discharge_information_yes_pct"]) for x in r]);self.obs=(~np.isnan(self.y)).astype(int)
        self.surveys=np.array([num(x["number_completed_surveys"]) for x in r]);self.rate=np.array([num(x["survey_response_rate_pct"]) for x in r])
        self.net={k:np.array([integer(x[k]) for x in r]) for k in ["hio","national_network","vendor_network","current_tefca"]}
        self.fixed=self._fixed();self.orig=self._orig()
    def _fixed(self):
        c=[self.cah,self.year]+[self.profile==i for i in range(6)]+[self.states==s for s in self.state_levels]+[self.rucc==i for i in range(1,10)]+[self.obs]
        y=self.y.copy();y[np.isnan(y)]=np.nanmean(y);c += [y,np.isnan(self.y)]
        for a,tr in [(self.surveys,np.log1p),(self.rate,lambda z:z)]:
            z=a.copy();m=np.isnan(z);z[m]=np.nanmedian(z);c += [tr(z),m]
        for level in ["Government","Nonprofit","For-profit","Unknown"]:c.append(np.array([(x["cms_ownership_3cat"] or "Unknown")==level for x in self.r]))
        c.append(np.array([str(x["emergency_services"]).strip().upper()=="YES" for x in self.r]));c.extend(self.net.values())
        return np.column_stack([np.asarray(x,float) for x in c])
    def _orig(self):
        d={}
        for name,_ in TARGETS:
            d[name]=np.array([OWN.get(x["ahrq_ownership_3cat"],np.nan) for x in self.r],float) if name=="ownership_code" else np.array([num(x[name]) for x in self.r])
        return d
    def initial(self):
        d={}
        for name,kind in TARGETS:
            a=self.orig[name].copy();m=np.isnan(a)
            for g in [0,1]:
                o=(self.cah==g)&~m;v=np.nanmedian(a[o]) if kind=="continuous" else Counter(a[o].astype(int)).most_common(1)[0][0];a[(self.cah==g)&m]=v
            d[name]=a
        return d
    def impX(self,d,target):
        b=[self.fixed]
        for name,kind in TARGETS:
            if name==target:continue
            a=d[name]
            b.extend([(a==i).astype(float)[:,None] for i in [0,1,2]] if kind=="categorical" else [a[:,None]])
        return np.hstack(b)
    def weightX(self,d):
        b=[np.ones(self.n)];pcols={}
        for i in [0,1,2,4,5]:pcols[i]=(self.profile==i).astype(float);b.append(pcols[i])
        b.append(self.cah.astype(float));b.extend([pcols[i]*self.cah for i in [0,1,2,4,5]]);b.append(d["log2_beds_plus1"])
        own=d["ownership_code"];b.extend([(own==i).astype(float) for i in [1,2]])
        b += [d["health_system_affiliated"],d["teaching_intensity"],d["high_dsh_flag"],d["uncompensated_care_burden"],d["high_uncompensated_care_flag"],self.nonmetro.astype(float),self.year.astype(float)]
        b.extend([(self.states==s).astype(float) for s in self.state_levels[1:]])
        bed=d["log2_beds_plus1"];bed2=bed**2;c=self.cah.astype(float);y=self.year.astype(float);b += [bed2,bed*c,bed2*c,bed*y,bed2*y]
        return np.column_stack(b)

def pmm(a,o,X,rng,k):
    m=make_pipeline(StandardScaler(),BayesianRidge())
    with warnings.catch_warnings(record=True) as ws:warnings.simplefilter("always");m.fit(X[o],a[o])
    po=m.predict(X[o]);pm=m.predict(X[~o]);ov=a[o];out=a.copy();kk=min(k,len(po))
    for j,p in zip(np.where(~o)[0],pm):near=np.argpartition(abs(po-p),kk-1)[:kk];out[j]=ov[rng.choice(near)]
    return out,{"iterations":int(m[-1].n_iter_),"warnings":len(ws)}
def logdraw(a,o,X,rng,categorical):
    y=a[o].astype(int);out=a.copy()
    if not categorical and len(np.unique(y))<2:return out,{"iterations":0,"warnings":0}
    m=make_pipeline(StandardScaler(),LogisticRegression(max_iter=2000,C=1,solver="lbfgs"))
    with warnings.catch_warnings(record=True) as ws:warnings.simplefilter("always",ConvergenceWarning);m.fit(X[o],y)
    pr=m.predict_proba(X[~o]);classes=m[-1].classes_.astype(int)
    out[~o]=[rng.choice(classes,p=p/p.sum()) for p in pr] if categorical else rng.binomial(1,pr[:,1])
    return out,{"iterations":int(np.max(m[-1].n_iter_)),"warnings":sum(issubclass(w.category,ConvergenceWarning) for w in ws)}
def impute(ctx,seed,cycles,k):
    rng=np.random.default_rng(seed);d=ctx.initial();trace=[];fits=[]
    for cycle in range(1,cycles+1):
        for name,kind in TARGETS:
            X=ctx.impX(d,name);o=~np.isnan(ctx.orig[name]);a=d[name].copy();a[o]=ctx.orig[name][o]
            upd,fit=pmm(a,o,X,rng,k) if kind=="continuous" else logdraw(a,o,X,rng,kind=="categorical")
            upd[o]=ctx.orig[name][o];d[name]=upd;v=upd[~o]
            trace.append({"cycle":cycle,"target":name,"imputed_mean":float(v.mean()),"imputed_min":float(v.min()),"imputed_max":float(v.max())});fits.append({"cycle":cycle,"target":name,"model_type":kind,**fit})
    return d,trace,fits

def probability(y,X,max_iter):
    m=make_pipeline(StandardScaler(),LogisticRegression(max_iter=max_iter,C=100,solver="lbfgs",tol=1e-6))
    with warnings.catch_warnings(record=True) as ws:warnings.simplefilter("always",ConvergenceWarning);m.fit(X,y)
    return np.clip(m.predict_proba(X)[:,1],1e-6,1-1e-6),{"iterations":int(np.max(m[-1].n_iter_)),"convergence_warnings":sum(issubclass(w.category,ConvergenceWarning) for w in ws)}
def weights(ctx,d,max_iter):
    pden,dfit=probability(ctx.obs,ctx.weightX(d),max_iter);Xn=np.column_stack([np.ones(ctx.n),ctx.cah,ctx.year]);pnum,nfit=probability(ctx.obs,Xn,max_iter)
    oi=np.where(ctx.obs==1)[0];raw=pnum[oi]/pden[oi];lo,hi=np.quantile(raw,[.01,.99]);w=np.clip(raw,lo,hi);w/=w.mean()
    return {"observed_idx":oi,"weights":w,"raw_weights":raw,"pden":pden,"pnum":pnum,"lower_trim":float(lo),"upper_trim":float(hi),"ess":float(w.sum()**2/np.sum(w**2)),"method":"NearUnpenalizedLogistic","denominator_fit":dfit,"numerator_fit":nfit}
def invariants(ctx,imps):
    change=donor=ib=ic=0
    for d in imps:
        for name,kind in TARGETS:
            o=~np.isnan(ctx.orig[name]);change+=int(np.sum(d[name][o]!=ctx.orig[name][o]));v=d[name][~o]
            if kind=="continuous":donor+=sum(x not in set(ctx.orig[name][o]) for x in v)
            elif kind=="binary":ib+=int(np.sum(~np.isin(v,[0,1])))
            else:ic+=int(np.sum(~np.isin(v,[0,1,2])))
    return {"observed_values_changed":change,"continuous_imputations_not_observed_donors":donor,"invalid_binary_imputations":ib,"invalid_categorical_imputations":ic,"passed":not any([change,donor,ib,ic])}
def balance(ctx,imps,runs):
    rec=defaultdict(lambda:{"before":[],"after":[]});sr=defaultdict(lambda:{"before":[],"after":[]})
    for d,run in zip(imps,runs):
        oi=run["observed_idx"];own=d["ownership_code"];a={"CAH":ctx.cah.astype(float),"profile_0":(ctx.profile==0).astype(float),"profile_1":(ctx.profile==1).astype(float),"profile_2":(ctx.profile==2).astype(float),"profile_4":(ctx.profile==4).astype(float),"profile_5":(ctx.profile==5).astype(float),"log2_beds_plus1":d["log2_beds_plus1"],"ownership_nonprofit":(own==1).astype(float),"ownership_forprofit":(own==2).astype(float),"health_system_affiliated":d["health_system_affiliated"],"teaching_intensity":d["teaching_intensity"],"high_dsh_flag":d["high_dsh_flag"],"uncompensated_care_burden":d["uncompensated_care_burden"],"high_uncompensated_care_flag":d["high_uncompensated_care_flag"],"nonmetro":ctx.nonmetro.astype(float),"year2025":ctx.year.astype(float)}
        for name,x in a.items():
            sd=np.std(x,ddof=1);before=(np.mean(x[oi])-np.mean(x))/sd if sd>=1e-12 else 0;after=(np.average(x[oi],weights=run["weights"])-np.mean(x))/sd if sd>=1e-12 else 0;rec[name]["before"].append(float(before));rec[name]["after"].append(float(after))
            for g in [0,1]:
                for y in [0,1]:
                    si=ctx.idx[(ctx.cah==g)&(ctx.year==y)];om=(ctx.cah[oi]==g)&(ctx.year[oi]==y);oo=oi[om]
                    if len(si)<2 or len(oo)<2:continue
                    sd=np.std(x[si],ddof=1);b=(np.mean(x[oo])-np.mean(x[si]))/sd if sd>=1e-12 else 0;af=(np.average(x[oo],weights=run["weights"][om])-np.mean(x[si]))/sd if sd>=1e-12 else 0;sr[(name,g,y)]["before"].append(float(b));sr[(name,g,y)]["after"].append(float(af))
    out=[]
    for name in BAL:
        b=np.array(rec[name]["before"]);a=np.array(rec[name]["after"]);out.append({"variable":name,"mean_smd_before":float(b.mean()),"mean_abs_smd_before":float(abs(b).mean()),"max_abs_smd_before":float(abs(b).max()),"mean_smd_after":float(a.mean()),"mean_abs_smd_after":float(abs(a).mean()),"max_abs_smd_after":float(abs(a).max())})
    strata=[]
    for (name,g,y),v in sorted(sr.items()):
        b=np.array(v["before"]);a=np.array(v["after"]);strata.append({"variable":name,"hospital_group":"Critical Access" if g else "Acute Care","onc_survey_year":2025 if y else 2024,"mean_smd_before":float(b.mean()),"mean_abs_smd_before":float(abs(b).mean()),"max_abs_smd_before":float(abs(b).max()),"mean_smd_after":float(a.mean()),"mean_abs_smd_after":float(abs(a).mean()),"max_abs_smd_after":float(abs(a).max())})
    return out,strata
def imp_rows(ctx,imps):
    out=[]
    for i,d in enumerate(imps,1):
        r={"imputation":i}
        for name,_ in TARGETS:
            v=d[name][np.isnan(ctx.orig[name])];r[f"{name}_imputed_mean"]=float(v.mean());r[f"{name}_imputed_min"]=float(v.min());r[f"{name}_imputed_max"]=float(v.max())
        out.append(r)
    return out
def weight_rows(runs):
    out=[]
    for i,r in enumerate(runs,1):
        raw=r["raw_weights"];w=r["weights"];p=r["pden"];out.append({"imputation":i,"observed_n":len(w),"raw_min":float(raw.min()),"raw_p01":float(np.quantile(raw,.01)),"raw_median":float(np.median(raw)),"raw_p99":float(np.quantile(raw,.99)),"raw_max":float(raw.max()),"trim_lower":r["lower_trim"],"trim_upper":r["upper_trim"],"trimmed_min":float(w.min()),"trimmed_max":float(w.max()),"effective_sample_size":r["ess"],"denominator_probability_min":float(p.min()),"denominator_probability_p01":float(np.quantile(p,.01)),"denominator_probability_median":float(np.median(p)),"denominator_probability_max":float(p.max()),"fit_method":r["method"]})
    return out
def run_summary(runs,strata):
    return {"observed_n_each_imputation":sorted({len(r["weights"]) for r in runs}),"mean_weight_min":min(float(r["weights"].mean()) for r in runs),"mean_weight_max":max(float(r["weights"].mean()) for r in runs),"mean_effective_sample_size":float(np.mean([r["ess"] for r in runs])),"minimum_effective_sample_size":float(np.min([r["ess"] for r in runs])),"mean_upper_trim":float(np.mean([r["upper_trim"] for r in runs])),"maximum_raw_weight":float(max(r["raw_weights"].max() for r in runs)),"minimum_denominator_probability":float(min(r["pden"].min() for r in runs)),"denominator_convergence_warnings":sum(r["denominator_fit"]["convergence_warnings"] for r in runs),"numerator_convergence_warnings":sum(r["numerator_fit"]["convergence_warnings"] for r in runs),"denominator_iterations_min":min(r["denominator_fit"]["iterations"] for r in runs),"denominator_iterations_max":max(r["denominator_fit"]["iterations"] for r in runs),"maximum_absolute_smd_before":max(x["max_abs_smd_before"] for x in strata),"maximum_absolute_smd_after":max(x["max_abs_smd_after"] for x in strata),"largest_residual_row":max(strata,key=lambda x:x["max_abs_smd_after"])}

def build_stage4_imputation_weights(root:Path)->dict[str,Any]:
    spec=json.loads((root/"config/stage4_analysis_spec.json").read_text());settings=spec["imputation"];ctx=Ctx(rows(root/"data/processed/Hospital_Network_Analysis_Ready_v1.csv"));seeds=[settings["base_seed"]+settings["seed_increment"]*i for i in range(settings["imputations"])]
    gen=Parallel(n_jobs=settings["parallel_jobs"])(delayed(impute)(ctx,s,settings["cycles"],settings["pmm_donors"]) for s in seeds);imps=[x[0] for x in gen];traces=[x[1] for x in gen];fits=[x[2] for x in gen];inv=invariants(ctx,imps)
    if not inv["passed"]:raise RuntimeError(inv)
    legacy=[weights(ctx,d,spec["observation_weighting"]["legacy_max_iter"]) for d in imps];canon=[weights(ctx,d,spec["observation_weighting"]["canonical_max_iter"]) for d in imps];lb,ls=balance(ctx,imps,legacy);cb,cs=balance(ctx,imps,canon)
    diag=root/"outputs/diagnostics";log=root/"outputs/logs";inter=root/"data/interim";diag.mkdir(parents=True,exist_ok=True);log.mkdir(parents=True,exist_ok=True);inter.mkdir(parents=True,exist_ok=True)
    csvwrite(diag/"imputation_diagnostics.csv",imp_rows(ctx,imps));csvwrite(diag/"legacy_weight_diagnostics.csv",weight_rows(legacy));csvwrite(diag/"legacy_balance_diagnostics.csv",lb);csvwrite(diag/"legacy_balance_diagnostics_by_stratum.csv",ls);csvwrite(diag/"weight_diagnostics.csv",weight_rows(canon));csvwrite(diag/"balance_diagnostics.csv",cb);csvwrite(diag/"balance_diagnostics_by_stratum.csv",cs)
    csvwrite(diag/"imputation_trace.csv",[{"imputation":i,"seed":s,**z} for i,(s,t) in enumerate(zip(seeds,traces),1) for z in t]);fitrows=[{"imputation":i,"seed":s,**z} for i,(s,t) in enumerate(zip(seeds,fits),1) for z in t];csvwrite(diag/"imputation_model_fit_diagnostics.csv",fitrows)
    if sum(x["warnings"] for x in fitrows):raise RuntimeError("imputation model warning")
    comp=[]
    for i,(a,b) in enumerate(zip(legacy,canon),1):comp.append({"imputation":i,"legacy_denominator_iterations":a["denominator_fit"]["iterations"],"legacy_denominator_convergence_warnings":a["denominator_fit"]["convergence_warnings"],"canonical_denominator_iterations":b["denominator_fit"]["iterations"],"canonical_denominator_convergence_warnings":b["denominator_fit"]["convergence_warnings"],"max_abs_denominator_probability_difference":float(abs(b["pden"]-a["pden"]).max()),"mean_abs_denominator_probability_difference":float(abs(b["pden"]-a["pden"]).mean()),"max_abs_normalized_weight_difference":float(abs(b["weights"]-a["weights"]).max()),"mean_abs_normalized_weight_difference":float(abs(b["weights"]-a["weights"]).mean()),"legacy_effective_sample_size":a["ess"],"canonical_effective_sample_size":b["ess"]})
    csvwrite(diag/"weight_convergence_comparison.csv",comp)
    payload={name:np.stack([d[name] for d in imps]) for name,_ in TARGETS};payload.update(seeds=np.array(seeds,np.int64),ccn=np.array([x["ccn"] for x in ctx.r]));np.savez_compressed(inter/"stage4_imputations.npz",**payload)
    for name,runs in [("stage4_legacy_observation_weights.npz",legacy),("stage4_observation_weights.npz",canon)]:np.savez_compressed(inter/name,weights=np.stack([x["weights"] for x in runs]),raw_weights=np.stack([x["raw_weights"] for x in runs]),denominator_probabilities=np.stack([x["pden"] for x in runs]),numerator_probabilities=np.stack([x["pnum"] for x in runs]),observed_idx=runs[0]["observed_idx"],ccn=np.array([ctx.r[j]["ccn"] for j in runs[0]["observed_idx"]]),seeds=np.array(seeds,np.int64))
    paths={"imputation_diagnostics.csv":diag/"imputation_diagnostics.csv","weight_diagnostics.csv":diag/"legacy_weight_diagnostics.csv","balance_diagnostics.csv":diag/"legacy_balance_diagnostics.csv","balance_diagnostics_by_stratum.csv":diag/"legacy_balance_diagnostics_by_stratum.csv"};hashes={k:sha(v) for k,v in paths.items()};matches={k:hashes[k]==spec["expected_archived_output_sha256"][k] for k in paths}
    if not all(matches.values()):raise RuntimeError(matches)
    lsum=run_summary(legacy,ls);csum=run_summary(canon,cs)
    if csum["denominator_convergence_warnings"]:raise RuntimeError(csum)
    summary={"status":"stage4_reproduced_and_convergence_corrected","settings":{"source_n":ctx.n,"primary_outcome_observed_n":int(ctx.obs.sum()),"imputations":settings["imputations"],"cycles":settings["cycles"],"base_seed":settings["base_seed"],"seed_increment":settings["seed_increment"],"pmm_donors":settings["pmm_donors"],"legacy_observation_model_max_iter":spec["observation_weighting"]["legacy_max_iter"],"canonical_observation_model_max_iter":spec["observation_weighting"]["canonical_max_iter"]},"missing_counts":{n:int(np.isnan(ctx.orig[n]).sum()) for n,_ in TARGETS},"imputation_invariants":inv,"imputation_model_fits":{"total_model_fits":len(fitrows),"warnings":0,"maximum_iterations":max(x["iterations"] for x in fitrows),"maximum_iterations_by_target":{n:max(x["iterations"] for x in fitrows if x["target"]==n) for n,_ in TARGETS}},"legacy_archived_reproduction":{"diagnostic_hashes":hashes,"diagnostic_hash_match":matches,"all_diagnostic_hashes_match":True,"weighting":lsum},"canonical_converged_weighting":csum,"legacy_to_canonical_comparison":{"maximum_absolute_denominator_probability_difference":max(x["max_abs_denominator_probability_difference"] for x in comp),"maximum_mean_absolute_denominator_probability_difference":max(x["mean_abs_denominator_probability_difference"] for x in comp),"maximum_absolute_normalized_weight_difference":max(x["max_abs_normalized_weight_difference"] for x in comp),"maximum_mean_absolute_normalized_weight_difference":max(x["mean_abs_normalized_weight_difference"] for x in comp)},"stage5_input_files":{"imputations":"data/interim/stage4_imputations.npz","canonical_weights":"data/interim/stage4_observation_weights.npz","legacy_weights":"data/interim/stage4_legacy_observation_weights.npz"}}
    write_json(log/"stage4_summary.json",summary);return summary
