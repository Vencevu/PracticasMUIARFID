import datetime
import json
import random
import time
import click

import spade


class PushAgent(spade.agent.Agent):

    
    async def setup(self):
        self.value = random.randint(1, 1000)

        start_at = datetime.datetime.now() + datetime.timedelta(seconds=5)
        self.add_behaviour(self.PullBehaviour(period=2, start_at=start_at))
        template = spade.template.Template(metadata={"performative": "REQ2"})
        self.add_behaviour(self.RecvBehaviour(), template)
        template = spade.template.Template(metadata={"performative": "PULL"})
        self.add_behaviour(self.Recv2Behaviour(), template)

        print("{} ready.".format(self.name))

    def add_value(self, value):
        # seleccion del valor adecuado entre el propio y el nuevo
        self.value = max(self.value, value)

    def add_contacts(self, contact_list):
        self.contacts = [c.jid for c in contact_list if c.jid != self.jid]
        self.length = len(self.contacts)

    class PullBehaviour(spade.behaviour.PeriodicBehaviour):
        async def run(self):
            k=1
            random_contacts = random.sample(self.agent.contacts, k)
            for jid in random_contacts:
                body = json.dumps({"value": 0, "timestamp": time.time()})
                msg = spade.message.Message(to=str(jid), body=body, metadata={"performative": "REQ2"})
                await self.send(msg)

    # comportamiento encargado de responder a la peticion REQ
    class RecvBehaviour(spade.behaviour.CyclicBehaviour):

        async def run(self):
            msg = await self.receive(timeout=2)
            if msg:
                body = json.loads(msg.body)
                senderID = msg.sender
                body = json.dumps({"value": self.agent.value, "timestamp": time.time()})
                msg = spade.message.Message(to=str(senderID), body=body, metadata={"performative": "PULL"})
                await self.send(msg)


    # comportamiento encargado de responder a la peticion REQ
    class Recv2Behaviour(spade.behaviour.CyclicBehaviour):

        async def run(self):
            msg = await self.receive(timeout=2)
            if msg:
                body = json.loads(msg.body)
                self.agent.add_value(body["value"])


@click.command()
@click.option('--count', default=10, help='Number of agents.')
def main(count):
    agents = []
    print("Creating {} agents...".format(count))
    for x in range(1, count + 1):
        print("Creating agent {}...".format(x))
        # nos guardamos la lista de agentes para poder visualizar el estado del proceso gossiping
        # el servidor estÃ¡ fijado a gtirouter.dsic.upv.es, si se tiene un serviodor XMPP en local, se puede sustituir por localhost
        agents.append(PushAgent("alcargra_{}@localhost".format(x), "test"))

    # este tiempo trata de esperar que todos los agentes estan registrados, depende de la cantidad de agentes que se lancen
    time.sleep(4)

    # se le pasa a cada agente la lista de contactos
    for ag in agents:
        ag.add_contacts(agents)
        ag.value = 0

    # se lanzan todos los agentes
    for ag in agents:
        ag.start()

    # este tiempo trata de esperar que todos los agentes estan ready, depende de la cantidad de agentes que se lancen
    time.sleep(3)
    
    # este bucle imprime los valores que almacena cada agente y termina cuando todos tienen el mismo valor (consenso)
    while True:
        try:
            time.sleep(1)
            status = [ag.value for ag in agents]
            print("STATUS: {}".format(status))
            if len(set(status)) <= 1:
                print("Gossip done.")
                break
        except KeyboardInterrupt:
            break

    # se para a todos los agentes
    for ag in agents:
        ag.stop()
    print("Agents finished")


if __name__ == '__main__':
    main()