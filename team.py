from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.python import PythonTools
from agno.tools.arxiv import ArxivTools
from agno.tools.googlesearch import GoogleSearchTools
from agno.tools.hackernews import HackerNewsTools
import os
import streamlit as st

# Data Analyst Agent
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
data_agent = Agent(
    model = Groq("qwen/qwen3-32b"),
    name = "Data Analysis Agent",
    role = "Analyze environmental datasets (mock or real CSV)",
    instructions = "Read CSV with air quality data, summarize trends",
    tools=[PythonTools(), GoogleSearchTools()],
    show_tool_calls=True,
    markdown = True
)

data_agent.print_response(
    "Write a python script for fibonacci series and display the result till the 10th number"
)

# News Agent
news_agent = Agent(
    model = Groq("qwen/qwen3-32b"),
    name = 'News Analyst',
    role="Find recent news on sustainability initiatives",
    instructions= "Search for city-level green project in the last year",
    tools=[ArxivTools(), GoogleSearchTools()],
    show_tool_calls=True,
    markdown= True
)

# Policy Reviewer Agent
policy_agent = Agent(
    model = Groq("qwen/qwen3-32b"),
    name = 'Policy Reviewer',
    role="Summarize government policies",
    instructions= "Search official sites for city policy updates",
    tools=[ArxivTools(), GoogleSearchTools()],
    show_tool_calls=True,
    markdown= True
)

# Innovative Agent
scout_agent = Agent(
    model = Groq("qwen/qwen3-32b"),
    name="Hackernews Team",
    role = "Find innovative green tech ideas",
    instructions = '''Search for “urban sustainability tech''',
    tools=[HackerNewsTools(), GoogleSearchTools()],
    show_tool_calls=True,
    markdown=True,
)
scout_agent.print_response(
    "Write an engaging summary of the users with the top 2 stories on hackernews. Please mention the stories as well.",
)

# Collaborative Team

student_team = Agent(
    team=[data_agent, news_agent, scout_agent, policy_agent],
    model=Groq(id="qwen/qwen3-32b"),
    role = '''Coordinate a team of specialized agents (Data, News, Policy, HN Scout) to answer user requests about green tech and sustainability. Decide who should work, in what order, and merge results into one final, cited summary.''',
    instructions=['''
                  1. Deliver a professional, trustworthy answer with clear sources and a short action list.
                  2. Pick the right specialist(s). If a task spans areas, run them sequentially (e.g., News → Policy) and then synthesize.
                  3. When delegating, pass a one-line goal + input constraints + required output format.
                  4. Prefer official sources > reputable media > community posts. If findings conflict, note both and state confidence.
                  5. Assume timezone Asia/Karachi. Treat “recent” as ≤12 months unless the user says otherwise.
                  6. Always include links (or identifiers) each specialist returned.
                  7. Stop when the question is answered with at least two independent sources or when the user asked for a specific operation that’s complete.
'''],
    show_tool_calls=True,
    markdown=True,
)

# ---------------- UI ----------------
st.set_page_config(page_title="Green Team — Lightly Interactive", page_icon="🤝", layout="centered")
st.title("🤝 Green Team — Lightly Interactive UI")
st.caption("A tiny bit more control: choose coordinator or a specialist, set city & time window, optionally upload a CSV for data analysis.")

if not groq_api_key:
    st.warning("GROQ_API_KEY is missing. Add it to your .env before running prompts.")

mode = st.radio(
    "Who should handle this?",
    ["Team Coordinator", "Single Specialist"],
    horizontal=True,
)

colA, colB = st.columns(2)
with colA:
    city = st.text_input("City (optional)", placeholder="e.g., Karachi, Lahore, NYC")
with colB:
    months = st.slider("Lookback window (months)", 1, 12, 12)

# Optional CSV for the Data agent
uploader = st.file_uploader("Optional CSV for Data Analysis Agent", type=["csv"]) 

# Specialist selection if not using coordinator
spec = None
if mode == "Single Specialist":
    spec = st.selectbox(
        "Pick a specialist",
        ("Data Analysis Agent", "News Analyst", "Policy Reviewer", "HackerNews Scout"),
    )

# Prompt box
DEFAULT_COORD_PROMPT = (
    "Compare recent city-level green initiatives and summarize policy implications and data-driven impacts."
)
DEFAULT_SPECIALIST = {
    "Data Analysis Agent": "Analyze the uploaded CSV (if provided). Summarize PM2.5/PM10/NO2 trends with 2–3 bullets.",
    "News Analyst": "Find recent city-level green project announcements and summarize with sources.",
    "Policy Reviewer": "Summarize a recent city policy update with effective dates and who is affected.",
    "HackerNews Scout": "Summarize the top 2 Hacker News stories on urban sustainability tech and the leading commenters.",
}

prompt = st.text_area(
    "Prompt",
    value=(DEFAULT_COORD_PROMPT if mode == "Team Coordinator" else DEFAULT_SPECIALIST[spec]),
    height=110,
)

run = st.button("Run")

# ---------------- Run logic ----------------
if run:
    if not groq_api_key:
        st.error("Missing GROQ_API_KEY. Add it to your .env and restart.")
        st.stop()

    # Prepare helper context for the agent(s)
    context_bits = []
    if city.strip():
        context_bits.append(f"City: {city}")
    if months:
        context_bits.append(f"Time window: last {months} months")

    context_text = ("\n" + "\n".join(context_bits) + "\n") if context_bits else "\n"

    # If a CSV is uploaded and Data agent is involved, save it and nudge the prompt
    csv_path = None
    if uploader is not None:
        csv_bytes = uploader.read()
        csv_path = os.path.join("tmp", "uploaded.csv")
        os.makedirs("tmp", exist_ok=True)
        with open(csv_path, "wb") as f:
            f.write(csv_bytes)

    final_prompt = (
        f"{prompt}{context_text}"
        "Instructions: Prefer official sources; keep bullets concise; include links/dates where applicable."
    )

    # If single specialist chosen, route directly
    try:
        with st.spinner("Thinking…"):
            if mode == "Single Specialist":
                target = {
                    "Data Analysis Agent": data_agent,
                    "News Analyst": news_agent,
                    "Policy Reviewer": policy_agent,
                    "HackerNews Scout": scout_agent,
                }[spec]

                # If Data agent and CSV provided, hint the file path
                if target is data_agent and csv_path:
                    final_prompt += f"\nCSV_PATH: {csv_path} (read this file if needed)."

                res = target.run(final_prompt)
            else:
                # Team Coordinator path
                if csv_path:
                    final_prompt += f"\nIf data analysis is needed, ask the Data Analysis Agent to read: {csv_path}."
                res = student_team.run(final_prompt)

            text = getattr(res, "content", getattr(res, "text", str(res)))
            st.markdown(text)

            with st.expander("🔧 Debug context", expanded=False):
                st.code(
                    {
                        "mode": mode,
                        "city": city,
                        "months": months,
                        "csv_path": csv_path,
                    },
                    language="json",
                )
    except Exception as e:
        st.error(f"Error: {e}")

st.markdown("<small>Lightly interactive • Agno + Groq • Coordinator or Specialist, city & time filters, CSV upload.</small>", unsafe_allow_html=True)

# # ---------------- UI ----------------
# st.set_page_config(page_title="Green Team — Sidebar UI", page_icon="🤝", layout="centered")
# st.title("🤝 Green Team — Sidebar Agent Selector")
# st.caption("Choose an agent from the sidebar, adjust context, and run your query.")

# if not groq_api_key:
#     st.warning("GROQ_API_KEY is missing. Add it to your .env before running prompts.")

# # Sidebar selection
# st.sidebar.header("⚙️ Agent Settings")
# agent_choice = st.sidebar.radio(
#     "Select agent",
#     (
#         "Team Coordinator (student_team)",
#         "Data Analysis Agent",
#         "News Analyst",
#         "Policy Reviewer",
#         "HackerNews Scout",
#     ),
# )

# city = st.sidebar.text_input("City (optional)", placeholder="e.g., Karachi, Lahore, NYC")
# months = st.sidebar.slider("Lookback window (months)", 1, 12, 12)

# uploader = st.sidebar.file_uploader("Optional CSV (for Data Analysis Agent)", type=["csv"]) 

# # Prompt box with defaults
# DEFAULTS = {
#     "Team Coordinator (student_team)": "Compare recent city-level green initiatives and summarize policy implications and data-driven impacts.",
#     "Data Analysis Agent": "Analyze the uploaded CSV (if provided). Summarize PM2.5/PM10/NO2 trends with 2–3 bullets.",
#     "News Analyst": "Find recent city-level green project announcements and summarize with sources.",
#     "Policy Reviewer": "Summarize a recent city policy update with effective dates and who is affected.",
#     "HackerNews Scout": "Summarize the top 2 Hacker News stories on urban sustainability tech and the leading commenters.",
# }

# prompt = st.text_area("Prompt", value=DEFAULTS[agent_choice], height=120)

# run = st.button("Run")

# if run:
#     if not prompt.strip():
#         st.warning("Please enter a prompt.")
#         st.stop()

#     if not groq_api_key:
#         st.error("Missing GROQ_API_KEY. Add it to your .env and restart.")
#         st.stop()

#     # Prepare helper context
#     context_bits = []
#     if city.strip():
#         context_bits.append(f"City: {city}")
#     if months:
#         context_bits.append(f"Time window: last {months} months")

#     context_text = ("\n" + "\n".join(context_bits) + "\n") if context_bits else "\n"

#     # If a CSV is uploaded and Data agent is involved, save it and nudge the prompt
#     csv_path = None
#     if uploader is not None:
#         csv_bytes = uploader.read()
#         csv_path = os.path.join("tmp", "uploaded.csv")
#         os.makedirs("tmp", exist_ok=True)
#         with open(csv_path, "wb") as f:
#             f.write(csv_bytes)

#     final_prompt = (
#         f"{prompt}{context_text}"
#         "Instructions: Prefer official sources; keep bullets concise; include links/dates where applicable."
#     )

#     # Route to selected agent
#     try:
#         with st.spinner("Thinking…"):
#             target = {
#                 "Team Coordinator (student_team)": student_team,
#                 "Data Analysis Agent": data_agent,
#                 "News Analyst": news_agent,
#                 "Policy Reviewer": policy_agent,
#                 "HackerNews Scout": scout_agent,
#             }[agent_choice]

#             if target is data_agent and csv_path:
#                 final_prompt += f"\nCSV_PATH: {csv_path} (read this file if needed)."

#             res = target.run(final_prompt)
#             text = getattr(res, "content", getattr(res, "text", str(res)))
#             st.markdown(text)

#             with st.expander("🔧 Debug context", expanded=False):
#                 st.code(
#                     {
#                         "agent_choice": agent_choice,
#                         "city": city,
#                         "months": months,
#                         "csv_path": csv_path,
#                     },
#                     language="json",
#                 )
#     except Exception as e:
#         st.error(f"Error: {e}")

# st.markdown("<small>Sidebar selection • Agno + Groq • City & time filters, CSV upload.</small>", unsafe_allow_html=True)
