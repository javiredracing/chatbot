import urllib.request
import urllib.parse
import json
from prettytable import PrettyTable
import datetime
import time

class VisualtimeApi:
    TOKEN = "YVhSbGNqUXhOemM9ODgwMDhhMDFlNjM3OTkxNTE1ODBmMmQzYWYxNzcxMDhmZjczNDljYzM4MzlmM2RmZDVlNTBkOWMyNzlhODQzNw%3D%3D"
    URI = "https://vtliveapi.visualtime.net/api/v2"
    URL = URI + "/ScheduleService.svc/"
    URL_EMPLOYEE = URI + "/EmployeeService.svc/"
    URL_ACCRUALS = URI + "/AccrualsService.svc/"
    URL_PUNCHES = URI + "/PunchesService.svc/"
    
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
        #return x.get_string()
        return x.get_formatted_string("html")
        
    @staticmethod
    def getHolidays(employeeID, start_date = None, end_date = None):
        today = datetime.datetime.now()            
        if end_date is None :           
            if start_date is None:                
                year = today.year
                end_date = '{}-12-31 23:59:50'.format(year)
            else:
                t = datetime.datetime(today.year + 1, today.month, 1, 0, 0)
                end_date = t.strftime("%Y-%m-%d %H:%M:%S") 
        else:
            end_date = end_date + " 23:59:50"
        
        if start_date is None:            
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

            finded = False
            for index, day in enumerate(data_json["Value"]):
                divider = False
                #set divider: check if next day is upper than today
                if(index<(len(data_json["Value"])-1)) and not finded:  
                    nextDay = data_json["Value"][index + 1]
                    nextDay_date = datetime.datetime.strptime(nextDay["PlannedDate"]["Data"].split(" ")[0], '%Y-%m-%d')
                    divider = nextDay_date > today
                    finded = divider
                current_date = datetime.datetime.strptime(day["PlannedDate"]["Data"].split(" ")[0], '%Y-%m-%d')
                datetime1 = current_date.strftime('%A, %d %B %Y')

                x.add_row([datetime1, day["ReasonName"]], divider=divider)
            
            #return x.get_string() 
            return x.get_html_string()          
        else:
            return None
    
    @staticmethod   
    def getIdentifier(username):
        value = urllib.parse.quote(username + "@iter.es")    
        contents = urllib.request.urlopen(VisualtimeApi.URL_EMPLOYEE + "GetEmployees?Token=" + VisualtimeApi.TOKEN + "&OnlyWithActiveContract=true&IncludeOldData=false&FieldName=Correo%20electr%C3%B3nico&FieldValue="+value).read()
        data_json = json.loads(contents)
        identifier = None
        for user in data_json["Value"]:
            identifier = str(user["ID"])
        return identifier
    
    @staticmethod     
    def getAccruals(employeeID, params=None):
        now = datetime.datetime.now()
        atDate = now.strftime("%Y-%m-%d %H:%M:%S") + " +01"
        atDate = urllib.parse.quote(atDate)
        contents = urllib.request.urlopen(VisualtimeApi.URL_ACCRUALS + "GetAccrualsAtDate?Token=" + VisualtimeApi.TOKEN + "&AtDate=" + atDate + "&Employee=" + employeeID).read()
        data_json = json.loads(contents)
        x = PrettyTable()
        x.title = "Saldos actuales " + now.strftime("%d/%m/%Y")
        empty_list = True
        for accrual in data_json["Value"]:
            if accrual["AccrualShortName"] == "Vpe" and (params == "VAC" or params is None):
                x.add_column("Vacaciones pendientes", [str(accrual["AccrualValue"]) + " días"])
                empty_list = False
            elif accrual["AccrualShortName"] == "VAA"  and (params == "VAC" or params is None):
                if accrual["AccrualValue"] > 0:
                    x.add_column("Vacaciones año anterior", [str(accrual["AccrualValue"]) + " días"])
                    empty_list = False
            elif accrual["AccrualShortName"] == "APD"  and (params == "VAC" or params is None):
                x.add_column("Asuntos propios pendientes", [str(accrual["AccrualValue"]) + " días"])
                empty_list = False
            elif accrual["AccrualShortName"] == "BHS"  and (params == "BHS" or params is None):
                timeformat = ""
                if accrual["AccrualValue"] >= 0.0:   
                    timeformat = '+{0:02.0f}:{1:02.0f}'.format(*divmod(accrual["AccrualValue"] * 60, 60))                    
                else:
                    timeformat = '-{0:02.0f}:{1:02.0f}'.format(*divmod(accrual["AccrualValue"] * 60 * -1, 60))               
                x.add_column("Bolsa horas mensual", [timeformat])
                empty_list = False
            elif accrual["AccrualShortName"] == "LCD"  and (params == "LAC" or params is None):
                if accrual["AccrualValue"] > 0:
                    x.add_column("Lactancia", [str(accrual["AccrualValue"]) + " días"])
                    empty_list = False 
            elif accrual["AccrualShortName"] == "LCH"  and (params == "LAC" or params is None):
                if accrual["AccrualValue"] > 0:
                    timeformat = '{0:02.0f}:{1:02.0f}'.format(*divmod(accrual["AccrualValue"] * 60, 60))
                    x.add_column("Lactancia", [timeformat])      
                    empty_list = False
            elif accrual["AccrualShortName"] == "HSM"  and (params == "HSM" or params is None):
                if accrual["AccrualValue"] > 0:
                    timeformat = '{0:02.0f}:{1:02.0f}'.format(*divmod(accrual["AccrualValue"] * 60, 60))
                    x.add_column("Horas sindicales", [timeformat])     
                    empty_list = False
            elif accrual["AccrualShortName"] == "PAU"  and (params == "PAU" or params is None):
                timeformat = '{0:02.0f}:{1:02.0f}'.format(*divmod(accrual["AccrualValue"] * 60, 60))
                x.add_column("Horas recuperables anual", [timeformat])
                empty_list = False
            elif accrual["AccrualShortName"] == "SCD"  and (params == "SCD" or params is None):
                if accrual["AccrualValue"] > 0:
                    timeformat = '{0:02.0f}:{1:02.0f}'.format(*divmod(accrual["AccrualValue"] * 60, 60))
                    x.add_column("Horas compensadas pendientes", [timeformat])
                    empty_list = False
    
        if empty_list:
            return None
        else:
            #return x.get_string()
            return x.get_formatted_string("html")
            
    @staticmethod     
    def getSignings(employeeID, start_date = None, end_date = None):        
        if start_date is not None and end_date is not None:
            offset = " +01"  #winter time
            if time.localtime().tm_isdst > 0:
                offset = " +02"     #summer time
                        
            date1 = start_date.strftime("%Y-%m-%d %H:%M:%S")        
            date2 = end_date.strftime("%Y-%m-%d %H:%M:%S")
            start_date = urllib.parse.quote(date1 + offset)
            end_date = urllib.parse.quote(date2 + offset)
            contents = urllib.request.urlopen(VisualtimeApi.URL_PUNCHES + "GetPunchesBetweenDates?Token=" + VisualtimeApi.TOKEN + "&StartDate=" + start_date + "&EndDate=" + end_date + "&EmployeeID=" + employeeID).read()       
            data_json = json.loads(contents)
            x = PrettyTable()
            x.title = "Fichajes"  
            x.field_names = ["Fecha", "Hora", "Tipo"]            
            #mycolum = []
            #current_date = None
            for sign in data_json["Value"]:
                split = sign["DateTime"]["Data"].split(" ")            
                signType = "E" if sign["ActualType"] == 1 else "S" #check E/S
                mySignDay = split[0]
                mySignHours =  split[1]
                date_object = datetime.datetime.strptime(mySignDay, '%Y-%m-%d')
                date_title = date_object.strftime("%a,%d/%m/%Y")
                x.add_row([date_title, mySignHours, signType]) 
                # if current_date is None:
                    # current_date = date_title
                # if date_title != current_date:                
                    # x.add_column(current_date, mycolum) 
                    # mycolum = []
                    # current_date = date_title                
                # mycolum.append(mySignHours + " " + signType)
                # print(mySignHours)

            # if len(mycolum)> 0:
                # x.add_column(current_date, mycolum)
                   
            #return x.get_string()
            return x.get_formatted_string("html") 
        else:
            return None
       