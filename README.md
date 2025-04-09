# DSO462-WebKit

**A lightweight web starter-kit for students enrolled in DSO 462 - Managing Small Business on the Internet at USC.**  
This kit is designed to help you create and deploy your own business website using **HTML/CSS**, **Flask**, and **MongoDB**.

<!--  🌐 **[Live Demo on genez.io](https://genez.io)**  
A simple working version of this web app is hosted for demonstration purposes. -->

---

## 🚀 Features

- HTML/CSS frontend integrated with Flask backend
- MongoDB database support
- LightFM-based hybrid recommendation engine (collaborative + content-based)
- Starter templates for web analytics, ad integration, and hosting
- Beginner-friendly documentation and setup guides

---

## 📁 Project Structure

```
├── app.py # Flask web server
├── static/ # HTML, CSS and JS files
├── requirements.txt # Python libraries
├── recommendation_system/ # Recommendation engine using LightFM
└── setup-guides/ # Complete setup documentation
```

---

## 🛠️ How to Run the Web App Locally

1. **Clone this repository**
   ```bash
   git clone https://github.com/balajkhalid/dso462-webkit
   cd dso462-webkit
   ```
2. **Create and activate a virtual environmenty**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install required libraries**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the app**
   ```bash
   python app.py
   ```
5. **Visit http://localhost:5000 in your browser.**

## 📚 Setup Guides

All guides are in the setup-guides/ folder:

- MongoDB Setup (Contains direction to Python and Homebrew Installation)
- Web Hosting on Genez.io
- Web Hosting on Render
- GitHub & Version Control
- Google AdSense Integration
- Google Analytics Setup
- Recommendation Engine using LightFM

## 📊 Recommendation Engine

A simple hybrid recommendation engine using the LightFM library is also included.
Setup instructions in setup-guides/ andcdemo code are recommendation_system/

## 🧑‍🏫 For Non-Programmers

We’ve included a beginner-friendly Web Development Presentation (presentation.pdf) covering:

- Website building tools (no-code & low-code)
- Domain & hosting essentials
- How to use GitHub, analytics, and ads

## 💡 Contribute

If you want to improve or expand this kit, feel free to fork the repo and submit a pull request!

## 📬 Contact

For questions or suggestions, reach out to Balaj Khalid

- 📧 Email: bkhalid@usc.edu
- 📍 University of Southern California
