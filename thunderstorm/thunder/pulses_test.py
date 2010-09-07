# -*- coding: utf-8 -*-

# Copyright (C) 2010 Trémouilles David

#This file is part of Thunderstorm.
#
#ThunderStrom is free software: you can redistribute it and/or modify
#it under the terms of the GNU Lesser General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#ThunderStorm is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU Lesser General Public License for more details.
#
#You should have received a copy of the GNU Lesser General Public License
#along with ThunderStorm.  If not, see <http://www.gnu.org/licenses/>.

"""
Testing pulses_dev.py
"""

from __future__ import division
from thunderstorm.thunder.pulses import *
import numpy as np


def test():
    test_pulse_set_time = TimePulseSet()
    print test_pulse_set_time.pulses_nb
    print test_pulse_set_time.pulses_length
    print "PulseSetTime() Ok"

    test_pulse_set_freq = FreqPulseSet()
    print test_pulse_set_freq.pulses_nb
    print test_pulse_set_freq.pulses_length
    print "PulseSetFreq() Ok"

    test_pulse_set_time_iv = IVTime()
    print test_pulse_set_time_iv.pulses_nb
    print test_pulse_set_time_iv.pulses_length
    print "IVTime() Ok"

    test_pulse_set_freq_iv = IVFreq()
    print test_pulse_set_freq_iv.pulses_nb
    print test_pulse_set_freq_iv.pulses_length
    print "IVFreq() Ok"

    test_pulse_set_time_vincref = VIncRefTime()
    print test_pulse_set_time_vincref.pulses_nb
    print test_pulse_set_time_vincref.pulses_length
    print "VIncRefTime() Ok"

    test_pulse_set_freq_vincref = VIncRefFreq()
    print test_pulse_set_freq_vincref.pulses_nb
    print test_pulse_set_freq_vincref.pulses_length
    print "VIncRefFreq() Ok"

    test_pulse_set_time_ab = ABTime()
    print test_pulse_set_time_ab.pulses_nb
    print test_pulse_set_time_ab.pulses_length
    print "ABTime() Ok"

    test_pulse_set_freq_ab = ABFreq()
    print test_pulse_set_freq_ab.pulses_nb
    print test_pulse_set_freq_ab.pulses_length
    print "ABFreq() Ok"

def testpulse(pulse_time):
    pulse_freq = pulse_time.to_freq
    back_time = pulse_freq.to_time
    import matplotlib.pyplot  as plt
    time_error = pulse_time.delta_t - back_time.delta_t
    print pulse_time.delta_t
    print back_time.delta_t
    print "time error = " + str(time_error)
    plt.figure()
    plt.plot
    plt.plot(pulse_time.current[0])
    plt.plot(back_time.current[0])
    plt.figure()
    print "delta_f = " + str(pulse_freq.delta_f)
    plt.plot(np.absolute(pulse_freq.current[0]))
    plt.show()

def testIV():
    size = 2**5 +1
    pulse_time = IVTime(size)
    pulse_time.current[0][:] = np.sin(np.arange(size)/2.0)
    pulse_time.voltage[0][:] = np.arange(size)*(-0.1)
    pulse_time.delta_t = 0.4e-9
    #pulse_time.time[:] = np.arange(size)*0.4e-9
    testpulse(pulse_time)

def testVIncRef():
    size = 2**9
    pulse_time = VIncRefTime(size)
    pulse_time.v_inc[0][:] = np.sin(num.arange(size)/2.0)
    pulse_time.v_ref[0][:] = np.arange(size) * (-0.1)
    pulse_time.time[:] = np.arange(size) * 0.4e-9
    testpulse(pulse_time)

def testab():
    size = 2**9
    pulse_time = ABTime(size)
    pulse_time.a[0][:] = np.sin(np.arange(size)/2.0)
    pulse_time.b[0][:] = np.arange(size) * (-0.1)
    pulse_time.time[:] = np.arange(size) * 0.4e-9
    testpulse(pulse_time)

def main():
    print "Module test"
    test()
    testIV()
    testVIncRef()
    testab()

    raw_input ("Press enter to end")

if __name__ == "__main__":
    main()
