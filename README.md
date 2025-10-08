# Cortex Tools - Google Forms Spammer

![Screenshot of the script running](https://i.imgur.com/vrGevgr.png)

A high-performance automation script, developed in Python, to submit responses to one or multiple Google Forms massively and concurrently. The tool features a rich command-line interface (CLI) built with the `rich` library, which displays the real-time progress of multiple tasks.

<br>

<details>
<summary>🇧🇷 Clique aqui para ver a versão em Português</summary>

## Cortex Tools - Google Forms Spammer (PT-BR)

Um script de automação de alto desempenho, desenvolvido em Python, para submeter respostas a um ou múltiplos Google Forms de forma massiva e concorrente. A ferramenta possui uma interface de linha de comando (CLI) rica e informativa, construída com a biblioteca `rich`, que exibe o progresso em tempo real de múltiplas tarefas.

</details>

## ✨ Technical Highlights

What makes this project robust and efficient:

-   **Dynamic Form Parsing:** The script doesn't require manual configuration of questions. It inspects the internal structure of the Google Form, **automatically identifying and cataloging all question types across all pages**, from simple text fields to complex grids.

-   **Session Management & Multi-Page Navigation:** For multi-page forms, the script accurately simulates a user's navigation. It captures and reuses the session token (`fbzx`) at each page turn, ensuring that multi-page submissions are validated and accepted by Google.

-   **Multi-Target Orchestration:** Manages and executes submissions to multiple links concurrently. The interface displays individual progress for each target, and the logic intelligently distributes the thread load among the forms that have not yet reached their goal.

-   **Comprehensive Auto-Filling:** Supports and randomly fills a wide range of question types, including text, multiple choice, checkboxes, dropdowns, linear scales, grids, and date/time fields.

-   **Proxy Support with Automated Testing:** Utilizes proxy lists to anonymize and distribute requests. The script downloads lists from known sources and tests each proxy to ensure only functional ones are used in the operation.

## 🚀 Installation

### Prerequisites

-   Python 3.7 or higher
-   Pip (Python Package Manager)
-   Git

### Steps

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/nyxxbit/Google-forms-spammer.git](https://github.com/nyxxbit/Google-forms-spammer.git)
    cd Google-forms-spammer
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## 💻 How to Use

1.  Navigate to the project directory in your terminal.
2.  Run the script with the following command:
    ```bash
    python form_spammer.py
    ```
3.  The program will interactively prompt for the following information:
    -   **Form URLs:** Enter one Google Forms link at a time and press Enter. Leave blank to finish.
    -   **Use Proxies:** `y` for yes or `n` for no.
    -   **Delay:** Time in seconds between submissions (e.g., `0.1`).
    -   **Successful Submissions:** The target number of successful submissions *per link*.
    -   **Total Threads:** The total number of concurrent submissions that will be distributed among the links.

The script will then start the process, displaying the real-time progress dashboard.

## 🤝 Contributing

-   **Suggestions:** If you have ideas for improvements or new features, feel free to open a **Pull Request**.
-   **Issues:** If you encounter any bugs or problems, please open an **Issue** in the GitHub repository.

## ⚠️ Legal Disclaimer

This tool was developed for educational, study, and testing purposes. The misuse of this script to overload services or for any malicious activity is the sole responsibility of the user. **Use responsibly.**