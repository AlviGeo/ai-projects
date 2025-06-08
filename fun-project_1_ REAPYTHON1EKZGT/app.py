import streamlit as st
import urllib.parse

st.set_page_config(page_title="Mini Profession Quiz", layout="centered")
st.audio("./assets/audio/background-music.mp3")
st.title("Which profession is right for you?")

professions = {
  "programmer": {
    "title": "You are a true PROGRAMMER! 💻",
    "desc": "Programmers are digital solution builders. They love creating software, crafting algorithms, and turning coffee into code. 🔧💡",
    "gif": "https://media.giphy.com/media/qgQUggAC3Pfv687qPC/giphy.gif",
    "note": "You're a true problem solver. The digital world needs more people like you! 🚀",
  },
  "designer": {
    "title": "You are a creative DESIGNER! 🎨",
    "desc": "Designers are visual visionaries. They know how to create harmony between aesthetics and function. From wireframe to masterpiece! ✨",
    "gif": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExenc1b2Q1ZDhpbTBuMGQwOW95NjVsd2Uwamo4eXlxMndhYmpvbGN0MyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/4tnhW4SZOPqmIf9Avt/giphy.gif",
    "note": "Your imagination can make the world more beautiful and well-structured. 🌟",
  },
  "data_scientist": {
    "title": "You are a modern DATA SCIENTIST! 📊",
    "desc": "Data Scientists turn data into stories. They excel at analyzing, predicting, and supporting big decisions. 📈🔍",
    "gif": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOGgya3B2eGpwdnFtMWg4dmN5enY4djRyOXUwd2JlZjVza2dzMzRneCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/xT5LMWNOjGqJzUfyve/giphy.gif",
    "note": "You're like Sherlock Holmes, but with Python and datasets! 🧠",
  },
}

# List of Questions
st.subheader("1. What is your favorite activity?")
question_1 = st.radio(
    "Choose one:",
    ["Solving puzzles", "Creating art", "Analyzing data"]
)
st.subheader("2. What tools do you prefer to work with?")
question_2 = st.radio(
    "Choose one:",
    ["VS Code", "Figma", "Google Colab"]
)
st.subheader("3. What motivates you the most?")
question_3 = st.radio(
    "Choose one:",
    ["Keep calm and debug the code", "Design is thinking made visual", "In data we trust"]
)

# The result contents
if st.button("View Results"):
    scores = {
        "programmer": 0,
        "designer": 0,
        "data_scientist": 0
    }
    if question_1 == "Solving puzzles":
        scores["programmer"] += 1
    elif question_1 == "Creating art":
        scores["designer"] += 1
    elif question_1 == "Analyzing data":
        scores["data_scientist"] += 1
    
    if question_2 == "VS Code":
        scores["programmer"] += 1
    elif question_2 == "Figma":
        scores["designer"] += 1
    elif question_2 == "Google Colab":
        scores["data_scientist"] += 1
        
    if question_3 == "Keep calm and debug the code":
        scores["programmer"] += 1
    elif question_3 == "Design is thinking made visual":
        scores["designer"] += 1
    elif question_3 == "In data we trust":
        scores["data_scientist"] += 1

    profession = max(scores, key=scores.get)
    st.write("### Your Results:")
    st.success(professions[profession]["title"])
    st.image(professions[profession]["gif"])
    st.write(professions[profession]["note"])
    st.balloons()

    # --- Share Feature ---
    share_text = f"I just discovered I'm a {profession.replace('_', ' ').title()}! Check yours at: https://yourapp.streamlit.app"
    encoded = urllib.parse.quote(share_text)
    x_url = f"https://x.com/intent/tweet?text={encoded}"
    st.markdown(f"[📤 Share on X platform]({x_url})")