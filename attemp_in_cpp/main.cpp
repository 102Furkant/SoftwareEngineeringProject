#include <iostream>
#include "backend.h"
#include "ui.h"

int main() {

    size_t nx = 100;
    size_t ny = 100;
    
    try {
        std::cout << "Starting Fluid Simulator..." << std::endl;
        std::cout << "Grid size: " << nx << " x " << ny << std::endl;
        

        FluidSimulatorUI simulator_ui(nx, ny);
        simulator_ui.run();
        
        std::cout << "Simulator closed." << std::endl;
    } 
    catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    } 
    catch (...) {
        std::cerr << "Unknown error occurred!" << std::endl;
        return 1;
    }
    
    return 0;
}
