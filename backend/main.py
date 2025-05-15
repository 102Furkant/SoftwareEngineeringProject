#burada ui ve simulation elementleri import edilip cagirildiktan sorna kullanılacak
'''

from simulation import FluidSimulator
from ui import someuielement

def main():
    sim = FluidSimulator(width=200, height=200)
    sim.set_obstacle('circle', radius=40)
    run_ui(sim)  # run_ui, her karede sim.inject ve sim.step i cagirip ekrani guncelliyor

if __name__ == "__main__":
    main()

'''

#yukaridaki koda benzeyen bir kod yazilabilir
