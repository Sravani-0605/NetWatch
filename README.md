# NetWatch — Network Monitoring and Troubleshooting System

NetWatch is a Python and Streamlit dashboard for checking TCP service connectivity, measuring TCP connection-establishment time, reviewing test history, and exporting results.

## Features

- Check TCP connectivity for up to 10 hostnames per run
- Configure the destination TCP port and timeout
- Check multiple hosts concurrently
- Display Online / Failed status and connection details
- Show summary metrics and host-wise success rates
- Visualize connection times and Online vs Failed counts
- Keep session-based monitoring history
- Download results as a CSV report
- Optional auto-refresh at a selected interval
- Include a troubleshooting guide

## Tech stack

- Python
- Streamlit
- Pandas
- Python `socket` and `concurrent.futures`

## Project structure

```text
NetWatch/
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Requirements

- Python 3.10 or newer recommended
- pip
- Internet/network access for checking public hosts

## Setup on Windows

1. Download or clone this repository.
2. Open the project folder in VS Code.
3. Create a virtual environment:

   ```powershell
   python -m venv .venv
   ```

4. Activate it:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use Command Prompt instead:

   ```bat
   .venv\Scripts\activate.bat
   ```

5. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

6. Run the application:

   ```powershell
   python -m streamlit run app.py
   ```

7. Open the local address shown in the terminal, usually `http://localhost:8501`.

## How to use

1. Enter one hostname per line in the sidebar.
2. Choose a TCP port and timeout.
3. Select **Check All Hosts** to run a manual check.
4. Optionally enable automatic checks and choose an interval.
5. Review metrics, host results, charts, and history.
6. Use **Download CSV Report** to export the current session history.

## Important limitations

- NetWatch checks TCP connection establishment only. It does not measure packet loss, perform ICMP ping, inspect network packets, or measure the full response time of an application.
- Checks run only when requested or when auto-refresh is enabled.
- History is stored in Streamlit session state; it is not a permanent database and may reset when the session restarts.
- A successful TCP connection does not guarantee that the full application is healthy.
- Only test systems and services you own or are authorized to check.

## Future enhancements

- Persistent database storage
- Uptime and availability reports over longer periods
- Configurable per-host ports
- Alerting for repeated failures
- Authentication and role-based access
- Deployment to a hosted platform

## Author

Add your name, course, college, and contact links here before publishing.
