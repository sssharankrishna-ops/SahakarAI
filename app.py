import streamlit as st
import pandas as pd
from datetime import date, timedelta, datetime
from agents import ForecastingAgent, AggregationAgent, PricingEngine, NegotiationAgent
import db

st.set_page_config(page_title='SahakarAI | Collective Bargaining', page_icon='🧵', layout='wide', initial_sidebar_state='expanded')
db.init_db()
forecast_agent=ForecastingAgent(); aggregation_agent=AggregationAgent(); pricing_engine=PricingEngine(); negotiation_agent=NegotiationAgent()
PRODUCTS=['Silk Saree','Cotton Saree','Handwoven Scarf','Handloom Fabric']

st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif} .stApp{background:#f6f7f4;color:#172b3a}
[data-testid="stSidebar"]{background:#142b3a} [data-testid="stSidebar"] *{color:#f5f7f5!important}
.hero{background:linear-gradient(120deg,#17394a,#245c60);padding:25px 28px;border-radius:18px;color:white;margin-bottom:18px}
.hero h1{font-family:Manrope,sans-serif;font-size:2rem;margin:0 0 5px 0;color:white}.hero p{margin:0;color:#d9e8e4}
.kpi{background:white;border:1px solid #e2e8e4;border-radius:14px;padding:16px 18px;min-height:110px}.kpi-label{font-size:.84rem;color:#60727c}.kpi-value{font-size:1.8rem;font-weight:800;color:#18394a}.kpi-note{font-size:.78rem;color:#19816c}
.section-title{font-family:Manrope,sans-serif;color:#18394a;font-size:1.2rem;font-weight:800;margin:12px 0}
div.stButton>button{border-radius:9px;font-weight:600} .stTabs [data-baseweb="tab-list"]{gap:8px}
.small-muted{color:#667781;font-size:.86rem}.warning-box{background:#fff5e6;border-left:4px solid #d99028;padding:12px;border-radius:7px}
</style>''', unsafe_allow_html=True)

def money(x): return f"₹{float(x):,.2f}"
def metric(label,value,note=''):
    st.markdown(f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-note">{note}</div></div>',unsafe_allow_html=True)
def get_weavers(): return db.rows('SELECT * FROM weavers ORDER BY id')
def all_orders(): return db.rows('SELECT * FROM orders ORDER BY id DESC')
def load_demo():
    db.init_db(reset=True); db.audit('DEMO_RESET',{'message':'Seed data reloaded'}); st.session_state.pop('last_allocation',None); st.session_state.pop('last_pricing',None); st.session_state.pop('last_order_id',None)

with st.sidebar:
    st.markdown('## 🧵 SahakarAI')
    st.caption('Collective Intelligence for Weaver Cooperatives')
    page=st.radio('NAVIGATION',['Overview','Weavers','Demand Intelligence','Bulk Orders','Price Protection','Negotiation','Officer Approvals','Audit & Reports'],label_visibility='collapsed')
    st.markdown('---')
    st.caption('DEMO ENVIRONMENT')
    st.caption('All seeded people, costs and orders are simulated.')
    if st.button('↻ Load Demo Scenario',use_container_width=True):
        load_demo(); st.success('Demo data reset.'); st.rerun()
    st.markdown('---')
    st.caption('SahakarAI • Prototype v1.0')

st.markdown('<div class="hero"><h1>One Cooperative. One Collective Voice.</h1><p>Coordinate demand, pool production capacity and negotiate with transparent cost protection.</p></div>',unsafe_allow_html=True)

if page=='Overview':
    weavers=get_weavers(); orders=all_orders(); offers=db.rows('SELECT * FROM offers'); approvals=db.rows('SELECT * FROM approvals')
    capacity=sum(w['capacity']-w['committed'] for w in weavers)
    forecast_sum=0
    for p in PRODUCTS:
        hist=db.rows('SELECT quantity FROM demand WHERE product=? ORDER BY id',(p,))
        forecast_sum+=forecast_agent.forecast([x['quantity'] for x in hist])['forecast']
    c=st.columns(4)
    with c[0]: metric('Registered weavers',str(len(weavers)),'Synthetic demo profiles')
    with c[1]: metric('Available capacity',f'{capacity:,}','Units not committed')
    with c[2]: metric('Forecast demand',f'{forecast_sum:,}','Next-period baseline')
    with c[3]: metric('Orders / offers',f'{len(orders)} / {len(offers)}','Saved orders / evaluated offers')
    st.markdown('<div class="section-title">Cooperative pulse</div>',unsafe_allow_html=True)
    left,right=st.columns([1.3,1])
    with left:
        st.subheader('Demand trend by product')
        d=db.rows('SELECT product,period,quantity FROM demand ORDER BY id')
        df=pd.DataFrame(d)
        if not df.empty:
            pivot=df.pivot(index='period',columns='product',values='quantity')
            st.line_chart(pivot,use_container_width=True)
    with right:
        st.subheader('Capacity by product')
        capdf=pd.DataFrame([{'Product':p,'Available units':sum(max(0,w['capacity']-w['committed']) for w in weavers if w['product']==p)} for p in PRODUCTS])
        st.bar_chart(capdf.set_index('Product'))
        st.info('Forecasts are baseline estimates from seeded synthetic history. Validate against real cooperative data before operational use.')
    st.markdown('<div class="section-title">Recent orders</div>',unsafe_allow_html=True)
    if orders: st.dataframe(pd.DataFrame(orders)[['id','product','quantity','status','target_unit','created_at']],use_container_width=True,hide_index=True)
    else: st.caption('No orders yet. Go to Bulk Orders to create the first demo order.')

elif page=='Weavers':
    st.subheader('Weaver Cooperative Management')
    weavers=get_weavers(); df=pd.DataFrame(weavers)
    f1,f2=st.columns(2)
    with f1: product_filter=st.selectbox('Filter by product',['All']+PRODUCTS)
    with f2: search=st.text_input('Search weaver name or ID')
    if product_filter!='All': df=df[df.product==product_filter]
    if search: df=df[df.name.str.contains(search,case=False) | df.id.astype(str).str.contains(search)]
    st.dataframe(df.rename(columns={'id':'ID','name':'Weaver','product':'Specialisation','capacity':'Capacity','committed':'Committed','unit_cost':'Unit cost (₹)','quality':'Quality','status':'Status'}),use_container_width=True,hide_index=True)
    st.markdown('#### Add a weaver')
    with st.form('add_weaver'):
        a,b,c=st.columns(3)
        name=a.text_input('Name'); product=b.selectbox('Specialisation',PRODUCTS); quality=c.selectbox('Quality',['Standard','Premium'])
        d,e,f=st.columns(3)
        capacity=d.number_input('Total capacity',min_value=1,value=20); unit_cost=e.number_input('Production cost per unit (₹)',min_value=0.01,value=1000.0,step=50.0); status=f.selectbox('Status',['Active','Inactive'])
        if st.form_submit_button('Add weaver'):
            if name.strip():
                db.execute('INSERT INTO weavers(name,product,capacity,committed,unit_cost,quality,status) VALUES(?,?,?,?,?,?,?)',(name.strip(),product,int(capacity),0,float(unit_cost),quality,status)); db.audit('WEAVER_CREATED',{'name':name,'product':product}); st.success('Weaver added.'); st.rerun()
            else: st.error('Enter a name.')

elif page=='Demand Intelligence':
    st.subheader('Demand Intelligence Agent')
    product=st.selectbox('Product category',PRODUCTS)
    hist=db.rows('SELECT period,quantity FROM demand WHERE product=? ORDER BY id',(product,))
    df=pd.DataFrame(hist)
    if not df.empty:
        st.line_chart(df.set_index('period'),y='quantity',use_container_width=True)
    x,y=st.columns(2)
    with x: horizon=st.slider('Forecast horizon (periods)',1,6,1)
    with y: seasonal=st.slider('Seasonal adjustment',0.5,2.0,1.0,0.05)
    if st.button('Generate Demand Forecast',type='primary'):
        result=forecast_agent.forecast([h['quantity'] for h in hist],horizon,seasonal)
        st.session_state['forecast_result']={'product':product,**result}
        db.audit('FORECAST_GENERATED',{'product':product,**result})
    result=st.session_state.get('forecast_result')
    if result and result['product']==product:
        a,b=st.columns(2)
        with a: metric('Estimated demand',f"{result['forecast']:,} units",result['method'])
        with b: st.warning(result['warning'])
        st.success(f"Planning suggestion: review production capacity for approximately {result['forecast']} units of {product} over the selected horizon.")
    st.caption('Forecasting agent uses a transparent recent-period mean. It is a planning baseline, not a verified market forecast.')

elif page=='Bulk Orders':
    st.subheader('Bulk Order Builder · Cooperative Supply Aggregation Agent')
    a,b,c=st.columns(3)
    with a: product=st.selectbox('Product',PRODUCTS)
    with b: quantity=st.number_input('Required quantity',min_value=1,value=100,step=5)
    with c: quality=st.selectbox('Quality requirement',['Any','Standard','Premium'])
    d,e=st.columns(2)
    with d: deadline=st.date_input('Delivery deadline',value=date.today()+timedelta(days=30),min_value=date.today())
    with e: shared=st.number_input('Shared order expenses (₹)',min_value=0.0,value=10000.0,step=500.0)
    markup=st.slider('Approved target markup',0.0,0.50,0.10,0.01,help='Markup is applied to total cost; it is not the same as profit margin.')
    if st.button('Generate Allocation Plan',type='primary'):
        allocation=aggregation_agent.allocate(get_weavers(),product,int(quantity),quality)
        st.session_state['last_allocation']=allocation; st.session_state['last_order_inputs']={'product':product,'quantity':int(quantity),'quality':quality,'deadline':str(deadline),'shared':float(shared),'markup':markup}
        if allocation['feasible']:
            pricing=pricing_engine.calculate(allocation['allocations'],shared,markup)
            st.session_state['last_pricing']=pricing
            db.audit('ALLOCATION_PLAN_GENERATED',{'product':product,'quantity':quantity,'allocations':allocation['allocations'],'pricing':pricing})
        else: st.session_state.pop('last_pricing',None)
    allocation=st.session_state.get('last_allocation')
    if allocation:
        if allocation['feasible']:
            st.success(f"Feasible: allocated {allocation['allocated']} of {allocation['requested']} units.")
            st.dataframe(pd.DataFrame(allocation['allocations']),use_container_width=True,hide_index=True)
            pricing=st.session_state['last_pricing']; c1,c2,c3=st.columns(3)
            with c1: metric('Production cost',money(pricing['production_cost']),'Sum of assigned weaver costs')
            with c2: metric('Total order cost',money(pricing['total_cost']),'Includes shared expenses')
            with c3: metric('Target price / unit',money(pricing['target_unit']),f"Markup {st.session_state['last_order_inputs']['markup']:.0%}")
            if st.button('Save Bulk Order',type='primary'):
                inp=st.session_state['last_order_inputs']
                oid=db.execute('INSERT INTO orders(product,quantity,quality,deadline,status,production_cost,shared_expenses,target_unit,created_at) VALUES(?,?,?,?,?,?,?,?,?)',(inp['product'],inp['quantity'],inp['quality'],inp['deadline'],'Awaiting negotiation',pricing['production_cost'],pricing['shared_expenses'],pricing['target_unit'],datetime.now().isoformat(timespec='seconds')))
                for al in allocation['allocations']:
                    db.execute('INSERT INTO allocations(order_id,weaver_id,quantity,unit_cost,line_cost) VALUES(?,?,?,?,?)',(oid,al['weaver_id'],al['quantity'],al['unit_cost'],al['line_cost']))
                    db.execute('UPDATE weavers SET committed=committed+? WHERE id=?',(al['quantity'],al['weaver_id']))
                db.audit('ORDER_CREATED',{'order_id':oid,'product':inp['product'],'quantity':inp['quantity'],'target_unit':pricing['target_unit']}); st.success(f'Order #{oid} saved.'); st.session_state['last_order_id']=oid
        else:
            st.error(f"Infeasible: requested {allocation['requested']} units, but only {allocation['allocated']} are currently available. Shortage: {allocation['shortage']} units.")
            st.info('Try a smaller quantity, a different quality requirement or a later deadline.')

elif page=='Price Protection':
    st.subheader('Cost Intelligence & Weaver-Level Price Protection')
    orders=all_orders()
    if not orders: st.info('Create a feasible order in Bulk Orders to inspect price protection.'); st.stop()
    chosen=st.selectbox('Select order',orders,format_func=lambda o:f"#{o['id']} · {o['product']} · {o['quantity']} units · {o['status']}")
    alloc=db.rows('SELECT a.*,w.name,w.product FROM allocations a JOIN weavers w ON w.id=a.weaver_id WHERE a.order_id=?',(chosen['id'],))
    pricing=pricing_engine.calculate([{'weaver_id':a['weaver_id'],'name':a['name'],'quantity':a['quantity'],'unit_cost':a['unit_cost'],'line_cost':a['line_cost']} for a in alloc],chosen['shared_expenses'],(chosen['target_unit']*chosen['quantity']/max(1,chosen['production_cost']+chosen['shared_expenses'])-1))
    c1,c2,c3=st.columns(3)
    with c1: metric('Break-even / unit',money(pricing['break_even_unit']),'Cost floor before markup')
    with c2: metric('Target / unit',money(chosen['target_unit']),'Stored order target')
    with c3: metric('Total order cost',money(pricing['total_cost']),'Production + shared costs')
    st.markdown('#### Participant-level cost coverage')
    df=pd.DataFrame(pricing['allocations'])
    if not df.empty:
        df['Total allocated cost'] = df['line_cost'] + df['shared_cost']
        df['Allocated cost / unit'] = (df['Total allocated cost']/df['quantity']).round(2)
        st.dataframe(df[['name','quantity','unit_cost','shared_cost','Allocated cost / unit','minimum_compensation_per_unit']],use_container_width=True,hide_index=True)
    st.caption('The price floor is calculated from the saved allocation and configured expenses. The prototype uses proportional shared-expense allocation; cooperatives should approve the method and member compensation rules.')

elif page=='Negotiation':
    st.subheader('Buyer Negotiation Simulator · Negotiation Agent')
    orders=all_orders()
    if not orders: st.warning('First create and save a feasible order in Bulk Orders.'); st.stop()
    chosen=st.selectbox('Bulk order',orders,format_func=lambda o:f"#{o['id']} · {o['product']} · {o['quantity']} units")
    alloc=db.rows('SELECT a.*,w.name FROM allocations a JOIN weavers w ON w.id=a.weaver_id WHERE a.order_id=?',(chosen['id'],))
    pricing=pricing_engine.calculate([{'weaver_id':a['weaver_id'],'name':a['name'],'quantity':a['quantity'],'unit_cost':a['unit_cost'],'line_cost':a['line_cost']} for a in alloc],chosen['shared_expenses'],max(0,chosen['target_unit']*chosen['quantity']/max(1,chosen['production_cost']+chosen['shared_expenses'])-1))
    with st.form('buyer_offer'):
        a,b,c=st.columns(3)
        buyer=a.text_input('Buyer / exporter name',value='Demo Exporter Ltd')
        offer=b.number_input('Buyer offer per unit (₹)',min_value=0.0,value=float(chosen['target_unit']*0.90),step=50.0)
        payment=c.number_input('Payment delay (days)',min_value=0,value=30,step=15)
        maxdays=st.number_input('Cooperative payment policy limit (days)',min_value=0,value=45,step=5)
        delivery_ok=st.checkbox('Delivery feasibility confirmed',value=True)
        submit=st.form_submit_button('Evaluate Offer',type='primary')
    if submit:
        result=negotiation_agent.evaluate(offer,pricing,payment,delivery_ok,maxdays)
        offer_id=db.execute('INSERT INTO offers(order_id,buyer,offer_unit,payment_days,action,message,reasons,created_at) VALUES(?,?,?,?,?,?,?,?)',(chosen['id'],buyer,offer,payment,result['action'],result['message'],'; '.join(result['reasons']),datetime.now().isoformat(timespec='seconds')))
        db.audit('OFFER_EVALUATED',{'offer_id':offer_id,'order_id':chosen['id'],'buyer':buyer,**result})
        st.session_state['last_offer_result']={'id':offer_id,'order_id':chosen['id'],'buyer':buyer,**result}
    result=st.session_state.get('last_offer_result')
    if result and result['order_id']==chosen['id']:
        if result['action']=='WITHIN_LIMITS': st.success('Within configured limits — requires authorised approval before commitment.')
        elif result['action']=='COUNTEROFFER': st.warning('Counteroffer recommended')
        else: st.error('Human review required')
        a,b,c=st.columns(3)
        with a: metric('Buyer offer / unit',money(result['offer_per_unit']),'Buyer-submitted amount')
        with b: metric('Estimated order profit',money(result['estimated_profit']),'Before unmodelled costs/taxes')
        with c: metric('Suggested target / unit',money(chosen['target_unit']),'From saved order policy')
        st.markdown('#### Agent explanation')
        for reason in result['reasons']: st.write('• '+reason)
        st.markdown('#### Draft response')
        st.info(result['message'])
        if result['action']=='HUMAN_REVIEW' or result['below_floor'] or result['below_target']:
            st.caption(f"Offer #{result['id']} is recorded for review. No real buyer has been contacted.")
        else: st.caption('Offer is only recommended for the next authorised step; it has not been accepted as a binding agreement.')
    st.markdown('#### Recent offers')
    offers=db.rows('SELECT * FROM offers WHERE order_id=? ORDER BY id DESC',(chosen['id'],))
    if offers: st.dataframe(pd.DataFrame(offers)[['id','buyer','offer_unit','payment_days','action','created_at']],use_container_width=True,hide_index=True)

elif page=='Officer Approvals':
    st.subheader('Cooperative Officer Approval Queue')
    offers=db.rows("SELECT f.*,o.product,o.quantity,o.target_unit,o.status AS order_status FROM offers f JOIN orders o ON o.id=f.order_id WHERE f.action IN ('HUMAN_REVIEW','COUNTEROFFER','WITHIN_LIMITS') ORDER BY f.id DESC")
    approvals=db.rows('SELECT * FROM approvals')
    done={a['offer_id'] for a in approvals}
    pending=[o for o in offers if o['id'] not in done]
    if not pending: st.success('No pending offers. Evaluate an offer in Negotiation to create a review item.'); st.stop()
    selected=st.selectbox('Pending offer',pending,format_func=lambda o:f"Offer #{o['id']} · Order #{o['order_id']} · {o['buyer']} · {o['action']}")
    st.write(f"**Product:** {selected['product']} · **Quantity:** {selected['quantity']} · **Buyer offer:** {money(selected['offer_unit'])}/unit · **Target:** {money(selected['target_unit'])}/unit")
    st.write('**Agent reason:** '+selected['reasons'])
    st.info(selected['message'])
    with st.form('approval_form'):
        officer=st.text_input('Officer identifier',value='Demo Officer')
        decision=st.selectbox('Decision',['Approve for next authorised step','Reject offer','Return for revision'])
        reason=st.text_area('Decision reason (required)')
        if st.form_submit_button('Record decision',type='primary'):
            if not reason.strip(): st.error('A reason is required for the audit trail.')
            else:
                db.execute('INSERT INTO approvals(offer_id,decision,reason,officer,created_at) VALUES(?,?,?,?,?)',(selected['id'],decision,reason.strip(),officer.strip() or 'Demo Officer',datetime.now().isoformat(timespec='seconds')))
                db.audit('OFFICER_DECISION',{'offer_id':selected['id'],'decision':decision,'reason':reason,'officer':officer})
                st.success('Decision recorded.'); st.rerun()
    st.markdown('#### Decision history')
    if approvals: st.dataframe(pd.DataFrame(approvals),use_container_width=True,hide_index=True)

elif page=='Audit & Reports':
    st.subheader('Audit Log & Reports')
    events=db.rows('SELECT * FROM audit ORDER BY id DESC')
    if events:
        st.dataframe(pd.DataFrame(events),use_container_width=True,hide_index=True)
        csv=pd.DataFrame(events).to_csv(index=False).encode('utf-8')
        st.download_button('Download audit log CSV',csv,'sahakarai_audit_log.csv','text/csv')
    else: st.caption('No audit events recorded yet.')
    st.markdown('#### Orders report')
    orders=all_orders()
    if orders:
        df=pd.DataFrame(orders); st.dataframe(df,use_container_width=True,hide_index=True)
        st.download_button('Download orders CSV',df.to_csv(index=False).encode('utf-8'),'sahakarai_orders.csv','text/csv')
    st.markdown('#### Offers report')
    offers=db.rows('SELECT * FROM offers ORDER BY id DESC')
    if offers:
        df=pd.DataFrame(offers); st.dataframe(df,use_container_width=True,hide_index=True)
        st.download_button('Download offers CSV',df.to_csv(index=False).encode('utf-8'),'sahakarai_offers.csv','text/csv')

st.markdown('---')
st.caption('SahakarAI is a hackathon prototype. Data is simulated. Pricing outputs are estimates and must be reviewed under real cooperative rules. No real buyer is contacted and no binding contract is made.')
