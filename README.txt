════════════════════════════════════════════════════════════════════
   HYPERSONIC NOZZLE DESIGN TOOL — README
   Mach 18 Helium Wind Tunnel Nozzle — Senior Design Project
════════════════════════════════════════════════════════════════════

  Contents
  ────────
  1. What this project does
  2. Folder structure
  3. Getting the code with Git (FIRST TIME ONLY)
  4. Setup instructions (FIRST TIME ONLY)
  5. How to run the code
  6. How to change the design parameters
  7. Making and saving changes with Git
  8. Code explanation — runALL.py
  9. Code explanation — Isentropic-Analysis.py
  10. Output files explained
  11. Troubleshooting


────────────────────────────────────────────────────────────────────
1. WHAT THIS PROJECT DOES
────────────────────────────────────────────────────────────────────

This tool designs the internal contour (shape) of an axisymmetric
(round) supersonic/hypersonic wind tunnel nozzle for helium gas.

Given a target Mach number, throat size, and stagnation conditions,
it:
  - Computes helium gas properties (viscosity, gamma, etc.)
  - Runs the Sivells method-of-characteristics solver (via the
    "conturpy" wrapper around a Fortran executable called contur.exe)
  - Calculates the full nozzle wall coordinates including a boundary
    layer correction
  - Generates a cubic Bezier contraction section
  - Exports wall coordinates for ANSYS (CFD software) import
  - Produces diagnostic plots (contours, boundary layer thickness, etc.)

The second script (Isentropic-Analysis.py) is a quick survey tool:
it sweeps across Mach numbers 4–20 and reports exit conditions
(temperature, pressure, Reynolds number, etc.) assuming ideal
isentropic flow.


────────────────────────────────────────────────────────────────────
2. FOLDER STRUCTURE
────────────────────────────────────────────────────────────────────

  Hypersonic-Nozzle/
  ├── README.txt              ← You are here
  ├── setup.bat               ← Double-click to install everything
  ├── requirements.txt        ← List of Python packages needed
  ├── SETUP.txt               ← Original manual setup notes
  │
  ├── conturpy/               ← Python wrapper for the Sivells solver
  │   ├── conturpy/           ← Library source code
  │   │   ├── __init__.py
  │   │   ├── create_input_cards.py  ← Builds Fortran input files
  │   │   ├── run_contur.py          ← Calls contur.exe
  │   │   ├── read_output.py         ← Parses Fortran output
  │   │   └── plot_results.py        ← Generates diagnostic plots
  │   └── setup.py            ← conturpy package definition
  │
  ├── Helium/
  │   ├── runALL.py           ← MAIN SCRIPT: designs the nozzle
  │   ├── Isentropic-Analysis.py  ← Survey script across Mach range
  │   └── outputs/            ← Created automatically when you run
  │       └── nozzle_M18.0_T900R/   ← Results for each run
  │
  └── Air/                    ← Earlier air-nozzle work (for reference)


────────────────────────────────────────────────────────────────────
3. GETTING THE CODE WITH GIT (FIRST TIME ONLY)
────────────────────────────────────────────────────────────────────

Git is a version control system — it tracks changes to files over
time, lets multiple people collaborate, and lets you safely undo
mistakes. Think of it as a detailed save-history for the entire
project folder.

What you need to know up front:
  • The project lives in a "repository" (repo) hosted on GitHub.
  • "Cloning" downloads a full copy of the repo to your machine.
  • "Committing" saves a snapshot of your changes locally.
  • "Pushing" uploads your commits back to GitHub.
  • "Pulling" downloads other people's latest commits to your machine.

─────────────────────
Step 1 — Install Git
─────────────────────
  1. Go to: https://git-scm.com/download/win
  2. Download and run the installer.
  3. Accept all defaults. When asked about the default editor,
     choose "Visual Studio Code" if it appears in the list.
  4. When the installer finishes, open a NEW terminal and type:

       git --version

     You should see something like "git version 2.45.2". If you
     get an error, restart your computer and try again.

──────────────────────────────────────────────
Step 2 — Configure Git with your name and email
──────────────────────────────────────────────
  Run these two commands once (replace the placeholders):

    git config --global user.name  "Your Name"
    git config --global user.email "you@example.com"

  Git stamps every commit you make with this information.

────────────────────────────────────
Step 3 — Clone the repository
────────────────────────────────────
  "Cloning" creates a local copy of the project on your machine.

  1. On the GitHub page for this project, click the green
     "< > Code" button and copy the URL shown under "HTTPS".
     It will look like:
       https://github.com/OWNER/Hypersonic-Nozzle.git

  2. Open a terminal (Win + R, type "cmd", press Enter).

  3. Navigate to the folder where you want the project to live.
     For example, to put it on your Desktop:

       cd C:\Users\YourName\Desktop

  4. Run the clone command with the URL you copied:

       git clone https://github.com/OWNER/Hypersonic-Nozzle.git

  5. Git will create a new folder called "Hypersonic-Nozzle" and
     download all the code into it. This takes under a minute.

  6. Enter the folder:

       cd Hypersonic-Nozzle

  You now have the full project. Continue to Section 4 to set up
  the Python environment.

────────────────────────────────────────────────────────────────────
4. SETUP INSTRUCTIONS (FIRST TIME ONLY)
────────────────────────────────────────────────────────────────────

Prerequisites
─────────────
  • Windows 10 or 11
  • Python 3.10 or newer
      → Download from: https://www.python.org/downloads/
      → During install, CHECK the box "Add Python to PATH"
  • VS Code (recommended editor)
      → Download from: https://code.visualstudio.com/

Automated Setup (recommended)
──────────────────────────────
  1. Open the "Hypersonic-Nozzle" folder in File Explorer
  2. Double-click "setup.bat"
  3. A black terminal window will open and install everything.
     This takes 2–5 minutes depending on internet speed.
  4. When it says "Setup complete!", close the window.

  That's it. The script:
    - Creates an isolated Python environment (.venv folder)
    - Installs all required packages (numpy, scipy, CoolProp, etc.)
    - Installs the local "conturpy" library

Configure VS Code to use the environment
──────────────────────────────────────────
  After setup.bat finishes, tell VS Code which Python to use:

  1. Open VS Code
  2. Open the Hypersonic-Nozzle folder (File → Open Folder)
  3. Press  Ctrl + Shift + P
  4. Type:  Python: Select Interpreter    then press Enter
  5. Choose the option that shows ".venv" in its path
     (something like ".venv\Scripts\python.exe")

  You only need to do this once per machine.


────────────────────────────────────────────────────────────────────
5. HOW TO RUN THE CODE
────────────────────────────────────────────────────────────────────

Main nozzle design (runALL.py)
───────────────────────────────
  1. Open VS Code
  2. Open  Helium/runALL.py
  3. Click the triangle "Run" button in the top-right corner
     (or press Ctrl+F5)
  4. Watch the terminal at the bottom for progress messages
  5. When finished, output files appear in  Helium/outputs/

Isentropic survey (Isentropic-Analysis.py)
───────────────────────────────────────────
  1. Open  Helium/Isentropic-Analysis.py
  2. Run it the same way
  3. A table prints to the terminal and three plot windows open

Note: runALL.py calls the Fortran solver (contur.exe) which can
take 30–120 seconds. The terminal will appear to pause — this is
normal.


────────────────────────────────────────────────────────────────────
6. HOW TO CHANGE THE DESIGN PARAMETERS
────────────────────────────────────────────────────────────────────

All user-adjustable settings are at the TOP of runALL.py, clearly
marked with a banner:

  # ══════ USER PARAMETERS — edit here ══════

The parameters you can change:

  fluid             The working gas. Keep as 'Helium' for this nozzle.

  dmach             Design Mach number (e.g., 18 for Mach 18).

  throat_radius     Radius of the nozzle throat in inches.
                    Written as:  0.5 * ureg.inch  (= half an inch)

  T0                Stagnation (reservoir) temperature in Kelvin.
                    500 K is a typical starting value.

  P0                Stagnation pressure in Pascals.
                    20e5 = 2,000,000 Pa = ~20 atm.

  T_wall            Nozzle wall temperature in Kelvin.
                    300 K assumes no water cooling.

  pipe_width        Inner diameter of the upstream supply pipe [in].

  contraction_length  Length of the contraction section [in].

  XLOW, XEND, XINC  Range and step size for the output contour [in].
                    Increase XEND if the nozzle is longer than 60 in.

After changing any parameter, just save the file (Ctrl+S) and run
it again. A new output folder is created automatically for each run
so previous results are not overwritten.


────────────────────────────────────────────────────────────────────
7. MAKING AND SAVING CHANGES WITH GIT
────────────────────────────────────────────────────────────────────

Once you have the code cloned and have made changes, use Git to
save and share them. The daily workflow has three steps:
  Pull → Edit → Add → Commit → Push

─────────────────────────────────────────────────────────
Before you start working — pull the latest changes
─────────────────────────────────────────────────────────
  Always start a work session by downloading any updates that
  others may have pushed since you last worked:

    git pull

  This keeps your local copy in sync with GitHub. Do this every
  time before editing files.

─────────────────────────────────────────────────────────
See what has changed
─────────────────────────────────────────────────────────
  At any point, run this to see which files you have modified:

    git status

  Files listed under "Changes not staged for commit" have been
  edited. Files listed under "Untracked files" are new and Git
  does not know about them yet.

  To see exactly what changed inside a file:

    git diff Helium/runALL.py

─────────────────────────────────────────────────────────
Stage the files you want to save (git add)
─────────────────────────────────────────────────────────
  "Staging" tells Git which changed files to include in your next
  snapshot. You can stage individual files:

    git add Helium/runALL.py

  Or stage everything that changed at once:

    git add .

  Note: the outputs/ folder is excluded from Git tracking on
  purpose (it is listed in .gitignore) because those files are
  large and can be regenerated by running the code.

─────────────────────────────────────────────────────────
Save a snapshot (git commit)
─────────────────────────────────────────────────────────
  A "commit" is a permanent record of your staged changes.
  Always include a short message describing WHAT you changed
  and WHY:

    git commit -m "Increase throat radius to 0.6 in for new test"

  Good messages make it easy to find a specific change later.
  Bad messages like "update" or "fix" are unhelpful.

  Verify the commit was created:

    git log --oneline

  You will see a list of recent commits with their short IDs.

─────────────────────────────────────────────────────────
Upload your commits to GitHub (git push)
─────────────────────────────────────────────────────────
  Once you have one or more commits, send them to GitHub:

    git push

  After this, anyone who clones or pulls the repo will see
  your changes.

─────────────────────────────────────────────────────────
Working on your own branch (recommended for big changes)
─────────────────────────────────────────────────────────
  A "branch" is an independent copy of the code where you can
  experiment without affecting the main version. This is the
  safest way to make large changes.

  Create a new branch and switch to it:

    git checkout -b my-feature-name

  Work normally (edit → add → commit). When finished, push
  the branch to GitHub:

    git push -u origin my-feature-name

  On GitHub you can then open a "Pull Request" to propose
  merging your branch into the main branch.

  To switch back to the main branch at any time:

    git checkout main

─────────────────────────────────────────────────────────
Undo a mistake
─────────────────────────────────────────────────────────
  Discard unsaved edits to a file (restores last committed version):

    git restore Helium/runALL.py

  Undo the last commit (keeps your file changes, removes the commit):

    git reset HEAD~1

  IMPORTANT: never use "git reset --hard" unless you are certain —
  it permanently discards changes.

─────────────────────────────────────────────────────────
Quick reference cheat sheet
─────────────────────────────────────────────────────────
  git clone <url>          Download the repo for the first time
  git pull                 Get the latest changes from GitHub
  git status               Show what files have changed
  git diff <file>          Show the exact lines that changed
  git add <file>           Stage a file for commit
  git add .                Stage all changed files
  git commit -m "message"  Save a snapshot with a description
  git push                 Upload commits to GitHub
  git log --oneline        View recent commit history
  git checkout -b <name>   Create and switch to a new branch
  git checkout main        Switch back to the main branch
  git restore <file>       Discard unsaved changes in a file


────────────────────────────────────────────────────────────────────
8. CODE EXPLANATION — runALL.py
────────────────────────────────────────────────────────────────────

Section 1: Imports
──────────────────
  The script loads external libraries:
    numpy    — array math (think of it as a powerful spreadsheet)
    scipy    — curve fitting (used to fit the viscosity model)
    pint     — unit conversions (inches ↔ feet, Kelvin ↔ Rankine)
    CoolProp — accurate gas property database
    conturpy — wrapper for the Sivells Fortran nozzle solver
    prettytable — prints nicely formatted tables to the terminal

Section 2: The State class (lines 47–78)
──────────────────────────────────────────
  A convenience wrapper around CoolProp.
  Give it two known properties (e.g., temperature and pressure) and
  it automatically looks up everything else: density, viscosity,
  speed of sound, specific heats, compressibility, Prandtl number.

  Example usage:
      s = State('Helium', T=300, P=101325)
      print(s.Cpmass)  # prints specific heat at 300 K, 1 atm

Section 3: Helper functions (lines 83–183)
───────────────────────────────────────────
  sutherlands(T, b, S)
    Implements the modified Sutherland viscosity law from Sivells.
    Viscosity is hard to measure at extreme temperatures, so this
    gives a smooth formula that fits CoolProp data. Below the
    Sutherland temperature S it uses a linear approximation
    instead of the power law (avoids errors at very low T).

  cubic_bezier(points, num)
    Draws a smooth cubic Bezier curve through 4 control points.
    Used to shape the contraction section from the supply pipe
    down to the nozzle throat. The result is a smooth, continuous
    curve with no sharp corners.

  mass_flow(mach, radius, area)
    Calculates mass flow rate using the isentropic flow equation.
    Useful for sizing the supply system. Requires either a throat
    radius or area as input.

  check_feasibility(T0, P0, mach)
    Runs two safety checks before the main solver:
      1. Parser overflow — the Fortran code uses fixed-width text
         columns. If the throat temperature exceeds ~999 R the
         numbers run into each other and corrupt the output.
         This check warns you before that happens.
      2. Helium condensation — helium turns liquid below ~4 K.
         If exit static temperature drops below the saturation
         point, the flow would change phase. This check warns
         you to increase T0 if needed.

  write_ansys_points(filename, arr, append)
    Writes (x, y, z) coordinates in a CSV-like format that ANSYS
    Fluent can import directly as a point cloud for geometry
    creation. z is always 0 because the contour is 2D; ANSYS
    revolves it into a 3D nozzle.

Section 4: Gas properties (lines 188–227)
──────────────────────────────────────────
  Converts T0 and P0 to imperial units (Rankine, psia) because
  the Fortran solver was written in imperial.

  Fits Sutherland coefficients b and S by calling CoolProp for
  helium viscosity at 600 temperature points and finding the
  best-fit curve. scipy's curve_fit does the optimization.

  Prints a summary table of key gas properties:
    Gamma  — ratio of specific heats (≈ 5/3 for monatomic helium)
    R      — gas constant
    Z      — compressibility (how much helium deviates from ideal)
    TBLRF  — turbulent boundary layer recovery factor (Pr^(1/3))
    b, S   — Sutherland viscosity constants in imperial units

Section 5: Contur input cards (lines 232–282)
──────────────────────────────────────────────
  Builds the "input deck" for the Sivells Fortran solver.
  These are configuration parameters documented in:
    Sivells, J.C., AEDC-TR-78-63 (1978)

  Key cards:
    ETAD = 60  — tells the solver to use the "full radial flow"
                 starting solution, standard for Mach > 5.
    RC = 6     — throat curvature radius, 6× the throat radius.
                 Sivells recommends 5.5–6.0 for smooth flow.
    CMC        — design Mach number.
    MT, MD     — number of characteristic mesh points.
    LR = -45   — negative sign tells it to also print the
                 transonic (near-throat) solution to a file.

Section 6: Run Contur (lines 288–308)
───────────────────────────────────────
  Creates output folders, writes the input cards to text files,
  then calls ConturApplication which launches contur.exe and
  waits for it to finish (up to 10 minutes timeout).

  If contur.exe produces no output, an error is raised. This
  usually means the input parameters are out of bounds for the
  solver — check the feasibility warnings printed earlier.

  save_all() exports all results (CSVs, plots, coordinates) into
  the output folder.

Section 7: Contraction geometry (lines 311–315)
─────────────────────────────────────────────────
  Defines 4 Bezier control points:
    node1 — start of contraction (at the supply pipe wall)
    ctrl1 — first handle (horizontal, extends contraction tangent)
    ctrl2 — second handle (vertical, approaches throat tangent)
    node2 — end at the throat
  The curve is evaluated at 125 points.

Section 8: ANSYS export (lines 325–333)
─────────────────────────────────────────
  Assembles the full nozzle boundary as a point list:
    • Two corner points at the inlet face (closes the geometry)
    • Bezier contraction curve (125 points)
    • Expansion section from the Fortran solver
    • Closing points at the exit and axis
  Writes everything to  AutoContourM18.0.txt  in imperial inches.


────────────────────────────────────────────────────────────────────
9. CODE EXPLANATION — Isentropic-Analysis.py
────────────────────────────────────────────────────────────────────

This script is a quick parametric survey — no nozzle geometry is
designed here. It answers the question: "What would the flow look
like at various Mach numbers?"

  Lines 1–77   Same State class as runALL.py (CoolProp wrapper).

  Lines 79–95  Defines a sweep of Mach numbers from 4 to 20 (17
               points). Sets fixed T0 = 500 K, P0 = 2 MPa.
               Calls pygasflow's isentropic_solver to get T/T0,
               P/P0, and A/A* ratios for each Mach number.
               Then computes actual exit T, P, and exit diameter
               from the isentropic relations.

  Lines 98–123 Loops over each Mach number, creates a helium State
               at the exit conditions, and extracts density,
               speed of sound, and viscosity from CoolProp.
               Computes Reynolds number per unit length:
                   Re/m = rho * a * M / mu
               This tells you how turbulent the flow is likely
               to be per meter of nozzle length.

  Lines 132–228 Prints a formatted table and creates three plots:
               • Nozzle exit diameter vs. Mach
               • Exit temperature and pressure vs. Mach
               • Reynolds number per unit length vs. Mach
               • (second figure) Viscosity, speed of sound,
                 density vs. Mach


────────────────────────────────────────────────────────────────────
10. OUTPUT FILES EXPLAINED
────────────────────────────────────────────────────────────────────

After running runALL.py, look in:
  Helium/outputs/nozzle_M18.0_T<temperature>R/

  Contours.png
    Wall contour of the nozzle (x = axial, y = radial), showing
    the shape from throat to exit.

  Boundary_Layer_Thickness.png
    Displacement thickness δ* along the nozzle wall. This is how
    much the effective flow area is reduced by the slower gas
    stuck to the wall. The solver accounts for this automatically.

  Boundary_Layer_Temperature.png
    Wall temperature distribution along the nozzle. Used to
    assess thermal loads on the nozzle material.

  Flow_Angles.png
    Flow angle (degrees from axis) along the nozzle. Should
    approach 0° at the exit — that means the flow is parallel
    to the axis, which is the design goal.

  CoordinatesAndDerivatives_0.csv
    The actual (x, y) wall coordinates from the solver, plus
    the slope dy/dx at each point. Import into Excel or MATLAB
    to post-process.

  BoundaryLayerCalculations_*.csv
    Detailed boundary layer data at each station along the wall.

  IntermediateLeftCharacteristic_*.csv
    Intermediate computation files from the method of
    characteristics. Rarely needed but kept for debugging.

  AutoContourM18.0.txt  (in the Helium/ folder, not outputs/)
    Point cloud of the full nozzle boundary in ANSYS format.
    Import this into ANSYS SpaceClaim or DesignModeler as a
    "point cloud" and use "3D Curve" to fit a spline, then
    revolve for the full 3D nozzle.

  Helium/inputcards/m18.0.txt
    The input deck sent to the Fortran solver. Useful to verify
    what parameters were actually used.


────────────────────────────────────────────────────────────────────
11. TROUBLESHOOTING
────────────────────────────────────────────────────────────────────

Problem: setup.bat says "Python was not found"
  → Install Python from https://www.python.org/downloads/
    Make sure to check "Add Python to PATH" during installation.

Problem: setup.bat fails at step 1 (creating virtual environment)
  → You may not have Python 3.10 installed.
    Download the 3.10 installer from:
    https://www.python.org/downloads/release/python-31011/
    Run setup.bat again after installing.

Problem: "Set-ExecutionPolicy" error in PowerShell
  → Windows is blocking script execution.
    Open PowerShell as Administrator, run:
        Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
    Then run setup.bat again.

Problem: "Contur produced no output" error
  → The Fortran solver rejected your input parameters.
    Check the feasibility warnings printed before the error.
    Common causes:
      • T0 too high (parser overflow) — lower T0
      • T0 too low (condensation risk) — raise T0
      • Mach number extreme — solver works best M = 5–20

Problem: VS Code shows "ModuleNotFoundError"
  → The wrong Python interpreter is selected.
    Press Ctrl+Shift+P → "Python: Select Interpreter"
    Choose the one with ".venv" in the path.

Problem: Plots don't appear
  → Close any existing plot windows, then run again.
    Or try running from the VS Code terminal:
        python Helium/runALL.py

Problem: "CoolProp" import error
  → Run setup.bat again. If it still fails, try manually:
    Open a terminal in the Hypersonic-Nozzle folder and run:
        .venv\Scripts\activate
        pip install CoolProp

────────────────────────────────────────────────────────────────────
  Contact: Lucas Brusa-OConnell — Senior Design Project 2025-2026
════════════════════════════════════════════════════════════════════
