import spade
import datetime
import json
import random
import time
import click

class AgenteTarea(spade.agent.Agent):

    def __init__(self, jid, password):
        super().__init__(jid, password)

    async def setup(self):
        self.asignado = ""
        self.puja = 0
        self.precio = random.randint(5,20)

        template = spade.template.Template(metadata={"performative": "MAKE_BET"})
        self.add_behaviour(self.RecepcionBehaviour(), template)

        print("{} ready.".format(self.name))
    
    class RecepcionBehaviour(spade.behaviour.CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=2)
            if msg:
                body = json.loads(msg.body)
                if body["puja"] > self.agent.puja:
                    self.agent.puja = int(body["puja"])
                    self.agent.asignado = msg.sender
                    self.precio += int(body["puja"])

class AgenteCliente(spade.agent.Agent):

    def __init__(self, jid, password):
        super().__init__(jid, password)

    async def setup(self):
        self.value = random.randint(1, 1000)
        self.msg_enviados = 0
        self.costes = {}
        self.tiempo_inicio = time.time()
        
        start_at = datetime.datetime.now() + datetime.timedelta(seconds=5)
        self.add_behaviour(self.PujaBehav(period=2, start_at=start_at))

        print("{} ready.".format(self.name))
    
    def add_contact(self, contact_list):
        self.contacts = [c.jid for c in contact_list]

    class PujaBehav(spade.behaviour.PeriodicBehaviour):
        async def run(self):
            for jid in self.agent.contacts:
                puja = self.agent.costes[jid]
                body = json.dumps({"puja": self.agent.value, "timestamp": time.time()})
                msg = spade.message.Message(to=str(jid), body=body, metadata={"performative": "MAKE_BET"})
                await self.send(msg)

@click.command()
@click.option('--count', default=10, help='Number of agents.')
def main(count):
    agentsC, agentsT = [], []
    print("Creating {} agents...".format(count))
    for x in range(1, count + 1):
        print("Creating agent {}...".format(x))
        agentsC.append(AgenteCliente("pujador_{}@localhost".format(x), "test"))
    
    for x in range(1, count + 1):
        print("Creating agent {}...".format(x))
        agentsT.append(AgenteTarea("tarea_{}@localhost".format(x), "test"))
    # este tiempo trata de esperar que todos los agentes estan registrados, depende de la cantidad de agentes que se lancen
    time.sleep(count*0.3)

    # se le pasa a cada agente la lista de contactos
    for ag in agentsC:
        ag.add_contact(agentsT)
        ag.value = 0

    for ag in agentsC:
        ag.start()

    for ag in agentsT:
        ag.start()
        
    # este tiempo trata de esperar que todos los agentes estan ready, depende de la cantidad de agentes que se lancen
    time.sleep(count*0.3)
    
    # este bucle imprime los valores que almacena cada agente y termina cuando todos tienen el mismo valor (consenso)
    while True:
        try:
            time.sleep(1)
            status = [a.asignado for a in agentsT if a.asignado == ""]
            print("STATUS: {}".format(status))
            if len(status) == 0:
                print("FIN")
                break
        except KeyboardInterrupt:
            break

    # se para a todos los agentes
    for ag in agentsC:
        ag.stop()
    print("Agents finished")

if __name__ == '__main__':
    main()