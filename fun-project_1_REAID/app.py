import streamlit as st

# Set page config
st.set_page_config(page_title="Find Your Dream Travel Destination", page_icon="🌍", layout="centered")
st.audio("https://raw.githubusercontent.com/AlviGeo/ai-projects/master/fun-project_1_REAID/assets/audio/background-music.mp3")
st.title("💼 Find Your Dream Travel Destination")

# Load assets
destinations = {
    "Beach Lover": {
        "score": 0,
        "image": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e",
        "description": "You love the sound of waves, sunshine, and relaxing on sandy beaches. Consider visiting Bali, Maldives, or Santorini."
    },
    "Nature Explorer": {
        "score": 0,
        "image": "https://images.unsplash.com/photo-1506744038136-46273834b3fb",
        "description": "You find peace in mountains, forests, and waterfalls. Try places like New Zealand, Patagonia, or Banff."
    },
    "City Wanderer": {
        "score": 0,
        "image": "https://plus.unsplash.com/premium_photo-1681628908570-3c95bed77a8e?q=80&w=3764&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        "description": "You love the energy of city life, street food, and museums. Explore Tokyo, New York, or Paris."
    }
}

# Title and description
st.write("Answer the questions below and we'll match you with a destination you'll love!")

# Questions
questions = [
    {
        "question": "What kind of scenery do you prefer?",
        "options": {
            "Beaches and oceans": "Beach Lover",
            "Mountains and forests": "Nature Explorer",
            "Skyscrapers and city lights": "City Wanderer"
        }
    },
    {
        "question": "What type of vacation do you enjoy?",
        "options": {
            "Relaxing and sunbathing": "Beach Lover",
            "Hiking and exploring nature": "Nature Explorer",
            "Shopping and trying new restaurants": "City Wanderer"
        }
    },
    {
        "question": "Your ideal weekend looks like...",
        "options": {
            "Lying on a beach with a good book": "Beach Lover",
            "Camping or going on a trail": "Nature Explorer",
            "Attending concerts or local events": "City Wanderer"
        }
    }
]

# Form for questions
with st.form("quiz_form"):
    for i, q in enumerate(questions):
        choice = st.radio(q["question"], list(q["options"].keys()), key=f"q{i}")
        destinations[q["options"][choice]]["score"] += 1
    submitted = st.form_submit_button("Find My Destination")

# Result
if submitted:
    scores = [v["score"] for v in destinations.values()]
    if scores.count(1) == 3:
        st.warning("😕 We couldn't determine your dream destination style. Try answering more consistently!")
    else:
        best = max(destinations.items(), key=lambda x: x[1]["score"])
        st.subheader(f"🌏 Your Dream Destination Style: {best[0]}")
        st.image(best[1]["image"])
        st.write(best[1]["description"])

        # Share result
        st.markdown("**Want to share your result?**")
        share_url = f"https://x.com/intent/tweet?text=I+got+{best[0].replace(' ', '+')}+as+my+travel+style+on+this+fun+Streamlit+quiz!+Try+it+too!"
        st.markdown(f"[Share on X]({share_url})")

        st.success("Result generated successfully!")
        st.balloons()
