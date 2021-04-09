#sqlite3 database stuff:
import sqlite3,os,datetime

conn = sqlite3.connect("/mnt/bot.db")
conn.row_factory = sqlite3.Row #https://itheo.nl/get-column-names-from-slqite-python

def createDB():
  c = conn.cursor()
  c.execute("""CREATE TABLE IF NOT EXISTS wager (id INTEGER PRIMARY KEY, 
                                     created_date DATE,
                                     creator_id INTEGER,
                                     invitee_id INTEGER,
                                     accepted_date DATE,
                                     declined_date DATE,
                                     claim_date DATE,
                                     strike_price INTEGER,
                                     creator_is_long BOOLEAN,
                                     smart_contract_id TEXT)""")
  c.execute("""CREATE TABLE IF NOT EXISTS wallet (discord_id INTEGER PRIMARY KEY,
                                     wallet_id TEXT)""")
  conn.commit() #commit the current transaction
  

#Check if invitee already has a pending invite, and if it does, return that row of the table:
def getPendingInvite(userid):
  sql = """SELECT * FROM wager WHERE invitee_id = ? AND accepted_date IS NULL AND declined_date IS NULL ORDER BY id DESC"""
  cur = conn.cursor()
  cur.execute(sql,[userid])
  rows = cur.fetchall()
  if len(rows) == 0: return None
  return dict(rows[0])

def createNewWager(creator_id, invitee_id, claim_date, strike_price, creator_is_long):
  sql = """INSERT INTO wager(created_date,creator_id,invitee_id,claim_date,strike_price,creator_is_long) VALUES(?,?,?,?,?,?) """
  cur = conn.cursor()
  cur.execute(sql,[datetime.date.today(), creator_id, invitee_id, claim_date, strike_price, creator_is_long])
  conn.commit()

def updateWagerAccept(row_id, smart_contract_id):
  sql = """UPDATE wager SET accepted_date = ?, smart_contract_id = ? WHERE id = ?"""
  cur = conn.cursor()
  cur.execute(sql,[datetime.date.today(), smart_contract_id, row_id])
  conn.commit()

def updateWagerDecline(row_id):
  sql = """UPDATE wager SET declined_date = ? WHERE id = ?"""
  cur = conn.cursor()
  cur.execute(sql,[datetime.date.today(), row_id])
  conn.commit()

#Return a list of wager smart contract id where claim_date is today and caller's id is in the row:
def getContractsClaimableTodayForUser(userid):
  today_text = str(datetime.date.today())
  sql = """SELECT smart_contract_id FROM wager WHERE claim_date = ? AND (creator_id = ? OR invitee_id = ?)"""
  cur = conn.cursor()
  cur.execute(sql,[today_text, userid, userid])
  rows = cur.fetchall()
  if len(rows) == 0: return []
  return [ x['smart_contract_id'] for x in rows ]

#Return a list of wager smart contract id where claim_date is today:
def getContractsClaimableToday():
  today_text = str(datetime.date.today())
  sql = """SELECT smart_contract_id FROM wager WHERE claim_date = ?"""
  cur = conn.cursor()
  cur.execute(sql,[today_text])
  rows = cur.fetchall()
  if len(rows) == 0: return []
  return [ x['smart_contract_id'] for x in rows ]

def addWalletForUser(userid,wallet_id):
  sql = """INSERT OR REPLACE INTO wallet(discord_id,wallet_id) VALUES(?,?) """
  cur = conn.cursor()
  cur.execute(sql,[userid,wallet_id])
  conn.commit()

def getWalletForUser(userid):
  sql = """SELECT wallet_id FROM wallet WHERE discord_id = ? """
  cur = conn.cursor()
  cur.execute(sql,[userid])
  rows = cur.fetchall()
  if len(rows) == 0: return None
  return rows[0][0]

#Test
if False:
  createDB()
  #createNewWager(1,2,'2020-01-01')
  print (str(getWalletForUser(766359369033187409)))
  print (str(getPendingInvite(670672994951233536)))
  print (str(getClaimableTodayContracts(766359369033187409)))

