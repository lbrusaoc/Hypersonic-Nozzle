import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import math
from math import comb
import numpy as np
from scipy.optimize import curve_fit
import pint
import CoolProp.CoolProp as cp
from conturpy import ConturSettings, ConturApplication, save_all
from prettytable import PrettyTable

ureg = pint.UnitRegistry()
ureg.default_system = 'imperial'
ureg.formatter.default_format = '~P'


# ══════════════════════════════════════════════════════════════════════════════
#  USER PARAMETERS  —  edit here, nothing below should need to change
# ══════════════════════════════════════════════════════════════════════════════

fluid         = 'Helium'
dmach         = 18                               # design Mach number
throat_radius = 0.5 * ureg.inch                  # throat radius [in]
T0            = 500                              # stagnation temperature [Kelvin]
P0            = 20e5                             # stagnation pressure [Pa]
T_wall        = 300                              # wall temperature (no water cooling assumed) [K]

# Contraction geometry
pipe_width         = 6    # [in]  upstream pipe inner diameter
contraction_length = 10   # [in]  axial length of contraction section

# Sutherland viscosity fit — temperature range [K] should span the nozzle flow
T_fit_low  = 10
T_fit_high = 500

# Contur output interpolation range
XLOW = 0      # [in]  start of interpolated contour
XEND = 60     # [in]  end of interpolated contour (increase if nozzle is longer)
XINC = 0.08   # [in]  interpolation increment

# ══════════════════════════════════════════════════════════════════════════════


# ── Classes ───────────────────────────────────────────────────────────────────

class State:
    """
    Thermodynamic state of a fluid computed via CoolProp.
    Initialise with exactly two known properties, e.g. State('Helium', T=300, P=101325).
    Supported keys: T [K], P [Pa], H [J/kg], S [J/kg·K], V [Pa·s], D [kg/m³],
                    Cpmass, Cvmass [J/kg/K], gas_constant [J/mol/K],
                    molarmass [kg/mol], Z [-], Prandtl [-]
    """
    _PROPS = ["T", "P", "H", "S", "V", "D",
              "Cpmass", "Cvmass", "gas_constant", "molarmass", "Z", "Prandtl"]

    def __init__(self, fluid, **kwargs):
        self.fluid = fluid
        self.properties = {k: None for k in self._PROPS}

        provided = {k: v for k, v in kwargs.items() if k in self.properties}
        if len(provided) != 2:
            raise ValueError("Exactly two properties must be provided.")
        self.properties.update(provided)

        (p1, v1), (p2, v2) = provided.items()
        for prop in self._PROPS:
            if self.properties[prop] is None:
                try:
                    self.properties[prop] = cp.PropsSI(prop, p1, v1, p2, v2, fluid)
                except ValueError:
                    self.properties[prop] = None
        for prop, value in self.properties.items():
            setattr(self, prop, value)

    def __repr__(self):
        return f"State({self.fluid}, {self.properties})"


# ── Functions ─────────────────────────────────────────────────────────────────

def sutherlands(T, b, S):
    """
    Modified Sutherland viscosity law (Sivells p.64).
    Above S:  mu = b * T^1.5 / (T + S)
    Below S:  mu = b * T / (2*sqrt(S))   [linear approximation]
    """
    T = np.asarray(T)
    mu = np.zeros_like(T, dtype=float)
    mask = T > S
    mu[mask]  = b * T[mask]**1.5 / (T[mask] + S)
    mu[~mask] = b * T[~mask] / (2 * np.sqrt(S))
    return mu


def cubic_bezier(points, num=125):
    """
    Evaluate a cubic Bézier curve.
    points : sequence of 4 control points [[x0,y0], ..., [x3,y3]]
    num    : number of output points
    Returns (num × 2) array.
    """
    P0c, P1c, P2c, P3c = [np.array(p, dtype=float) for p in points]
    t = np.linspace(0, 1, num)
    curve = np.zeros((num, 2))
    for i, Pi in enumerate([P0c, P1c, P2c, P3c]):
        curve += comb(3, i) * ((1 - t)**(3 - i))[:, None] * (t**i)[:, None] * Pi
    return curve


def mass_flow(mach, radius=None, area=None):
    """
    Isentropic mass flow rate through a cross-section.
    Requires either radius [in pint units] or area [in pint units²].
    Uses module-level T0, P0, gamma, R_gas_IMP.
    """
    if (radius is None) == (area is None):
        raise ValueError("Provide exactly one of: radius, area.")
    if radius is not None:
        area = math.pi * radius**2
    return (
        (area * P0 / T0**0.5)
        * (gamma / R_gas_IMP)**0.5
        * mach
        * (1 + 0.5 * (gamma - 1) * mach**2) ** (-(gamma + 1) / (2 * (gamma - 1)))
    ).to_base_units()


def check_feasibility(T0_rankine, P0_psi, mach, gamma_val=5/3):
    """
    Prints warnings if operating conditions are outside feasible bounds.

    Checks:
      1. Fortran parser overflow — edge temperature at throat must be < 1000 R.
         The BL output uses 7-char fixed-width fields; 4-digit temperatures
         collide with adjacent columns and corrupt the output.
      2. Helium condensation — exit static temperature must stay above
         CoolProp saturation temperature at exit pressure, with a 2 K margin.
    """
    warnings_issued = False

    # 1. Parser overflow
    T_throat_R = float(T0_rankine) * (2 / (gamma_val + 1))
    PARSER_LIMIT_R = 999.9
    if T_throat_R >= PARSER_LIMIT_R:
        T0_limit_R = PARSER_LIMIT_R / (2 / (gamma_val + 1))
        print(f"\n  WARNING [parser overflow]: throat edge temp = {T_throat_R:.1f} R  "
              f"(limit {PARSER_LIMIT_R:.0f} R).\n"
              f"  Boundary-layer output will be corrupt. "
              f"Keep T0 < {T0_limit_R:.0f} R  (~{T0_limit_R/1.8:.0f} K).")
        warnings_issued = True

    # 2. Condensation at nozzle exit (coldest point)
    T0_K  = float(T0_rankine) / 1.8
    P0_Pa = float(P0_psi) * 6894.76
    iso   = 1 + (gamma_val - 1) / 2 * mach**2
    T_exit_K  = T0_K  / iso
    P_exit_Pa = P0_Pa / iso ** (gamma_val / (gamma_val - 1))
    MARGIN_K = 2.0
    try:
        T_sat_K = cp.PropsSI('T', 'P', P_exit_Pa, 'Q', 0, 'Helium')
        if T_exit_K < T_sat_K + MARGIN_K:
            T0_min_K = (T_sat_K + MARGIN_K) * iso
            print(f"\n  WARNING [condensation]: exit static temp = {T_exit_K:.2f} K  "
                  f"(sat. temp = {T_sat_K:.2f} K at {P_exit_Pa:.2f} Pa).\n"
                  f"  Helium may condense. "
                  f"Increase T0 above {T0_min_K:.0f} K to keep a {MARGIN_K} K margin.")
            warnings_issued = True
    except Exception:
        pass  # CoolProp may not have saturation data at very low pressures

    if not warnings_issued:
        print(f"  Feasibility OK:  T_throat = {T_throat_R:.1f} R  |  "
              f"T_exit = {T_exit_K:.2f} K  (P_exit = {P_exit_Pa:.2f} Pa)")


def write_ansys_points(filename, arr, append=False):
    """Write nozzle boundary points in ANSYS point-cloud format (x,y,z)."""
    mode = 'a' if append else 'w'
    with open(filename, mode) as f:
        for x, y in arr:
            f.write(f"{x:.6f},{y:.6f},0\n")


# ── Gas properties ────────────────────────────────────────────────────────────

print(f"Mach: {dmach}")
print(f"T0 = {T0:.4f}   P0 = {P0:.4f}")
check_feasibility(T0.magnitude, P0.magnitude, dmach)

# Sutherland viscosity fit to CoolProp data over [T_fit_low, T_fit_high] K
P_ref  = 1.01325e5   # [Pa]  reference pressure for property lookup (1 atm)
T_avg  = (T_fit_low + T_fit_high) / 2
temps      = np.linspace(T_fit_low, T_fit_high, num=600)
viscosities = [State(fluid=fluid, T=T1, P=P_ref).V for T1 in temps]
(b_He, S_He), _ = curve_fit(sutherlands, xdata=temps, ydata=viscosities)

b_He_SI  = b_He * (ureg.pascal * ureg.second / ureg.degK**0.5)
b_He_IMP = b_He_SI.to(ureg.lbf * ureg.second / (ureg.foot**2 * ureg.degR**0.5))
S_He_SI  = S_He * ureg.degK
S_He_IMP = S_He_SI.to(ureg.degR)
# Note: Sutherland's law has ~25% error below 50 K, ~9% at 100 K, ~2% above 200 K.
# Helium in this nozzle reaches very low static temperatures, so BL viscosity
# near the exit carries significant uncertainty.

ref_state  = State(fluid=fluid, T=T_avg, P=P_ref)
gamma      = ref_state.Cpmass / ref_state.Cvmass
R_gas_SI   = ref_state.gas_constant / ref_state.molarmass * ureg.J / ureg.kg / ureg.K
R_gas_IMP  = R_gas_SI.to(ureg.ft**2 / (ureg.s**2 * ureg.degR))
Z_gas      = ref_state.Z
TBLRF      = ref_state.Prandtl ** (1/3)  # turbulent BL recovery factor

props_table = PrettyTable(["Property", "Value", "Unit"])
for name, val, unit in [
    ("Gamma",                                  gamma,             "Dimensionless"),
    ("Gas Constant",                           R_gas_IMP.magnitude, str(R_gas_IMP.units)),
    ("Compressibility Factor",                 Z_gas,             "Dimensionless"),
    ("Turbulent BL Recovery Factor",           TBLRF,             "Dimensionless"),
    ("Sutherland Constant  b",                 b_He_IMP.magnitude, str(b_He_IMP.units)),
    ("Sutherland Temperature  S",              S_He_IMP.magnitude, str(S_He_IMP.units)),
]:
    props_table.add_row([name, val, unit])
    props_table.add_divider()
print(props_table)


# ── Contur input cards ────────────────────────────────────────────────────────

c = ConturSettings()

# Card 1
c["ITLE"] = f"Mach {dmach}"
c["JD"]   = 0        # 0 = axisymmetric, -1 = planar

# Card 2 — gas properties (derived above from CoolProp + Sutherland fit)
c["GAM"]  = gamma
c["AR"]   = R_gas_IMP.magnitude   # ft²/s²/R
c["ZO"]   = Z_gas
c["RO"]   = TBLRF
c["VISC"] = b_He_IMP.magnitude    # Sutherland b  [lbf·s/(ft²·R^0.5)]
c["VISM"] = S_He_IMP.magnitude    # Sutherland S  [R]
c["SFOA"] = 0

# Card 3 — key design parameters
c["ETAD"]  = 60               # 60 = full radial flow (standard for M > 5)
c["RC"]    = 6                # throat radius of curvature [× throat radius]; Sivells: 5.5–6.0
c["FMACH"] = 0                # unused when ETAD = 60
c["BMACH"] = 0.85 * dmach     # unused when ETAD = 60
c["CMC"]   = dmach            # design Mach number
c["SF"]    = throat_radius.magnitude   # throat radius [in]

# Card 4 — solver grid  (Sivells AEDC-TR-78-63; reference: M6.5 example uses MT=61,LR=-45,NX=18)
# Rules: MT/MD odd ≤ 125; ND ≤ 150; |LR| + NT ≤ 149
c["MT"] = 101   # points on initial expansion characteristic CD
c["NT"] = 61    # points on transonic axis IE         (45 + 61 = 106 ≤ 149)
c["IX"] = 0     # 4th-degree velocity distribution    (recommended with ETAD=60)
c["IN"] = 10    # downstream 2nd-derivative control   (Sivells recommends 10)
c["IQ"] = 0     # 0 = complete contour
c["MD"] = 101   # points on downstream characteristic AB
c["ND"] = 121   # points on axis BC
c["NF"] = -101  # points on characteristic EG (negative = downstream only)
c["MP"] = 0
c["MQ"] = 0
c["JB"] = 1     # BL iterations before spline fit     (Sivells recommends 1)
c["JX"] = 0     # spline fit after inviscid calc
c["JC"] = 1
c["IT"] = 0
c["LR"] = -45   # throat characteristic points; negative prints transonic solution
c["NX"] = 18    # logarithmic upstream spacing         (Sivells example value)

# Card 6 — stagnation and heat transfer
c["PPQ"]  = (P0 * ureg.pascal).to('psi').magnitude              # stagnation pressure [psia]
c["TO"]   = (T0 * ureg.degK).to(ureg.degR).magnitude            # stagnation temperature [R]
c["TWT"]  = (T_wall * ureg.degK).to(ureg.degR).magnitude        # wall temperature [R]
c["TWAT"] = (T_wall * ureg.degK).to(ureg.degR).magnitude        # water-cooling temp [R]

# Card 7 — interpolation output range
c["XLOW"] = XLOW
c["XEND"] = XEND
c["XINC"] = XINC


# ── Run Contur ────────────────────────────────────────────────────────────────

os.makedirs('inputcards', exist_ok=True)
os.makedirs('outputs', exist_ok=True)

c.print_to_input(file_name=f'm{dmach:.1f}.txt', output_directory='inputcards')

ca  = ConturApplication(timeout=600)
res = ca.batch_input_folder('inputcards', output_dir='outputs')  # type: ignore

if not res:
    raise RuntimeError(
        "Contur produced no output. Check that contur.exe ran successfully "
        "and that the input cards in 'inputcards/' are valid."
    )

output_dir = os.path.join('outputs', f'nozzle_M{dmach:.1f}_T{int(T0.magnitude)}R')
save_all(res[0], output_dir)

ExpansionCoords = res[0].SuperBetterCoordinates[1:]
ExpansionCoords = np.concatenate(([[0, throat_radius.magnitude]], ExpansionCoords))


# ── Contraction geometry (cubic Bézier) ──────────────────────────────────────

node1 = (-contraction_length, pipe_width / 2)
ctrl1 = (-contraction_length / 2, node1[1])
node2 = (0, throat_radius.magnitude)
ctrl2 = (-contraction_length / 2, node2[1])
curve_points = cubic_bezier([node1, ctrl1, ctrl2, node2], num=125)


# ── Derived quantities ────────────────────────────────────────────────────────

print(f"Mass flow at throat: {mass_flow(radius=throat_radius, mach=1)}")


# ── Write ANSYS contour file ──────────────────────────────────────────────────

ansys_file = f'AutoContourM{dmach:.1f}.txt'

write_ansys_points(ansys_file, [[-contraction_length, 0],
                                 [-contraction_length, pipe_width / 2]], append=False)
write_ansys_points(ansys_file, curve_points,    append=True)
write_ansys_points(ansys_file, ExpansionCoords, append=True)
write_ansys_points(ansys_file, [ExpansionCoords[-1], [XEND, 0]], append=True)
write_ansys_points(ansys_file, [[XEND, 0], [-contraction_length, 0]], append=True)
