import datetime
import json
import random
import time
import click

import spade


class PushAgent(spade.agent.Agent):

    def __init__(self, jid, password, k = 1, calc = 'max'):
        super().__init__(jid, password)
        self.k = k
        self.calc = calc
    
    async def setup(self):
        self.value = random.randint(1, 1000)
        self.tiempo = 0
        self.msg_enviados = 0
        self.tiempo_inicio = time.time()
        
        start_at = datetime.datetime.now() + datetime.timedelta(seconds=5)
        self.add_behaviour(self.PullBehaviour(period=2, start_at=start_at))
        self.add_behaviour(self.PushBehaviour(period=2, start_at=start_at))
        template = spade.template.Template(metadata={"performative": "REQ2"})
        self.add_behaviour(self.RecvBehaviour(), template)
        template = spade.template.Template(metadata={"performative": "PULL"})
        self.add_behaviour(self.Recv2Behaviour(), template)
        template = spade.template.Template(metadata={"performative": "PUSH"})
        self.add_behaviour(self.Recv3Behaviour(), template)

        print("{} ready.".format(self.name))

    def add_value(self, value):
        # seleccion del valor adecuado entre el propio y el nuevo
        self.tiempo = time.time() - self.tiempo_inicio
        self.msg_recibidos += 1
        if(self.calc == 'max'):
            self.value = max(self.value, value)
        elif(self.calc == 'avg'):
            self.valuerec = (self.value + value)
        if self.msg_recibidos == self.k:
            self.value = self.valuerec / self.k
            self.valuerec = self.value
            self.msg_recibidos = 0

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
                self.agent.msg_enviados += 1
                await self.send(msg)
    
    class PushBehaviour(spade.behaviour.PeriodicBehaviour):

        async def run(self):
            # el numero de amigos estÃ¡ fijado a 1, se puede modificar
            k=1
            #print("{} period with k={}!".format(self.agent.name, k))
            random_contacts = random.sample(self.agent.contacts, self.agent.k)
            #print("{} sending to {}".format(self.agent.name, [x.localpart for x in random_contacts]))
            
            # se envia el mensaje con el dato a los k amigos seleccionados
            for jid in random_contacts:
                body = json.dumps({"value": self.agent.value, "timestamp": time.time()})
                msg = spade.message.Message(to=str(jid), body=body, metadata={"performative": "PUSH"})
                self.agent.msg_enviados += 1
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
                self.agent.msg_enviados += 1
                await self.send(msg)


    # comportamiento encargado de responder a la peticion REQ
    class Recv2Behaviour(spade.behaviour.CyclicBehaviour):

        async def run(self):
            msg = await self.receive(timeout=2)
            if msg:
                body = json.loads(msg.body)
                self.agent.add_value(body["value"])

    class Recv3Behaviour(spade.behaviour.CyclicBehaviour):

        async def run(self):
            msg = await self.receive(timeout=2)
            if msg:
                body = json.loads(msg.body)
                self.agent.add_value(body["value"])


@click.command()
@click.option('--k', default=1, help='Number of friends.')
@click.option('--count', default=10, help='Number of agents.')
@click.option('--calc', default='max', help='max or avg for accepting values from agents.')
def main(count,k,calc):
    agents = []
    print("Creating {} agents...".format(count))
    for x in range(1, count + 1):
        print("Creating agent {}...".format(x))
        # nos guardamos la lista de agentes para poder visualizar el estado del proceso gossiping
        # el servidor estÃ¡ fijado a gtirouter.dsic.upv.es, si se tiene un serviodor XMPP en local, se puede sustituir por localhost
        agents.append(PushAgent("alcargra_{}@gtirouter.dsic.upv.es".format(x), "test", k=k, calc=calc))

    # este tiempo trata de esperar que todos los agentes estan registrados, depende de la cantidad de agentes que se lancen
    time.sleep(count*0.3)

    # se le pasa a cada agente la lista de contactos
    for ag in agents:
        ag.add_contacts(agents)
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
            if(calc == 'max'):
                if len(set(status)) <= 1:
                    print("Gossip done.")
                    break
            elif(calc == 'avg'):
                minVal = min([ag.value for ag in agents])
                maxVal = max([ag.value for ag in agents])
                if maxVal-minVal <= 0.5:
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