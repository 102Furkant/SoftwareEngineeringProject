#include <SFML/Graphics.hpp>
#include <vector>
#include <cmath>
#include <random>
#include <algorithm>


const float GRAVITY = 0.1f;
const float AIR_SPEED = 4.0f;  
const float WATER_SPEED = 0.5f;
const float VISCOSITY = 0.05f;
const float ELASTICITY = 0.8f;
const float DENSITY_AIR = 1.0f;
const float DENSITY_WATER = 5.0f;
const float PARTICLE_RADIUS = 4.0f; 
const float INTERACTION_RADIUS = 10.0f; 


const float SCALE_FACTOR = 1.5f;
const int WINDOW_WIDTH = 400;
const int WINDOW_HEIGHT = 400;
const int SCALED_WIDTH = static_cast<int>(WINDOW_WIDTH * SCALE_FACTOR);
const int SCALED_HEIGHT = static_cast<int>(WINDOW_HEIGHT * SCALE_FACTOR);


enum ParticleType {
    AIR,
    WATER
};


class Particle {
public:
    sf::Vector2f position;
    sf::Vector2f velocity;
    sf::Vector2f force;
    float density;
    float pressure;
    ParticleType type;
    sf::Color color;

    Particle(float x, float y, ParticleType t) {
        position = sf::Vector2f(x, y);
        velocity = sf::Vector2f(0.0f, 0.0f);
        force = sf::Vector2f(0.0f, 0.0f);
        type = t;
        
        if (type == AIR) {
            density = DENSITY_AIR;
            color = sf::Color(200, 200, 255, 100);
            velocity.x = AIR_SPEED;  
        } else {
            density = DENSITY_WATER;
            color = sf::Color(0, 0, 255, 200);
            velocity.y = -WATER_SPEED;
        }
    }

    Particle(float x, float y, ParticleType t, float vel_x, float vel_y) {
        position = sf::Vector2f(x, y);
        velocity = sf::Vector2f(vel_x, vel_y);
        force = sf::Vector2f(0.0f, 0.0f);
        type = t;
        
        if (type == AIR) {
            density = DENSITY_AIR;
            color = sf::Color(200, 200, 255, 100);
        } else {
            density = DENSITY_WATER;
            color = sf::Color(0, 0, 255, 200);
        }
    }

    void update(float dt) {
   
        velocity += force * dt / density;
        
  
        if (type == AIR) {
     
            if (velocity.x < AIR_SPEED) velocity.x += 0.02f; 
        } else if (type == WATER) {
    
            velocity.y += GRAVITY;
        }
        
  
        position += velocity * dt;
        

        if (position.x < PARTICLE_RADIUS) {
            position.x = PARTICLE_RADIUS;
            velocity.x *= -ELASTICITY;
        }
        if (position.x > WINDOW_WIDTH - PARTICLE_RADIUS) {
            position.x = WINDOW_WIDTH - PARTICLE_RADIUS;
            velocity.x *= -ELASTICITY;
        }
        if (position.y < PARTICLE_RADIUS) {
            position.y = PARTICLE_RADIUS;
            velocity.y *= -ELASTICITY;
        }
        if (position.y > WINDOW_HEIGHT - PARTICLE_RADIUS) {
            position.y = WINDOW_HEIGHT - PARTICLE_RADIUS;
            velocity.y *= -ELASTICITY;
        }
        
  
        force = sf::Vector2f(0.0f, 0.0f);
    }

    void draw(sf::RenderWindow& window) {
        sf::CircleShape shape(PARTICLE_RADIUS * SCALE_FACTOR);  
        shape.setPosition((position - sf::Vector2f(PARTICLE_RADIUS, PARTICLE_RADIUS)) * SCALE_FACTOR);
        window.draw(shape);
    }
};


class Wall {
public:
    std::vector<sf::Vector2f> points;

    void addPoint(sf::Vector2f point) {
    
        points.push_back(sf::Vector2f(point.x / SCALE_FACTOR, point.y / SCALE_FACTOR));
    }

    bool checkCollision(sf::Vector2f& position, sf::Vector2f& velocity) {
        if (points.size() < 2) return false;
        
        for (size_t i = 0; i < points.size() - 1; ++i) {
            sf::Vector2f p1 = points[i];
            sf::Vector2f p2 = points[i + 1];
            
   
            sf::Vector2f v1 = position - p1;
            sf::Vector2f v2 = p2 - p1;
            float len = sqrt(v2.x * v2.x + v2.y * v2.y);
            sf::Vector2f v2_norm = v2 / len;
            
            float dot = v1.x * v2_norm.x + v1.y * v2_norm.y;
            
            sf::Vector2f closest;
            if (dot < 0) {
                closest = p1;
            } else if (dot > len) {
                closest = p2;
            } else {
                closest = p1 + v2_norm * dot;
            }
            

            sf::Vector2f distance_vec = position - closest;
            float distance = sqrt(distance_vec.x * distance_vec.x + distance_vec.y * distance_vec.y);
            
            if (distance < PARTICLE_RADIUS) {
             
                sf::Vector2f normal = distance_vec / distance;
                
            
                float vn = velocity.x * normal.x + velocity.y * normal.y;
                
                if (vn < 0) {
            
                    float vt = velocity.x * (-normal.y) + velocity.y * normal.x;
                    sf::Vector2f tangent(-normal.y, normal.x);
                    
        
                    vt *= (1.0f - VISCOSITY);
                    
          
                    velocity = tangent * vt - normal * vn * ELASTICITY;
                    
       
                    position = closest + normal * PARTICLE_RADIUS;
                    
                    return true;
                }
            }
        }
        return false;
    }

    void draw(sf::RenderWindow& window) {
        if (points.size() < 2) return;
        
        sf::VertexArray lines(sf::LineStrip, points.size());
        for (size_t i = 0; i < points.size(); ++i) {
      
            lines[i].position = points[i] * SCALE_FACTOR;
            lines[i].color = sf::Color::White;
        }
        window.draw(lines);
    }
};


void resolveWaterCollisions(std::vector<Particle>& particles) {
    for (size_t i = 0; i < particles.size(); ++i) {
        if (particles[i].type != WATER) continue;
        
        for (size_t j = i + 1; j < particles.size(); ++j) {
            if (particles[j].type != WATER) continue;
            
            sf::Vector2f diff = particles[i].position - particles[j].position;
            float dist = sqrt(diff.x * diff.x + diff.y * diff.y);
            
            if (dist < 2 * PARTICLE_RADIUS) {
                sf::Vector2f normal = dist > 0 ? diff / dist : sf::Vector2f(1, 0);
                float overlap = 2 * PARTICLE_RADIUS - dist;
                
      
                particles[i].position += normal * overlap * 0.5f;
                particles[j].position -= normal * overlap * 0.5f;
                
             
                sf::Vector2f relVel = particles[i].velocity - particles[j].velocity;
                float velAlongNormal = relVel.x * normal.x + relVel.y * normal.y;
                
                if (velAlongNormal > 0) continue;
                
                float j_impulse = -(1 + ELASTICITY) * velAlongNormal;
                j_impulse /= 1/particles[i].density + 1/particles[j].density;
                
                sf::Vector2f impulse = normal * j_impulse;
                particles[i].velocity += impulse / particles[i].density;
                particles[j].velocity -= impulse / particles[j].density;
            }
        }
    }
}


void createWaterDroplets(std::vector<Particle>& particles, int count) {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<float> distr_x(50, WINDOW_WIDTH - 50);
    
    for (int i = 0; i < count; ++i) {
        particles.emplace_back(distr_x(gen), 50, WATER, 0.0f, 3.0f);
    }
}


void createAirParticles(std::vector<Particle>& particles, int count) {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<float> distr_y(50, WINDOW_HEIGHT - 50);
    
    for (int i = 0; i < count; ++i) {
        particles.emplace_back(50, distr_y(gen), AIR, AIR_SPEED, 0.0f); 
    }
}


void createRisingWaterParticles(std::vector<Particle>& particles, int count) {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<float> distr_x(50, WINDOW_WIDTH - 50);
    
    for (int i = 0; i < count; ++i) {
        particles.emplace_back(distr_x(gen), WINDOW_HEIGHT - 50, WATER, 0.0f, -WATER_SPEED * 2);
    }
}

int main() {

    sf::RenderWindow window(sf::VideoMode(SCALED_WIDTH, SCALED_HEIGHT), "Akışkan Simülasyonu");
    window.setFramerateLimit(60);

    sf::View view(sf::FloatRect(0, 0, SCALED_WIDTH, SCALED_HEIGHT));
    window.setView(view);
    

    std::vector<Particle> particles; 
    std::vector<Wall> walls;
    Wall currentWall;
    

    std::random_device rd;
    std::mt19937 gen(rd());
    

    bool isDrawing = false;
    

    bool spacePressed = false;
    bool wPressed = false;
    bool upPressed = false;
    

    sf::Clock clock;
    sf::Clock keyTimer;
    

    sf::Font font;
    bool fontLoaded = font.loadFromFile("arial.ttf");
    

    while (window.isOpen()) {
        sf::Time deltaTime = clock.restart();
        float dt = deltaTime.asSeconds();
        
 
        sf::Event event;
        while (window.pollEvent(event)) {
            if (event.type == sf::Event::Closed)
                window.close();
                
            if (event.type == sf::Event::MouseButtonPressed && event.mouseButton.button == sf::Mouse::Left) {
                isDrawing = true;
                currentWall = Wall();
                currentWall.addPoint(sf::Vector2f(event.mouseButton.x, event.mouseButton.y));
            }
            
            if (event.type == sf::Event::MouseMoved && isDrawing) {
                currentWall.addPoint(sf::Vector2f(event.mouseMove.x, event.mouseMove.y));
            }
            
            if (event.type == sf::Event::MouseButtonReleased && event.mouseButton.button == sf::Mouse::Left) {
                isDrawing = false;
                walls.push_back(currentWall);
            }
            
            if (event.type == sf::Event::KeyPressed) {
                if (event.key.code == sf::Keyboard::Space) {
                    spacePressed = true;
                }
                if (event.key.code == sf::Keyboard::W) {
                    wPressed = true;
                }
                if (event.key.code == sf::Keyboard::Up) {
                    upPressed = true;
                }
 
                if (event.key.code == sf::Keyboard::C) {
                    particles.clear();
                    walls.clear();
                }
            }
            
            if (event.type == sf::Event::KeyReleased) {
                if (event.key.code == sf::Keyboard::Space) {
                    spacePressed = false;
                }
                if (event.key.code == sf::Keyboard::W) {
                    wPressed = false;
                }
                if (event.key.code == sf::Keyboard::Up) {
                    upPressed = false;
                }
            }
        }
        
    
        if (keyTimer.getElapsedTime().asMilliseconds() > 50) { 
            if (spacePressed) {
                createAirParticles(particles, 5); 
            }
            if (wPressed) {
                createWaterDroplets(particles, 5); 
            }
            if (upPressed) {
                createRisingWaterParticles(particles, 5); 
            }
            keyTimer.restart();
        }

        for (auto& p : particles) {
            p.update(dt);
            
 
            for (auto& wall : walls) {
                wall.checkCollision(p.position, p.velocity);
            }
        }
        

        resolveWaterCollisions(particles);
        

        window.clear(sf::Color(30, 30, 40));
        

        for (auto& wall : walls) {
            wall.draw(window);
        }
        
  
        if (isDrawing) {
            currentWall.draw(window);
        }
        

        for (auto& p : particles) {
            p.draw(window);
        }
        
  
        if (fontLoaded) {
            sf::Text text;
            text.setFont(font);
            text.setCharacterSize(16 * SCALE_FACTOR);  
            text.setFillColor(sf::Color::White);
            text.setPosition(10 * SCALE_FACTOR, 10 * SCALE_FACTOR);
            text.setString(
                "Kontroller:\n"
                "Space: Hava molekulleri\n"
                "W: Su damlalari\n"
                "Up: Yukselen su\n"
                "Fare: Duvar ciz\n"
                "C: Temizle\n\n"
                "Parcacik sayisi: " + std::to_string(particles.size())
            );
            window.draw(text);
        }
        
        window.display();
        
      
        if (particles.size() > 1000) {  
            particles.erase(particles.begin(), particles.begin() + 100);
        }
    }
    
    return 0;
}
