import math
import numpy as np
import matplotlib.pyplot as plt

from pydrake.examples.pendulum import (PendulumPlant, PendulumState)
from pydrake.all import (DirectCollocation, PiecewisePolynomial,
                         SolutionResult)

plant = PendulumPlant()
context = plant.CreateDefaultContext()

kNumTimeSamples = 21
kMinimumTimeStep = 0.2
kMaximumTimeStep = 0.5

dircol = DirectCollocation(plant, context, kNumTimeSamples, kMinimumTimeStep,
                           kMaximumTimeStep)

dircol.AddEqualTimeIntervalsConstraints()

kTorqueLimit = 3.0  # N*m.
u = dircol.input()
dircol.AddConstraintToAllKnotPoints(-kTorqueLimit <= u[0])
dircol.AddConstraintToAllKnotPoints(u[0] <= kTorqueLimit)

initial_state = PendulumState()
initial_state.set_theta(0.0)
initial_state.set_thetadot(0.0)
dircol.AddBoundingBoxConstraint(initial_state.get_value(),
                                initial_state.get_value(),
                                dircol.initial_state())
# More elegant version is blocked on drake #8315:
# dircol.AddLinearConstraint(dircol.initial_state()
#                               == initial_state.get_value())

final_state = PendulumState()
final_state.set_theta(math.pi)
final_state.set_thetadot(0.0)
dircol.AddBoundingBoxConstraint(final_state.get_value(),
                                final_state.get_value(),
                                dircol.final_state())
# dircol.AddLinearConstraint(dircol.final_state() == final_state.get_value())

R = 10  # Cost on input "effort".
dircol.AddRunningCost(R*u[0]**2)

initial_x_trajectory = \
    PiecewisePolynomial.FirstOrderHold([0., 4.],
                                       [initial_state.get_value(),
                                        final_state.get_value()])
dircol.SetInitialTrajectory(PiecewisePolynomial(), initial_x_trajectory)

result = dircol.Solve()
assert(result == SolutionResult.kSolutionFound)

x_trajectory = dircol.ReconstructStateTrajectory()

from visualizer import PendulumVisualizer
vis = PendulumVisualizer()
ani = vis.animate(x_trajectory, repeat=True)

x_knots = np.hstack([x_trajectory.value(t) for t in
                     np.linspace(x_trajectory.start_time(),
                                 x_trajectory.end_time(), 100)])
plt.figure()
plt.plot(x_knots[0, :], x_knots[1, :])

plt.show()