import time

from RpiMotorLib import RpiMotorLib


alt_pins = (17, 18, 27, 22)
direction = 16
step = 23
EN_pin = 24


class AltitudeMotor:
    def __init__(self, rpimotor_object, gpiopins, steps_360, inv=False, wait=0.003, gear_ratio=1,
                 steptype="full"):
        '''
        please provide gear ratio as a float corresponding to
        the amount of times to motor has to turn 360° to fully
        rotate to telescope once.

        the steps_360 parameter asks for the amount of steps your stepper motor has to turn to turn 360° in full step mode
        '''

        self.current_position = 0.0
        self.rpimotor_object = rpimotor_object
        self.ccwise = False
        self.degrees_to_turn: float
        self.steps: int

        # self.altitude_motor = RpiMotorLib.BYJMotor()
        # self.altitude_motor.motor_run(gpiopins=alt_pins, wait=.003, steps=1536, ccwise=False,
        # verbose=False, steptype="full", initdelay=.001)
        def align_altitude():
            pass


class AzimuthMotor:
    def __init__(self, rpimotor_object, steps_360, inv=False, wait=0.003, gear_ratio=1, steptype="full"):
        '''
        please provide gear ratio as a float corresponding to
        the amount of times to motor has to turn 360° to fully
        rotate to telescope once.

        the steps_360 parameter asks for the amount of steps your stepper motor has to turn to turn 360° in full step mode
        '''

        self.current_position = 0.0
        self.rpimotor_object = rpimotor_object
        self.clockwise = False
        self.degrees_to_turn: float
        self.steps: int

    def align_azimuth(self, target_az):
        # finding delta degrees
        a = target_az - self.current_position
        a = (a + 180) % 360 - 180
        self.degrees_to_turn = a

        self.steps = int(((a / 360) * self.steps_360) * self.gear_ratio)
        print(self.degrees_to_turn)

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