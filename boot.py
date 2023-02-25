# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()
import machine, ujson, network, urequests, time, ntptime, esp32, framebuf

from machine import Timer

import ui
import epd290, uiepd, image
import _thread
#库~
#===========================================================================================================

MAX_TIME   =   15
PIN_WAKE   =   2
RTC_WAKE   =   4
#常量定义

config     =   {}
timertc    =   []
respj      =   []
weatj      =   []
#变量定义

wifi = network.WLAN(network.STA_IF)
ap = network.WLAN(network.AP_IF)
rtc = machine.RTC()
#wlan,RTC相关定义

UP       =      25
DOWN     =      26
MENU     =      27
ENTER    =      33
#按键映射

tim0 = Timer(1)#timenu
timupdate = Timer(1)#timeupdate
#计时器定义

#初始定义
#===========================================================================================================

epd = epd290.EPD_2in9_Portrait()
epd.init(epd290.full_update)
epd.Clear(0xff)
epd.init(epd290.partial_update)
epd.fill(0xff)
imagebuf = framebuf.FrameBuffer(bytearray(image.boot_image), 50, 50, framebuf.MONO_HLSB)
epd.blit(imagebuf, 40, 110)
epd.text("Sivon&Parallfolk", 0, 288, 0x00)
epd.display(epd.buffer)

#屏幕驱动初始化

def uiprint(x):
    print(x)
#shell显示相关函数

def display_print(x, y, data):
    epd.fill(0xff)
    epd.text(data, x, y, 0x00)
    epd.display(epd.buffer)

def display_add(x, y, data):
    epd.text(data, x, y, 0x00)

def display_image(x, y, xlen, ylen, data):
    for i in xlen:
        for j in ylen:
            epd.pixel(x + j, y + i, data[i * 10 + j])
    epd.display(epd.buffer)
    
def display_on():
    epd.display(epd.buffer)
    
def display_clear():
    epd.fill(0xff)
#屏幕输出相关

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
    
menu_pin = machine.Pin(MENU, machine.Pin.IN, machine.Pin.PULL_DOWN)
down_pin = machine.Pin(DOWN, machine.Pin.IN, machine.Pin.PULL_DOWN)
up_pin = machine.Pin(UP, machine.Pin.IN, machine.Pin.PULL_DOWN)
enter_pin = machine.Pin(ENTER, machine.Pin.IN, machine.Pin.PULL_DOWN)
#初始化machine.Pin类

esp32.wake_on_ext0(menu_pin, esp32.WAKEUP_ANY_HIGH)
#初始化中断函数（菜单中断）

#基础配置初始化
#===========================================================================================================
def wifi_init_sta():#WiFi station模式初始化
    global config
    if wifi.active() or ap.active():
        wifi.active(False)
        ap.active(False)
    wifi.active(True)
    wifi.connect(config['ssid'],config['password'])

def wifi_init_ap():#WiFi ap模式初始化
    if wifi.active() or ap.active():
        wifi.active(False)
        ap.active(False)
    ap.config(ssid='ESP32wifi')
    ap.config(maxxlients=10)
    ap.active(True)
    
def init_time():#初始化全局时间
    ntptime.NTP_DELTA = 3155644800
    time.sleep_ms(2000)
    ntptime.host = 'time1.aliyun.com'
    time.sleep_ms(2000)
    ntptime.settime()
    
def display_basic_menu(location):
    epd.fill(0xff)
    epd.text(uiepd.basic_menu1, 5, 10, 0x00)
    epd.text(uiepd.basic_menu2, 5, 20, 0x00)
    epd.text(uiepd.basic_menu3, 5, 30, 0x00)
    epd.text(uiepd.selector, 13, 10 * location + 10, 0x00)
    epd.display(epd.buffer)
    
def display_menu(location):
    epd.fill(0xff)
    epd.text(uiepd.menu1, 5, 10, 0x00)
    epd.text(uiepd.menu2, 5, 20, 0x00)
    epd.text(uiepd.selector, 13, 10 * location + 10, 0x00)
    epd.display(epd.buffer)
    
def display_selector(location):
    epd.fill_rect(13, 10, 8, 50, 0xff)
    epd.text(uiepd.selector, 13, 10 * location + 10, 0x00)
    epd.display(epd.buffer)
    
def display_true_false(location):
    epd.fill(0xff)
    epd.text(uiepd.true_false1, 5, 10, 0x00)
    epd.text(uiepd.true_false2, 5, 20, 0x00)
    epd.text(uiepd.selector, 13, 10 * location + 10, 0x00)
    epd.display(epd.buffer)
    
def display_speed(location):
    epd.fill(0xff)
    epd.text(uiepd.update_speed1, 5, 10, 0x00)
    epd.text(uiepd.update_speed2, 5, 20, 0x00)
    epd.text(uiepd.update_speed3, 5, 30, 0x00)
    epd.text(uiepd.selector, 13, 10 * location + 10, 0x00)
    epd.display(epd.buffer)
    
def display_other_menu(location):
    epd.fill(0xff)
    epd.text(uiepd.other_menu1, 5, 10, 0x00)
    epd.text(uiepd.selector, 13, 10 * location + 10, 0x00)
    epd.display(epd.buffer)
    
def display_recovery(location):
    epd.fill(0xff)
    epd.text("Clean Data?",5, 10, 0x00)
    epd.text(uiepd.true_false1, 5, 20, 0x00)
    epd.text(uiepd.true_false2, 5, 30, 0x00)
    epd.text(uiepd.selector, 13, 10 * location + 20, 0x00)
    epd.display(epd.buffer)
    
#高级功能初始化
#===========================================================================================================

def wifi_connect():#WiFi连接
    uiprint("WiFi Connecting...")
    display_add(5, 10, "WiFi Connecting...")
    display_on()
    i = 0
    while i < 15:
        time.sleep(1)
        i += 1
        if wifi.isconnected():
            uiprint("WiFi Connected!")
            display_add(5, 20, "WiFi Connected!")
            display_on()
            break
    if not wifi.isconnected():
        uiprint("WiFi Connect Error! Plase check the WiFi config or your ruote")
        raise Exception('WiFi Connect Error! Plase check the WiFi config or your ruote')
    pass

def wifi_connect_background():#WiFi连接
    i = 0
    while i < 15:
        time.sleep(1)
        i += 1
        if wifi.isconnected():
            break
    if not wifi.isconnected():
        uiprint("WiFi Connect Error! Plase check the WiFi config or your ruote")
        raise Exception('WiFi Connect Error! Plase check the WiFi config or your ruote')
    pass

def check_wlan_connect():#检查网络连接
    global config
    try:
        response = urequests.get(config['update_url'])
        uiprint("Internet Connected!")
        display_add(5, 30, "Internet Connected!")
        display_on()
    except:
        uiprint("Internet Connect Error!")
        return False
    time.sleep_ms(50)
    return True

def get_webcontext():
    global config
    global response
    global weather
    global respj
    global weatj
    if not wifi.isconnected():
        if not check_wlan_connect():
            wifi_init_sta()
            wifi_connect_background()
    try:
        response = urequests.get(config['update_url'])
        respj = response.json()
    except:
        pass

    try:
        weather = urequests.get(config['weather_url'])
        weatj = weather.json()
    except:
        pass
    uiprint("up to date")
    timupdate.init(period=1 * 60 * 1000, mode=Timer.ONE_SHOT, callback=tim_get_webcontext)
#=========================================
def tim_get_webcontext(timupdate):
    global config
    global response
    get_webcontext()
#=========================================

def print_webcontext():#打印网页内容
    global respj
    global weatj
    uiprint(respj['title'])
    display_add(5, 30,respj['title'])
    uiprint(weatj.get('results')[0].get('now')['text'])
    display_add(5, 5, weatj.get('results')[0].get('now')['text'])
    uiprint(weatj.get('results')[0].get('now')['temperature'])
    display_add(104, 5, weatj.get('results')[0].get('now')['temperature'])
    time.sleep_ms(10)

def print_time():#打印当前时间
    global timertc
    timertc = time.localtime()
    uiprint("%d/%d/%d %d:%d:%d" %(timertc[0], timertc[1], timertc[2], timertc[3], timertc[4], timertc[5]))
    display_add(5, 278, "%d/%d/%d" %(timertc[0], timertc[1], timertc[2]))
    display_add(5, 288, "%d:%d:%d" %(timertc[3], timertc[4], timertc[5]))
    time.sleep_ms(10)
    pass
#===========================================================================================================

def start_note_home():
    display_clear()
    if config['setting_clock_show']:
        print_time()
    print_webcontext()
    epd.display(epd.buffer)
    pass

#界面函数
#===========================================================================================================


