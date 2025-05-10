import numpy as np
import pytest
from simulation import FluidSimulator

def test_initial_state_is_empty():
    sim = FluidSimulator(width=10, height=10)
    assert np.all(sim.density == 0.0)
    assert np.all(sim.Vx == 0.0)
    assert np.all(sim.Vy == 0.0)
    # obstacle mask should be all False
    assert not sim.obstacle.any()

def test_set_obstacle_square_clears_fields():
    sim = FluidSimulator(width=10, height=10)
    # fill fields with non-zero
    sim.density[:] = 1.0
    sim.Vx[:] = 1.0
    sim.Vy[:] = 1.0

    sim.set_obstacle('square', size=4)
    mask = sim.obstacle
    # obstacle area must be 4×4
    assert mask.sum() == 16
    # density and velocities inside obstacle must be zero
    assert np.all(sim.density[mask] == 0.0)
    assert np.all(sim.Vx[mask] == 0.0)
    assert np.all(sim.Vy[mask] == 0.0)

def test_inject_top_and_left():
    sim = FluidSimulator(width=5, height=5)
    sim.inject(amount=2.5, direction='top')
    # top row, non-obstacle cells should have been increased
    top = sim.density[0]
    assert np.all(top == 2.5)

    sim = FluidSimulator(width=5, height=5)
    sim.inject(amount=1.0, direction='left')
    left = sim.density[:, 0]
    assert np.all(left == 1.0)

    # invalid direction raises
    with pytest.raises(ValueError):
        sim.inject(amount=1.0, direction='bottom')

def test_step_without_injection_keeps_empty():
    sim = FluidSimulator(width=8, height=8)
    before = sim.density.copy()
    sim.step(dt=0.1)
    assert np.allclose(sim.density, before)

def test_circle_obstacle_and_flow():
    sim = FluidSimulator(width=20, height=20)
    sim.set_obstacle('circle', radius=5)
    # obstacle region remains empty throughout
    for _ in range(5):
        sim.inject(amount=1.0, direction='top')
        sim.step(dt=0.05)
        assert np.all(sim.density[sim.obstacle] == 0.0)
    # ensure some fluid has entered the domain
    assert sim.density.max() > 0.0

def test_invalid_shape_in_set_obstacle():
    sim = FluidSimulator(width=10, height=10)
    with pytest.raises(ValueError):
        sim.set_obstacle('hexagon')

def test_custom_obstacle_mask():
    mask = [
        [1, 0, 1],
        [0, 1, 0],
        [1, 0, 1]
    ]
    sim = FluidSimulator(width=3, height=3)
    sim.density[:] = 1.0
    sim.Vx[:] = 1.0
    sim.Vy[:] = 1.0

    sim.set_obstacle('custom', mask=mask)
    mask_arr = np.array(mask, dtype=bool)
    # obstacle count matches
    assert mask_arr.sum() == sim.obstacle.sum()
    # fields zeroed inside
    assert np.all(sim.density[mask_arr] == 0.0)
    assert np.all(sim.Vx[mask_arr] == 0.0)
    assert np.all(sim.Vy[mask_arr] == 0.0)