from boot import *

EXIT_STATE =   0
MENUSET1   =   0
MENUSET2   =   0
MENUSET3   =   0
SPEEDSET   =   0
CLOCKSET   =   0
SAVESET    =   0

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
            uiprint(ui.basic_menuarr[MENUSET2])
            display_basic_menu(MENUSET2)
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
            uiprint(ui.basic_menuarr[MENUSET2])
            display_basic_menu(MENUSET2)
            
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
            
            uiprint(ui.basic_menuarr[MENUSET2])
            display_basic_menu(MENUSET2)
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
            uiprint(ui.basic_menuarr[MENUSET2])
            display_basic_menu(MENUSET2)
            
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
            uiprint(ui.basic_menuarr[MENUSET2])
            display_basic_menu(MENUSET2)
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
            uiprint(ui.basic_menuarr[MENUSET2])
            display_basic_menu(MENUSET2)
            
            while enter_pin.value():
                time.sleep_ms(50)
            return
    pass

def menuexit(tim0):
    global EXIT_STATE
    EXIT_STATE = 1
    
def basic_menu():
    global EXIT_STATE, MENUSET2
    
    tim0.init(period=30000,mode=Timer.ONE_SHOT,callback=menuexit)
    uiprint(ui.basic_menuarr[MENUSET2])
    display_basic_menu(MENUSET2)
    while enter_pin.value():
        time.sleep_ms(50)
    
    while True:
        if EXIT_STATE:
            EXIT_STATE = 0
            return
        
        if menu_pin.value():
            tim0.deinit()
            tim0.init(period=30000,mode=Timer.ONE_SHOT,callback=menuexit)
            uiprint(ui.menuarr[MENUSET1])
            display_menu(MENUSET1)
            while enter_pin.value():
                time.sleep_ms(50)
            return
        
        if up_pin.value():
            tim0.deinit()
            tim0.init(period=30000,mode=Timer.ONE_SHOT,callback=menuexit)
            time.sleep_ms(30)
            
            if MENUSET2 == 0:
                MENUSET2 = 2
                pass
            else:
                MENUSET2 = MENUSET2 - 1
                
            while up_pin.value():
                time.sleep_ms(30)
            uiprint(ui.basic_menuarr[MENUSET2])
            display_selector(MENUSET2)
        
        if down_pin.value():
            tim0.deinit()
            tim0.init(period=30000,mode=Timer.ONE_SHOT,callback=menuexit)
            time.sleep_ms(30)
            
            if MENUSET2 == 2:
                MENUSET2 = 0
            else:
                MENUSET2 = MENUSET2 + 1
            
            while down_pin.value():
                time.sleep_ms(30)
            uiprint(ui.basic_menuarr[MENUSET2])
            display_selector(MENUSET2)
        
        if enter_pin.value():
            tim0.deinit()
            tim0.init(period=30000,mode=Timer.ONE_SHOT,callback=menuexit)
            time.sleep_ms(30)
            
            if MENUSET2 == 0:
                setting_power_save_mode()
            if MENUSET2 == 1:
                setting_update_speed()
            if MENUSET2 == 2:
                setting_clock_show()
    pass

def recovery():
    global EXIT_STATE
    tim0.init(period=30000,mode=Timer.ONE_SHOT,callback=menuexit)
    selector = 0
    uiprint("Clean Data?")
    uiprint(ui.tfarr[selector])
    display_recovery(selector)
    while enter_pin.value():
        time.sleep_ms(50)
        
    while True:
        if EXIT_STATE:
            EXIT_STATE = 0
            return
        
        if menu_pin.value():
            tim0.deinit()
            tim0.init(period=30000,mode=Timer.ONE_SHOT,callback=menuexit)
            uiprint(ui.other_menuarr[MENUSET3])
            display_other_menu(MENUSET3)
            while menu_pin.value():
                time.sleep_ms(50)
            return

        if up_pin.value() or down_pin.value():
            tim0.deinit()
            tim0.init(period=30000,mode=Timer.ONE_SHOT,callback=menuexit)
            
            time.sleep_ms(30)
            selector = not selector
            uiprint(ui.tfarr[selector])
            display_recovery(selector)
            
            while up_pin.value() or down_pin.value():
                time.sleep_ms(30)

        if enter_pin.value():
            tim0.deinit()
            tim0.init(period=30000,mode=Timer.ONE_SHOT,callback=menuexit)
            
            if selector == 0:
                import os
                os.remove(config.json)
                ################################################################
                uiprint("Success!Please Restart the device")
            if selector == 1:
                display_other_menu(MENUSET3)
                while enter_pin.value():
                    time.sleep_ms(50)
            return
    pass

def other_menu():
    global EXIT_STATE, MENUSET3

    tim0.init(period=30000,mode=Timer.ONE_SHOT,callback=menuexit)
    uiprint(ui.other_menuarr[MENUSET3])
    display_other_menu(MENUSET3)
    while enter_pin.value():
        time.sleep_ms(50)

    while True:
        if EXIT_STATE:
            EXIT_STATE = 0
            return

        if menu_pin.value():
            tim0.deinit()
            tim0.init(period=30000,mode=Timer.ONE_SHOT,callback=menuexit)
            uiprint(ui.menuarr[MENUSET1])
            display_menu(MENUSET1)
            while menu_pin.value():
                time.sleep_ms(50)
            return
            break
        
        if up_pin.value():
            tim0.deinit()
            tim0.init(period=30000,mode=Timer.ONE_SHOT,callback=menuexit)
            time.sleep_ms(30)
            
            if MENUSET3 == 0:
                MENUSET3 = 0
                pass
            else:
                MENUSET3 = MENUSET3 - 1
                
            while up_pin.value():
                time.sleep_ms(30)
            uiprint(ui.basic_menuarr[MENUSET3])
            display_selector(MENUSET3)

        if down_pin.value():
            tim0.deinit()
            tim0.init(period=30000,mode=Timer.ONE_SHOT,callback=menuexit)
            time.sleep_ms(30)
            
            if MENUSET3 == 0:
                MENUSET3 = 0
                pass
            else:
                MENUSET3 = MENUSET3 + 1
                
            while up_pin.value():
                time.sleep_ms(30)
            uiprint(ui.basic_menuarr[MENUSET3])
            display_selector(MENUSET3)

        if enter_pin.value():
            tim0.deinit()
            tim0.init(period=30000,mode=Timer.ONE_SHOT,callback=menuexit)
            time.sleep_ms(10)
            
            if MENUSET3 == 0:
                recovery()
    pass

def start_menu():
    global EXIT_STATE, MENUSET1
    
    tim0.init(period=30000,mode=Timer.ONE_SHOT,callback=menuexit)
    uiprint(ui.menuarr[MENUSET1])
    display_menu(MENUSET1)
    while menu_pin.value():
        time.sleep_ms(50)
    
    while True:
        if EXIT_STATE:
            EXIT_STATE = 0
            return

        if menu_pin.value():
            tim0.deinit()
            break
        
        if up_pin.value():
            tim0.deinit()
            tim0.init(period=30000,mode=Timer.ONE_SHOT,callback=menuexit)
            time.sleep_ms(30)
            
            if MENUSET1 == 0:
                MENUSET1 = 1
                pass
            else:
                MENUSET1 = MENUSET1 - 1
                
            while up_pin.value():
                time.sleep_ms(30)
            uiprint(ui.menuarr[MENUSET1])
            display_selector(MENUSET1)

        if down_pin.value():
            tim0.deinit()
            tim0.init(period=30000,mode=Timer.ONE_SHOT,callback=menuexit)
            time.sleep_ms(30)
            
            if MENUSET1 == 1:
                MENUSET1 = 0
                pass
            else:
                MENUSET1 = MENUSET1 + 1
                
            while up_pin.value():
                time.sleep_ms(30)
            uiprint(ui.menuarr[MENUSET1])
            display_selector(MENUSET1)

        if enter_pin.value():
            tim0.deinit()
            tim0.init(period=30000,mode=Timer.ONE_SHOT,callback=menuexit)
            time.sleep_ms(30)
            
            if MENUSET1 == 0:
                basic_menu()
            if MENUSET1 == 1:
                other_menu()