import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# Gas properties (Helium)
# -----------------------------
gamma = 1.66

# -----------------------------
# Prandtl–Meyer functions
# -----------------------------
def nu(M):
    g = gamma
    return np.sqrt((g+1)/(g-1)) * np.arctan(
        np.sqrt((g-1)/(g+1)*(M**2 - 1))
    ) - np.arctan(np.sqrt(M**2 - 1))

def invert_nu(nu_target, M_guess=2.0):
    M = M_guess
    for _ in range(20):
        f = nu(M) - nu_target
        dnudM = np.sqrt(M**2 - 1) / (M*(1 + (gamma-1)/2*M**2))
        M -= f / dnudM
    return M

# -----------------------------
# Computational grid
# -----------------------------
N_stream = 40      # number of streamlines
N_x = 600          # marching steps
dx = 0.002         # marching step size (m)

# Streamfunction coordinate (normalized)
psi = np.linspace(0, 1.0, N_stream)

# -----------------------------
# Allocate fields
# -----------------------------
M = np.ones((N_x, N_stream))
theta = np.zeros((N_x, N_stream))
nu_field = np.zeros((N_x, N_stream))

x = np.zeros((N_x, N_stream))
r = np.zeros((N_x, N_stream))

# -----------------------------
# Initial conditions (throat)
# -----------------------------
# Define throat
r_throat = 0.00254/2  # meters
r[0, :] = r_throat * psi          # 0 at centerline, r_throat at outer streamline
theta[0, :] = 0.005 * psi         # small initial fan
M[0, :] = 1.01                    # slightly supersonic
nu_field[0, :] = nu(M[0, :])
x[0, :] = 0.0

# -----------------------------
# Prescribed centerline turning rate
# -----------------------------
theta_max = nu(18.0) / 2    # half-angle expansion
theta_centerline = np.linspace(0, theta_max, N_x)

# -----------------------------
# March downstream
# -----------------------------
for i in range(1, N_x):

    # Centerline condition
    theta[i, 0] = 0.0
    nu_field[i, 0] = nu_field[i-1, 0] + (theta_centerline[i] - theta_centerline[i-1])
    M[i, 0] = invert_nu(nu_field[i, 0], M[i-1, 0])

    # March across streamlines
    for j in range(1, N_stream):

        # Smooth turning across streamlines
        dtheta_dpsi = (theta[i-1, j] - theta[i-1, j-1]) / (psi[j] - psi[j-1])
        dtheta_dpsi = max(dtheta_dpsi, 0.0)  # enforce expansion only

        theta[i, j] = theta[i, j-1] + dtheta_dpsi * (psi[j] - psi[j-1])
        nu_field[i, j] = nu_field[i-1, j] + (theta[i, j] - theta[i-1, j])
        M[i, j] = invert_nu(nu_field[i, j], M[i-1, j])

    # Geometry update
    x[i, :] = x[i-1, :] + dx * np.cos(theta[i, :])
    r[i, :] = r[i-1, :] + dx * np.sin(theta[i, :])

# -----------------------------
# Plot nozzle contour
# -----------------------------
plt.figure(figsize=(10,4))
plt.plot(x[:, -1], r[:, -1], 'k', lw=2)
plt.plot(x[:, -1], -r[:, -1], 'k', lw=2)
plt.xlabel("x (m)")
plt.ylabel("r (m)")
plt.title("Axisymmetric Nozzle Contour (Streamfunction–Mach Method)")
plt.axis("equal")
plt.grid(True)
plt.show()

# -----------------------------
# Exit Mach profile
# -----------------------------
plt.figure()
plt.plot(psi, M[-1, :], lw=2)
plt.xlabel("Normalized Streamfunction ψ")
plt.ylabel("Mach number")
plt.title("Exit Mach Distribution")
plt.grid(True)
plt.show()