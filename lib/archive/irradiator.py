#
# 
# 
# 
# 
# NOT USED
# 
# 
# 
# 
# 
# 

import pytz

import pvlib
from pvlib.pvsystem import PVSystem, Array, FixedMount
from pvlib.location import Location
from pvlib.modelchain import ModelChain


latitude = 58.3780
longitude = 26.7290

TIMEZONE = pytz.timezone("Europe/Tallinn")


class Irradiator:

    def solar_irradiation(date_time):
        sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod')
        sapm_inverters = pvlib.pvsystem.retrieve_sam('cecinverter')
        module = sandia_modules['Canadian_Solar_CS5P_220M___2009_']
        inverter = sapm_inverters['ABB__MICRO_0_25_I_OUTD_US_208__208V_']

        print(module["Area"])

        temperature_model_parameters = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']

        loc = Location(latitude, longitude, TIMEZONE)
        mount = FixedMount(surface_tilt=0, surface_azimuth=180)
        array = Array(mount=mount, module_parameters=module, temperature_model_parameters=temperature_model_parameters)

        weather = pvlib.iotools.get_pvgis_tmy(latitude, longitude, map_variables=True)[0]

        system = PVSystem(arrays=[array], inverter_parameters=inverter)
        mc = ModelChain(system, loc)  
        mc.run_model(weather)


        annual_energy = mc.results.ac
