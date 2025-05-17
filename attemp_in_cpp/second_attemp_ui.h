#ifndef UI_H
#define UI_H

#include <SFML/Graphics.hpp>
#include <iostream>
#include <string>
#include <memory>
#include "backend.h"  

class FluidSimulatorUI {
private:
    
    const size_t nx, ny;
    std::unique_ptr<FluidSimulator> simulator;
    

    sf::RenderWindow window;
    sf::Font font;
    sf::Text infoText;
    sf::VertexArray velocityField;
    sf::VertexArray pressureField;
    

    bool showVelocity = true;
    bool showPressure = false;
    bool running = true;
    bool paused = false;
    

    sf::Color velocityToColor(double u, double v, double maxVel) {
        
        double mag = std::sqrt(u*u + v*v);   //calculate velocity magnitude and direction
        double normalizedMag = maxVel > 0 ? mag / maxVel : 0;
        
        
        uint8_t r = static_cast<uint8_t>(255 * normalizedMag);   //map velocity to a color
        uint8_t g = 0;
        uint8_t b = static_cast<uint8_t>(255 * (1.0 - normalizedMag));
        uint8_t a = 255;
        
        return sf::Color(r, g, b, a);
    }
    
    sf::Color pressureToColor(double pressure, double minP, double maxP) {
        
        double range = maxP - minP;   //normalize pressure
        double normalizedP = range > 0 ? (pressure - minP) / range : 0.5;
        
        uint8_t r, g, b;
        if (normalizedP < 0.5) {

            double t = normalizedP * 2.0;   //maviden beyaza
            r = static_cast<uint8_t>(255 * t);
            g = static_cast<uint8_t>(255 * t);
            b = 255;
        } else {

            double t = (normalizedP - 0.5) * 2.0;   //beyazdan kırımızıya
            r = 255;
            g = static_cast<uint8_t>(255 * (1.0 - t));
            b = static_cast<uint8_t>(255 * (1.0 - t));
        }
        
        return sf::Color(r, g, b);
    }
    
    void updateVelocityVisualization() {
        auto [u, v] = simulator->getVelocity();
        double maxVel = simulator->getMaxVelocityMagnitude();
        
 
        const float vectorScale = 15.0f;
        

        velocityField.clear();
        velocityField.setPrimitiveType(sf::Lines);
        

        const int skip = 5; 
        for (size_t i = skip; i < ny; i += skip) {
            for (size_t j = skip; j < nx; j += skip) {
                if (simulator->getObstacle()[idx(i, j, nx)]) continue;
                
                float x = static_cast<float>(j);
                float y = static_cast<float>(i);
                float u_val = static_cast<float>(u[idx(i, j, nx)]);
                float v_val = static_cast<float>(v[idx(i, j, nx)]);
                
                sf::Color color = velocityToColor(u_val, v_val, maxVel);
                

                velocityField.append(sf::Vertex(sf::Vector2f(x, y), color));
                velocityField.append(sf::Vertex(
                    sf::Vector2f(x + u_val * vectorScale, y + v_val * vectorScale), 
                    color
                ));
            }
        }
    }
    
    void updatePressureVisualization() {
        const std::vector<double>& p = simulator->getPressure();
        

        double minP = 0, maxP = 0;
        for (double val : p) {
            minP = std::min(minP, val);
            maxP = std::max(maxP, val);
        }
        

        pressureField.clear();
        pressureField.setPrimitiveType(sf::Quads);
        
        for (size_t i = 0; i < ny; ++i) {
            for (size_t j = 0; j < nx; ++j) {
                if (simulator->getObstacle()[idx(i, j, nx)]) continue;
                
                float x = static_cast<float>(j);
                float y = static_cast<float>(i);
                sf::Color color = pressureToColor(p[idx(i, j, nx)], minP, maxP);
                

                pressureField.append(sf::Vertex(sf::Vector2f(x, y), color));
                pressureField.append(sf::Vertex(sf::Vector2f(x+1, y), color));
                pressureField.append(sf::Vertex(sf::Vector2f(x+1, y+1), color));
                pressureField.append(sf::Vertex(sf::Vector2f(x, y+1), color));
            }
        }
    }
    
    void drawObstacles() {
        const std::vector<bool>& obstacles = simulator->getObstacle();
        
        for (size_t i = 0; i < ny; ++i) {
            for (size_t j = 0; j < nx; ++j) {
                if (!obstacles[idx(i, j, nx)]) continue;
                
                sf::RectangleShape rect;
                rect.setPosition(static_cast<float>(j), static_cast<float>(i));
                rect.setSize(sf::Vector2f(1.0f, 1.0f));
                rect.setFillColor(sf::Color(100, 100, 100));  //gri (duvarlar için)
                
                window.draw(rect);
            }
        }
    }
    
    void updateInfoText() {
        std::string info = "Fluid Simulator | ";
        info += paused ? "PAUSED | " : "";
        info += "Press V: Toggle Velocity | ";
        info += "Press P: Toggle Pressure | ";
        info += "Press Space: Pause/Resume | ";
        info += "Press R: Reset | ";
        info += "Press Esc: Exit";
        
        infoText.setString(info);
    }
    
    void handleEvents() {
        sf::Event event;
        while (window.pollEvent(event)) {
            switch (event.type) {
                case sf::Event::Closed:
                    window.close();
                    running = false;
                    break;
                
                case sf::Event::KeyPressed:
                    switch (event.key.code) {
                        case sf::Keyboard::Escape:
                            window.close();
                            running = false;
                            break;
                        
                        case sf::Keyboard::V:
                            showVelocity = !showVelocity;
                            break;
                        
                        case sf::Keyboard::P:
                            showPressure = !showPressure;
                            break;
                        
                        case sf::Keyboard::Space:
                            paused = !paused;
                            break;
                        
                        case sf::Keyboard::R:
                            resetSimulation();
                            break;
                        
                        default:
                            break;
                    }
                    break;
                
                default:
                    break;
            }
        }
    }
    
    void resetSimulation() {

        simulator = std::make_unique<FluidSimulator>(nx, ny);
        

        std::vector<bool> obstacle(nx * ny, false);
        double cx = nx / 2.0;
        double cy = ny / 2.0;
        double radius = ny / 8.0;
        
        for (size_t i = 0; i < ny; ++i) {
            for (size_t j = 0; j < nx; ++j) {
                double dist = std::sqrt(std::pow(i - cy, 2) + std::pow(j - cx, 2));
                if (dist < radius) {
                    obstacle[idx(i, j, nx)] = true;
                }
            }
        }
        
        simulator->setObstacle(obstacle);
    }

public:
    FluidSimulatorUI(size_t nx, size_t ny)
        : nx(nx), ny(ny),
          velocityField(sf::Lines),
          pressureField(sf::Quads) {
        
 
        float scale = 6.0f; 
        window.create(sf::VideoMode(
            static_cast<unsigned int>(nx * scale),
            static_cast<unsigned int>(ny * scale)
        ), "Fluid Simulator");
        window.setFramerateLimit(60);
        

        sf::View view(sf::FloatRect(0, 0, static_cast<float>(nx), static_cast<float>(ny)));
        window.setView(view);
        

        bool fontLoaded = false;
        
 
        std::vector<std::string> fontPaths = {
            "arial.ttf",
            "fonts/arial.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf",  
            "/usr/share/fonts/TTF/arial.ttf",                   
            "C:\\Windows\\Fonts\\arial.ttf",                    
            "/Library/Fonts/Arial.ttf"                          
        };
        
        for (const auto& path : fontPaths) {
            if (font.loadFromFile(path)) {
                std::cout << "Successfully loaded font from: " << path << std::endl;
                fontLoaded = true;
                break;
            }
        }
        
        if (!fontLoaded) {
            std::cerr << "Warning: Failed to load font! Using default system font." << std::endl;

            infoText.setCharacterSize(12);
            infoText.setFillColor(sf::Color::White);
        } else {
            infoText.setFont(font);
            infoText.setCharacterSize(12);
            infoText.setFillColor(sf::Color::White);
        }
        
        infoText.setPosition(5, 5);
        
        simulator = std::make_unique<FluidSimulator>(nx, ny);
        resetSimulation();
    }
    
    void run() {
        while (running && window.isOpen()) {
            handleEvents();
            updateInfoText();
            
            if (!paused) {
                simulator->step();
            }
            
            if (showVelocity) {
                updateVelocityVisualization();
            }
            
            if (showPressure) {
                updatePressureVisualization();
            }
            
            window.clear(sf::Color::Black);
            
            if (showPressure) {
                window.draw(pressureField);
            }
            
            drawObstacles();
            
            if (showVelocity) {
                window.draw(velocityField);
            }
            
            sf::View currentView = window.getView();
            window.setView(window.getDefaultView());
            window.draw(infoText);
            window.setView(currentView);
            
            window.display();
        }
    }
};

#endif
