import urllib.request
import urllib.parse
import json
from prettytable import PrettyTable
import datetime

class VisualtimeApi:
    TOKEN = "YVhSbGNqUXhOemM9ODgwMDhhMDFlNjM3OTkxNTE1ODBmMmQzYWYxNzcxMDhmZjczNDljYzM4MzlmM2RmZDVlNTBkOWMyNzlhODQzNw%3D%3D"
    URL = "https://vtliveapi.visualtime.net/api/v2/ScheduleService.svc/"
    
    @staticmethod
    def getPublicHolidays():
        contents = urllib.request.urlopen(VisualtimeApi.URL + "GetPublicHolidays?Token="+VisualtimeApi.TOKEN).read()
        data_json = json.loads(contents) 
        x = PrettyTable()
        x.field_names = ["Festivo", "Fecha", "Tipo"]
        for days in data_json["Value"]:
            title = days["ID"]
            for day in days["PublicHolidaysDetails"]:
                datetime1 = datetime.datetime.strptime(day["PublicHolidayDate"]["Data"].split(" ")[0], '%Y-%m-%d').strftime('%A, %d %B %Y')
                x.add_row([day["Description"], datetime1, title])                          
        return x.get_string()
        
    @staticmethod
    def getHolidays(identifier, date1 = None, date2 = None):
            
        start_date = "2023-01-05%2007%3A30%3A00%2B02"
        end_date = "2023-09-07%2012%3A30%3A00%2B02"
        if date1 == None:
            today = datetime.date.today()
            year = today.year
            start_date = '{}-01-01 00:00:00 +01'.format(year)
           
        if date2 == None :
            today = datetime.date.today()
            if date1 == None:                
                year = today.year
                end_date = '{}-12-31 23:59:50 +01'.format(year)
            else:
                t = datetime.datetime(today.year + 1, today.month, 1, 0, 0)
                endDate = t.strftime('%Y-%m-%d H%:M%:S%') + " +01"
                
        #if date1 < date2:        
        start_date = urllib.parse.quote(start_date)
        end_date = urllib.parse.quote(end_date)              
        employeeID = "457"
        contents = urllib.request.urlopen(VisualtimeApi.URL + "GetHolidays?Token=" + VisualtimeApi.TOKEN + "&StartDate=" + start_date + "&EndDate=" + end_date + "&EmployeeID=" + employeeID).read()
        data_json = json.loads(contents) 
        x = PrettyTable()
        x.field_names = ["Fecha", "Motivo"]
        for day in data_json["Value"]:
            datetime1 = datetime.datetime.strptime(day["PlannedDate"]["Data"].split(" ")[0], '%Y-%m-%d').strftime('%A, %d %B %Y')
            x.add_row([datetime1, day["ReasonName"]])
        return x.get_string()    
        #else:
            #return "Init date must be higher than ending date"