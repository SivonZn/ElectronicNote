import menu
DEBUG = 0
load_config()
wifi_init_sta()
if not wifi.isconnected():
    wifi_connect()
else:
    uiprint("WiFi Connected!")
check_wlan_connect()
get_webcontext()
#init_time()

while DEBUG < 2:
    if machine.wake_reason() == PIN_WAKE:
        _thread.start_new_thread(wifi_connect_background,())
        menu.start_menu()
        pass
    
    if not wifi.isconnected():
        wifi_init_sta()
        wifi_connect_background()

    start_note_home()

    if config['setting_power_save_mode']:
        if timertc[3] >= 1 and timertc[3] <= 6:
            machine.deepsleep(19940 * 1000)
        pass

    if not config['setting_clock_show']:
        machine.lightsleep(config['setting_update_speed'] * 1000 * 60)
        get_webcontext()
    else:
        get_webcontext()
        machine.lightsleep((60 - timertc[5]) * 1000)#需要加上 *60 ,调试未加入方便减少时间
    DEBUG = DEBUG + 1
