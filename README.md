<div align="center">

# Google Forms Spammer

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/nyxxbit/Google-forms-spammer/graphs/commit-activity)

*A high-performance automation script for submitting responses to Google Forms with concurrent processing and real-time progress monitoring.*

![Screenshot of the script running](https://i.imgur.com/vrGevgr.png)

</div>

---

## Features

**Advanced Form Processing**
- **Dynamic Form Parsing** - Automatically identifies and catalogs all question types across multiple pages
- **Session Management** - Handles multi-page navigation with proper session token (`fbzx`) management
- **Multi-Target Support** - Concurrent submissions to multiple forms with individual progress tracking

**Performance & Reliability**
- **Comprehensive Auto-Filling** - Supports text, multiple choice, checkboxes, dropdowns, linear scales, grids, and date/time fields
- **Proxy Integration** - Built-in proxy support with automated testing and validation
- **Rich CLI Interface** - Real-time progress dashboard with concurrent task monitoring

## Installation

**Requirements**
- Python 3.7+
- pip package manager

**Setup**
```bash
# Clone the repository
git clone https://github.com/nyxxbit/Google-forms-spammer.git
cd Google-forms-spammer

# Install dependencies
pip install -r requirements.txt
```

## Usage

**Quick Start**
```bash
python form_spammer.py
```

**Configuration Options**
The script will prompt for:
- **Form URLs** - Enter Google Forms links (one per line, blank to finish)
- **Proxy Usage** - Enable/disable proxy support (`y`/`n`)
- **Submission Delay** - Time between requests in seconds
- **Target Count** - Number of successful submissions per form
- **Thread Pool** - Total concurrent workers distributed across forms

## Technical Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Form Parser   │───▶│  Session Mgmt   │───▶│   Submission    │
│                 │    │                 │    │    Engine       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Question Map   │    │  Multi-Page     │    │   Concurrent    │
│   Generator     │    │   Navigator     │    │   Processing    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Contributing

**Development**
- Fork the repository
- Create a feature branch
- Submit a pull request

**Bug Reports**
- Use GitHub Issues for bug reports
- Include reproduction steps and environment details

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

> **Educational Use Only**
> 
> This tool is designed for educational, research, and testing purposes. Users are responsible for ensuring compliance with applicable terms of service and local regulations. The developers assume no liability for misuse.

---

<div align="center">

**Made with ❤️ for the developer community**

</div>