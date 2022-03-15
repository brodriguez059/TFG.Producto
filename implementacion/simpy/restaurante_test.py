from framework.simulator import Simulator
from framework.generators import exponential_dist, normal_dist
import random # For random number generation

# We specify the endogen variables and its values
in_vars = {
    'capacidad' : 25,
    'tp_dur_estancia_media' : 90,
    'tp_dur_estancia_dsvtip' : 20,
    'tp_abierto' : 300,
    'tp_entrellegada' : 15,
    'gasto_persona_media' : 25,
    'gasto_persona_dsvtip' : 3
}

# We specify the state variables and its values
state_vars = {
    'libres':0,
}

# We specify the statistical counters and its values
count_vars = {
    'gasto':0.0,
    'gasto_total':0.0
}

def generar_grupo():
    """Custom random number generator for our model.

    Returns:
        int: A random number uniformly distributed in [1,4]
    """
    return random.randint(1,4)

# We create the instance of our simulator and pass the relevant parameters.
# We are going to execute 30 simulations
sim = Simulator(in_vars, state_vars, count_vars, n_sims=30)

# We add the stop condition
@sim.stop()
def stop_cond(in_vars, state_vars, count_vars) -> bool:
    return (sim.clock >= in_vars['tp_abierto'])

# We add a new kind of event
@sim.event("Inicio") # The name of our new event type is here
def suceso_inicio(in_vars, state_vars, count_vars, data=None):
    count_vars['gasto_total'] = 0.0
    state_vars['libres'] = in_vars['capacidad']
    sim.spawn(sim.clock + exponential_dist(in_vars['tp_entrellegada']), 'Llegada')
    sim.spawn(sim.clock + in_vars['tp_abierto'], 'Fin')

# We add a new kind of event
@sim.event("Llegada") # The name of our new event type is here
def suceso_llegada(in_vars, state_vars, count_vars, data=None):
    sim.spawn(sim.clock + exponential_dist(in_vars['tp_entrellegada']), 'Llegada')
    grupo = generar_grupo()
    if(state_vars['libres'] >= grupo):
        sim.spawn(sim.clock + normal_dist(in_vars['tp_dur_estancia_media'], in_vars['tp_dur_estancia_dsvtip']), 'Salida', data={'grupo':grupo})
        state_vars['libres'] -= grupo
        for i in range(grupo):
            gasto = normal_dist(in_vars['gasto_persona_media'], in_vars['gasto_persona_dsvtip'])
            count_vars['gasto_total'] += gasto

# We add a new kind of event
@sim.event("Salida") # The name of our new event type is here
def suceso_salida(in_vars, state_vars, count_vars, data=None):
    state_vars['libres'] += data['grupo']

# We add a new kind of event
@sim.event("Fin") # The name of our new event type is here
def suceso_fin(in_vars, state_vars, count_vars, data=None):
    print(f"Simulation {sim.sim_index} finished")

# We add a new evaluation metric
@sim.metric('gasto_total_calc') # The name of our metric is here
def gasto_total_calc(in_vars, state_vars, count_vars):
    return count_vars['gasto_total']

# We launch the simulation and get its data
df = sim()
print(df)

# We store the data
df.to_csv('Data.csv')