# Jarvis AI

Jarvis AI is a simple voice-activated assistant similar to a beginner version of Siri. It can respond to queries about the weather, news, jokes, time, date, and reminders.

## Features

- Get the current weather for a specified city.
- Get the latest news headlines.
- Hear a random joke.
- Get the current time for a specified city or your current location.
- Get the current date for a specified city or your current location.
- Set and retrieve reminders.

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/yourusername/jarvis-ai.git
    cd jarvis-ai
    ```

2. Create a virtual environment and activate it:

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required dependencies:

    ```sh
    pip install -r requirements.txt
    ```

4. Set up your environment variables. Create a `.env` file in the root directory of the project and add your API keys:

    ```env
    OPENCAGE_API_KEY=your-opencage-api-key
    NEWS_API_KEY=your-news-api-key
    IP_API_KEY=your-ipstack-api-key
    ```

## Usage

1. Run the Flask server:

    ```sh
    python app.py
    ```

2. Open your web browser and navigate to `http://localhost:5000`.

3. Click the "Start Listening" button and speak your query. For example:
    - "What's the weather in New York?"
    - "Tell me a joke."
    - "What's the time in London?"
    - "What's today's date?"
    - "Set a reminder to buy groceries."

## Project Structure

- `app.py`: The main Flask application file.
- `requirements.txt`: The list of dependencies required for the project.
- `.env`: Environment variables file (not included in the repository).
- `.gitignore`: Git ignore file to exclude unnecessary files from version control.

## Dependencies

- Flask==2.0.1
- requests==2.31.0
- Werkzeug==2.0.1
- urllib3==2.1.0

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## Acknowledgements

- [Flask](https://flask.palletsprojects.com/)
- [requests](https://docs.python-requests.org/en/latest/)
- [OpenCage Geocoding API](https://opencagedata.com/)
- [News API](https://newsapi.org/)
- [ipstack](https://ipstack.com/)