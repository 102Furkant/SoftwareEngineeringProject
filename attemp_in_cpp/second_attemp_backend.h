#ifndef BACKEND_H
#define BACKEND_H

#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>

inline size_t idx(size_t i, size_t j, size_t nx) {
    return i * nx + j;
}

std::vector<double> laplacian(const std::vector<double>& field, size_t nx, size_t ny, double dx) {
    std::vector<double> lap(nx * ny, 0.0);
    
    for (size_t i = 1; i < ny - 1; ++i) {
        for (size_t j = 1; j < nx - 1; ++j) {
            lap[idx(i, j, nx)] = (
                field[idx(i-1, j, nx)] + field[idx(i+1, j, nx)] +
                field[idx(i, j-1, nx)] + field[idx(i, j+1, nx)] -
                4.0 * field[idx(i, j, nx)]
            ) / (dx * dx);
        }
    }
    
    return lap;
}

class FluidSimulator {
private:
    size_t nx, ny;
    double dx, dt;
    double nu;  // viscosity
    double u_in;
    
    std::vector<double> u;
    std::vector<double> v;
    std::vector<double> p;
    std::vector<bool> obstacle;
    

    std::vector<double> advect(const std::vector<double>& field, 
                               const std::vector<double>& u0, 
                               const std::vector<double>& v0) {
        std::vector<double> advected(nx * ny, 0.0);
        double dt_dx = dt / dx;
        
        for (size_t i = 0; i < ny; ++i) {
            for (size_t j = 0; j < nx; ++j) {
                if (obstacle[idx(i, j, nx)]) continue;
                

                double x_back = j - u0[idx(i, j, nx)] * dt_dx;
                double y_back = i - v0[idx(i, j, nx)] * dt_dx;
                
           
                x_back = std::max(0.0, std::min(static_cast<double>(nx - 1), x_back));
                y_back = std::max(0.0, std::min(static_cast<double>(ny - 1), y_back));
                
           
                size_t x0 = static_cast<size_t>(std::floor(x_back));
                size_t y0 = static_cast<size_t>(std::floor(y_back));
                size_t x1 = std::min(x0 + 1, nx - 1);
                size_t y1 = std::min(y0 + 1, ny - 1);
                
        
                double sx = x_back - x0;
                double sy = y_back - y0;
                

                double f00 = field[idx(y0, x0, nx)];
                double f10 = field[idx(y0, x1, nx)];
                double f01 = field[idx(y1, x0, nx)];
                double f11 = field[idx(y1, x1, nx)];
                
                advected[idx(i, j, nx)] = (1-sx)*(1-sy)*f00 + sx*(1-sy)*f10 + 
                                          (1-sx)*sy*f01 + sx*sy*f11;
            }
        }
        
        return advected;
    }
    

    std::vector<double> diffuse(const std::vector<double>& field) {
        std::vector<double> result = field;
        std::vector<double> lap = laplacian(field, nx, ny, dx);
        
        for (size_t i = 0; i < ny; ++i) {
            for (size_t j = 0; j < nx; ++j) {
                result[idx(i, j, nx)] += nu * dt * lap[idx(i, j, nx)];
            }
        }
        
        return result;
    }
    

    void project() {
        std::vector<double> div(nx * ny, 0.0);
        std::vector<double> p_new(nx * ny, 0.0);
        

        for (size_t i = 1; i < ny - 1; ++i) {
            for (size_t j = 1; j < nx - 1; ++j) {
                div[idx(i, j, nx)] = (
                    (u[idx(i, j+1, nx)] - u[idx(i, j-1, nx)]) +
                    (v[idx(i+1, j, nx)] - v[idx(i-1, j, nx)])
                ) / (2.0 * dx);
            }
        }
        

        for (int iter = 0; iter < 100; ++iter) {
            for (size_t i = 1; i < ny - 1; ++i) {
                for (size_t j = 1; j < nx - 1; ++j) {
                    if (obstacle[idx(i, j, nx)]) {
                        p_new[idx(i, j, nx)] = 0.0;
                        continue;
                    }
                    
                    p_new[idx(i, j, nx)] = (
                        p[idx(i, j+1, nx)] + p[idx(i, j-1, nx)] +
                        p[idx(i+1, j, nx)] + p[idx(i-1, j, nx)] -
                        div[idx(i, j, nx)] * dx * dx
                    ) * 0.25;
                }
            }
            

            std::swap(p, p_new);
        }

        for (size_t i = 1; i < ny - 1; ++i) {
            for (size_t j = 1; j < nx - 1; ++j) {
                u[idx(i, j, nx)] -= (p[idx(i, j+1, nx)] - p[idx(i, j-1, nx)]) / (2.0 * dx);
                v[idx(i, j, nx)] -= (p[idx(i+1, j, nx)] - p[idx(i-1, j, nx)]) / (2.0 * dx);
            }
        }
        
    
        for (size_t i = 0; i < ny; ++i) {
            u[idx(i, 0, nx)] = u_in;    
            u[idx(i, nx-1, nx)] = 0.0;   
            v[idx(i, 0, nx)] = 0.0;      
            v[idx(i, nx-1, nx)] = 0.0;   
        }
        

        for (size_t i = 0; i < ny; ++i) {
            for (size_t j = 0; j < nx; ++j) {
                if (obstacle[idx(i, j, nx)]) {
                    u[idx(i, j, nx)] = 0.0;
                    v[idx(i, j, nx)] = 0.0;
                }
            }
        }
    }
    
public:
    FluidSimulator(size_t nx, size_t ny, double dx = 1.0, double dt = 0.1,
                  double viscosity = 0.02, double u_in = 1.0)
        : nx(nx), ny(ny), dx(dx), dt(dt), nu(viscosity), u_in(u_in) {
        
        size_t size = nx * ny;
        u.resize(size, 0.0);
        v.resize(size, 0.0);
        p.resize(size, 0.0);
        obstacle.resize(size, false);
    }
    
    void setObstacle(const std::vector<bool>& mask) {
        if (mask.size() != obstacle.size()) {
            std::cerr << "Error: Obstacle mask size mismatch" << std::endl;
            return;
        }
        
        obstacle = mask;
        
        for (size_t i = 0; i < ny; ++i) {
            for (size_t j = 0; j < nx; ++j) {
                if (obstacle[idx(i, j, nx)]) {
                    u[idx(i, j, nx)] = 0.0;
                    v[idx(i, j, nx)] = 0.0;
                    p[idx(i, j, nx)] = 0.0;
                }
            }
        }
    }
    
    void step() {
        double max_dt = dx * dx / (4.0 * nu);
        if (dt > max_dt) {
            dt = max_dt;
        }
        
        std::vector<double> u0 = u;
        std::vector<double> v0 = v;
        
        // Advect
        u = advect(u, u0, v0);
        v = advect(v, u0, v0);
        
        u = diffuse(u);
        v = diffuse(v);
        
        project();
    }
    
    //getters
    size_t getWidth() const { return nx; }
    size_t getHeight() const { return ny; }
    
    std::pair<std::vector<double>, std::vector<double>> getVelocity() const {
        return {u, v};
    }
    
    const std::vector<double>& getPressure() const {
        return p;
    }
    
    const std::vector<bool>& getObstacle() const {
        return obstacle;
    }
    

    double getVelocityMagnitude(size_t i, size_t j) const {
        if (i >= ny || j >= nx) return 0.0;
        double u_val = u[idx(i, j, nx)];
        double v_val = v[idx(i, j, nx)];
        return std::sqrt(u_val * u_val + v_val * v_val);
    }
    

    double getMaxVelocityMagnitude() const {
        double max_vel = 0.0;
        for (size_t i = 0; i < ny; ++i) {
            for (size_t j = 0; j < nx; ++j) {
                double vel = getVelocityMagnitude(i, j);
                max_vel = std::max(max_vel, vel);
            }
        }
        return max_vel;
    }
};

#endif
