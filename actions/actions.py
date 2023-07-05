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
        if identifier is not None and password == "1111":            
            userCode = VisualtimeApi.getIdentifier(identifier)
            if userCode is not None:
                dispatcher.utter_message(response="utter_authenticated_successfully")
                return [SlotSet("access_idshow ", str(userCode)), SlotSet("password","TOKEN")]

        dispatcher.utter_message(response="utter_authentication_failure")
        return[SlotSet("password",None), SlotSet("identifier",None), SlotSet("access_id", None)]
        #return []

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
        userCode = tracker.get_slot("access_id")
        if userCode is not None:            
            result = VisualtimeApi.getHolidays(userCode) 
            if result is not None:
                dispatcher.utter_message(text = result)
                result = VisualtimeApi.getAccruals(userCode, "VAC")
                if result is None:                    
                    dispatcher.utter_message(text = result)
            else:
                dispatcher.utter_message(text = "No info found")
        else:
            dispatcher.utter_message(response = "utter_authentication_failure")
        return[]

class Accruals(Action):
    def name(self) -> Text:
        return "action_show_accruals"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:        
        userCode = tracker.get_slot("access_id")
        accrual = next(tracker.get_latest_entity_values("accruals"), None)
        if userCode is not None:            
            result = VisualtimeApi.getAccruals(userCode, accrual)
            if result is None:                    
                result = "No info found"
            dispatcher.utter_message(text = result)
        else:
            dispatcher.utter_message(response = "utter_authentication_failure")
        
class ClearLogin(Action): 
    def name(self) -> Text:
        return "action_clear_login"
        
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return[SlotSet("password",None), SlotSet("identifier",None), SlotSet("access_id", None)]
        
    
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