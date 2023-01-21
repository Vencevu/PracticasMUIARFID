import spade
import datetime
import json
import random
import time
import click

class AgenteMediador(spade.agent.Agent):

    def __init__(self, jid, password):
        super().__init__(jid, password)

    async def setup(self):
        self.value = 0
        template = spade.template.Template(metadata={"performative": "MAKE_BET"})
        self.add_behaviour(self.RecepcionBehaviour(), template)

        print("{} ready.".format(self.name))
    
    class RecepcionBehaviour(spade.behaviour.CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=2)
            if msg:
                print("Mensaje recibido")
                body = json.loads(msg.body)
                self.agent.value += 1

class AgenteCliente(spade.agent.Agent):

    def __init__(self, jid, password):
        super().__init__(jid, password)

    async def setup(self):
        self.value = random.randint(1, 1000)
        self.tiempo = 0
        self.tiempo_inicio = time.time()
        
        start_at = datetime.datetime.now() + datetime.timedelta(seconds=5)
        self.add_behaviour(self.EnvioBehaviour(period=2, start_at=start_at))

        print("{} ready.".format(self.name))
    
    def add_contact(self, contact):
        self.contact = contact.jid

    class EnvioBehaviour(spade.behaviour.PeriodicBehaviour):
        async def run(self):
            jid = self.agent.contact
            body = json.dumps({"value": self.agent.value, "timestamp": time.time()})
            msg = spade.message.Message(to=str(jid), body=body, metadata={"performative": "MAKE_BET"})
            await self.send(msg)
            print("Mensaje enviado por ", self.agent.jid)

@click.command()
@click.option('--count', default=10, help='Number of agents.')
def main(count):
    agents = []
    print("Creating {} agents...".format(count))
    for x in range(1, count + 1):
        print("Creating agent {}...".format(x))
        # nos guardamos la lista de agentes para poder visualizar el estado del proceso gossiping
        # el servidor estÃ¡ fijado a gtirouter.dsic.upv.es, si se tiene un serviodor XMPP en local, se puede sustituir por localhost
        agents.append(AgenteCliente("apostador_{}@localhost".format(x), "test"))
    
    agenteMediador = AgenteMediador("mediador@localhost", "1234")
    # este tiempo trata de esperar que todos los agentes estan registrados, depende de la cantidad de agentes que se lancen
    time.sleep(count*0.3)

    # se le pasa a cada agente la lista de contactos
    for ag in agents:
        ag.add_contact(agenteMediador)
        ag.value = 0

    # se lanzan todos los agentes
    agenteMediador.start()
    for ag in agents:
        ag.start()
        
    # este tiempo trata de esperar que todos los agentes estan ready, depende de la cantidad de agentes que se lancen
    time.sleep(count*0.3)
    
    # este bucle imprime los valores que almacena cada agente y termina cuando todos tienen el mismo valor (consenso)
    while True:
        try:
            time.sleep(1)
            status = agenteMediador.value
            print("STATUS: {}".format(status))
            if status == len(agents):
                print("Gossip done.")
                break
        except KeyboardInterrupt:
            break

    total_mensajes = sum([ag.msg_enviados for ag in agents])
    total_tiempo = max([ag.tiempo for ag in agents])
    print("tiempo: ", total_tiempo, " mensajes: ",total_mensajes)
    # se para a todos los agentes
    for ag in agents:
        ag.stop()
    print("Agents finished")

if __name__ == '__main__':
    main()