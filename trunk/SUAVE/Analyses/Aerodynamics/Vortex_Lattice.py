## @ingroup Analyses-Aerodynamics
# Vortex_Lattice.py
#
# Created:  Nov 2013, T. Lukaczyk
# Modified:     2014, T. Lukaczyk, A. Variyar, T. Orra
#           Feb 2016, A. Wendorff
#           Apr 2017, T. MacDonald
#           Nov 2017, E. Botero


# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

# SUAVE imports
import SUAVE

from SUAVE.Core import Data
from SUAVE.Core import Units

from SUAVE.Methods.Aerodynamics.Common.Fidelity_Zero.Lift import weissinger_vortex_lattice

# local imports
from .Aerodynamics import Aerodynamics

# package imports
import numpy as np


# ----------------------------------------------------------------------
#  Class
# ----------------------------------------------------------------------
## @ingroup Analyses-Aerodynamics
class Vortex_Lattice(Aerodynamics):
    """This builds a surrogate and computes lift using a basic vortex lattice.

    Assumptions:
    None

    Source:
    None
    """ 

    def __defaults__(self):
        """This sets the default values and methods for the analysis.

        Assumptions:
        None

        Source:
        N/A

        Inputs:
        None

        Outputs:
        None

        Properties Used:
        N/A
        """  
        self.tag = 'Vortex_Lattice'

        self.geometry = Data()
        self.settings = Data()

        # correction factors
        self.settings.fuselage_lift_correction           = 1.14
        self.settings.trim_drag_correction_factor        = 1.02
        self.settings.wing_parasite_drag_form_factor     = 1.1
        self.settings.fuselage_parasite_drag_form_factor = 2.3
        self.settings.aircraft_span_efficiency_factor    = 0.78
        self.settings.drag_coefficient_increment         = 0.0000

    def evaluate(self,state,settings,geometry):
        # unpack
        conditions = state.conditions
        propulsors = geometry.propulsors
        vehicle_reference_area = geometry.reference_area
        total_lift_coeff = 0
        total_drag_coeff = 0
        #total_lift       = 0
        #total_drag       = 0 
        
        # inviscid lift of wings only
        inviscid_wings_lift                                              = Data()
        inviscid_wings_lift.total                                        = Data()
        conditions.aerodynamics.lift_breakdown.inviscid_wings_lift       = Data()
        conditions.aerodynamics.lift_breakdown.inviscid_wings_lift.total = Data()
        state.conditions.aerodynamics.lift_coefficient                   = Data()
        state.conditions.aerodynamics.lift_coefficient_wing              = Data() 
                
        for wing in geometry.wings.values():
            [wing_lift_coeff, wing_lift, wing_drag_coeff, wing_drag]             = weissinger_vortex_lattice(conditions,settings,wing,propulsors)
            inviscid_wings_lift[wing.tag]                                        = wing_lift_coeff 
            conditions.aerodynamics.lift_breakdown.inviscid_wings_lift[wing.tag] = inviscid_wings_lift[wing.tag]
            state.conditions.aerodynamics.lift_coefficient_wing[wing.tag]        = inviscid_wings_lift[wing.tag]     
            total_lift_coeff                                                     += wing_lift_coeff * wing.areas.reference / vehicle_reference_area  
            
            ## lift 
            #total_lift  += wing_lift  
            
            ## inviscid drag 
            #total_drag  += wing_drag 
        
        conditions.aerodynamics.lift_breakdown.inviscid_wings_lift.total = total_lift_coeff
        state.conditions.aerodynamics.lift_coefficient                   = total_lift_coeff
        state.conditions.aerodynamics.inviscid_lift                      = total_lift_coeff 
        inviscid_wings_lift.total                                        = total_lift_coeff
        
        for wing in wing_CL_data.keys():
            wing_cl_surrogates[wing] = np.poly1d(np.polyfit(X_data, wing_CL_data[wing] ,1))


        self.surrogates.lift_coefficient = cl_surrogate
        self.surrogates.wing_lift_coefficients = wing_cl_surrogates

        return



# ----------------------------------------------------------------------
#  Helper Functions
# ----------------------------------------------------------------------


def calculate_lift_vortex_lattice(conditions,settings,geometry):
    """Calculate the total vehicle lift coefficient and specific wing coefficients (with specific wing reference areas)
    using a vortex lattice method.

    Assumptions:
    None

    Source:
    N/A

    Inputs:
    conditions                      (passed to vortex lattice method)
    settings                        (passed to vortex lattice method)
    geometry.reference_area         [m^2]
    geometry.wings.*.reference_area (each wing is also passed to the vortex lattice method)

    Outputs:
    

    Properties Used:
    
    """            

    # unpack
    vehicle_reference_area = geometry.reference_area

    # iterate over wings
    total_lift_coeff = 0.0
    wing_lifts = Data()

    for wing in geometry.wings.values():

        [wing_lift_coeff,wing_drag_coeff] = weissinger_vortex_lattice(conditions,settings,wing)
        total_lift_coeff += wing_lift_coeff * wing.areas.reference / vehicle_reference_area
        wing_lifts[wing.tag] = wing_lift_coeff

    return total_lift_coeff, wing_lifts
