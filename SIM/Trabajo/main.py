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
        print("{} ready.".format(self.name))

class AgenteCliente(spade.agent.Agent):

    def __init__(self, jid, password, k = 1):
        super().__init__(jid, password)
        self.k = k

    async def setup(self):
        self.value = random.randint(1, 1000)
        self.tiempo = 0
        self.msg_enviados = 0
        self.tiempo_inicio = time.time()
        
        start_at = datetime.datetime.now() + datetime.timedelta(seconds=5)
        self.add_behaviour(self.PullBehaviour(period=2, start_at=start_at))
        template = spade.template.Template(metadata={"performative": "REQ2"})
        self.add_behaviour(self.RecvBehaviour(), template)

        print("{} ready.".format(self.name))
    
    def add_contact(self, contact):
        self.contacts = contact

    class PullBehaviour(spade.behaviour.PeriodicBehaviour):
        async def run(self):
            k=1
            random_contacts = random.sample(self.agent.contacts, self.agent.k)
            for jid in random_contacts:
                body = json.dumps({"value": self.agent.value, "timestamp": time.time()})
                msg = spade.message.Message(to=str(jid), body=body, metadata={"performative": "REQ2"})
                self.agent.msg_enviados += 1
                await self.send(msg)

def main(count,k):
    agents = []
    print("Creating {} agents...".format(count))
    for x in range(1, count + 1):
        print("Creating agent {}...".format(x))
        # nos guardamos la lista de agentes para poder visualizar el estado del proceso gossiping
        # el servidor estÃ¡ fijado a gtirouter.dsic.upv.es, si se tiene un serviodor XMPP en local, se puede sustituir por localhost
        agents.append(AgenteCliente("alcargra_{}@localhost".format(x), "test", k=k))
    
    agenteMediador = AgenteMediador("alcargra_mediador@localhost", "1234")
    # este tiempo trata de esperar que todos los agentes estan registrados, depende de la cantidad de agentes que se lancen
    time.sleep(count*0.3)

    # se le pasa a cada agente la lista de contactos
    for ag in agents:
        ag.add_contact(agents)
        ag.value = 0
        ag.msg_enviados = 0

    # se lanzan todos los agentes
    for ag in agents:
        ag.start()

    # este tiempo trata de esperar que todos los agentes estan ready, depende de la cantidad de agentes que se lancen
    time.sleep(count*0.3)
    
    # este bucle imprime los valores que almacena cada agente y termina cuando todos tienen el mismo valor (consenso)
    while True:
        try:
            time.sleep(1)
            status = [ag.value for ag in agents]
            print("STATUS: {}".format(status))
            if len(set(status)) == 1:
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