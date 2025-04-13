<img src="https://www.logo.wine/a/logo/LinkedIn/LinkedIn-Wordmark-White-Dark-Background-Logo.wine.svg" alt="LinkedIn Automation" style="width:100%; height:300px; object-fit: cover;">
<br><br>

# LinkedIn Automation

A powerful Python-based automation tool that enhances your LinkedIn experience by streamlining networking and engagement to boost your professional presence.

[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff)](#)
[![Selenium](https://img.shields.io/badge/Selenium-43B02A?logo=selenium&logoColor=white)](#)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-4285F4?logo=google&logoColor=white)](#)
[![Git](https://img.shields.io/badge/Git-F05032?logo=git&logoColor=fff)](#)
[![Visual Studio Code](https://custom-icon-badges.demolab.com/badge/Visual%20Studio%20Code-0078d7.svg?logo=vsc&logoColor=white)](#)
[![Chrome](https://img.shields.io/badge/Google%20Chrome-4285F4?logo=GoogleChrome&logoColor=white)](#)
[![Firefox](https://img.shields.io/badge/Firefox-FF7139?logo=Firefox&logoColor=white)](#)

## 🚀 Features
- 👍 **Engagement Boost**: Automatically engage with posts from your network through likes and comments.
- 🤖 **AI-Powered Interactions**: Leverage Google Gemini to create natural, personalized messages.
- 🔄 **Session Management**: Utilize cookies for seamless authentication and session persistence.
- ⏱️ **Scheduling**: Set up automation tasks to run at specified times.
- 🛡️ **Safe Usage**: Built-in safeguards to maintain natural activity patterns and avoid LinkedIn restrictions.
- 🧠 **Smart Targeting**: Intelligently identify and engage with relevant connections based on your criteria.

## 🛠️ Tech Stack

### Core Technologies

- **Python**: Primary programming language for the automation scripts.
- **Selenium**: Browser automation framework for LinkedIn interactions.
- **Webdriver Manager**: Automated management of browser driver binaries.
- **Google Gemini AI**: Advanced AI model for generating natural text and interactions.
- **python-dotenv**: Environment variable management for secure configuration.

## 📋 Installation

```bash
# Clone the repository
git clone https://github.com/PacemakerX/LinkedIntel.git
cd LinkedIntel

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys and settings

# Set up cookies for authentication
cp cookies.example.json cookies.json
# Replace with your actual LinkedIn cookies
```

## 🔧 Configuration

### Requirements.txt

```
google-generativeai==1.10.0
openai==1.73.0
python-dotenv==1.1.0
selenium==4.31.0
webdriver-manager==4.0.2
```

### Cookie Authentication

This project uses cookie-based authentication to maintain LinkedIn sessions:

1. Log in to LinkedIn in your browser
2. Export your cookies to a `cookies.json` file (you can use browser extensions for this)
3. Place the file in the project root directory
4. An example structure is provided in `cookies.example.json`

### Environment Variables

Create a `.env` file with the following variables:

```
GEMINI_API_KEY=your_gemini_api_key
```

## 📝 Usage

```bash
# Run the main file
python main.py

```

## Link to the Repository:

<p align="center">
<a href="https://github.com/PacemakerX/LinkedIntel.git">
  <img src="https://github.com/Anmol-Baranwal/Cool-GIFs-For-GitHub/assets/74038190/993370af-11f4-48e7-9e0d-e5b79c2e7890" alt="Website Link" style="width:100%; height:300px; object-fit: cover;">
</a>
<p>

## Feel free to connect with me!

<p align="center">
  <a href="mailto:sparsh.officialwork@gmail.com">
    <img src="https://img.shields.io/badge/Gmail-sparsh.officialwork@gmail.com-D14836?style=for-the-badge&logo=gmail&logoColor=white" alt="Gmail Badge" />
  </a>
  <a href="https://www.linkedin.com/in/sparshsoni">
    <img src="https://img.shields.io/badge/LinkedIn-Connect-blue?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn Badge" />
  </a>
</p>
