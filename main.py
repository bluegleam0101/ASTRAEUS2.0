import time
import csv
from datetime import datetime
import astropy.units as units
from astropy.time import Time
import geocoder
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, get_body
from astropy.coordinates.name_resolve import NameResolveError
from astropy.coordinates import solar_system_ephemeris
from motor_controller import TelescopeMotorController, AltitudeMotor, AzimuthMotor
from RpiMotorLib import RpiMotorLib


class TelescopePointer:
    def __init__(self, telescope_motor_api):
        self.target = None
        self.time = Time(datetime.now())
        self.query = ""
        self.latlng = {}

    def calibrate(self, calibration_reference, latlng):
        self.set_target(query=calibration_reference, latlng=latlng)
        az = telescope_pointer.target.az
        alt = telescope_pointer.target.alt
        az = az.dms[0] + (az.dms[2] / az.dms[1])
        alt = alt.dms[0] + (alt.dms[2] / alt.dms[1])
        telescope_motor_api.az_motor.current_position = az
        telescope_motor_api.alt_motor.current_position = alt

    def set_target(self, query, latlng):
        """gets current ra, dec, distance, altitude and azimuth for a celestial object specified by the 'celestial_body' parameter,
         sets target. target astrometrics (ra, dec) given in floating point numbers which are degrees"""
        self.query = query
        self.latlng = latlng
        geo_location = EarthLocation(lat=latlng[0] * units.deg, lon=latlng[0] * units.deg, height=5 * units.m)
        try:
            self.target = SkyCoord.from_name(query)
            self.target = self.target.transform_to(AltAz(obstime=self.time, location=geo_location))

        except NameResolveError:
            self.target = get_body(body=query, time=self.time, location=geo_location)
            self.target = self.target.transform_to(AltAz(obstime=self.time, location=geo_location))

        print(self.target.az, self.target.alt, self.target.info)
        print(
            # f"right inclination axis: {self.target.transform_to(BaseRADecFrame()).ra} degrees\n"
            # f"declination axis: {self.target.transform_to(BaseRADecFrame()).dec} degrees\n"
            # f"distance: {self.target['dis']}\n"
            f"local altitude: {self.target.alt}\n"
            f"local azimuth: {self.target.az}\n"
            f"local altitude: {self.target.alt.dms}\n"
            f"local azimuth: {self.target.az.dms}\n"
        )

    # align func is a function you have to pass that takes a ra- and dec axis and points the telescopes

    def align(self, az, alt, telescope_motor_api, continuous=False, continuous_interval=10):
        """
        Aligns telescope by calling upon the telescope_motor_api function (that you have to create yourself).

        takes ra and dec, both in degrees.

        Set continuous to True if you want to keep aligning at an interval of 10 seconds. (10 is default but can be
        changed using the continuous_interval parameter)
        """
        # getting az/alt again because time exists

        # converting astropy angle to float
        az = az.dms[0] + (az.dms[2] / az.dms[1])
        alt = alt.dms[0] + (alt.dms[2] / alt.dms[1])

        print(f"converted to float: alt:{alt} az:{az}")

        if alt < 0:
            return print("WARNING: target under horizon, aborting...")
        if not continuous:
            telescope_motor_api.az_motor.align_azimuth(target_az=az)
            telescope_motor_api.alt_motor.align_altitude(target_alt=alt)
            print("aligning was successful")

        if continuous:
            print("continuously aligning...\nssss")
            while True:
                print('aligned')
                time.sleep(continuous_interval)

    def display_text(self, text):
        pass


# initializing objects #
pins_azmotor = [5, 6, 13, 11]

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
        inv=True,
        rpimotorlib_oddity=True,
        gpiopins=pins_azmotor
    )
)

telescope_pointer = TelescopePointer(telescope_motor_api=telescope_motor_api)

if __name__ == "__main__":
    while True:

        solar_system_ephemeris.set('jpl')
        latlng = geocoder.ip('me').latlng

        print(f"Current coordinates: lat: {latlng[0]}, long: {latlng[1]}.")
        if latlng is None:
            print("Could not get current coordinates.")
            current_long = str.title(input("please specify your longitude: "))
            current_lat = str.title(input("please specify your latitude: "))
            latlng = [current_lat, current_long]

        choice = input("would you like to set a new target or align or calibrate telescope? (S/A/C): ")

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
            continuous = bool(int(input("continuous? 1 for yes, 0 for no: ")))
            # temp fix
            telescope_pointer.time = Time(datetime.now())
            telescope_pointer.set_target(query=telescope_pointer.query, latlng=telescope_pointer.latlng)
            ##
            telescope_pointer.align(
                alt=telescope_pointer.target.alt,
                az=telescope_pointer.target.az,
                continuous=continuous,
                telescope_motor_api=telescope_motor_api
            )
            print("aligned")

        elif choice == 'C':
            telescope_pointer.calibrate(calibration_reference=input("\n calibration reference: "),latlng=latlng)
            print("calibrated")

        elif choice == 'exit':
            break
