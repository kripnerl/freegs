#!/usr/bin/env python

# Options for setting toroidal current
from jtor import ConstrainPaxisIp

# Plasma equilibrium (Grad-Shafranov) solver
from equilibrium import Equilibrium

# Coils and current circuits
import machine

# Control algorithms to constrain the shape,location
import constraints

# Nonlinear solver
import picard

#########################################
# Create the machine, which specifies coil locations
# and equilibrium, specifying the domain to solve over

tokamak = machine.TestTokamak()

eq = Equilibrium(tokamak=tokamak,
                 Rmin=0.1, Rmax=2.0,    # Radial domain
                 Zmin=-1.0, Zmax=1.0,   # Height range
                 nx=65, ny=65)          # Number of grid points

#########################################
# Plasma profiles

jtor_func = ConstrainPaxisIp(1e4, # Plasma pressure on axis [Pascals]
                             1e6) # Plasma current [Amps]

#########################################
# Coil current constraints
#
# Specify locations of the X-points
# to use to constrain coil currents

xpoints = [(1.1, -0.8),   # (R,Z) locations of X-points
           (1.1, 0.8)]

constrain = lambda eq : constraints.xpointConstrain(eq, xpoints)

#########################################
# Nonlinear solve

picard.solve(eq,           # The equilibrium to adjust
             jtor_func,    # The toroidal current profile function
             constrain)    # Constraint function to set coil currents

# eq now contains the solution

print("Done!")

tokamak.printCurrents()

##############################################
# Final plot

from plotting import plotEquilibrium
import matplotlib.pyplot as plt

# Get the solution 
psi = eq.psi()

import critical
opt, xpt = critical.find_critical(eq.R, eq.Z, psi)
psi_bndry = xpt[0][2]

ax = plotEquilibrium(eq.R, eq.Z, psi)
for r,z,_ in xpt:
    ax.plot(r,z,'ro')
for r,z,_ in opt:
    ax.plot(r,z,'go')
psi_bndry = xpt[0][2]
sep_contour=ax.contour(eq.R, eq.Z,psi, levels=[psi_bndry], colors='r')

plt.show()