import sqlite3, os, json
from datetime import datetime

DB_PATH = os.environ.get('SAHAKARAI_DB', os.path.join(os.path.dirname(__file__), 'sahakarai.db'))

def conn():
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c

def init_db(reset=False):
    c=conn(); cur=c.cursor()
    if reset:
        cur.execute('DROP TABLE IF EXISTS weavers'); cur.execute('DROP TABLE IF EXISTS demand'); cur.execute('DROP TABLE IF EXISTS orders'); cur.execute('DROP TABLE IF EXISTS allocations'); cur.execute('DROP TABLE IF EXISTS offers'); cur.execute('DROP TABLE IF EXISTS approvals'); cur.execute('DROP TABLE IF EXISTS audit')
    cur.executescript('''
    CREATE TABLE IF NOT EXISTS weavers(id INTEGER PRIMARY KEY, name TEXT, product TEXT, capacity INTEGER, committed INTEGER DEFAULT 0, unit_cost REAL, quality TEXT, status TEXT DEFAULT 'Active');
    CREATE TABLE IF NOT EXISTS demand(id INTEGER PRIMARY KEY, product TEXT, period TEXT, quantity INTEGER);
    CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY AUTOINCREMENT, product TEXT, quantity INTEGER, quality TEXT, deadline TEXT, status TEXT, production_cost REAL DEFAULT 0, shared_expenses REAL DEFAULT 0, target_unit REAL DEFAULT 0, created_at TEXT);
    CREATE TABLE IF NOT EXISTS allocations(id INTEGER PRIMARY KEY AUTOINCREMENT, order_id INTEGER, weaver_id INTEGER, quantity INTEGER, unit_cost REAL, line_cost REAL);
    CREATE TABLE IF NOT EXISTS offers(id INTEGER PRIMARY KEY AUTOINCREMENT, order_id INTEGER, buyer TEXT, offer_unit REAL, payment_days INTEGER, action TEXT, message TEXT, reasons TEXT, created_at TEXT);
    CREATE TABLE IF NOT EXISTS approvals(id INTEGER PRIMARY KEY AUTOINCREMENT, offer_id INTEGER, decision TEXT, reason TEXT, officer TEXT, created_at TEXT);
    CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY AUTOINCREMENT, event TEXT, detail TEXT, created_at TEXT);
    ''')
    if cur.execute('SELECT COUNT(*) FROM weavers').fetchone()[0]==0:
        products=['Silk Saree','Cotton Saree','Handwoven Scarf','Handloom Fabric']
        costs={'Silk Saree':[3000,3200,2800,3100,2950,3300], 'Cotton Saree':[900,850,980,920], 'Handwoven Scarf':[350,320,400], 'Handloom Fabric':[500,540,480]}
        n=1
        for p in products:
            for j,cost in enumerate(costs[p]):
                capacity=[10,15,20,25,30][(j+n)%5]
                cur.execute('INSERT INTO weavers(id,name,product,capacity,committed,unit_cost,quality,status) VALUES(?,?,?,?,?,?,?,?)',(n,f'Weaver {n:02d}',p,capacity, min(capacity//5,2),cost,['Standard','Premium'][j%2],'Active')); n+=1
    if cur.execute('SELECT COUNT(*) FROM demand').fetchone()[0]==0:
        samples={'Silk Saree':[35,42,40,48,52,55,50,62,64,68,72,78], 'Cotton Saree':[70,75,68,80,83,90,87,92,98,100,96,108], 'Handwoven Scarf':[90,85,100,105,110,115,108,120,125,130,135,142], 'Handloom Fabric':[60,62,65,63,70,74,72,78,80,85,88,91]}
        for p,vals in samples.items():
            for i,v in enumerate(vals): cur.execute('INSERT INTO demand(product,period,quantity) VALUES(?,?,?)',(p,f'P{i+1:02d}',v))
    c.commit(); c.close()

def rows(query, args=()):
    c=conn(); out=[dict(r) for r in c.execute(query,args).fetchall()]; c.close(); return out

def execute(query,args=()):
    c=conn(); cur=c.execute(query,args); c.commit(); ident=cur.lastrowid; c.close(); return ident

def audit(event, detail):
    execute('INSERT INTO audit(event,detail,created_at) VALUES(?,?,?)',(event, json.dumps(detail, ensure_ascii=False, default=str), datetime.now().isoformat(timespec='seconds')))
