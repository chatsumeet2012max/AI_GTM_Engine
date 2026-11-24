import streamlit as st
import pandas as pd
import graphviz
import json, os, urllib.request
from datetime import datetime, timezone
from engine import CONFIG,load,discover,draft
st.set_page_config(page_title='GTM Engine',page_icon='🎯',layout='wide')
st.title('GTM Engine | Revenue Intelligence')
st.warning('DEMO MODE — synthetic records and unverified contacts. No real messages are sent.')
if 'pipeline' not in st.session_state: st.session_state.pipeline=load('pipeline')
if 'audit' not in st.session_state: st.session_state.audit=[]
if 'messages' not in st.session_state: st.session_state.messages={}
if 'icp' not in st.session_state: st.session_state.icp=None
p=st.session_state.pipeline
sector=st.sidebar.selectbox('Sector',list(CONFIG)); defaults=CONFIG[sector]
product=st.sidebar.text_input('Product name','AdVision Interactive' if sector=='AI Advertising' else '',key='product_'+sector)
description=st.sidebar.text_area('Product description','AI-powered interactive advertising for brands and agencies' if sector=='AI Advertising' else '',key='desc_'+sector)
weight=st.sidebar.slider('Fit weight',0,100,60)/100
st.sidebar.caption('Other sectors have ICP templates but no matching seed accounts unless industries overlap.')
tabs=st.tabs(['1 · ICP','2 · Discovery','3 · Graph','4 · Outreach','5 · Pipeline','6 · Audit'])
with tabs[0]:
 st.subheader('Define and approve your ideal customer profile')
 st.caption('Template-based inference by default; optional OpenAI API for AI generation. Review all recommendations.')
 if st.button('Generate ICP with AI (optional)'):
  key=os.getenv('OPENAI_API_KEY')
  if not key: st.info('Set OPENAI_API_KEY to enable AI inference. Use the editable template below meanwhile.')
  else:
   try:
    payload={'model':os.getenv('OPENAI_MODEL','gpt-4.1-mini'),'messages':[{'role':'system','content':'Return JSON only with keys industries, roles, triggers (arrays of strings), min_employees, max_employees (integers). Suggest an ICP; do not invent evidence.'},{'role':'user','content':f'{sector}: {product}. {description}'}],'response_format':{'type':'json_object'}}
    req=urllib.request.Request('https://api.openai.com/v1/chat/completions',data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=20) as r: ai=json.loads(json.load(r)['choices'][0]['message']['content'])
    st.session_state['ai_'+sector]=ai
   except Exception as e: st.error('AI request failed; template remains available: '+str(e))
 ai=st.session_state.get('ai_'+sector,{})
 industries=st.text_input('Target industries (comma separated)',', '.join(ai.get('industries',defaults[0])),key='inds_'+sector+str(ai)).split(',')
 roles=st.text_input('Buyer roles',', '.join(ai.get('roles',defaults[1])),key='roles_'+sector+str(ai)).split(',')
 triggers=st.text_input('Buying triggers',', '.join(ai.get('triggers',defaults[2])),key='triggers_'+sector+str(ai)).split(',')
 lo,hi=st.slider('Employee range',0,20000,(100,10000),step=100)
 if st.button('Approve ICP',type='primary',disabled=not bool(product.strip() and description.strip())):
  st.session_state.icp={'sector':sector,'product':product,'description':description,'industries':[x.strip() for x in industries],'roles':[x.strip() for x in roles],'triggers':[x.strip() for x in triggers],'lo':lo,'hi':hi}; st.success('ICP approved')
 icp=st.session_state.icp
 if icp: st.json(icp)
active=icp and (icp['sector'],icp['product'],icp['description'])==(sector,product,description)
results=discover(icp['industries'],icp['lo'],icp['hi'],icp['triggers'],weight) if active else pd.DataFrame()
with tabs[1]:
 st.subheader('Ranked account discovery')
 if not active: st.info('Approve the current product ICP first.')
 elif results.empty: st.info('No matching synthetic accounts. Add sector-specific seed data to extend coverage.')
 else:
  st.metric('Matching accounts',len(results)); st.dataframe(results[['company_id','name','industry','employees','fit_score','intent_score','score','tier','evidence']],hide_index=True,use_container_width=True)
  st.download_button('Export matches',results.to_csv(index=False),'matches.csv')
 st.subheader('Synthetic competitor intelligence'); st.dataframe(load('competitors') if sector=='AI Advertising' else pd.DataFrame(),hide_index=True)
with tabs[2]:
 st.subheader('Account relationship graph')
 if not results.empty:
  cid=st.selectbox('Account',results.company_id,format_func=lambda x:results.set_index('company_id').loc[x,'name'])
  company=results.set_index('company_id').loc[cid,'name']; people=load('people').query('company_id == @cid'); signals=load('signals').query('company_id == @cid')
  g=graphviz.Digraph(); g.attr(rankdir='LR'); g.node(cid,company,shape='box'); g.node('product',product,shape='box'); g.edge(cid,'product',label='matched_to')
  for r in people.itertuples(): g.node(r.person_id,r.name+'\n'+r.title); g.edge(r.person_id,cid,label='works_at')
  for r in signals.itertuples(): g.node(r.signal_id,r.type); g.edge(cid,r.signal_id,label='has_signal')
  st.graphviz_chart(g,use_container_width=True)
 else: st.info('Generate matching accounts to explore the graph.')
with tabs[3]:
 st.subheader('Human-controlled outreach')
 if not results.empty:
  cid=st.selectbox('Prospect',results.company_id,key='outreach_company'); company=results.set_index('company_id').loc[cid,'name']; contacts=load('people').query('company_id == @cid'); person=st.selectbox('Decision maker',contacts.person_id,format_func=lambda x:contacts.set_index('person_id').loc[x,'title']); contact=contacts.set_index('person_id').loc[person]; st.write(contact.email,'—',contact.verification)
  sig=load('signals').query('company_id == @cid').sort_values('relevance',ascending=False).iloc[0]['type']; channel=st.radio('Channel',['Email','LinkedIn'],horizontal=True); mid=f'{sector}|{product}|{person}|{channel}'
  if mid not in st.session_state.messages: st.session_state.messages[mid]={'body':draft(product,company,contact.title,sig,channel),'status':'Pending'}
  m=st.session_state.messages[mid]; body=st.text_area('Edit draft',m['body'],height=180,key='body_'+mid)
  if body!=m['body']: m.update(body=body,status='Pending')
  a,b,c=st.columns(3)
  def log(event): st.session_state.audit.append({'time':datetime.now(timezone.utc).isoformat(),'actor':'Human','account':cid,'event':event})
  if a.button('Approve',disabled=m['status']=='Simulated sent'): m['status']='Approved'; log('Approved draft')
  if b.button('Reject',disabled=m['status']=='Simulated sent'): m['status']='Rejected'; log('Rejected draft')
  if c.button('Simulate send',disabled=m['status']!='Approved'):
   m['status']='Simulated sent'; mask=p.company_id.eq(cid)&p.stage.eq('Matched'); p.loc[mask,['stage','owner_type']]=['Contacted','Human']; log('Simulated send'); st.rerun()
  st.write('Status:',m['status'])
 else: st.info('Approve an ICP with matching accounts first.')
with tabs[4]:
 st.subheader('Advertising seed pipeline — simulated historical data')
 if sector!='AI Advertising' or product!='AdVision Interactive': st.info('Historical pipeline belongs to the advertising seed product; it is not a new product forecast.')
 a,b,c=st.columns(3); a.metric('Accounts',len(p)); b.metric('Gross pipeline',f'${p.deal_usd.sum():,.0f}'); c.metric('Weighted seed value',f'${p.weighted_usd.sum():,.0f}')
 st.bar_chart(p.stage.value_counts()); st.dataframe(p,use_container_width=True,hide_index=True); st.download_button('Export pipeline',p.to_csv(index=False),'pipeline.csv')
with tabs[5]:
 st.subheader('Session audit log'); st.dataframe(pd.DataFrame(st.session_state.audit),use_container_width=True); st.caption('Session-only state; refreshing or restarting can reset data.')
