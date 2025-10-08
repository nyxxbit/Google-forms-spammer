# Cortex Tools - Google Forms Spammer

![Screenshot of the script running](https://i.imgur.com/vrGevgr.png)

A high-performance automation script developed in Python to submit responses to one or multiple Google Forms massively and concurrently. The tool features a rich command-line interface (CLI) built with the `rich` library that displays real-time progress.

## ✨ Features

- **Multiple Targets:** Send responses to several Google Forms links simultaneously in the same session.
- **Proxy Support:** Utilizes HTTP/HTTPS proxy lists to anonymize and distribute requests, automatically downloading and testing them.
- **Intelligent Navigation:** Handles multi-page forms transparently, simulating user navigation.
- **Interface:** Presents a terminal dashboard with individual progress bars for each target, real-time status, and colored logs.
- **High Performance:** Uses multi-threading to send a large number of submissions in a short period, intelligently distributing threads among active targets.
- **Random Data Generation:** Automatically fills all common question types (text, multiple choice, checkboxes, dropdown lists, grids, etc.) with random data.

## 🚀 Installation

### Prerequisites

- Python 3.7 or higher
- Pip (Python package manager)

### Steps

1. **Save the script:**
    Save the code in a file with the `.py` extension (e.g., `form_spammer.py`).

2. **Create the `requirements.txt` file:**
    In the same directory, create a file called `requirements.txt` with the following content:
    ```
    requests
    beautifulsoup4
    rich
    pyfiglet
    ```

3. **Install dependencies:**
    Open a terminal or command prompt in the project directory and run:
    ```bash
    pip install -r requirements.txt
    ```

## 💻 How to Use

1. Navigate to the project directory in your terminal.
2. Run the script with the following command:
    ```bash
    python form_spammer.py
    ```
3. The program will interactively request the following information:
    - **Form URLs:** Enter one Google Forms link at a time and press Enter. Leave blank and press Enter to finish adding links.
    - **Use Proxies:** `y` for yes or `n` for no.
    - **Delay:** Time in seconds between submissions (e.g., `0.1`).
    - **Successful Submissions:** Target number of successful submissions *per link*.
    - **Total Threads:** The total number of simultaneous submissions that will be distributed among active links.

The script will start the process, displaying a dashboard with real-time progress.

## ⚠️ Legal Disclaimer

This tool was developed for educational, study, and testing purposes. Misuse of this script to overload services or for any malicious activity is the sole responsibility of the user. **Use responsibly.**
