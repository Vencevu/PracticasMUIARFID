import spade
import datetime
import json
import random
import time
import click

random.seed(42)

class AgenteTarea(spade.agent.Agent):

    def __init__(self, jid, password):
        super().__init__(jid, password)

    async def setup(self):
        self.asignado = ""
        self.puja = 0
        self.precio = 0
        self.contacts = []

        template = spade.template.Template(metadata={"performative": "MAKE_BET"})
        self.add_behaviour(self.RecepcionBehaviour(), template)

        print("{} ready.".format(self.name))
    
    def add_contact(self, contact_list):
        self.contacts = [c.jid for c in contact_list]
    
    class RecepcionBehaviour(spade.behaviour.CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=2)
            if msg:
                body = json.loads(msg.body)
                if body["puja"] > self.agent.puja:
                    self.agent.puja = int(body["puja"])
                    self.agent.asignado = msg.sender
                    self.agent.precio += int(body["puja"])

                    body = json.dumps({"asignacion": 1, "precio": self.agent.precio, "timestamp": time.time()})
                    msg = spade.message.Message(to=str(msg.sender), body=body, metadata={"performative": "ACCEPT_BET"})
                    await self.send(msg)

                    for pujador in self.agent.contacts:
                        if(pujador != msg.sender):
                            body = json.dumps({"precio": self.agent.precio, "timestamp": time.time()})
                            msg = spade.message.Message(to=str(pujador), body=body, metadata={"performative": "UPDATE_PRICE"})
                            await self.send(msg)

class AgenteCliente(spade.agent.Agent):

    def __init__(self, jid, password):
        super().__init__(jid, password)

    async def setup(self):
        self.msg_enviados = 0
        self.tarea_asignada = ""
        self.costes = {}
        self.precios = {}
        self.tiempo_inicio = time.time()
        
        start_at = datetime.datetime.now() + datetime.timedelta(seconds=5)
        self.add_behaviour(self.PujaBehav(period=2, start_at=start_at))

        template = spade.template.Template(metadata={"performative": "ACCEPT_BET"})
        self.add_behaviour(self.RespuestaBehaviour(), template)

        template = spade.template.Template(metadata={"performative": "UPDATE_PRICE"})
        self.add_behaviour(self.UpdateBehaviour(), template)

        print("{} ready.".format(self.name))
    
    def add_contact(self, contact_list):
        self.contacts = [c.jid for c in contact_list]

    def calc_coste(self, id):
        return self.costes[self.jid][id] + self.precios[id]

    class PujaBehav(spade.behaviour.PeriodicBehaviour):
        async def run(self):
            if(self.agent.tarea_asignada == ""):
                pujas = {k.jid: self.agent.calc_coste(k.jid) for k in self.agent.contacts}
                pujas = dict(sorted(pujas.items(), key=lambda item: item[1]))
                puja1, puja2 = list(pujas.values())[0], list(pujas.values())[1]
                puja_value = puja2 - puja1
                puja_id = list(pujas.keys())[0]
                body = json.dumps({"puja": puja_value, "timestamp": time.time()})
                msg = spade.message.Message(to=str(puja_id), body=body, metadata={"performative": "MAKE_BET"})
                await self.send(msg)

    class RespuestaBehaviour(spade.behaviour.PeriodicBehaviour):
        async def run(self):
            if(self.agent.tarea_asignada == ""):
                msg = await self.receive(timeout=2)
                if msg:
                    body = json.loads(msg.body)
                    if(body["asignacion"]): self.agent.tarea_asignada = msg.sender
    
    class UpdateBehaviour(spade.behaviour.PeriodicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=2)
            if msg:
                body = json.loads(msg.body)
                self.agent.precios[msg.sender] = body["precio"]

@click.command()
@click.option('--count', default=10, help='Number of agents.')
def main(count):
    agentsC, agentsT = [], []
    print("Creating {} agents...".format(count))
    for x in range(1, count + 1):
        print("Creating agent Pujador {}...".format(x))
        agentsC.append(AgenteCliente("pujador_{}@localhost".format(x), "test"))
    
    for x in range(1, count + 1):
        print("Creating agent Tarea {}...".format(x))
        agentsT.append(AgenteTarea("tarea_{}@localhost".format(x), "test"))
    # este tiempo trata de esperar que todos los agentes estan registrados, depende de la cantidad de agentes que se lancen
    time.sleep(count*0.3)

    #Creamos tablas de coste y precios
    costes = {k.jid: {t.jid: random.uniform(1.0,20.9) for t in agentsT} for k in agentsC}
    precios = {k.jid: random.uniform(1.0,20.9) for k in agentsT}

    # se le pasa a cada agente la lista de contactos, costes y precios
    for ag in agentsT:
        ag.add_contact(agentsC)
        ag.asignado = ""
        ag.precio = precios[ag.jid]
    
    for ag in agentsC:
        ag.add_contact(agentsT)
        ag.costes = costes
        ag.precios = precios

    for ag in agentsC:
        ag.start()

    for ag in agentsT:
        ag.start()
        
    # este tiempo trata de esperar que todos los agentes estan ready, depende de la cantidad de agentes que se lancen
    time.sleep(count*2*0.3)
    
    # este bucle imprime los valores que almacena cada agente y termina cuando todos tienen el mismo valor (consenso)
    while True:
        try:
            time.sleep(1)
            status = [a.asignado for a in agentsT if a.asignado == ""]
            costeTotal = [a.precio for a in agentsT if a.asignado != ""]
            print("COSTE TOTAL: {}".format(sum(costeTotal)))
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