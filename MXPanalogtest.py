import time
import Adafruit_ADS1x15

# Create an ADS1115 ADC (16-bit) instance on I2C-1.
adc = Adafruit_ADS1x15.ADS1115(address=0x48, busnum=1)

# Choose a gain of 1 for reading voltages from 0 to 4.09V.
GAIN = 1

# ADS1115 full-scale range for gain=1 is ±4.096V, so the resolution is 4.096V / 32768
VOLTAGE_RANGE = 4.096
RESOLUTION = VOLTAGE_RANGE / 32768

print('Reading ADS1115 values, press Ctrl-C to quit...')
print('| {0:>10} | {1:>10} | {2:>10} | {3:>10} |'.format('Channel 0 (V)', 'Channel 1 (V)', 'Channel 2 (V)', 'Channel 3 (V)'))
print('-' * 49)

# Main loop.
while True:
    # Read all the ADC channel values in a list.
    values = [0]*4
    for i in range(4):
        # Read the specified ADC channel using the previously set gain value.
        raw_value = adc.read_adc(i, gain=GAIN)
        # Convert raw ADC value to voltage.
        values[i] = raw_value * RESOLUTION
    # Print the voltage values.
    print('| {0:>10.4f} | {1:>10.4f} | {2:>10.4f} | {3:>10.4f} |'.format(*values))
    # Pause for one second.
    time.sleep(1)