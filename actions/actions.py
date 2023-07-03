# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker#, FormValidationAction
from rasa_sdk.events import SlotSet, AllSlotsReset
from rasa_sdk.executor import CollectingDispatcher

from APIs.VisualtimeApi import *

class AuthenticatedAction(Action):
    def name(self) -> Text:
        return "action_authenticated"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        identifier = tracker.get_slot("identifier")
        password = tracker.get_slot("password")
        access_level = "1"
        if identifier is not None and password == "1111":
            dispatcher.utter_message(response="utter_authenticated_successfully")
            return [SlotSet("access_level", access_level), SlotSet("password","1111")]
        else:
            dispatcher.utter_message(response="utter_authentication_failure")
            return[ SlotSet("password",None), SlotSet("identifier",None), SlotSet("access_level", "0")]
        return []

class DaysOff(Action):
    def name(self) -> Text:
        return "action_show_days_off"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        result = VisualtimeApi.getPublicHolidays()
        dispatcher.utter_message(text = result)
        return[]
        
class Holidays(Action):
    def name(self) -> Text:
        return "action_show_holidays"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        identifier = tracker.get_slot("identifier")
        if identifier != None:
            code = 457
            result = VisualtimeApi.getHolidays(code)
            dispatcher.utter_message(text = result)
        else:
            dispatcher.utter_message(response = "utter_authentication_failure")
        return[]

class ClearLogin(Action): 
    def name(self) -> Text:
        return "action_clear_login"
        
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return[ SlotSet("password",None), SlotSet("identifier",None), SlotSet("access_level", "0")]
        
    
'''        
class ValidateAuthFormAction(FormValidationAction):
    def name(self) -> Text:
        return "validate_auth_form"

    #def validate_identifier(self, value: Text, dispatcher: "CollectingDispatcher", tracker: "Tracker", domain: "DomainDict",) -> List[EventType]:
    def validate_identifier(self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict,) -> Dict[Text, Any]:
        returned_slots = {}    
        if value is not None: #check if valid
            returned_slots = {"identifier":value}
        else:
            returned_slots = {"identifier": None}
            if value is None:
                dispatcher.utter_message(template="utter_identifier_not_valid")
            elif not is_valid_user(value):
                dispatcher.utter_message(template="utter_identifier_not_registered")
        return returned_slots
    
    def validate_password(self, value: TEXT, dispatcher: "CollectingDispatcher", tracker: "Tracker", domain: "DomainDict",) -> Dict[Text, Any]:
        identifier = tracker.get_slot("identifier")
        password = tracker.get_slot("password")
        returned_slots = {}
        if value is not None and password == "1111":
            returned_slots = {"password":value}
        else:
            returned_slots = {"password":None}
            dispatcher.utter_message(template="utter_pass_not_valid")
        return returned_slots
 '''