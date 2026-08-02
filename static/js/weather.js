// ============================================
// WEATHER WIDGET - The Egerton Advertiser
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // Load weather on page load
    loadWeather();
    
    // Refresh weather every 30 minutes
    setInterval(loadWeather, 1800000);
    
    // Update time every minute
    updateTime();
    setInterval(updateTime, 60000);
});

function loadWeather() {
    const weatherElement = document.getElementById('weather-temp');
    const conditionElement = document.getElementById('weather-condition');
    const iconElement = document.querySelector('.weather-info i');
    
    if (!weatherElement) return;
    
    // Get API key from global variable
    const apiKey = window.OPENWEATHER_API_KEY || '';
    
    if (!apiKey || apiKey === '') {
        console.warn('OpenWeather API key not found. Using fallback.');
        weatherElement.textContent = '--°C';
        if (conditionElement) conditionElement.textContent = 'Weather unavailable';
        if (iconElement) iconElement.className = 'fas fa-cloud-sun';
        return;
    }
    
    // Use Egerton coordinates
    const lat = window.WEATHER_LAT || '-0.5';
    const lon = window.WEATHER_LON || '35.8';
    const url = `${window.OPENWEATHER_BASE_URL || 'https://api.openweathermap.org/data/2.5/'}weather?lat=${lat}&lon=${lon}&units=metric&appid=${apiKey}`;
    
    // Show loading state
    weatherElement.textContent = '...°C';
    if (conditionElement) conditionElement.textContent = 'Loading...';
    if (iconElement) iconElement.className = 'fas fa-spinner fa-spin';
    
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.cod && data.cod !== 200) {
                throw new Error(`API error: ${data.message}`);
            }
            
            if (data.main && data.main.temp) {
                const temp = Math.round(data.main.temp);
                weatherElement.textContent = `${temp}°C`;
                
                // Update weather icon
                if (iconElement && data.weather && data.weather[0]) {
                    const condition = data.weather[0].main.toLowerCase();
                    iconElement.className = `fas fa-${getWeatherIcon(condition)}`;
                }
                
                // Update condition text
                if (conditionElement && data.weather && data.weather[0]) {
                    const desc = data.weather[0].description;
                    conditionElement.textContent = desc.charAt(0).toUpperCase() + desc.slice(1);
                }
                
                // Update footer weather
                updateFooterWeather(data);
                
                console.log('Weather loaded:', data.main.temp, '°C', data.weather[0].description);
            }
        })
        .catch(error => {
            console.error('Error fetching weather:', error);
            weatherElement.textContent = '--°C';
            if (conditionElement) conditionElement.textContent = 'Weather unavailable';
            if (iconElement) iconElement.className = 'fas fa-cloud-sun';
            
            // Try fallback using wttr.in
            fetchFallbackWeather();
        });
}

function fetchFallbackWeather() {
    // Fallback to wttr.in (free, no API key)
    const url = 'https://wttr.in/Egerton,Kenya?format=j1';
    const iconElement = document.querySelector('.weather-info i');
    
    fetch(url)
        .then(response => {
            if (!response.ok) throw new Error('wttr.in failed');
            return response.json();
        })
        .then(data => {
            if (data.current_condition && data.current_condition[0]) {
                const temp = data.current_condition[0].temp_C;
                const condition = data.current_condition[0].weatherDesc[0].value;
                
                const weatherElement = document.getElementById('weather-temp');
                const conditionElement = document.getElementById('weather-condition');
                
                if (weatherElement) weatherElement.textContent = `${temp}°C`;
                if (conditionElement) conditionElement.textContent = condition;
                if (iconElement) {
                    const conditionLower = condition.toLowerCase();
                    iconElement.className = `fas fa-${getWeatherIcon(conditionLower)}`;
                }
                
                // Update footer weather
                const footerTemp = document.getElementById('footerWeatherTemp');
                if (footerTemp) footerTemp.textContent = `${temp}°C`;
            }
        })
        .catch(error => {
            console.error('Fallback weather also failed:', error);
            if (iconElement) iconElement.className = 'fas fa-cloud-sun';
        });
}

function updateFooterWeather(data) {
    const footerTemp = document.getElementById('footerWeatherTemp');
    const footerCondition = document.getElementById('footerWeatherCondition');
    const footerIcon = document.querySelector('.weather-widget .weather-icon i');
    
    if (footerTemp && data.main && data.main.temp) {
        const temp = Math.round(data.main.temp);
        footerTemp.textContent = `${temp}°C`;
    }
    
    if (footerCondition && data.weather && data.weather[0]) {
        const desc = data.weather[0].description;
        footerCondition.textContent = desc.charAt(0).toUpperCase() + desc.slice(1);
    }
    
    if (footerIcon && data.weather && data.weather[0]) {
        const condition = data.weather[0].main.toLowerCase();
        footerIcon.className = `fas fa-${getWeatherIcon(condition)}`;
    }
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

function updateTime() {
    const now = new Date();
    
    // Update date
    const dateOptions = { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric'
    };
    const dateElements = document.querySelectorAll('#current-date');
    dateElements.forEach(el => {
        el.textContent = now.toLocaleDateString('en-US', dateOptions);
    });
    
    // Update footer time
    const timeStr = now.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: false 
    });
    const dateStr = now.toLocaleDateString('en-US', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
    
    const timeEl = document.getElementById('footerTime');
    const dateEl = document.getElementById('footerDate');
    if (timeEl) timeEl.textContent = timeStr;
    if (dateEl) dateEl.textContent = dateStr;
}

// Also update on visibility change (when user returns to tab)
document.addEventListener('visibilitychange', function() {
    if (!document.hidden) {
        loadWeather();
        updateTime();
    }
});