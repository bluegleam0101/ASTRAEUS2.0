import time
import csv
from datetime import datetime
import astropy.units as units
from astropy.time import Time
import geocoder
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, BaseRADecFrame
from motor_controller import TelescopeMotorController, AltitudeMotor, AzimuthMotor
from RpiMotorLib import RpiMotorLib


class TelescopePointer:
    def __init__(self, telescope_motor_api):
        self.target: object

    def set_target(self, query, latlng):
        """gets current ra, dec, distance, altitude and azimuth for a celestial object specified by the 'celestial_body' parameter,
         sets target. target astrometrics (ra, dec) given in floating point numbers which are degrees"""

        time = Time(datetime.now())
        geo_location = EarthLocation(lat=latlng[0] * units.deg, lon=latlng[0] * units.deg, height=5 * units.m)

        self.target = SkyCoord.from_name(query)
        self.target = self.target.transform_to(AltAz(obstime=time, location=geo_location))
        print(self.target.az, self.target.alt, self.target.info)
        print(
            # f"right inclination axis: {self.target.transform_to(BaseRADecFrame()).ra} degrees\n"
            # f"declination axis: {self.target.transform_to(BaseRADecFrame()).dec} degrees\n"
            # f"distance: {self.target['dis']}\n"
            f"local altitude: {self.target.alt}\n"
            f"local azimuth: {self.target.az}\n"
        )

    # align func is a function you have to pass that takes a ra- and dec axis and points the telescopes

    def align(self, az, alt, telescope_motor_api, continuous=False, continuous_interval=10):
        """
        Aligns telescope by calling upon the telescope_motor_api function (that you have to create yourself).

        takes ra and dec, both in degrees.

        Set continuous to True if you want to keep aligning at an interval of 10 seconds. (10 is default but can be
        changed using the continuous_interval parameter)
        """
        if not continuous:
            telescope_motor_api.az_motor.align_azimuth(target_az=az)
            print("aligning was successful")

        if continuous:
            print("continuously aligning...\nssss")
            while True:
                telescope_motor_api()
                print('aligned')
                time.sleep(continuous_interval)

    def display_text(self, text):
        pass


# initializing objects #


telescope_motor_api = TelescopeMotorController(az_motor=AzimuthMotor(
    rpimotor_object=RpiMotorLib.A4988Nema(
        direction_pin=26,
        step_pin=19,
        mode_pins=(21, 21, 21),
        motor_type="DRV8825"
    ),

    steps_360=200,
    gear_ratio=3,
    inv=True

    ),

    alt_motor=AltitudeMotor(
        rpimotor_object=RpiMotorLib.BYJMotor(),
        steps_360=4096,
        gear_ratio=3,
        gpiopins=[5, 6, 13, 11],
        inv=True,
        rpimotorlib_oddity=True
    )
)

telescope_pointer = TelescopePointer(telescope_motor_api=telescope_motor_api)

if __name__ == "__main__":
    while True:
        latlng = geocoder.ip('me').latlng
        print(f"Current coordinates: lat: {latlng[0]}, long: {latlng[1]}.")
        if latlng is None:
            print("Could not get current coordinates.")
            current_long = str.title(input("please specify your longitude: "))
            current_lat = str.title(input("please specify your latitude: "))
            latlng = [current_lat, current_long]

        choice = input("would you like to set a new target or align telescope? (S/A): ")

        if choice == 'S':
            for i in range(1, 100):
                try:
                    telescope_pointer.set_target(query=input("Please enter celestial object to set as target: "),
                                                 latlng=latlng)
                    print("target set, ready to align.")
                except ValueError:
                    print("Celestial object not found, please try again.")
                    continue
                break

        elif choice == 'A':
            continuous = bool(int(input("Continuous align? 1 for yes, 0 for no: ")))
            telescope_pointer.align(
                alt=telescope_pointer.target.alt,
                az=telescope_pointer.target.az,
                continuous=continuous,
                telescope_motor_api=telescope_motor_api
            )

    # pointer.align(dgbsdhfb
