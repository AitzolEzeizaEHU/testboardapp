import time
from gpiozero import Button, LED

import os

# To disable SPI
def disable_spi():
    os.system("sudo raspi-config nonint do_spi 1")

# To reenable SPI
def reenable_spi():
    os.system("sudo raspi-config nonint do_spi 0")

class PMODKeypad:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.keys = [
            ['1', '2', '3', 'A'],
            ['4', '5', '6', 'B'],
            ['7', '8', '9', 'C'],
            ['0', 'F', 'E', 'D'],
        ]
        
        self.row_pins = [Button(pin) for pin in self.rows]
        self.col_pins = [LED(pin, initial_value=True) for pin in self.cols]

    def get_key(self):
        for col_index, col_pin in enumerate(self.col_pins):
            col_pin.off()
            for row_index, row_pin in enumerate(self.row_pins):
                if row_pin.is_pressed:
                    col_pin.on()
                    return self.keys[row_index][col_index]
            col_pin.on()
        return None

def main():
    disable_spi() # Call this function to disable SPI
    time.sleep(1)
    
    cols = [11, 9, 10, 8]
    rows = [18, 20, 21, 19]
    keypad = PMODKeypad(rows, cols)
    
    try:
        while True:
            key = keypad.get_key()
            if key:
                print(f"Key pressed: {key}")
                while keypad.get_key() == key:
                    pass
            time.sleep(0.1)
    except KeyboardInterrupt:
        reenable_spi()  # Call this function to enable SPI again
        print("Program terminated.")


if __name__ == "__main__":
    main()
