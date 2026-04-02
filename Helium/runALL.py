import math
from math import sqrt, comb # Python's built-in binomial coefficient  
import numpy as np
from scipy.optimize import curve_fit
import pint
ureg = pint.UnitRegistry()
ureg.default_system = 'imperial'
ureg.formatter.default_format = '~P'

import CoolProp.CoolProp as cp
from conturpy import ConturSettings, ConturApplication
# import warnings
# warnings.filterwarnings("ignore")
from prettytable import PrettyTable
table = PrettyTable()
import matplotlib.pyplot as plt

class State:
    def __init__(self, fluid, **kwargs):
        """
        Initialize the thermodynamic state with exactly two properties.

        Parameters:
            fluid (str): The working fluid (e.g., 'Water', 'Air').
            kwargs: Thermodynamic properties as keyword arguments.
                Supported keys: 'T', 'P', 'H', 'S', 'Q', 'V'
                Example: T=300, P=101325
        """
        self.fluid = fluid
        self.properties = {
            "T": None,   # Temperature in K
            "P": None,   # Pressure in Pa
            "H": None,   # Mass Specific Enthalpy in J/kg
            "S": None,   # Mass Specific Entropy in J/kg.K
            "V": None,   # Dynamic Viscovity in Pa.s
            "D": None,   # Density in kg/m^3
            "Cpmass": None,         # Constant Pressure Specific Heat (mass based) in J/kg/K
            "Cvmass": None,         # Constant Volume Specific Heat (mass based) in J/kg/K
            "gas_constant": None,   # Molar Gas Constant in J/mol/K
            "molarmass": None,      # Molar Mass in kg/mol
            "Z": None,   #compressibility factor (dimensionless)
            "Prandtl": None,        # Prandtl number (dimensionless)
        }


        # Populate provided properties
        provided_properties = {k: v for k, v in kwargs.items() if k in self.properties}
        # Error handling to make sure every state is defined by at least 2 properties
        if len(provided_properties) != 2:
            raise ValueError("Exactly two properties must be provided to initialize the state.")

        self.properties.update(provided_properties)

        # Extract the provided property names and values
        (prop1_name, prop1_value), (prop2_name, prop2_value) = provided_properties.items()

        # Calculate missing properties
        self._calculate_properties(prop1_name, prop1_value, prop2_name, prop2_value)

        # Set class attributes for each property
        for prop, value in self.properties.items():
            setattr(self, prop, value)


    def _calculate_properties(self, prop1_name, prop1_value, prop2_name, prop2_value):
        """
        Calculate and fill in all missing thermodynamic properties using CoolProp.
        """
        # List of all properties for CoolProp
        property_keys = list(self.properties.keys())

        # Use CoolProp to calculate missing properties
        for prop in property_keys:
            if self.properties[prop] is None:
                try:
                    self.properties[prop] = cp.PropsSI(
                        prop, prop1_name, prop1_value, prop2_name, prop2_value, self.fluid
                    )
                except ValueError:
                    # Handle cases where the property cannot be calculated
                    #print("ur fucked")########################################################################################
                    self.properties[prop] = None


    def __repr__(self):
        """
        String representation of the thermodynamic state for print outs
        """
        return f"{self.properties}"
# End State class
# sutherlands law of viscocity curve fitting to NIST values
def sutherlands(T, b, S): # modified sutherlands used by sevills in his code (p.64)
    T = np.asarray(T)

    # allocate result array
    mu = np.zeros_like(T, dtype=float)

    # region T > S
    mask = T > S
    mu[mask] = b * (T[mask]**1.5) / (T[mask] + S)

    # region T <= S
    mu[~mask] = b * T[~mask] / (2 * np.sqrt(S))

    return mu

def write_ansys_points(filename, arr, number, append=False):
    mode = 'a' if append else 'w'
    with open(filename, mode) as f:
        for idx, (x, y) in enumerate(arr, start=1):
            i = number
            j = idx
            z = 0.0
            f.write(f"{x:.6f},{y:.6f},{z:.0f}\n")

def write_SolidWorks_points(filename, arr, number, append=False):
    mode = 'a' if append else 'w'
    with open(filename, mode) as f:
        for idx, (x, y) in enumerate(arr, start=1):
            z = 0.0
            f.write(f"{x:.6f}\t{y:.6f}\t{z:.0f}\n")

c = ConturSettings()
fluid = 'Helium'
throat_radius = 0.15/2 * ureg.inch  # inches
dmach = 18               # design mach
print("Mach: ", dmach)
# Chamber Properties
T0  = (500*ureg.degK).to(ureg.degR) # 500 Kelvin converted to Rankine
P0 = (20e5*ureg.pascal).to('psi') # 20 bar converted to psi
print(T0, P0)

# Average fluid properties
P_He = 1.01325e5
T_low = 10
T_high = 500
T_avg = (T_high + T_low)/2

DataPoints = 600
temps = np.linspace(T_low, T_high, num=DataPoints)
viscocities = [State(fluid=fluid,T=T1,P=P_He).V for T1 in temps]
results = curve_fit(sutherlands, xdata = temps, ydata = viscocities)[0]
b_He,S_He = results[0], results[1]
b_He_SI = b_He * (ureg.pascal * ureg.second / ureg.degK**0.5)  # Pa * s / K^1/2
b_He_IMP = b_He_SI.to(ureg.lbf * ureg.second / (ureg.foot**2 * ureg.degR**0.5))
S_He_SI = S_He * ureg.degK
S_He_IMP = S_He_SI.to(ureg.degR)

ref_State = State(fluid=fluid,T=T_avg,P=P_He) # reference state
gamma = ref_State.Cpmass/ref_State.Cvmass
R_gas_SI = ref_State.gas_constant/ref_State.molarmass * ureg.J/ureg.kg/ureg.K
R_gas_IMP = R_gas_SI.to(ureg.ft**2 /(ureg.s**2 * ureg.degR))
Z_gas = ref_State.Z
TBLRF = (ref_State.Prandtl)**(1/3) # Turbulent boundary layer recovery factor
table.field_names = ["Property", "Value", "Unit"]
table.add_row(["Gamma", gamma, "Dimensionless"])
table.add_divider()
table.add_row(["Gas Constant", R_gas_IMP.magnitude, R_gas_IMP.units])
table.add_divider()
table.add_row(["Compressibility Factor", Z_gas, "Dimensionless"])
table.add_divider()
table.add_row(["Turbulent Boundary Layer Recovery Factor", TBLRF, "Dimensionless"])
table.add_divider()
table.add_row(["Sutherlands Constant", b_He_IMP.magnitude, b_He_IMP.units])
table.add_divider()
table.add_row(["Sutherlands Temperature", S_He_IMP.magnitude, S_He_IMP.units])
print(table)


# CARDS
#Card 1: the title of the simulation
c["ITLE"] = f"Mach {dmach}"
c["JD"] = 0         # Axisymmetric or planar nozzle. Set to 0 for axisymmetric or -1 for planar nozzle.


# Card 2 contains gas properties. As air is the assumed working fluid, no changes are required
# All properties taken from sutherlands code
c["GAM"] = gamma      # Ratio of specific heats.
c["AR"] = R_gas_IMP.magnitude   # Gas constant in ft^2/sec^2 * R [or ft*lbf/(slug*R)]
c["ZO"] = Z_gas         # Compressability factor for axisymmetric nozzle. Untested: half distance (in) between walls and assumed compressability factor of 1
c["RO"] = TBLRF       # Turbulent boundary layer recovery factor (see Sivells' paper)
# Sutherlands Law has a 25% error at 50K, 8.8% error at 100K, and 2% error 200-600K. The law is much more accurate at higher temperatures, which is bad since our nozzle continuously decreases the temperature
c["VISC"]= b_He_IMP.magnitude  # b: Constant in viscosity law (see Sivells' paper) [in lbf * s / (ft^2 * R^1/2)]
# VISC appears to be the sutherland constant as calculate by NACA on pg22 of Sivells
c["VISM"] = S_He_IMP.magnitude    # S: Sutherland temperature in Rankine
# VISM might be a lowerbound cutoff temperature for sutherland law instead: "Viscocity follows sutherlands law above VISM, but is linear with temperature below VISM" Sivells' paper pg64
c["SFOA"] = 0         # If zero: 3rd or 4th degree velocity distribution depending on IX. If negative: absolute value is distance from throat to point G (see Sivells' paper). If positive: distance from throat to point A (see Sivells' paper).
#c["XBL"] = 1000      # Where to start interpolating. If 1000, use spline fit to get evenly spaced points on wall contour.


# Card 3: key design parameters
c["ETAD"] = 60        # Angle at point D. Inflection angle for radial flow. If ETAD=60, the entire centerline velocity distribution is specified; IQ=1 and IX=0 on card 4.
#print((0.5)/throat_radius * 6) # correction ratio for radius of curvature
c["RC"] = (0.5/throat_radius*6).magnitude         # The radius of curvature of the throat: multiples of throat radius. [Suggest in the neighborhood of 5.5-6.0 for air]
c["FMACH"] = 0        # If ETAD is not 60, Mach number at point F (see Sivells' paper)
c["BMACH"] = 0        # If ETAD is not 60, Mach number at point B (see Sivells' paper)
c["CMC"] = dmach      # The design mach number at point C (see Sivells' paper). This should be the design mach number of the nozzle. If ETAD is not 0, check Sivells' paper as this parameter is important.
c["SF"] = throat_radius.magnitude # If positive, the nozzle has this as the throat radius (or half height) in inches. If 0, the nozzle has radius (or half height) 1 inch. If negative, the nozzle has this as the exit radius (or half height) in inches.
#c["PP"] = 0          # Location of point A (see Sivells' paper). Strongly suggest setting to 0 (driven dimension) unless user is positive they want to specify location A.
#c["XC"] = 0          # Nondimensional distance from radial source to point C (see Sivells' paper). Suggest 0 (4th degree velocity distribution).

# # Card 4: 
# c["MT"] = 81	    #Number of points on characteristic CD if ETAD=60 or EG if ETAD is not 60 (see Sivells' paper). Must be odd.
# c["NT"] = 41	    # Number of points on axis IE (see Sivells' paper). Make sure abs(LR) + abs(NT) extless{}= 149. Must be odd.
# c["IX"] = 0	# Unsure.
# c["IN"] = 10	    # If nonzero, the downstream value of the second derivative of velocity at point B is 0.1 * IN times the transonic value if ETAD=60 or 0.1 * abs(IN) times the radial value if ETAD is not 60. Use 0 for throat only. Suggest 10.
# c["IQ"] = 0	    # If ETAD is not 60, 0 for complete contour, 1 for throat only, and -1 for downstream only.
# c["MD"] = 61	    # Number of points on characteristic AB (see Sivells' paper). No more than 125. Must be odd.
# c["ND"] = 69	    # Number of points on axis BC (see Sivells' paper). No more than 150.
# c["NF"] = -61	    # Number of points on characteristic CD if ETAD is not 60. See Sivells' paper if using.
# c["MP"] = 0	    # Number of points on section GA (see Sivells' paper) if FMACH is not equal to BMACH. Sivells notes "Usually not known for initial calculation"
# c["MQ"] = 0	    # Number of points downstream of point D if parallel contour desired. Negative to stop inviscid printout.
# c["JB"] = 1	    # If positive: number of boundary layer calculations before spline fit. Negative impact is unknown, see Sivells' paper. Suggest 1.
# c["JX"] = 0	    # Positive calculates streamlines. If XBL = 1000, spline fit after invisid calculation if JX=0 or repeat of calculation if negative. If XBL is not 1000, repeat calculations.
# c["JC"] = 1	    # If not zero, print out inviscid characteristics for every JC characteristic. Positive for upstream and negative for downstream.
# c["IT"] = 0	# Unsure.
# c["LR"] = -25	    # Number of points on throat characteristic. Negative prints out transonic solution. If 0, M=1 at point I. See NT.
# c["NX"] = 13	    # Logarithmic spacing for upstream contour. 10 is closer spacing and 20 is further spacing. Between 10 or 20. Suggest 13.

# # Card 5: 
# c["NOUP"] = 50	# Unsure.
# c["NPCT"] = 85	# Unsure.
# c["NODO"] = 50	# Unsure.


# Card 6 (B): stagnation and heat transfer properties
# 290 psi and 900R for Parziale
c["PPQ"] = P0.magnitude      # Stagnation pressure [psia] (unkown breaking point) #120 starting
c["TO"] = T0.magnitude      # Stagnation temperature [R] (breaks at 1219: investigate) #1000 starting
c["TWT"] = 540      # Wall temperature [R]
c["TWAT"] = 540     # Water-cooling temp [R] (suggest setting to TWT since water cooling not assumed)


# Card 7 (D): interpolation parameters
c["XLOW"] = 0       # Point to begin interpolating contour [in]
c["XEND"] = 60      # Point to end interpolating contour [in]
c["XINC"] = .08      # Increment to interpolate by [in]

# Create the input text file and save it to 'm5.0.txt' in the folder 'inputcards'
c.print_to_input(file_name=f'm{dmach:.1f}.txt', output_directory='inputcards')
ca = ConturApplication()
res = ca.batch_input_folder('inputcards', output_dir='outputs') # type: ignore
#print(res[0].SuperBetterCoordinates)
ExpansionCoords = res[0].SuperBetterCoordinates[1:]
ExpansionCoords = np.concatenate(([[0,throat_radius.magnitude]], ExpansionCoords))




def cubic_bezier(points, num=125):
    """
    points: list or tuple of 4 control points P0, P1, P2, P3
            each must be a length-2 iterable [x, y]
    num: number of points evaluated along the curve
    
    Returns: (num x 2) array of curve points
    """
    P0, P1, P2, P3 = [np.array(p, dtype=float) for p in points]
    t = np.linspace(0, 1, num)

    curve = np.zeros((num, 2))
    for i in range(4):
        binom = comb(3, i)
        curve += binom * ((1 - t)**(3 - i))[:, None] * (t**i)[:, None] * [P0, P1, P2, P3][i]

    return curve

pipe_width = 6
contraction_length = 10
node1 = (-contraction_length, pipe_width/2)
ctrl1 = (-contraction_length/2, node1[1])

node2 = (0, throat_radius.magnitude)
ctrl2 = (-contraction_length/2, node2[1])

# Order: P0, P1, P2, P3
points = [node1, ctrl1, ctrl2, node2]

# Compute cubic Bézier points
curve_points = cubic_bezier(points, num=125)




def mass_flow(mach, radius = None, area = None):
    if (radius is None) and (area is None):
        raise ValueError("You must supply either radius or area.")
    if (radius is not None) and (area is not None):
        raise ValueError("Provide only one: radius OR area, not both.")
    if radius is not None:
        area = math.pi * radius**2

    
    return ((area*P0/(T0**(0.5))) * ((gamma/R_gas_IMP)**(0.5) *mach) * (1+0.5*(gamma-1)*mach**2)**(-(gamma+1)/(2*(gamma-1)))).to_base_units()



print("mass flow: ", mass_flow(radius=throat_radius,mach=1))

file = 'AutoContour.txt'

Inlet = [[-contraction_length,0],
         [-contraction_length, pipe_width/2]]
write_ansys_points(file, Inlet, number=1, append=False)

# Contraction Section
write_ansys_points(file,curve_points, number=2,  append=True)

# Expansion Section
write_ansys_points(file,ExpansionCoords, number=3, append=True)

Outlet = [ExpansionCoords[-1],
          [60,0]]
write_ansys_points(file, Outlet, number=4, append=True)

Symmetry = [Outlet[1],Inlet[0]]
write_ansys_points(file, Symmetry, number=5, append=True)