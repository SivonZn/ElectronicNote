from boot import *
import menu
DEBUG = 0
load_config()
wifi_init_sta()
if not wifi.isconnected():
    wifi_connect()
else:
    uiprint("WiFi Connected!")
check_wlan_connect()

init_time()
get_webcontext()


while DEBUG < 2:
    if machine.wake_reason() == PIN_WAKE:
        wifi_init_sta()
        menu.start_menu()
        pass
    
    if not wifi.isconnected():
        wifi_init_sta()
        wifi_connect()

    start_note_home()

    if config['setting_power_save_mode']:
        if timertc[3] >= 1 and timertc[3] <= 6:
            machine.deepsleep(19940 * 1000)
        pass

    if not config['setting_clock_show']:
        machine.lightsleep(config['setting_update_speed'] * 1000 * 60)
    else:
        machine.lightsleep(57 * 1000)#需要加上 *60 ,调试未加入方便减少时间