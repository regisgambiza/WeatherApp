import sys
import requests
import warnings
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from urllib3.exceptions import NotOpenSSLWarning

# Suppress the NotOpenSSLWarning
warnings.filterwarnings("ignore", category=NotOpenSSLWarning)


class WeatherThread(QThread):
    # Signals to communicate between threads
    weather_data_received = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, api_key, city):
        super().__init__()
        self.api_key = api_key
        self.city = city

    def run(self):
        try:
            # Make API request to OpenWeatherMap
            url = f'http://api.openweathermap.org/data/2.5/weather?q={self.city}&units=metric&appid={self.api_key}'
            response = requests.get(url)
            data = response.json()

            # Check if the response contains necessary data
            if 'main' in data and 'weather' in data:
                self.weather_data_received.emit(data)  # Emit signal with weather data
            else:
                self.error_occurred.emit('Invalid API response format')  # Emit signal for error

        except Exception as e:
            self.error_occurred.emit(str(e))  # Emit signal for error


class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.api_key = '052d8dc856579311e1c7093d3e8e8249'  # Replace with your actual API key
        self.init_ui()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.get_weather_periodically)
        self.timer.start(300000)  # Update every 5 minutes (300,000 milliseconds)

        try:
            with open("cyberpunk_2077.qss") as f:
                style = f.read()
                self.setStyleSheet(style)
        except FileNotFoundError:
            print("Stylesheet file not found")
        except Exception as e:
            print(f"Error loading stylesheet: {str(e)}")

    def init_ui(self):
        # Set up the layout
        self.layout = QVBoxLayout()

        # Widgets for user input
        self.city_label = QLabel('Enter City:')
        self.city_input = QLineEdit()
        self.get_weather_button = QPushButton('Get Weather')

        # Widget to display weather information
        self.weather_label = QLabel('Weather Information will be displayed here.')
        self.weather_label.setWordWrap(True)  # Enable word wrap for better display

        # Add widgets to the layout
        self.layout.addWidget(self.city_label)
        self.layout.addWidget(self.city_input)
        self.layout.addWidget(self.get_weather_button)
        self.layout.addWidget(self.weather_label)

        # Connect button click event to get_weather method
        self.get_weather_button.clicked.connect(self.get_weather)

        # Set up the layout for the main window
        self.setLayout(self.layout)
        self.setWindowTitle('Weather App')
        self.show()

    def get_weather(self):
        # Get the city entered by the user
        city = self.city_input.text()

        # Check if a city is entered
        if city:
            # Create a thread for making the API request
            self.thread = WeatherThread(self.api_key, city)

            # Connect signals from the thread to methods in this class
            self.thread.weather_data_received.connect(self.display_weather)
            self.thread.error_occurred.connect(self.display_error)

            # Start the thread
            self.thread.start()
        else:
            self.display_error('Please enter a city.')

    def get_weather_periodically(self):
        # This method is called every time the timer times out (every 5 minutes)
        self.get_weather()

    def display_weather(self, data):
        try:
            # Extract relevant weather information from the API response
            temperature = data['main']['temp']
            description = data['weather'][0]['description']
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']
            city_name = data['name']
            current_temp = data['main']['temp']
            max_temp = data['main']['temp_max']
            min_temp = data['main']['temp_min']

            # Create a styled HTML string with the weather information
            weather_info = (
                f'<html><body>'
                f'<h2 style="color: #007BFF;">{city_name}</h2>'
                f'<p><b>Current Temperature:</b> {current_temp}°C</p>'
                f'<p><b>Max Temperature:</b> {max_temp}°C</p>'
                f'<p><b>Min Temperature:</b> {min_temp}°C</p>'
                f'<p><b>Description:</b> {description}</p>'
                f'<p><b>Humidity:</b> {humidity}%</p>'
                f'<p><b>Wind Speed:</b> {wind_speed} m/s</p>'
                f'</body></html>'
            )

            # Set the HTML-formatted text to the QLabel
            self.weather_label.setText(weather_info)

        except KeyError as e:
            self.display_error(f'Error parsing weather data: {e}')

    def display_error(self, error):
        # Display an error message in the label
        self.weather_label.setText(f'Error: {error}')


if __name__ == '__main__':
    # Start the application
    app = QApplication(sys.argv)
    weather_app = WeatherApp()
    sys.exit(app.exec_())
