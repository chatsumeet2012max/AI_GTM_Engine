import pandas as pd
from pathlib import Path
DATA=Path(__file__).parent/'data'
def load(name): return pd.read_csv(DATA/f'{name}.csv')
CONFIG={
'AI Advertising':(['Retail','Automotive','CPG','Entertainment','Advertising agency'],['CMO','VP Marketing','Creative Director'],['Product launch','Rebranding','Marketing hire','New campaign','Agency appointment']),
'Retail':(['Retail','Wholesale'],['COO','Inventory Manager'],['New store','Supply disruption']),
'Engineering':(['Manufacturing','Industrial automation'],['Plant Manager','Engineering Director'],['Factory expansion','Equipment upgrade']),
'Healthcare':(['Hospitals','Medical distributors'],['Procurement Director','Orthopedic Director'],['Facility expansion','Tender']),
'Pharma':(['Biotechnology','Pharmaceuticals'],['Research Director','Clinical Operations'],['Trial launch','Funding']),
'Food & Beverage':(['Food manufacturing','Distribution'],['Supply Chain Director','COO'],['Distribution expansion','Product launch']),
'Agrosciences':(['Agriculture','Agtech'],['Farm Manager','Operations Director'],['Seasonal demand','Equipment upgrade']),
'Finance':(['Asset management','Financial services'],['CIO','Research Director'],['New fund','Technology upgrade']),
'Education':(['Schools','NGOs'],['Principal','Program Director'],['New program','Grant award'])}
def discover(industries,lo,hi,triggers,weight):
 c=load('companies'); s=load('signals'); s=s[s.type.isin(triggers)]
 c['fit_score']=60*c.industry.isin(industries).astype(int)+40*c.employees.between(lo,hi).astype(int)
 c['intent_score']=c.company_id.map(s.groupby('company_id').relevance.max()).fillna(0)
 c['score']=(weight*c.fit_score+(1-weight)*c.intent_score).round().astype(int)
 c['tier']=pd.cut(c.score,[-1,59,79,100],labels=['C','B','A'])
 return c[c.industry.isin(industries)&c.employees.between(lo,hi)].sort_values('score',ascending=False)
def draft(product,company,role,signal,channel):
 return f'Hi {role} at {company},\n\nI noticed a potential opportunity related to {signal} (simulated signal). {product} may help your team address this priority. Would you be open to a brief discussion?' if channel=='Email' else f'Hi {role}, would love to connect about {product} and your team’s {signal} initiative (simulated).'
