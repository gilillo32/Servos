# PCA9685.py
# 2016-01-31
# Public Domain

import time

import pigpio


class PWM:
    """
   This class provides an interface to the I2C PCA9685 PWM chip.

   The chip provides 16 PWM channels.

   All channels use the same frequency which may be set in the
   range 24 to 1526 Hz.

   If used to drive servos the frequency should normally be set
   in the range 50 to 60 Hz.

   The duty cycle for each channel may be independently set
   between 0 and 100%.

   It is also possible to specify the desired pulse width in
   microseconds rather than the duty cycle.  This may be more
   convenient when the chip is used to drive servos.

   The chip has 12 bit resolution, i.e. there are 4096 steps
   between off and full on.
   """

    _MODE1 = 0x00
    _MODE2 = 0x01
    _SUBADR1 = 0x02
    _SUBADR2 = 0x03
    _SUBADR3 = 0x04
    _PRESCALE = 0xFE
    _LED0_ON_L = 0x06
    _LED0_ON_H = 0x07
    _LED0_OFF_L = 0x08
    _LED0_OFF_H = 0x09
    _ALL_LED_ON_L = 0xFA
    _ALL_LED_ON_H = 0xFB
    _ALL_LED_OFF_L = 0xFC
    _ALL_LED_OFF_H = 0xFD

    _RESTART = 1 << 7
    _AI = 1 << 5
    _SLEEP = 1 << 4
    _ALLCALL = 1 << 0

    _OCH = 1 << 3
    _OUTDRV = 1 << 2

    def __init__(self, pi, bus=1, address=0x40):

        self.pi = pi
        self.bus = bus
        self.address = address

        self.h = pi.i2c_open(bus, address)

        self._write_reg(self._MODE1, self._AI | self._ALLCALL)
        self._write_reg(self._MODE2, self._OCH | self._OUTDRV)

        time.sleep(0.0005)

        mode = self._read_reg(self._MODE1)
        self._write_reg(self._MODE1, mode & ~self._SLEEP)

        time.sleep(0.0005)

        self.set_duty_cycle(-1, 0)
        self.set_frequency(200)

    def get_frequency(self):

        "Returns the PWM frequency."

        return self._frequency

    def set_frequency(self, frequency):

        "Sets the PWM frequency."

        prescale = int(round(25000000.0 / (4096.0 * frequency)) - 1)

        if prescale < 3:
            prescale = 3
        elif prescale > 255:
            prescale = 255

        mode = self._read_reg(self._MODE1);
        self._write_reg(self._MODE1, (mode & ~self._SLEEP) | self._SLEEP)
        self._write_reg(self._PRESCALE, prescale)
        self._write_reg(self._MODE1, mode)

        time.sleep(0.0005)

        self._write_reg(self._MODE1, mode | self._RESTART)

        self._frequency = (25000000.0 / 4096.0) / (prescale + 1)
        self._pulse_width = (1000000.0 / self._frequency)

    def set_duty_cycle(self, channel, percent):

        "Sets the duty cycle for a channel.  Use -1 for all channels."

        steps = int(round(percent * (4096.0 / 100.0)))

        if steps < 0:
            on = 0
            off = 4096
        elif steps > 4095:
            on = 4096
            off = 0
        else:
            on = 0
            off = steps

        if (channel >= 0) and (channel <= 15):
            self.pi.i2c_write_i2c_block_data(self.h, self._LED0_ON_L + 4 * channel,
                                             [on & 0xFF, on >> 8, off & 0xFF, off >> 8])

        else:
            self.pi.i2c_write_i2c_block_data(self.h, self._ALL_LED_ON_L,
                                             [on & 0xFF, on >> 8, off & 0xFF, off >> 8])

    def set_pulse_width(self, channel, width):

        "Sets the pulse width for a channel.  Use -1 for all channels."

        self.set_duty_cycle(channel, (float(width) / self._pulse_width) * 100.0)

    def cancel(self):

        "Switches all PWM channels off and releases resources."

        self.set_duty_cycle(-1, 0)
        self.pi.i2c_close(self.h)

    def _write_reg(self, reg, byte):
        self.pi.i2c_write_byte_data(self.h, reg, byte)

    def _read_reg(self, reg):
        return self.pi.i2c_read_byte_data(self.h, reg)


if __name__ == "__main__":

    import time

    import pigpio

    pi = pigpio.pi()

    if not pi.connected:
        exit(0)

    pwm = PWM(pi)  # defaults to bus 1, address 0x40

    pwm.set_frequency(50)  # suitable for servos

    # for dc in range(5, 11):
    # pwm.set_duty_cycle(-1, dc) # -1 for all channels
    # time.sleep(1)

    while True:
        pwm.set_pulse_width(0, 500)
        pwm.set_pulse_width(4, 500)
        time.sleep(0.5)

        pwm.set_pulse_width(0, 1000)
        pwm.set_pulse_width(4, 1000)
        time.sleep(0.5)

        pwm.set_pulse_width(0, 525)
        pwm.set_pulse_width(4, 525)
        time.sleep(0.5)

        pwm.set_pulse_width(0, 550)
        pwm.set_pulse_width(4, 600)
        time.sleep(0.5)

        pwm.set_pulse_width(0, 575)
        pwm.set_pulse_width(4, 600)
        time.sleep(0.5)

        pwm.set_pulse_width(0, 600)
        pwm.set_pulse_width(4, 700)
        time.sleep(0.5)

        pwm.set_pulse_width(0, 625)
        pwm.set_pulse_width(4, 800)
        time.sleep(0.5)

        pwm.set_pulse_width(0, 650)
        pwm.set_pulse_width(4, 900)
        time.sleep(0.5)

        pwm.set_pulse_width(0, 675)
        pwm.set_pulse_width(4, 1000)
        time.sleep(0.5)

        pwm.set_pulse_width(0, 700)
        pwm.set_pulse_width(4, 1100)
        time.sleep(0.5)

        pwm.set_pulse_width(0, 725)
        pwm.set_pulse_width(4, 1200)
        time.sleep(0.5)

        pwm.set_pulse_width(0, 775)
        pwm.set_pulse_width(4, 1300)
        time.sleep(0.5)

        pwm.set_pulse_width(0, 800)
        pwm.set_pulse_width(4, 1400)
        time.sleep(0.5)

        pwm.set_pulse_width(0, 825)
        pwm.set_pulse_width(4, 1500)
        time.sleep(0.5)

        pwm.set_pulse_width(0, 850)
        pwm.set_pulse_width(4, 1600)
        time.sleep(0.5)

        pwm.set_pulse_width(0, 900)
        pwm.set_pulse_width(4, 1700)
        time.sleep(0.5)

        pwm.set_pulse_width(0, 925)
        pwm.set_pulse_width(4, 1800)
        time.sleep(0.5)

        pwm.set_pulse_width(0, 950)
        pwm.set_pulse_width(4, 1900)
        time.sleep(0.5)

        pwm.set_pulse_width(0, 975)
        pwm.set_pulse_width(4, 2000)
        time.sleep(0.5)

        pwm.set_pulse_width(0, 1000)
        pwm.set_pulse_width(4, 2100)
        time.sleep(0.5)

        pwm.set_pulse_width(0, 500)
        pwm.set_pulse_width(4, 2200)
        time.sleep(0.5)

        pwm.set_pulse_width(0, 750)
        pwm.set_pulse_width(4, 2300)
        time.sleep(0.5)

        pwm.set_pulse_width(0, 900)
        pwm.set_pulse_width(4, 2400)
        time.sleep(0.5)

        pwm.set_pulse_width(0, 500)
        pwm.set_pulse_width(4, 2500)
        time.sleep(0.5)

        pwm.set_pulse_width(0, 1000)
        pwm.set_pulse_width(4, 1000)
        time.sleep(1)

        pwm.set_pulse_width(0, 500)
        pwm.set_pulse_width(4, 2200)
        time.sleep(0.5)

        pwm.set_pulse_width(0, 750)
        pwm.set_pulse_width(4, 2300)
        time.sleep(0.5)

        pwm.set_pulse_width(0, 900)
        pwm.set_pulse_width(4, 2400)
        time.sleep(0.5)

        pwm.set_pulse_width(0, 500)
        pwm.set_pulse_width(4, 2500)
        time.sleep(0.5)

        pwm.set_pulse_width(0, 1000)
        pwm.set_pulse_width(4, 1000)
        time.sleep(0.5)

        pwm.set_pulse_width(0, 600)
        pwm.set_pulse_width(4, 2000)
        time.sleep(0.5)

    pwm.cancel()

    pi.stop()
