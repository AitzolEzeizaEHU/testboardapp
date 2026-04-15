import logging
import os
import time

from flask import Flask, jsonify, render_template
import Adafruit_ADS1x15
from gpiozero import Button, LED

from PMODKYPDTest import PMODKeypad, disable_spi


app = Flask(__name__)
logger = logging.getLogger(__name__)

GAIN = 1
VOLTAGE_RANGE = 4.096
RESOLUTION = VOLTAGE_RANGE / 32768
KEYPAD_MAP = {
    'A': 10,
    'B': 11,
    'C': 12,
    'D': 13,
    'E': 14,
    'F': 15,
    '0': 16,
}
OUTPUT_PIN_IDS = [12, 13, 24, 17, 27, 22, 5]
INPUT_PIN_IDS = [14, 15]
KEYPAD_COLS = [11, 9, 10, 8]
KEYPAD_ROWS = [18, 20, 21, 19]

adc = None
keypad = None
output_pins = {}
input_pins = {}


def initialize_hardware():
    global adc, keypad, output_pins, input_pins

    try:
        disable_spi()
        time.sleep(1)
    except Exception as exc:
        logger.warning("SPI disable step failed: %s", exc)

    try:
        adc = Adafruit_ADS1x15.ADS1115(address=0x48, busnum=1)
        logger.info("ADC initialized")
    except Exception as exc:
        adc = None
        logger.exception("ADC initialization failed: %s", exc)

    try:
        keypad = PMODKeypad(KEYPAD_ROWS, KEYPAD_COLS)
        logger.info("Keypad initialized")
    except Exception as exc:
        keypad = None
        logger.exception("Keypad initialization failed: %s", exc)

    output_pins = {}
    for pin in OUTPUT_PIN_IDS:
        try:
            output_pins[pin] = LED(pin)
        except Exception as exc:
            logger.exception("Output pin %s init failed: %s", pin, exc)

    input_pins = {}
    for pin in INPUT_PIN_IDS:
        try:
            input_pins[pin] = Button(pin)
        except Exception as exc:
            logger.exception("Input pin %s init failed: %s", pin, exc)


def get_pressed_button():
    if keypad is None:
        return 0

    try:
        key = keypad.get_key()
    except Exception as exc:
        logger.exception("Failed reading keypad state: %s", exc)
        return 0

    if not key:
        return 0

    if key in KEYPAD_MAP:
        return KEYPAD_MAP[key]

    try:
        return int(key)
    except ValueError:
        logger.warning("Received unknown keypad value: %s", key)
        return 0


def get_analog_values():
    if adc is None:
        return {"analog0": None, "analog1": None, "analog2": None, "analog3": None}

    values = [0]*4
    for i in range(4):
        try:
            raw_value = adc.read_adc(i, gain=GAIN)
            values[i] = raw_value * RESOLUTION
        except Exception as exc:
            logger.exception("Failed reading ADC channel %s: %s", i, exc)
            values[i] = None
    return {
        "analog0": values[0],
        "analog1": values[1],
        "analog2": values[2],
        "analog3": values[3],
    }


def get_matrix_state():
    matrix_state = {f'btn{i}': False for i in range(1, 17)}
    pressed_button = get_pressed_button()
    if pressed_button != 0:
        matrix_state[f'btn{pressed_button}'] = True
    return matrix_state


def get_input_state(pin):
    if pin not in input_pins:
        return None

    pressed = bool(input_pins[pin].is_pressed)
    active = not pressed
    return {
        'pressed': pressed,
        'active': active,
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/toggle/<int:pin>', methods=['POST'])
def toggle(pin):
    if pin in output_pins:
        output_pins[pin].toggle()
        return jsonify({'status': 'success', 'pin': pin, 'state': output_pins[pin].is_lit})
    return jsonify({'status': 'error', 'message': 'Invalid pin'}), 400

@app.route('/states/<int:pin>', methods=['GET'])
def states(pin):
    state = get_input_state(pin)
    if state is not None:
        return jsonify({'status': 'success', 'pin': pin, 'state': state['active'], 'pressed': state['pressed']}), 200
    return jsonify({'status': 'error', 'message': 'Invalid pin'}), 400


@app.route('/healthz', methods=['GET'])
def healthz():
    hardware = {
        'adc': adc is not None,
        'keypad': keypad is not None,
        'output_pins_ready': sorted(output_pins.keys()),
        'input_pins_ready': sorted(input_pins.keys()),
    }

    return jsonify(
        {
            'status': 'ok',
            'outputs': sorted(output_pins.keys()),
            'inputs': sorted(input_pins.keys()),
            'hardware': hardware,
        }
    ), 200

@app.route('/matrix_states', methods=['GET'])
def matrix_states():
    raw_state = get_matrix_state()
    matrix_state = {
        key: ("Pressed" if value else "Released")
        for key, value in raw_state.items()
    }
    return jsonify(matrix_state)

@app.route('/analog_values', methods=['GET'])
def analog_values():
    values = get_analog_values()
    return jsonify(values)


@app.route('/status', methods=['GET'])
def status():
    inputs = {}
    for pin in INPUT_PIN_IDS:
        pin_state = get_input_state(pin)
        inputs[str(pin)] = pin_state

    return jsonify(
        {
            'status': 'success',
            'inputs': inputs,
            'matrix': get_matrix_state(),
            'analog': get_analog_values(),
            'outputs': {
                str(pin): output_pins[pin].is_lit
                for pin in sorted(output_pins.keys())
            },
        }
    )

if __name__ == '__main__':
    logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO').upper())
    initialize_hardware()
    app.run(
        host=os.getenv('TESTBOARD_HOST', '0.0.0.0'),
        port=int(os.getenv('TESTBOARD_PORT', '5000')),
        debug=os.getenv('TESTBOARD_DEBUG', 'false').lower() == 'true',
    )