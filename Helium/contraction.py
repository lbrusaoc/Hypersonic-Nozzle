
import numpy as np
import matplotlib.pyplot as plt
import math
from math import sqrt



T0 = 900 # Kelvin
P0 = 20e5 # Pascal (1 bar = 1e5 Pa)

R = 2077.2636899696745 # J / K.kg
gamma = 1.666549332667606



def mass_flow(mach, radius = None, area = None):
    if (radius is None) and (area is None):
        raise ValueError("You must supply either radius or area.")
    if (radius is not None) and (area is not None):
        raise ValueError("Provide only one: radius OR area, not both.")
    if radius is not None:
        area = math.pi * radius**2
    
    return (area*P0/sqrt(T0)) * (sqrt(gamma/R)*mach) * (1+0.5*(gamma-1)*mach**2)**(-(gamma+1)/(2*(gamma-1)))


print(mass_flow(radius=0.001905,mach=1), " kg/s")


import bezier
# Define nodes using your method
node1 = np.array([0.0, 5])
ctrl1 = np.array([5, node1[1]])

node2 = np.array([10, 0.0756])
ctrl2 = np.array([5, node2[1]])

# Stack into a single 2×4 array for bezier.Curve
nodes = np.column_stack([node1, ctrl1, ctrl2, node2])

# Create cubic Bézier curve
curve = bezier.Curve(nodes, degree=3)

# Plot
s_vals = np.linspace(0.0, 1.0, 125)
curve_points = curve.evaluate_multi(s_vals)

# ----- Comma-separated output for Excel -----
print(",".join(f"{v-10:.6f}" for v in curve_points[0, :]))  # x-values
print()
print(",".join(f"{v:.6f}" for v in curve_points[1, :]))  # y-values
# --------------------------------------------

plt.plot(curve_points[0, :], curve_points[1, :], label="Bezier curve")
plt.scatter(nodes[0, :], nodes[1, :], color='red', label='Control points')
plt.legend()
plt.axis("equal")
plt.show()
