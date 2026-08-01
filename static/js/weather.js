// Weather Widget

document.addEventListener('DOMContentLoaded', function() {
    loadWeather();
    setInterval(loadWeather, 1800000); // Refresh every 30 minutes
});

function loadWeather() {
    const weatherElement = document.getElementById('weather-temp');
    if (!weatherElement) return;
    
    // Get user's location or use default (Egerton, Kenya)
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                fetchWeather(lat, lon);
            },
            function() {
                // Default to Egerton coordinates
                fetchWeather(-0.5, 35.8);
            }
        );
    } else {
        fetchWeather(-0.5, 35.8);
    }
}

function fetchWeather(lat, lon) {
    // Using OpenWeatherMap API (you'll need an API key)
    const apiKey = 'YOUR_OPENWEATHER_API_KEY';
    const url = `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&units=metric&appid=${apiKey}`;
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.main && data.main.temp) {
                const temp = Math.round(data.main.temp);
                const weatherElement = document.getElementById('weather-temp');
                if (weatherElement) {
                    weatherElement.textContent = `${temp}°C`;
                }
                
                // Update weather icon
                const iconElement = document.querySelector('.weather-info i');
                if (iconElement && data.weather && data.weather[0]) {
                    const condition = data.weather[0].main.toLowerCase();
                    iconElement.className = `fas fa-${getWeatherIcon(condition)}`;
                }
            }
        })
        .catch(error => {
            console.error('Error fetching weather:', error);
        });
}

function getWeatherIcon(condition) {
    const icons = {
        'clear': 'sun',
        'clouds': 'cloud',
        'rain': 'cloud-rain',
        'drizzle': 'cloud-drizzle',
        'thunderstorm': 'bolt',
        'snow': 'snowflake',
        'mist': 'smog',
        'fog': 'smog',
        'haze': 'smog',
        'smoke': 'smog'
    };
    return icons[condition] || 'cloud-sun';
}