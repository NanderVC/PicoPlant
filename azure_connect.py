import machine
from secrets_azure import secrets
import network
import time
import utime
from machine import Pin, ADC
from umqtt.simple import MQTTClient



wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets["SSID"], secrets["PASSWORD"])
max_wait = 10

while max_wait > 0:
 if wlan.status() < 0 or wlan.status() >= 3:
  break
  max_wait -= 1
  print('waiting for connection...')
  time.sleep(1)
print(wlan.ifconfig())

#https://learn.microsoft.com/pt-br/azure/iot-hub/iot-hub-mqtt-support
#Gebruik link hieronder om te zien hoe je een sas token maakt
#https://learn.microsoft.com/pt-br/cli/azure/iot/hub?view=azure-cli-latest#az-iot-hub-generate-sas-token
CLIENTID = "Naam van je device in de iot hub"
MQTTSERVER="URL van je iot hub"
USERNAME="URL van je iot hub/Naam van je device in de iot hub/?api-version=2021-04-12"
SASTOKEN="Gegenereerde SAS token, zie comment hierboven"
c = MQTTClient(CLIENTID, MQTTSERVER, user=USERNAME, password=SASTOKEN, ssl=True)

c.connect()

#Deze calibratiepunten moet je zelf vinden voor jouw sensor
dry_cal = 40000
wet_cal = 25500

adcpin = 28
moist = ADC(adcpin)

#Enviando dados
while True:
    adc_value = moist.read_u16()
        
    normal_val = (adc_value-wet_cal)/(dry_cal-wet_cal)
        
    perc_val = (1-normal_val)*100
        
    if perc_val < 0:
        perc_val = 0
    
    if perc_val > 100:
        perc_val = 100
        
    output = round(perc_val)
    
    c.publish(b"devices/Naam van je device in de iot Hub/messages/events/", f"{{\"moisture\": {output} }}".encode())
    print(output)
    #Verander het getal hieronder om het interval van meetpunten te veranderen
    utime.sleep(60)
    
c.disconnect()