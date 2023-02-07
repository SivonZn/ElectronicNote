import machine,ujson,network,urequests,time,ntptime

#库~
#===========================================================================================================

MAX_TIME = 15
#常量定义

config = {}
#变量定义

wifi = network.WLAN(network.STA_IF)
ap = network.WLAN(network.AP_IF)
rtc = machine.RTC()
#wlan,RTC相关定义

#初始定义
#===========================================================================================================

def uiprint(x):
    print(x)
#显示相关函数

def load_config():
    global config
    try:
        cfg = open('config.json','r')
        config = ujson.loads(cfg.read())
    except:
        cfg = open('config.json','w')
        cfgo = open('config.cfg','r')
        cfg.write(cfgo.read())
        cfg.close()
        cfgo.close()
        cfg = open('config.json','r')
        config = ujson.loads(cfg.read())
        pass
    cfg.close()
#读取配置文件（可扩展更新）
    
#基础配置初始化
#===========================================================================================================

def wifi_init_sta():
    global config
    if wifi.active() or ap.active():
        wifi.active(False)
        ap.active(False)
    wifi.active(True)
    wifi.connect(config['ssid'],config['password'])

def wifi_init_ap():
    if wifi.active() or ap.active():
        wifi.active(False)
        ap.active(False)
    ap.config(ssid='ESP32wifi')
    ap.config(maxxlients=10)
    ap.active(True)
    
def init_time():
    ntptime.NTP_DELTA = 3155644800
    ntptime.host = 'ntp1.aliyun.com'
    ntptime.settime()
    time.sleep_ms(2000)

#高级功能初始化
#===========================================================================================================

def wifi_connect():
    if wifi.isconnected():
        return
    i = 0
    while i < 15:
        time.sleep(1)
        i += 1
        if wifi.isconnected():
            uiprint("WiFi Connected!")
            break
    if not wifi.isconnected():
        uiprint("WiFi Connect Error! Plase check the WiFi config or your ruote")
        raise Exception('WiFi Connect Error! Plase check the WiFi config or your ruote')
    pass

def print_webcontext():
    global config
    response = urequests.get(config['update_url'])
    uiprint(response.text)
    time.sleep_ms(10)

def check_wlan_connect():
    global config
    try:
        response = urequests.get(config['update_url'])
        uiprint("Internet Connected!")
    except:
        uiprint("Internet Connect Error!")
    pass

def print_time():
    pass

#===========================================================================================================

def setting_power_save_mode():#设置夜间1到6点停止更新数据，进入深度睡眠（时间不更新）
    pass
    
def setting_update_speed():#设置数据更新速度，3到30分钟不等
    pass

def setting_clock_show():#设置是否显示当前时间（省电？）
    pass

#设置类
#===========================================================================================================

#while True:
load_config()
wifi_init_sta()
if not wifi.isconnected():
    wifi_connect()
check_wlan_connect()

init_time()

print_webcontext()
timertc = time.localtime()
uiprint("%d年 %d月 %d日 %d：%d：%d" %(timertc[0], timertc[1], timertc[2], timertc[3], timertc[4], timertc[5]))
time.sleep_ms(10)

if config['setting_power_save_mode']:
    pass
machine.lightsleep(config['setting_update_speed']*1000)#需要加上 *60 ,调试未加入方便减少时间