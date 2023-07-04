import urllib.request
import urllib.parse
import json
from prettytable import PrettyTable
import datetime

class VisualtimeApi:
    TOKEN = "YVhSbGNqUXhOemM9ODgwMDhhMDFlNjM3OTkxNTE1ODBmMmQzYWYxNzcxMDhmZjczNDljYzM4MzlmM2RmZDVlNTBkOWMyNzlhODQzNw%3D%3D"
    URI = "https://vtliveapi.visualtime.net/api/v2"
    URL = URI + "/ScheduleService.svc/"
    URL_EMPLOYEE = URI + "/EmployeeService.svc/"
    URL_ACCRUALS = URI + "/AccrualsService.svc/"
    @staticmethod
    def getPublicHolidays():
        contents = urllib.request.urlopen(VisualtimeApi.URL + "GetPublicHolidays?Token="+VisualtimeApi.TOKEN).read()
        data_json = json.loads(contents) 
        x = PrettyTable()
        x.title = "Days off"
        x.field_names = ["Festivo", "Fecha", "Tipo"]
        for days in data_json["Value"]:
            title = days["ID"]
            for day in days["PublicHolidaysDetails"]:
                datetime1 = datetime.datetime.strptime(day["PublicHolidayDate"]["Data"].split(" ")[0], '%Y-%m-%d').strftime('%A, %d %B %Y')
                x.add_row([day["Description"], datetime1, title])                          
        return x.get_string()
        
    @staticmethod
    def getHolidays(employeeID, start_date = None, end_date = None):
        today = datetime.datetime.now()            
        if end_date == None :           
            if start_date == None:                
                year = today.year
                end_date = '{}-12-31 23:59:50'.format(year)
            else:
                t = datetime.datetime(today.year + 1, today.month, 1, 0, 0)
                end_date = t.strftime("%Y-%m-%d %H:%M:%S") 
        else:
            end_date = end_date + " 23:59:50"
        
        if start_date == None:            
            year = today.year
            start_date = '{}-01-01 00:00:00'.format(year)
        else:
            start_date = start_date + " 00:00:00"         
        
        date1 = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')     
        date2 = datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')         
        if date1 < date2:        
            start_date = urllib.parse.quote(start_date + " +01")
            end_date = urllib.parse.quote(end_date + " +01")              
            contents = urllib.request.urlopen(VisualtimeApi.URL + "GetHolidays?Token=" + VisualtimeApi.TOKEN + "&StartDate=" + start_date + "&EndDate=" + end_date + "&EmployeeID=" + employeeID).read()
            data_json = json.loads(contents) 
            x = PrettyTable()
            x.title = "Holidays planned between "+ date1.strftime("%d/%m/%Y")  + " and " + date2.strftime("%d/%m/%Y")
            x.field_names = ["Fecha", "Motivo"]
            for day in data_json["Value"]:
                current_date = datetime.datetime.strptime(day["PlannedDate"]["Data"].split(" ")[0], '%Y-%m-%d')
                datetime1 = current_date.strftime('%A, %d %B %Y')
                if current_date > today:
                    datetime1 = datetime1 + " *"
                x.add_row([datetime1, day["ReasonName"]])
            return x.get_string()    
        else:
            return "Init date must be higher than ending date"
    
    @staticmethod   
    def getIdentifier(username):
        value = urllib.parse.quote(username + "@iter.es")    
        contents = urllib.request.urlopen(VisualtimeApi.URL_EMPLOYEE + "GetEmployees?Token=" + VisualtimeApi.TOKEN + "&OnlyWithActiveContract=true&IncludeOldData=false&FieldName=Correo%20electr%C3%B3nico&FieldValue="+value).read()
        data_json = json.loads(contents)
        identifier = None
        for user in data_json["Value"]:
            identifier = user["ID"]
        
        return identifier
    
    @staticmethod     
    def getAccruals(employeeID, params = None):
        now = datetime.datetime.now()
        atDate = now.strftime("%Y-%m-%d %H:%M:%S") + " +01"
        atDate = urllib.parse.quote(atDate)
        contents = urllib.request.urlopen(VisualtimeApi.URL_ACCRUALS + "GetAccrualsAtDate?Token=" + VisualtimeApi.TOKEN + "&AtDate=" + atDate + "&Employee=" + employeeID).read()
        data_json = json.loads(contents)
        x = PrettyTable()
        x.title = "Current accruals at " + now.strftime("%d/%m/%Y")
        empty_list = True
        for accrual in data_json["Value"]:
            if accrual["AccrualShortName"] == "Vpe" and (params == "VAC" or params == None):
                x.add_column("Vacaciones pendientes", [str(accrual["AccrualValue"]) + " días"])
                empty_list = False
            elif accrual["AccrualShortName"] == "VAA"  and (params == "VAC" or params == None):
                if accrual["AccrualValue"] > 0:
                    x.add_column("Vacaciones año anterior", [str(accrual["AccrualValue"]) + " días"])
                    empty_list = False
            elif accrual["AccrualShortName"] == "APD"  and (params == "VAC" or params == None):
                x.add_column("Asuntos propios pendientes", [str(accrual["AccrualValue"]) + " días"])
                empty_list = False
            elif accrual["AccrualShortName"] == "BHS"  and (params == "BHS" or params == None):
                timeformat = ""
                if accrual["AccrualValue"] >= 0.0:   
                    timeformat = '{0:02.0f}:{1:02.0f}'.format(*divmod(accrual["AccrualValue"] * 60, 60))                    
                else:
                    value = value * -1.0
                    timeformat = '-{0:02.0f}:{1:02.0f}'.format(*divmod(accrual["AccrualValue"] * 60, 60))               
                x.add_column("Bolsa horas mensual", [timeformat])
                empty_list = False
            elif accrual["AccrualShortName"] == "LCD"  and (params == "LCD" or params == None):
                if accrual["AccrualValue"] > 0:
                    x.add_column("Lactancia", [str(accrual["AccrualValue"]) + " días"])
                    empty_list = False 
            elif accrual["AccrualShortName"] == "LCH"  and (params == "LCH" or params == None):
                if accrual["AccrualValue"] > 0:
                    timeformat = '{0:02.0f}:{1:02.0f}'.format(*divmod(accrual["AccrualValue"] * 60, 60))
                    x.add_column("Lactancia", [timeformat])      
                    empty_list = False
            elif accrual["AccrualShortName"] == "HSM"  and (params == "HSM" or params == None):
                if accrual["AccrualValue"] > 0:
                    timeformat = '{0:02.0f}:{1:02.0f}'.format(*divmod(accrual["AccrualValue"] * 60, 60))
                    x.add_column("Horas sindicales", [timeformat])     
                    empty_list = False
            elif accrual["AccrualShortName"] == "PAU"  and (params == "PAU" or params == None):
                timeformat = '{0:02.0f}:{1:02.0f}'.format(*divmod(accrual["AccrualValue"] * 60, 60))
                x.add_column("Horas recuperables anual", [timeformat])
                empty_list = False
            elif accrual["AccrualShortName"] == "SCD"  and (params == "SCD" or params == None):
                if accrual["AccrualValue"] > 0:
                    timeformat = '{0:02.0f}:{1:02.0f}'.format(*divmod(accrual["AccrualValue"] * 60, 60))
                    x.add_column("Horas compensadas pendientes", [timeformat])
                    empty_list = False
    
        if empty_list:
            return None
        else:
            return x.get_string()