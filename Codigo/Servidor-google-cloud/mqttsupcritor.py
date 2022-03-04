import paho.mqtt.client as mqtt
import MySQLdb
# This is the Subscriber

def on_connect(client, userdata, flags, rc):
  print("Connected with result code "+str(rc))
  client.subscribe("hidroponia/datos")

def on_message(client, userdata, msg):
    data = msg.payload.decode()
    sensor = (data.split("|")[2])
    if sensor == 't':
                      tem = (data.split("|")[3])

                      db = MySQLdb.connect(host="34.139.167.162",  # your host
                                           user="6lowpan",       # username
                                           passwd="user",     # passwo
                                           db="temperatura")   # name of the database
                      val = (tem)
                      cur = db.cursor()
                      sql = "INSERT INTO tempe (tem) VALUES (%s)"
                      val = [tem]
                      cur.execute(sql,val)
                      db.commit()
#                      db.close()

    if sensor == 'h':
                      hume =  (data.split("|")[3])
                      dbhum = MySQLdb.connect(host="34.139.167.162",  # your host
                                              user="6lowpan",       # username
                                              passwd="user",     # password
                                              db="humedad")   # name of the database
                      cur = dbhum.cursor()
                      sqlhum = "INSERT INTO `dato`(`hum`) VALUES (%s)"
#                      sqlhum = "INSERT INTO hum (hum) VALUES (%s)"
                      valhum = [(hume)]
                      cur.execute(sqlhum,valhum)
                      dbhum.commit()
    if sensor == 'p':
                      ph = (data.split("|")[3])
                      dbph = MySQLdb.connect(host="34.139.167.162",  # your host
                                              user="6lowpan",       # username
                                              passwd="user",     # password
                                              db="ph")   # name of the database
                      cur = dbph.cursor()
                      sqlph = "INSERT INTO dato (ph) VALUES (%s)"
                      valph = [ph]
                      cur.execute(sqlph,valph)
                      dbph.commit()
#
    print data
#    print tem
#    print msg.payload.decode()
#  if msg.payload.decode() == "Hello":
#    print("Yes!")
#    client.disconnect() 
client = mqtt.Client()
client.connect("34.139.167.162",1883,60)

client.on_connect = on_connect
client.on_message = on_message

client.loop_forever()