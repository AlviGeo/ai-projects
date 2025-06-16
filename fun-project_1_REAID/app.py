import streamlit as st

# Set page config
st.set_page_config(page_title="Find Your Dream Travel Destination", page_icon="🌍", layout="centered")
st.audio("https://raw.githubusercontent.com/AlviGeo/ai-projects/master/fun-project_1_REAID/assets/audio/background-music.mp3")


# Inject CSS to style the sidebar
st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #001f3f !important;  /* Navy Blue */
        color: white !important;
    }
    [data-testid="stSidebar"] a {
        color: #1abc9c !important;  /* Teal links */
    }
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar content (always shown)
with st.sidebar:
    st.markdown("## ✨ About the Projects")
    st.markdown("A fun and interactive web app built with Streamlit that helps you discover your ideal travel style.")
    st.divider()
    st.markdown("## 🔗 Connect with Me!")
    st.markdown("- [GitHub](https://github.com/AlviGeo)")
    st.markdown("- [LinkedIn](https://www.linkedin.com/in/alvigeovanny)")
    st.markdown("- [Instagram](https://instagram.com/alvigeovanny)")

st.title("💼 Find Your Dream Travel Destination")
st.write("Answer the questions below and we'll match you with a destination you'll love!")

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

# List Questions
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
    },
    {
        "question": "What type of weather makes you happiest?",
        "options": {
            "Sunny and breezy": "Beach Lover",
            "Cool and crisp": "Nature Explorer",
            "Mild and ever-changing": "City Wanderer"
        }
    },
    {
        "question": "Which activity appeals to you most?",
        "options": {
            "Snorkeling or surfing": "Beach Lover",
            "Climbing or wildlife watching": "Nature Explorer",
            "Museum hopping or city walking tours": "City Wanderer"
        }
    },
    {
        "question": "What type of photos do you take most?",
        "options": {
            "Sunsets, waves, and beaches": "Beach Lover",
            "Trees, mountains, and trails": "Nature Explorer",
            "Architecture and cityscapes": "City Wanderer"
        }
    }
]

# Initialize scores in session state
if "scores" not in st.session_state:
    st.session_state.scores = {k: 0 for k in destinations.keys()}

# Form for quiz
with st.form("quiz_form"):
    for i, q in enumerate(questions):
        choice = st.radio(q["question"], list(q["options"].keys()), key=f"q{i}")
        selected_category = q["options"][choice]
        st.session_state.scores[selected_category] += 1
    submitted = st.form_submit_button("Find My Destination")

# Show result section
if submitted:
    scores = st.session_state.scores
    top_score = max(scores.values())
    top_destinations = [k for k, v in scores.items() if v == top_score]

    if len(top_destinations) > 1:
        st.warning("😕 It's a tie! Try answering more consistently so we can better match your travel style.")
    else:
        best = top_destinations[0]
        st.subheader(f"🌏 Your Dream Destination Style: {best}")
        st.image(destinations[best]["image"])
        st.write(destinations[best]["description"])

        # Share result
        st.markdown("**Want to share your result?**")
        share_url = f"https://x.com/intent/tweet?text=I+got+{best.replace(' ', '+')}+as+my+travel+style+on+this+fun+Streamlit+quiz!+Try+it+too!"
        st.markdown(f"[Share on X]({share_url})")

        st.success("Result generated successfully!")
        st.balloons()

    # Reset scores after submission 
    st.session_state.scores = {k: 0 for k in scores.keys()}
