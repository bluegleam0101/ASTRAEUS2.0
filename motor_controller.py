from RpiMotorLib import RpiMotorLib


class AltitudeMotor:
    def __init__(self, rpimotor_object, steps_360, gpiopins=None, inv=False, wait=0.003, gear_ratio=1, steptype="full", rpimotorlib_oddity=False):
        """
        please provide gear ratio as a float corresponding to
        the amount of times to motor has to turn 360° to fully
        rotate to telescope once.

        the steps_360 parameter asks for the amount of steps your stepper motor has to turn to turn 360° in full step mode
        """
        self.oddity = rpimotorlib_oddity
        self.gpiopins = gpiopins
        self.steps_360 = steps_360
        self.gear_ratio = gear_ratio
        self.current_position = 0.0
        self.rpimotor_object = rpimotor_object
        self.clockwise = False
        self.degrees_to_turn = 0
        self.steps = 0
        self.inv = inv

    def align_altitude(self, target_alt):
        # finding delta degrees
        a = float(target_alt) - self.current_position
        a = (a + 180) % 360 - 180
        self.degrees_to_turn = a

        self.steps = int(((a / 360) * self.steps_360) * self.gear_ratio)
        print(self.degrees_to_turn)
        #determining direction
        if self.degrees_to_turn < 0:
            self.clockwise = False
        if self.inv:
            self.clockwise = not self.clockwise
        if self.oddity:
            self.clockwise = not self.clockwise

        self.rpimotor_object.motor_run(self,
                                       gpiopins=self.gpiopins,
                                       wait=.001,
                                       steps=self.steps,
                                       ccwise=self.clockwise,
                                       verbose=False, steptype="half", initdelay=.001
                                       )


class AzimuthMotor:
    def __init__(self, rpimotor_object, steps_360, gpiopins=None, inv=False, wait=0.003, gear_ratio=1, steptype="full", rpimotorlib_discrepancy=False):
        """
        please provide gear ratio as a float corresponding to
        the amount of times to motor has to turn 360° to fully
        rotate to telescope once.

        the steps_360 parameter asks for the amount of steps your stepper motor has to turn to turn 360° in full step mode
        """
        self.oddity = rpimotorlib_discrepancy
        self.inv = inv
        self.steps_360 = steps_360
        self.gear_ratio = gear_ratio
        self.current_position = 0.0
        self.rpimotor_object = rpimotor_object
        self.clockwise = False
        self.degrees_to_turn = None
        self.steps = None

    def align_azimuth(self, target_az):
        # finding delta degrees
        a = float(target_az) - self.current_position
        a = (a + 180) % 360 - 180
        self.degrees_to_turn = abs(a)
        self.steps = abs(int(((a / 360) * self.steps_360) * self.gear_ratio))
        print(self.degrees_to_turn)
        # determining direction
        if self.degrees_to_turn < 0:
            self.clockwise = False
        if self.inv:
            self.clockwise = not self.clockwise
        if self.oddity:
            self.clockwise = not self.clockwise

        self.rpimotor_object.motor_go(clockwise=self.clockwise, steptype="Full", steps=self.steps, stepdelay=.005,
                                      initdelay=0.1)


class TelescopeMotorController():
    def __init__(self, alt_motor, az_motor):
        self.az_motor = az_motor
        self.alt_motor = alt_motor

        # self.rpimotor_object()

###########################s
# Actual motor control

# GPIO.setmode(GPIO.BOARD)
# GPIO.setup(EN_pin, GPIO.OUT)
# x = 0
# for i in range(0,2):
#    GPIO.output(EN_pin, GPIO.LOW)  #s pull enable to low to enable motor
#   mymotortest.motor_go(False,  # True=Clockwise, False=Counter-Clockwise
#                          "Full",  # Step type (Full,Half,1/4,1/8,1/16,1/32)
#                         200,  # number of steps
#                        .0005,  # step delay [sec]
#                       False,  # True = print verbose output
#                      .05)  # initial delay [sec]
# time.sleep(5)


# GPIO.cleanup()  # clear GPIO allocations after run
# skskksksksk
