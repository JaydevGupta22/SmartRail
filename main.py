import requests
import json
from datetime import datetime
from dotenv import load_dotenv
import os


class Rail:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://indianrailapi.com/api/v2/"

    def get_train_schedule(self, train_number):
        url = f"{self.base_url}TrainSchedule/apikey/{self.api_key}/TrainNumber/{train_number}/"
        response = requests.get(url)

        try:
            data = response.json()
            if 'Route' in data:
                print(f"\n{'Station Name':<25} {'Arrival Time':<15} {'Departure Time':<15} {'Distance (KM)':<15}")
                print("-" * 75)
                for station in data['Route']:
                    print(f"{station['StationName']:<25} {station['ArrivalTime']:<15} {station['DepartureTime']:<15} {station['Distance']:<15}")
            else:
                print("Route not found in the response.")
        except requests.exceptions.JSONDecodeError:
            print("❌ Error: Invalid JSON response.")
            print("Response text:", response.text)

    def get_live_train_status(self, train_number, date):
        url = f"{self.base_url}livetrainstatus/apikey/{self.api_key}/trainnumber/{train_number}/date/{date}"
        response = requests.get(url)
        try:
            data = response.json()
            print(json.dumps(data, indent=4))
        except Exception:
            print("❌ Could not fetch live train status.")

    def get_pnr_status(self, pnr_number):
        url = f"{self.base_url}PNRCheck/apikey/{self.api_key}/PNRNumber/{pnr_number}/"
        response = requests.get(url)
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            print("❌ Error: Invalid JSON response.")
            print("Response text:", response.text)
            return {"error": "Invalid response"}

    def get_train_number_info(self, train_number):
        url = f"{self.base_url}TrainInformation/apikey/{self.api_key}/TrainNumber/{train_number}/"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            self.display_train_info(data)
        else:
            print(f"❌ Error fetching train info: {response.status_code}")

    def get_station_name(self, station_code):
        url = f"{self.base_url}StationCodeToName/apikey/{self.api_key}/StationCode/{station_code}/"
        response = requests.get(url)
        try:
            data = response.json()
            if data.get("ResponseCode") == '200':
                return data.get("Station", {}).get("NameEn", station_code)
            return station_code
        except:
            return station_code

    def display_train_info(self, data):
        try:
            train_no = data.get('TrainNo', 'N/A')
            train_name = data.get('TrainName', 'N/A')

            source_code = data.get('Source', {}).get('Code', 'N/A')
            dest_code = data.get('Destination', {}).get('Code', 'N/A')

            source_name = self.get_station_name(source_code)
            destination_name = self.get_station_name(dest_code)

            source_arrival = data.get('Source', {}).get("Arrival", 'N/A')
            dest_arrival = data.get('Destination', {}).get('Arrival', 'N/A')

            print("\n--- Train Information ---")
            print(f"Train Number         : {train_no}")
            print(f"Train Name           : {train_name}")
            print(f"Source Station       : {source_name} ({source_code})")
            print(f"Departure Time       : {source_arrival}")
            print(f"Destination Station  : {destination_name} ({dest_code})")
            print(f"Arrival Time         : {dest_arrival}")
        except Exception as e:
            print("❌ Error displaying train info:", e)

    def get_fare(self, train_number, station_from, station_to, quota):
        url = f"{self.base_url}TrainFare/apikey/{self.api_key}/TrainNumber/{train_number}/From/{station_from}/To/{station_to}/Quota/{quota}"
        response = requests.get(url)
        try:
            data = response.json()
            print(json.dumps(data, indent=4))
        except:
            print("❌ Unable to fetch fare details.")

    def coach_layout(self, train_number):
        url = f"{self.base_url}CoachLayout/apikey/{self.api_key}/TrainNumber/{train_number}"
        response = requests.get(url)
        try:
            data = response.json()
            if 'Coaches' in data:
                print(f"\n{'Serial No':<15} {'Code':<15} {'Name':<15}")
                print("-" * 50)
                for coach in data['Coaches']:
                    print(f"{coach['SerialNo']:<15} {coach['Code']:<15} {coach['Name']:<15}")
            else:
                print("⚠️ Coach data not found.")
        except:
            print("❌ Error fetching coach layout.")

    def trains_on_station(self, station_code):
        url = f"{self.base_url}AllTrainOnStation/apikey/{self.api_key}/StationCode/{station_code}/"
        response = requests.get(url)
        try:
            data = response.json()
        except ValueError:
            print("❌ Invalid JSON response received from the API.")
            print("Raw response:", response.text)
            return

        if 'Trains' in data and data['Trains']:
            print(f"\n📍 Trains Stopping at Station: {station_code.upper()}")
            print("-" * 130)
            print(f"{'Train No.':<12} {'Train Name':<30} {'Source':<10} {'Arrival':<10} {'Destination':<15} {'Departure':<10}")
            print("-" * 130)
            for train in data['Trains']:
                print(f"{train.get('TrainNo', 'N/A'):<12} {train.get('TrainName', 'N/A'):<30} {train.get('Source', 'N/A'):<10} "
                      f"{train.get('ArrivalTime', 'N/A'):<10} {train.get('Destination', 'N/A'):<15} {train.get('DepartureTime', 'N/A'):<10}")
            print("-" * 130)
        else:
            print(f"⚠️ No train data found for station code: {station_code}")

    def train_between_station(self, station_from, station_to):
        url = f"{self.base_url}TrainBetweenStation/apikey/{self.api_key}/From/{station_from}/To/{station_to}"
        response = requests.get(url)
        try:
            data = response.json()
            print(json.dumps(data, indent=4))
        except:
            print("❌ Error fetching trains between stations.")

    def menu(self):
        while True:
            print("\n" + "-" * 40)
            choice = input(
                "How would you like to proceed?\n"
                "1) Live Train Status\n"
                "2) PNR Status\n"
                "3) Train Schedule\n"
                "4) Train Number Information\n"
                "5) Get Fare\n"
                "6) Coach Layout\n"
                "7) Trains on Station\n"
                "8) Trains Between Station\n"
                "9) Exit\n"
                "Enter choice: "
            )

            if choice == '1':
                train_no = input("Enter Train Number: ")
                date = input("Enter Date (yyyy-mm-dd): ")
                self.get_live_train_status(train_no, date)

            elif choice == '2':
                pnr = input("Enter PNR Number: ")
                result = self.get_pnr_status(pnr)
                print("\n--- PNR Status ---")
                print(json.dumps(result, indent=4))

            elif choice == '3':
                train_no = input("Enter Train Number: ")
                self.get_train_schedule(train_no)

            elif choice == '4':
                train_no = input("Enter Train Number: ")
                self.get_train_number_info(train_no)

            elif choice == '5':
                train_number = input("Enter Train Number: ")
                station_from = input("Enter Source Station Code: ")
                station_to = input("Enter Destination Station Code: ")
                quota = input("Enter Quota (GN for General / CK for Current Booking): ")
                self.get_fare(train_number, station_from, station_to, quota)

            elif choice == '6':
                train_number = input("Enter Train Number: ")
                self.coach_layout(train_number)

            elif choice == '7':
                station_code = input("Enter Station Code: ")
                self.trains_on_station(station_code)

            elif choice == '8':
                station_from = input("Enter Source Station Code: ")
                station_to = input("Enter Destination Station Code: ")
                self.train_between_station(station_from, station_to)

            elif choice == '9':
                print("✅ Exiting... Thank you!")
                break

            else:
                print("❌ Invalid option! Please select a valid number (1–9).")



if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("api_key")  
    rail_system = Rail(api_key)
    rail_system.menu()
