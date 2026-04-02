import CoolProp.CoolProp as cp
import numpy as np
from pygasflow.solvers import isentropic_solver
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
            "viscosity": None,   # Dynamic Viscovity in Pa.s
            "Dmass": None,   # Density in kg/m^3
            "Cpmass": None,         # Constant Pressure Specific Heat (mass based) in J/kg/K
            "Cvmass": None,         # Constant Volume Specific Heat (mass based) in J/kg/K
            "Z": None,              #compressibility factor (dimensionless)
            "speed_of_sound": None,    # Speed of sound (m/s)
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

Machs = np.linspace(4.0, 20.0, num=17)
total_T = 500
total_P = 20e5
throat_D = 0.1 * 0.0254

results = isentropic_solver("m", Machs, gamma=(5/3), to_dict=True)
# Convert pygasflow results to a plain dictionary
results = {key: np.array(val, dtype=float) for key, val in results.items()}
# add exit temperatures and pressures to result dictionary
results["T_exit"] = np.array(results["tr"] * total_T, dtype=float)
results["P_exit"] = np.array(results["pr"] * total_P, dtype=float)
results["D_exit"] = np.array(np.sqrt(results["ars"]) * throat_D, dtype=float)

processed = []
for i in range(len(results["m"])):
    entry = {key: float(results[key][i]) for key in results}
    processed.append(entry)


## Calculated properties from exit conditions
rho = []
a   = []
mu  = []
ReLen  = []
for res in processed:
    # create state from exit T and P
    State1 = State(fluid='Helium',
                   T= res["T_exit"],
                   P= res["P_exit"])
    # extract other properties at specified (T,P)
    rho.append(State1.Dmass)
    a.append(  State1.speed_of_sound)
    mu.append( State1.viscosity)
    
    ReLen.append(
        State1.Dmass
        * State1.speed_of_sound
        * float(res["m"])
        #* float(res["D_exit"])
        / State1.viscosity
    )
results["rho"] = np.array(rho, dtype=float)
results["a"] = np.array(a, dtype=float)
results["mu"] = np.array(mu, dtype=float)
results["Re/m"] = np.array(ReLen, dtype=float)



## Graphing and Such ##



from prettytable import PrettyTable
table = PrettyTable()

table.field_names = [
    "Mach",
    "T/T0",
    "T_exit [K]",    
    "P/P0",
    "P_exit [Pa]",
    "A/A*",
    "D_exit [m]",
    "Density [kg/m^3]",
    "Sound [m/s]",
    "Visc [Pa*s]",
    "Re/m"
]
for i in range(len(results["m"])):
    table.add_row([
        f"{results['m'][i]:.1f}",
        f"{results['tr'][i]:.5f}",
        f"{results['T_exit'][i]:.2f}",
        f"{results['pr'][i]:.5e}",
        f"{results['P_exit'][i]:.3e}",
        f"{results['ars'][i]:.2f}",
        f"{results['D_exit'][i]:.4f}",
        f"{results['rho'][i]:.4f}",
        f"{results['a'][i]:.4f}",
        f"{results['mu'][i]:.3e}",
        f"{results['Re/m'][i]:.3e}",
    ])
print(table)

import matplotlib.pyplot as plt

Mach = results["m"]

fig, (ax_left, ax_middle, ax_right ) = plt.subplots(1, 3, figsize=(14, 6), sharex=True)

# --- Thermodynamic properties ---
ax_left.set_xlabel("Mach Number")
ax_left.set_ylabel("D_exit [cm]", color="tab:green")
ax_left.plot(Mach, 100*results["D_exit"], color="tab:green", lw=2)
ax_left.tick_params(axis="y", labelcolor="tab:green")
ax_left.grid(True)

ax_left.set_title("Geometry")

# --- Thermodynamic properties ---
ax_middle.set_xlabel("Mach Number")
ax_middle.set_ylabel("T_exit [K]", color="tab:red")
ax_middle.plot(Mach, results["T_exit"], color="tab:red", lw=2)
ax_middle.tick_params(axis="y", labelcolor="tab:red")
ax_middle.grid(True)

twin_middle = ax_middle.twinx()
twin_middle.set_ylabel("P_exit [Pa]", color="tab:blue")
twin_middle.plot(Mach, results["P_exit"], color="tab:blue", lw=2)
twin_middle.tick_params(axis="y", labelcolor="tab:blue")

ax_middle.set_title("Thermodynamic Properties")

# --- Flow and transport properties ---
ax_right.set_xlabel("Mach Number")
ax_right.set_ylabel("Reynolds Number per unit length [m^-1]", color="k")
ax_right.plot(Mach, results["Re/m"], color="k", lw=2)
ax_right.tick_params(axis="y", labelcolor="k")
ax_right.grid(True)

ax_right.set_title("Flow Properties")

fig2, ax = plt.subplots()

ax.set_xlabel("Mach Number")
ax.set_ylabel("Viscosity [Pa·s]", color="tab:orange")
ax.plot(Mach, results["mu"], color="tab:orange", lw=2)
ax.tick_params(axis="y", labelcolor="tab:orange")

# First twin
twin1 = ax.twinx()
twin1.set_ylabel("Speed of Sound [m/s]", color="tab:brown")
twin1.plot(Mach, results["a"], color="tab:brown", lw=2)
twin1.tick_params(axis="y", labelcolor="tab:brown")

# Second twin
twin2 = ax.twinx()
twin2.spines["right"].set_position(("outward", 60))
twin2.spines["right"].set_visible(True)
twin2.set_ylabel("Density [kg/m³]", color="tab:purple")
twin2.plot(Mach, results["rho"], color="tab:purple", lw=2)

twin2.yaxis.set_ticks_position("right")
twin2.yaxis.set_label_position("right")
twin2.tick_params(axis="y", labelcolor="tab:purple")

ax.set_title("Properties")

fig.tight_layout()
fig2.tight_layout()
plt.show()