# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionBuyProduct(Action):

    def name(self) -> Text:
        return "buy_product"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        p = next(tracker.get_latest_entity_values("producto"), None)

        if not p:
            msg = "Producto no encontrado"
        else:
            msg = str(p)+" encargado, algo más?"

        dispatcher.utter_message(text=msg)

        return []
