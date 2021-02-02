#!/usr/bin/env python3

import pigpio
import time

PWM_FREQ = 50
DUTY_PP_DOWN       =  35000
DUTY_PP_UP         =  75000
DUTY_TEST          =  90000
DUTY_ALARM_RELEASE = 110000

class TouchProbe:
    def __init__(self, gpio_hw_pwm, gpio_sw):
        self.__gpio_hw_pwm = gpio_hw_pwm
        self.__gpio_sw = gpio_sw

        self.__pi = pigpio.pi()

        self.__pi.set_mode(self.__gpio_hw_pwm, pigpio.OUTPUT)

        self.__pi.set_mode(self.__gpio_sw, pigpio.INPUT)
        self.__pi.set_pull_up_down(self.__gpio_sw, pigpio.PUD_UP)
        self.__pi.callback(self.__gpio_sw, pigpio.FALLING_EDGE, self.__callback_sw)

        self.reset_touched()

    def reset_touched(self):
        self.__touched = False

    @property
    def is_touched(self):
        return self.__touched

    def __callback_sw(self, gpio, level, tick):
        if not self.__touched:
            self.pp_up()
            self.__touched = True

    def pp_down(self):
        self.__pi.hardware_PWM(self.__gpio_hw_pwm, PWM_FREQ, DUTY_PP_DOWN)

    def pp_up(self):
        self.__pi.hardware_PWM(self.__gpio_hw_pwm, PWM_FREQ, DUTY_PP_UP)

    def test(self):
        self.__pi.hardware_PWM(self.__gpio_hw_pwm, PWM_FREQ, DUTY_TEST)

    def alarm_release(self):
        self.__pi.hardware_PWM(self.__gpio_hw_pwm, PWM_FREQ, DUTY_ALARM_RELEASE)

    def wait_touched(self):
        self.reset_touched()

        for i in range(5):
            pp_action = self.pp_down if i % 2 == 0 else self.pp_up
            pp_action()
            time.sleep(0.5)
        while True:
            if self.is_touched:
                break
            time.sleep(1)
