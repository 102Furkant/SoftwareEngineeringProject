import numpy as np
import pytest
from simulation import FluidSimulator

def test_initial_state_is_empty():
    sim = FluidSimulator(nx=10, ny=10)
    assert np.all(sim.p == 0.0)
    assert np.all(sim.u == 0.0)
    assert np.all(sim.v == 0.0)
    # obstacle mask should be all False
    assert not sim.obstacle.any()

def test_set_obstacle_clears_fields():
    sim = FluidSimulator(nx=10, ny=10)
    # fill fields with non-zero
    sim.p[:] = 1.0
    sim.u[:] = 1.0
    sim.v[:] = 1.0

    mask = np.zeros((10, 10), dtype=bool)
    mask[3:7, 3:7] = True  # 4x4 square
    sim.set_obstacle(mask)
    # obstacle area must be 4×4
    assert mask.sum() == 16
    # fields inside obstacle must be zero
    assert np.all(sim.p[mask] == 0.0)
    assert np.all(sim.u[mask] == 0.0)
    assert np.all(sim.v[mask] == 0.0)

def test_step_without_injection_keeps_empty():
    sim = FluidSimulator(nx=8, ny=8)
    before = sim.p.copy()
    sim.step()
    assert np.allclose(sim.p, before)

def test_step_with_inflow():
    sim = FluidSimulator(nx=10, ny=10)
    sim.u[0, :] = 1.0  # Inflow at top
    sim.step()
    assert sim.u[0, :].max() > 0.0

def test_obstacle_remains_after_step():
    sim = FluidSimulator(nx=10, ny=10)
    mask = np.zeros((10, 10), dtype=bool)
    mask[2:5, 2:5] = True
    sim.set_obstacle(mask)
    sim.u[0, :] = 1.0  # Inflow at top
    sim.step()
    # Obstacle region remains zero
    assert np.all(sim.u[mask] == 0.0)
    assert np.all(sim.v[mask] == 0.0)
    assert np.all(sim.p[mask] == 0.0)

def test_custom_obstacle_mask():
    mask = np.array([
        [1, 0, 1],
        [0, 1, 0],
        [1, 0, 1]
    ], dtype=bool)
    sim = FluidSimulator(nx=3, ny=3)
    sim.p[:] = 1.0
    sim.u[:] = 1.0
    sim.v[:] = 1.0

    sim.set_obstacle(mask)
    # obstacle count matches
    assert mask.sum() == sim.obstacle.sum()
    # fields zeroed inside
    assert np.all(sim.p[mask] == 0.0)
    assert np.all(sim.u[mask] == 0.0)
    assert np.all(sim.v[mask] == 0.0)