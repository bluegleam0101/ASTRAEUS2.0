
class AltitudeMotor:
    def __init__(self, rpimotor_object, steps_360, gpiopins=None, inv=False, wait=0.01, gear_ratio=1, steptype="full", rpimotorlib_oddity=False):
        """
        please provide gear ratio as a float corresponding to
        the amount of times to motor has to turn 360° to fully
        rotate to telescope once.


        the steps_360 parameter asks for the amount of steps your stepper motor has to turn to turn 360° in full step mode
        """
        self.steptype = steptype
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
        self.wait = wait

    def align_altitude(self, target_alt):
        # finding delta degrees
        a = float(target_alt) - self.current_position
        a = (a + 180) % 360 - 180
        self.degrees_to_turn = a

        self.steps = abs(int(((self.degrees_to_turn / 360) * self.steps_360) * self.gear_ratio))
        print(f"alt: degrees to turn:{self.degrees_to_turn}")
        print(f"alt: steps to turn:{self.steps}")

        #determining direction
        if self.degrees_to_turn < 0:
            self.clockwise = False
        if self.inv:
            self.clockwise = not self.clockwise
        if self.oddity:
            self.clockwise = not self.clockwise

        self.rpimotor_object.motor_run(
                                       gpiopins=self.gpiopins,
                                       wait=self.wait,
                                       steps=self.steps,
                                       ccwise=self.clockwise,
                                       verbose=False, steptype=self.steptype, initdelay=.02
                                       )
        self.current_position = target_alt


class AzimuthMotor:
    def __init__(self, rpimotor_object, steps_360, gpiopins=None, inv=False, wait=0.01, gear_ratio=1, steptype="full", rpimotorlib_discrepancy=False):
        """
        please provide gear ratio as a float corresponding to
        the amount of times to motor has to turn 360° to fully
        rotate to telescope once.

        the steps_360 parameter asks for the amount of steps your stepper motor has to turn to turn 360° in full step mode
        """
        self.steptype = steptype
        self.oddity = rpimotorlib_discrepancy
        self.inv = inv
        self.steps_360 = steps_360
        self.gear_ratio = gear_ratio
        self.current_position = 0.0
        self.rpimotor_object = rpimotor_object
        self.clockwise = False
        self.degrees_to_turn = None
        self.steps = None
        self.wait = wait

    def align_azimuth(self, target_az):
        # finding delta degrees
        a = float(target_az) - self.current_position
        a = (a + 180) % 360 - 180
        self.degrees_to_turn = abs(a)
        self.steps = abs(int(((a / 360) * self.steps_360) * self.gear_ratio))
        print(self.degrees_to_turn)
        print(f"az: degrees to turn:{self.degrees_to_turn}")
        print(f"az: steps to turn:{self.steps}")
        # determining direction
        if self.degrees_to_turn < 0:
            self.clockwise = False
        if self.inv:
            self.clockwise = not self.clockwise
        if self.oddity:
            self.clockwise = not self.clockwise

        self.rpimotor_object.motor_go(clockwise=self.clockwise, steptype=self.steptype, steps=self.steps, stepdelay=self.wait,
                                      initdelay=0.1)
        self.current_position = target_az


class TelescopeMotorController:
    def __init__(self, alt_motor, az_motor):
        self.az_motor = az_motor
        self.alt_motor = alt_motor


