import random
from framework.simulator import Simulator
from framework.generators import exponential_dist, normal_dist

in_vars = {
    'capacidad' : 25,
    'tp_dur_estancia_media' : 90,
    'tp_dur_estancia_dsvtip' : 20,
    'tp_abierto' : 300,
    'tp_entrellegada' : 15,
    'gasto_persona_media' : 25,
    'gasto_persona_dsvtip' : 3
}

state_vars = {
    'libres':0,
}

count_vars = {
    'gasto':0.0,
    'gasto_total':0.0
}

def generar_grupo():
    return random.randint(1,4)

sim = Simulator(in_vars, state_vars, count_vars, n_sims=30)

@sim.stop()
def stop_cond(in_vars, state_vars, count_vars) -> bool:
    return (sim.clock >= in_vars['tp_abierto'])

@sim.event("Inicio")
def suceso_inicio(in_vars, state_vars, count_vars, data=None):
    count_vars['gasto_total'] = 0.0
    state_vars['libres'] = in_vars['capacidad']
    sim.spawn(sim.clock + exponential_dist(in_vars['tp_entrellegada']), 'Llegada')
    sim.spawn(sim.clock + in_vars['tp_abierto'], 'Fin')

@sim.event("Llegada")
def suceso_llegada(in_vars, state_vars, count_vars, data=None):
    sim.spawn(sim.clock + exponential_dist(in_vars['tp_entrellegada']), 'Llegada')
    grupo = generar_grupo()
    if(state_vars['libres'] >= grupo):
        sim.spawn(sim.clock + normal_dist(in_vars['tp_dur_estancia_media'], in_vars['tp_dur_estancia_dsvtip']), 'Salida', data={'grupo':grupo})
        state_vars['libres'] -= grupo
        for i in range(grupo):
            gasto = normal_dist(in_vars['gasto_persona_media'], in_vars['gasto_persona_dsvtip'])
            count_vars['gasto_total'] += gasto

@sim.event("Salida")
def suceso_salida(in_vars, state_vars, count_vars, data=None):
    state_vars['libres'] += data['grupo']

@sim.event("Fin")
def suceso_fin(in_vars, state_vars, count_vars, data=None):
    print(f"Simulation {sim.sim_index} finished")

@sim.metric('gasto_total_calc')
def gasto_total_calc(in_vars, state_vars, count_vars):
    return count_vars['gasto_total']

df = sim()
df.to_csv('Data.csv')