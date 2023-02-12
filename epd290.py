# *****************************************************************************
# * | File        :	  Pico_ePaper-2.9.py
# * | Author      :   Waveshare team
# * | Function    :   Electronic paper driver
# * | Info        :
# *----------------
# * | This version:   V1.0
# * | Date        :   2021-03-16
# # | Info        :   python demo
# -----------------------------------------------------------------------------
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from machine import Pin, SPI
import framebuf
import utime

# Display resolution
EPD_WIDTH       = 128
EPD_HEIGHT      = 296

RST_PIN         = 19
DC_PIN          = 18
CS_PIN          = 15
BUSY_PIN        = 17


class EPD_2in9_Portrait(framebuf.FrameBuffer):
    def __init__(self):
        self.reset_pin = Pin(RST_PIN, Pin.OUT)
        
        self.busy_pin = Pin(BUSY_PIN, Pin.IN, Pin.PULL_UP)
        self.cs_pin = Pin(CS_PIN, Pin.OUT)
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
        
        lut_full_update = [
            0x50, 0xAA, 0x55, 0xAA, 0x11, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0xFF, 0xFF, 0x1F, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00
        ]

        lut_partial_update  = [
            0x10, 0x18, 0x18, 0x08, 0x18, 0x18,
            0x08, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x13, 0x14, 0x44, 0x12,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00
        ]
        
        self.lut = lut_partial_update
        
        self.spi = SPI(1)
        self.spi.init(baudrate=4000_000)
        self.dc_pin = Pin(DC_PIN, Pin.OUT)
        
        self.buffer = bytearray(self.height * self.width // 8)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_HLSB)
        self.init()

    def digital_write(self, pin, value):
        pin.value(value)

    def digital_read(self, pin):
        return pin.value()

    def delay_ms(self, delaytime):
        utime.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data):
        self.spi.write(bytearray(data))

    def module_exit(self):
        self.digital_write(self.reset_pin, 0)

    # Hardware reset
    def reset(self):
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(200) 
        self.digital_write(self.reset_pin, 0)
        self.delay_ms(2)
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(200)   

    def send_command(self, command):
        self.digital_write(self.dc_pin, 0)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([command])
        self.digital_write(self.cs_pin, 1)

    def send_data(self, data):
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([data])
        self.digital_write(self.cs_pin, 1)
        
    def ReadBusy(self):
        print("e-Paper busy")
        while(self.digital_read(self.busy_pin) == 1):      #  0: idle, 1: busy
            self.delay_ms(10) 
        print("e-Paper busy release")  

    def TurnOnDisplay(self):
        self.send_command(0x22) # DISPLAY_UPDATE_CONTROL_2
        self.send_data(0xC4)
        self.send_command(0x20)	# MASTER_ACTIVATION
        self.send_command(0xFF)	# TERMINATE_FRAME_READ_WRITE
        
        self.ReadBusy()

    def SendLut(self):
        self.send_command(0x32)
        for i in range(0, len(self.lut)):
            self.send_data(self.lut[i])
        self.ReadBusy()

    def SetWindow(self, x_start, y_start, x_end, y_end):
        self.send_command(0x44) # SET_RAM_X_ADDRESS_START_END_POSITION
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        self.send_data((x_start>>3) & 0xFF)
        self.send_data((x_end>>3) & 0xFF)
        self.send_command(0x45) # SET_RAM_Y_ADDRESS_START_END_POSITION
        self.send_data(y_start & 0xFF)
        self.send_data((y_start >> 8) & 0xFF)
        self.send_data(y_end & 0xFF)
        self.send_data((y_end >> 8) & 0xFF)

    def SetCursor(self, x, y):
        self.send_command(0x4E) # SET_RAM_X_ADDRESS_COUNTER
        self.send_data(x & 0xFF)
        
        self.send_command(0x4F) # SET_RAM_Y_ADDRESS_COUNTER
        self.send_data(y & 0xFF)
        self.send_data((y >> 8) & 0xFF)
        self.ReadBusy()
        
    def init(self):
        # EPD hardware init start     
        self.reset()

        self.ReadBusy()   
        self.send_command(0x01) # DRIVER_OUTPUT_CONTROL
        self.send_data((EPD_HEIGHT - 1) & 0xFF)
        self.send_data(((EPD_HEIGHT - 1) >> 8) & 0xFF)
        self.send_data(0x00) # GD = 0 SM = 0 TB = 0
        
        self.send_command(0x0C) # BOOSTER_SOFT_START_CONTROL 
        self.send_data(0xD7)
        self.send_data(0xD6)
        self.send_data(0x9D)
        
        self.send_command(0x2C) # WRITE_VCOM_REGISTER
        self.send_data(0xA8) # VCOM 7C
        
        self.send_command(0x3A) # SET_DUMMY_LINE_PERIOD
        self.send_data(0x1A) # 4 dummy lines per gate
        
        self.send_command(0x3B) # SET_GATE_TIME
        self.send_data(0x08) # 2us per line
        
        self.send_command(0x11) # DATA_ENTRY_MODE_SETTING
        self.send_data(0x03) # X increment Y increment
        self.ReadBusy()
        self.SendLut()
        # EPD hardware init end
        return 0

    def display(self, image):
        if (image == None):
            return
        self.SetWindow(0, 0, self.width - 1, self.height - 1)
        for j in range(0, self.height):
            self.SetCursor(0, j)
            self.send_command(0x24)
            for i in range(0, int(self.width / 8)):
                self.send_data(image[i + j * int(self.width / 8)])   
        self.TurnOnDisplay()
        
    def Clear(self, color):
        self.SetWindow(0, 0, self.width - 1, self.height - 1)
        for j in range(0, self.height):
            self.SetCursor(0, j)
            self.send_command(0x24) # WRITE_RAM
            for i in range(0, int(self.width / 8)):
                self.send_data(color)   
        self.TurnOnDisplay()

    def sleep(self):
        self.send_command(0x10) # DEEP_SLEEP_MODE
        self.send_data(0x01)
        
        self.delay_ms(2000)
        self.module_exit()
        

if __name__=='__main__':
    # Landscape
    epd = EPD_2in9_Landscape()
    epd.Clear(0xff)
    
    epd.fill(0xff)
    epd.text("Waveshare", 5, 10, 0x00)
    epd.text("Pico_ePaper-2.9", 5, 20, 0x00)
    epd.text("Raspberry Pico", 5, 30, 0x00)
    epd.display(epd.buffer)
    epd.delay_ms(2000)
    
    epd.vline(10, 40, 60, 0x00)
    epd.vline(120, 40, 60, 0x00)
    epd.hline(10, 40, 110, 0x00)
    epd.hline(10, 100, 110, 0x00)
    epd.line(10, 40, 120, 100, 0x00)
    epd.line(120, 40, 10, 100, 0x00)
    epd.display(epd.buffer)
    epd.delay_ms(2000)
    
    epd.rect(150, 5, 50, 55, 0x00)
    epd.fill_rect(150, 65, 50, 115, 0x00)
    epd.display_Base(epd.buffer)
    epd.delay_ms(2000)
    
    for i in range(0, 10):
        epd.fill_rect(220, 60, 10, 10, 0xff)
        epd.text(str(i), 222, 62, 0x00)
        epd.display_Partial(epd.buffer)

    # Portrait
    epd = EPD_2in9_Portrait()
    epd.Clear(0xff)
    
    epd.fill(0xff)
    epd.text("Waveshare", 5, 10, 0x00)
    epd.text("Pico_ePaper-2.9", 5, 40, 0x00)
    epd.text("Raspberry Pico", 5, 70, 0x00)
    epd.display(epd.buffer)
    epd.delay_ms(2000)
    
    epd.vline(10, 90, 60, 0x00)
    epd.vline(120, 90, 60, 0x00)
    epd.hline(10, 90, 110, 0x00)
    epd.hline(10, 150, 110, 0x00)
    epd.line(10, 90, 120, 150, 0x00)
    epd.line(120, 90, 10, 150, 0x00)
    epd.display(epd.buffer)
    epd.delay_ms(2000)
    
    epd.rect(10, 180, 50, 80, 0x00)
    epd.fill_rect(70, 180, 50, 80, 0x00)
    epd.display_Base(epd.buffer)
    epd.delay_ms(2000)
    
    for i in range(0, 10):
        epd.fill_rect(40, 270, 40, 10, 0xff)
        epd.text(str(i), 60, 270, 0x00)
        epd.display_Partial(epd.buffer)

    epd.init()
    epd.Clear(0xff)
    epd.delay_ms(2000)
    print("sleep")
    epd.sleep()