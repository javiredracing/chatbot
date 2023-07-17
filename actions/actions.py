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
import dateparser
from dateutil.relativedelta import relativedelta

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
                return [SlotSet("access_id", userCode), SlotSet("password","TOKEN")]

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
                if result is not None:                    
                    dispatcher.utter_message(text = result)
            else:
                dispatcher.utter_message(text = "Información no disponible")
        else:
            dispatcher.utter_message(response = "utter_authentication_failure")
        return[]

class Accruals(Action):
    def name(self) -> Text:
        return "action_show_accruals"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:        
        userCode = tracker.get_slot("access_id")
        print(json.dumps(tracker.latest_message['entities']))
        accrual = next(tracker.get_latest_entity_values("accruals"), None)
        if userCode is not None:            
            result = VisualtimeApi.getAccruals(userCode, accrual)
            if result is None:                    
                result = "Información no disponible"
            dispatcher.utter_message(text = result)
        else:
            dispatcher.utter_message(response = "utter_authentication_failure")

        return[]

class Signings(Action):
    def name(self) -> Text:
        return "action_show_signings"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        userCode = tracker.get_slot("access_id")
        
        start_date = None
        end_date = None
        jsondate = None
        
        #print(json.dumps(tracker.latest_message['entities']))
        for entity in tracker.latest_message['entities']:
            if entity['entity'] == 'time':
                if entity['additional_info']['type'] == "value":
                    jsondate = entity['additional_info']['values'][0]                    
                    if start_date is None:
                        start_date = dateparser.parse(jsondate['value'])
                    else:
                        end_date = dateparser.parse(jsondate['value'])
                        break           
                    
                elif entity['additional_info']['type'] == "interval":
                    start_date = dateparser.parse(entity['value']['from'])
                    end_date = dateparser.parse(entity['value']['to'])                    
                    break

        if start_date is None:
            today = datetime.datetime.now() 
            start_date = datetime.datetime(today.year, today.month, today.day, 0, 0)
            end_date = datetime.datetime(today.year, today.month, today.day, 23, 59)
        
        elif end_date is None:
            if jsondate['grain'] == "day":               
                end_date = start_date + datetime.timedelta(days=1)
            elif jsondate['grain'] == "month":
                if start_date.date() > datetime.date.today():
                    start_date = start_date + relativedelta(years=-1)
                end_date = start_date + relativedelta(months=+1)
            elif jsondate['grain'] == "week": 
                end_date = start_date + datetime.timedelta(weeks=1)
            else:
                end_date = start_date + relativedelta(years=-1)
        
        if start_date > end_date:
            tmp = start_date
            start_date = end_date
            end_date = tmp          
        
        #print(start_date)
        #print(end_date)
        if userCode is not None:
            result = VisualtimeApi.getSignings(userCode, start_date, end_date)
            if result is None:                    
                result = "Información no disponible"
            dispatcher.utter_message(text = result)
        else:
            dispatcher.utter_message(response = "utter_authentication_failure")
        return[]
        
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