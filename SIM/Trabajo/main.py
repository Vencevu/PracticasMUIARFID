import spade
import datetime
import json
import random
import time
import click

random.seed(42)

class AgenteTarea(spade.agent.Agent):

    async def setup(self):
        self.asignado = ""
        self.asignadoprev = ""
        self.puja = 0
        self.msg_enviados = 0
        self.tiempo = 0
        self.pujas_recibidas = {}
        self.ronda = 0

        template = spade.template.Template(metadata={"performative": "MAKE_BET"})
        self.add_behaviour(self.RecepcionBehaviour(), template)

        print("{} ready.".format(self.name))
        self.tiempo_inicio = time.time()
    
    def add_contact(self, contact_list):
        self.contacts = [c.jid for c in contact_list]
    
    class RecepcionBehaviour(spade.behaviour.CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=2)
            if msg:
                body = json.loads(msg.body)
                self.agent.pujas_recibidas[msg.sender] = body["puja"]
                print("Pujas a ", self.agent.name, ": ", len(self.agent.pujas_recibidas))
                self.agent.tiempo = time.time() - self.agent.tiempo_inicio
            if self.agent.ronda and len(self.agent.pujas_recibidas) > 0:
                print(self.agent.pujas_recibidas)
                mejor_pujador = max(self.agent.pujas_recibidas, key=self.agent.pujas_recibidas.get)
                self.agent.puja = self.agent.pujas_recibidas[mejor_pujador]
                self.agent.precio += self.agent.puja
                self.agent.asignado = mejor_pujador
                # print("Puja aceptada por ", self.agent.name)
                body = json.dumps({"asignacion": 1, "timestamp": time.time()})
                msg2 = spade.message.Message(to=str(mejor_pujador), body=body, metadata={"performative": "ACCEPT_BET"})
                await self.send(msg2)
                self.agent.msg_enviados += 1

                if self.agent.asignadoprev != "":
                    body = json.dumps({"asignacion": 0, "timestamp": time.time()})
                    msg3 = spade.message.Message(to=str(self.agent.asignadoprev), body=body, metadata={"performative": "REPLACE_BET"})
                    await self.send(msg3)
                    self.agent.msg_enviados += 1

                    # print("Tarea ", self.agent.name, " reemplazada")
                
                self.agent.asignadoprev = mejor_pujador

                for pujador in self.agent.contacts:
                    body = json.dumps({"precio": self.agent.precio, "timestamp": time.time()})
                    msg4 = spade.message.Message(to=str(pujador), body=body, metadata={"performative": "UPDATE_PRICE"})
                    await self.send(msg4)
                    self.agent.msg_enviados += 1

                    if pujador != mejor_pujador:
                        body2 = json.dumps({"deny": 1, "timestamp": time.time()})
                        msg = spade.message.Message(to=str(pujador), body=body2, metadata={"performative": "DENY_BET"})
                        await self.send(msg)
                        self.agent.msg_enviados += 1
                        # print("Puja de ",body["puja"] ,"denegada por ", self.agent.name, ". Puja minima: ", self.agent.puja)

                self.agent.pujas_recibidas = {}
                self.agent.ronda = 0
                self.agent.tiempo = time.time() - self.agent.tiempo_inicio


class AgenteCliente(spade.agent.Agent):

    async def setup(self):
        self.msg_enviados = 0
        self.tarea_obj = 0
        self.tarea_asignada = ""
        self.tiempo = 0
        self.puja_enable = True
        
        start_at = datetime.datetime.now() + datetime.timedelta(seconds=5)
        self.add_behaviour(self.PujaBehav(period=2, start_at=start_at))

        template = spade.template.Template(metadata={"performative": "ACCEPT_BET"})
        self.add_behaviour(self.RespuestaBehav(period=1, start_at=start_at), template)

        template = spade.template.Template(metadata={"performative": "UPDATE_PRICE"})
        self.add_behaviour(self.UpdateBehav(period=1, start_at=start_at), template)

        template = spade.template.Template(metadata={"performative": "REPLACE_BET"})
        self.add_behaviour(self.ReplaceBehav(period=1, start_at=start_at), template)

        template = spade.template.Template(metadata={"performative": "DENY_BET"})
        self.add_behaviour(self.DenyBehav(period=1, start_at=start_at), template)

        print("{} ready.".format(self.name))
        self.tiempo_inicio = time.time()

    def add_contact(self, contact_list):
        self.contacts = [c.jid for c in contact_list]

    def calc_coste(self, id):
        self.tiempo = time.time() - self.tiempo_inicio
        return self.costes[self.jid][id] + self.precios[id]

    class PujaBehav(spade.behaviour.PeriodicBehaviour):
        async def run(self):
            if self.agent.puja_enable:
                pujas = {k: self.agent.calc_coste(k) for k in self.agent.contacts}
                pujas = dict(sorted(pujas.items(), key=lambda item: item[1]))

                puja1, puja2 = list(pujas.values())[self.agent.tarea_obj], list(pujas.values())[self.agent.tarea_obj+1]
                puja_value = puja2 - puja1 + 0.001
 
                puja_id = list(pujas.keys())[self.agent.tarea_obj]
                body = json.dumps({"puja": puja_value, "timestamp": time.time()})
                msg = spade.message.Message(to=str(puja_id), body=body, metadata={"performative": "MAKE_BET"})
                await self.send(msg)
                self.agent.msg_enviados += 1
                self.agent.puja_enable = False
                
                print("Puja de ", self.agent.name, " a ", puja_id, " con valor ", puja_value, "(",puja1, "-",puja2 ,")")

    class RespuestaBehav(spade.behaviour.PeriodicBehaviour):
        async def run(self):
            if(self.agent.tarea_asignada == ""):
                msg = await self.receive(timeout=2)
                if msg:
                    body = json.loads(msg.body)
                    if(body["asignacion"] == 1): 
                        self.agent.tarea_asignada = msg.sender
                        self.agent.tarea_obj = 0
    
    class UpdateBehav(spade.behaviour.PeriodicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=2)
            if msg:
                body = json.loads(msg.body)
                self.agent.precios[msg.sender] = body["precio"]
    
    class ReplaceBehav(spade.behaviour.PeriodicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=2)
            if msg:
                body = json.loads(msg.body)
                if(body["asignacion"] == 0): self.agent.tarea_asignada = ""
                self.agent.puja_enable = True

    class DenyBehav(spade.behaviour.PeriodicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=2)
            if msg:
                # self.agent.tarea_obj = 1
                self.agent.puja_enable = True

@click.command()
@click.option('--count', default=10, help='Number of agents.')
def main(count):
    agentsC, agentsT = [], []
    print("Creating {} agents...".format(count*2 + 3))
    n_pujadores = count
    for x in range(1, n_pujadores + 1):
        print("Creating agent Pujador {}...".format(x))
        agentsC.append(AgenteCliente("pujador_{}@localhost".format(x), "test"))
    n_tareas = count + 3
    for x in range(1, n_tareas + 1):
        print("Creating agent Tarea {}...".format(x))
        agentsT.append(AgenteTarea("tarea_{}@localhost".format(x), "test"))
    # este tiempo trata de esperar que todos los agentes estan registrados, depende de la cantidad de agentes que se lancen
    time.sleep(count*3*0.3)

    #Creamos tablas de coste y precios
    costes = {k.jid: {t.jid: random.randint(1, n_tareas*2) for t in agentsT} for k in agentsC}
    precios = {k.jid: 0 for k in agentsT}

    # se le pasa a cada agente la lista de contactos, costes y precios
    for ag in agentsT:
        ag.add_contact(agentsC)
        ag.asignado = ""
        ag.precio = precios[ag.jid]
    
    for ag in agentsC:
        ag.add_contact(agentsT)
        ag.costes = costes
        ag.precios = precios
        ag.tarea_asignada = ""
    print("Iniciando pujadores...")
    for agc in agentsC:
        agc.start()
    print("Iniciando tareas...")
    for ag in agentsT:
        ag.start()
        
    # este tiempo trata de esperar que todos los agentes estan ready, depende de la cantidad de agentes que se lancen
    time.sleep(count*3*0.3)

    def minMax(arr):
        min_value = 0
        max_value = 0
        n=len(arr)
        
        arr.sort()
        j=n-3
        for i in range(n-1):
            min_value += arr[i]
            max_value += arr[j]
            j-=1

        print(min_value)
    
    # este bucle imprime los valores que almacena cada agente y termina cuando todos tienen el mismo valor (consenso)
    while True:
        try:
            time.sleep(1)
            status = [a.name for a in agentsT if a.asignado == ""]
            statusP = [a.name for a in agentsC if a.tarea_asignada == ""]
            costeTotal = [a.precio for a in agentsT if a.asignado != '']
            relaciones = {a.name: a.tarea_asignada for a in agentsC}
            print("COSTE TOTAL: {}".format(sum(costeTotal)))
            print([a.precio for a in agentsT])
            print([1 if a.puja_enable else 0 for a in agentsC])
            print([1 if a.asignado != '' else 0 for a in agentsT])
            if len([a for a in agentsC if a.puja_enable]) == 0:
                print("Ronda de pujas terminada")
                for aT in agentsT:
                    aT.ronda = 1
            if len(status) == 0 or len(statusP) == 0:
                print("FIN")
                num_msg = sum([a.msg_enviados for a in agentsT]) + sum([a.msg_enviados for a in agentsC])
                total_tiempo = max([ag.tiempo for ag in agentsC]+[ag.tiempo for ag in agentsT])
                print("MENSAJES ENVIADOS: ", num_msg)
                print("TIEMPO: ", total_tiempo)
                minMax([a.precio for a in agentsT])
                break
        except KeyboardInterrupt:
            break

    # se para a todos los agentes
    for ag in agentsC:
        ag.stop()
    print("Agents finished")

if __name__ == '__main__':
    main()