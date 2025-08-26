# Analyst-Researcher-Multi-Agent

A collaborative team of specialized AI agents built with Agno + Groq, designed to analyze data, review policies, scout innovations, and summarize news on green tech and sustainability.

This project showcases how multiple agents can work independently or collaboratively under a coordinator, providing professional research assistance with traceable sources and interactive controls.

## 🌟 Features

## Data Analysis Agent 🧮
Analyzes environmental datasets (CSV uploads supported) and summarizes trends in pollutants like PM2.5, PM10, and NO₂.

## News Analyst 📰
Finds and summarizes recent sustainability initiatives and city-level green projects.

## Policy Reviewer 🏛️
Summarizes government policies with effective dates, impacted groups, and official sources.

## HackerNews Scout 💡
Identifies innovative green-tech ideas and top discussions from the Hacker News community.

## Team Coordinator 🤝
Orchestrates collaboration across all agents, merging results into one professional, cited summary.

## 🖥️ Interactive UI

Built with Streamlit for lightweight interactivity:

Choose between Team Coordinator or Single Specialist mode.

Provide context with city and time window filters.

Upload your own CSV file for real data analysis.

View structured results with citations and optional debug context.

## 🚀 Getting Started

1. Set up environment
python -m venv myenv

2. Install dependencies
pip install -r requirements.txt

Create a .env file with your Groq API key:

GROQ_API_KEY=your_api_key_here

3. Run the app

streamlit run team.py

## 📂 Project Structure
team.py          # Main Streamlit app with agents and coordinator
requirements.txt # Dependencies (Agno, Groq, Streamlit, etc.)
.env.example     # Template for API key configuration

## ⚡ Example Use Cases
Compare recent green initiatives across cities.
Summarize a policy update and who it affects.
Discover innovative sustainability tech from Hacker News.

Upload a CSV to analyze real environmental data.

## 🤝 Contributing
Contributions are welcome! Feel free to fork the repo, create a branch, and submit a pull request.

## 📜 License

MIT License – feel free to use and adapt.
