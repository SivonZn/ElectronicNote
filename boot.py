# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()
import machine, ujson, network, urequests, time, ntptime, esp32

from machine import Timer

import ui
import epd290, uiepd
#库~
#===========================================================================================================

MAX_TIME   =   15
PIN_WAKE   =   2
RTC_WAKE   =   4
#常量定义

config     =   {}
timertc    =   []
EXIT_STATE =   0
MENUSET    =   0
SPEEDSET   =   0
CLOCKSET   =   0
SAVESET    =   0
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

tim0 = Timer(1)
#计时器定义

#初始定义
#===========================================================================================================

epd = epd290.EPD_2in9_Portrait()
#屏幕驱动初始化

def uiprint(x):
    print(x)
#shell显示相关函数

def display_print(x, y, data):
    pass
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
    ntptime.host = 'ntp.aliyun.com'
    time.sleep_ms(200)
    ntptime.settime()
    time.sleep_ms(2000)
    
def display_menu(location):
    epd.fill(0xff)
    epd.text(uiepd.menu1, 5, 10, 0x00)
    epd.text(uiepd.menu2, 5, 20, 0x00)
    epd.text(uiepd.menu3, 5, 30, 0x00)
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
    
#高级功能初始化
#===========================================================================================================

def wifi_connect():#WiFi连接
    uiprint("WiFi Connecting!")
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

def print_webcontext():#打印网页内容
    global config
    global response
    try:
        response = urequests.get(config['update_url'])
    except:
        pass
    uiprint(response.text)
    time.sleep_ms(10)

def check_wlan_connect():#检查网络连接
    global config
    try:
        response = urequests.get(config['update_url'])
        uiprint("Internet Connected!")
    except:
        uiprint("Internet Connect Error!")
    pass

def print_time():#打印当前时间
    global timertc
    timertc = time.localtime()
    uiprint("%d年 %d月 %d日 %d：%d：%d" %(timertc[0], timertc[1], timertc[2], timertc[3], timertc[4], timertc[5]))
    time.sleep_ms(10)
    pass
#===========================================================================================================

def setting_power_save_mode():#设置夜间1到6点停止更新数据，进入深度睡眠（时间不更新）
    global SAVESET
    
    uiprint(ui.tfarr[SAVESET])
    display_true_false(SAVESET)
    while enter_pin.value():
        time.sleep_ms(50)
    
    while True:
        if EXIT_STATE:
            return
        
        if menu_pin.value():
            tim0.deinit()
            tim0.init(period=30000,mode=Timer.ONE_SHOT,callback=menuexit)
            uiprint(ui.menuarr[MENUSET])
            display_menu(MENUSET)
            while enter_pin.value():
                time.sleep_ms(50)
            return
        
        if up_pin.value() or down_pin.value():
            tim0.deinit()
            tim0.init(period=30000,mode=Timer.ONE_SHOT,callback=menuexit)
            
            time.sleep_ms(30)
            SAVESET = not SAVESET
            uiprint(ui.tfarr[SAVESET])
            display_selector(SAVESET)
            
            while up_pin.value() or down_pin.value():
                time.sleep_ms(30)
        
        if enter_pin.value():
            tim0.deinit()
            tim0.init(period=30000,mode=Timer.ONE_SHOT,callback=menuexit)
            
            if SAVESET == 0:
                config['setting_power_save_mode'] = True
            if SAVESET == 1:
                config['setting_power_save_mode'] = False
            uiprint("Success!")
            time.sleep_ms(1000)
            uiprint(ui.menuarr[MENUSET])
            display_menu(MENUSET)
            
            while enter_pin.value():
                time.sleep_ms(50)
            return
    pass
    
def setting_update_speed():#设置数据更新速度，3到30分钟不等
    global SPEEDSET
    uiprint(ui.updatearr[SPEEDSET])
    display_speed(SPEEDSET)
    while enter_pin.value():
        time.sleep_ms(50)
    while True:
        if EXIT_STATE:
            return
        
        if menu_pin.value():
            tim0.deinit()
            tim0.init(period=30000,mode=Timer.ONE_SHOT,callback=menuexit)
            time.sleep_ms(30)
            
            uiprint(ui.menuarr[MENUSET])
            display_menu(MENUSET)
            return
        
        if up_pin.value():
            tim0.deinit()
            tim0.init(period=30000,mode=Timer.ONE_SHOT,callback=menuexit)
            time.sleep_ms(30)
            
            if SPEEDSET == 0:
                SPEEDSET = 2
            else:
                SPEEDSET = SPEEDSET - 1
            
            while up_pin.value():
                time.sleep_ms(30)
            uiprint(ui.updatearr[SPEEDSET])
            display_selector(SPEEDSET)
            
        if down_pin.value():
            tim0.deinit()
            tim0.init(period=30000,mode=Timer.ONE_SHOT,callback=menuexit)
            time.sleep_ms(30)
            
            if SPEEDSET == 2:
                SPEEDSET = 0
            else:
                SPEEDSET = SPEEDSET + 1
            
            while down_pin.value():
                time.sleep_ms(30)
            uiprint(ui.updatearr[SPEEDSET])
            display_selector(SPEEDSET)
            
        if enter_pin.value():
            tim0.deinit()
            tim0.init(period=30000,mode=Timer.ONE_SHOT,callback=menuexit)
            time.sleep_ms(30)
            
            if SPEEDSET == 0:
                config['setting_update_speed'] = 5
            if SPEEDSET == 1:
                config['setting_update_speed'] = 10
            if SPEEDSET == 2:
                config['setting_update_speed'] = 15
            uiprint("Success!")
            time.sleep_ms(1000)
            uiprint(ui.menuarr[MENUSET])
            display_menu(MENUSET)
            
            while enter_pin.value():
                time.sleep_ms(50)
            return
            pass
    pass

def setting_clock_show():#设置是否显示当前时间（省电？）
    global CLOCKSET
    
    uiprint(ui.tfarr[CLOCKSET])
    display_true_false(CLOCKSET)
    while enter_pin.value():
        time.sleep_ms(50)
    
    while True:
        if EXIT_STATE:
            return
        
        if menu_pin.value():
            tim0.deinit()
            tim0.init(period=30000,mode=Timer.ONE_SHOT,callback=menuexit)
            uiprint(ui.menuarr[MENUSET])
            display_menu(MENUSET)
            while enter_pin.value():
                time.sleep_ms(50)
            return
        
        if up_pin.value() or down_pin.value():
            tim0.deinit()
            tim0.init(period=30000,mode=Timer.ONE_SHOT,callback=menuexit)
            
            time.sleep_ms(30)
            CLOCKSET = not CLOCKSET
            uiprint(ui.tfarr[CLOCKSET])
            display_selector(CLOCKSET)
            
            while up_pin.value() or down_pin.value():
                time.sleep_ms(30)
        
        if enter_pin.value():
            tim0.deinit()
            tim0.init(period=30000,mode=Timer.ONE_SHOT,callback=menuexit)
            
            if CLOCKSET == 0:
                config['setting_clock_show'] = True
            if CLOCKSET == 1:
                config['setting_clock_show'] = False
            uiprint("Success!")
            time.sleep_ms(1000)
            uiprint(ui.menuarr[MENUSET])
            display_menu(MENUSET)
            
            while enter_pin.value():
                time.sleep_ms(50)
            return
    pass

def start_note_home():
    print_webcontext()
    if config['setting_clock_show']:
        print_time()
    pass

def menuexit(tim0):
    global EXIT_STATE
    EXIT_STATE = 1
    
def start_menu():
    global EXIT_STATE, MENUSET
    
    tim0.init(period=30000,mode=Timer.ONE_SHOT,callback=menuexit)
    uiprint(ui.menuarr[MENUSET])
    display_menu(MENUSET)
    
    while True:
        if EXIT_STATE:
            EXIT_STATE = 0
            break
        
        if menu_pin.value():
            break
        
        if up_pin.value():
            tim0.deinit()
            tim0.init(period=30000,mode=Timer.ONE_SHOT,callback=menuexit)
            time.sleep_ms(30)
            
            if MENUSET == 0:
                MENUSET = 2
                pass
            else:
                MENUSET = MENUSET - 1
                
            while up_pin.value():
                time.sleep_ms(30)
            uiprint(ui.menuarr[MENUSET])
            display_selector(MENUSET)
        
        if down_pin.value():
            tim0.deinit()
            tim0.init(period=30000,mode=Timer.ONE_SHOT,callback=menuexit)
            time.sleep_ms(30)
            
            if MENUSET == 2:
                MENUSET = 0
            else:
                MENUSET = MENUSET + 1
            
            while down_pin.value():
                time.sleep_ms(30)
            uiprint(ui.menuarr[MENUSET])
            display_selector(MENUSET)
        
        if enter_pin.value():
            tim0.deinit()
            tim0.init(period=30000,mode=Timer.ONE_SHOT,callback=menuexit)
            time.sleep_ms(30)
            
            if MENUSET == 0:
                setting_power_save_mode()
            if MENUSET == 1:
                setting_update_speed()
            if MENUSET == 2:
                setting_clock_show()
    pass


#界面函数
#===========================================================================================================

