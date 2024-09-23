import streamlit as st
from langchain_helper import get_qa_chain, create_vector_db
import torch

# Initialize the language model chain
chain = get_qa_chain()

# Set page config for a better layout
st.set_page_config(
    page_title="FashionGPT",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar setup
st.sidebar.title("COZA AI")

# Add instructions to the sidebar
page_options = st.sidebar.radio("Navigation", ["Home", "View History", "Instructions"])

# Initialize or load the user history
if "history" not in st.session_state:
    st.session_state.history = []

# Reset session state for input fields
def reset_inputs():
    st.session_state.custom_query = ""
    st.session_state.gender = "Male"
    st.session_state.body_shape = "Hourglass"
    st.session_state.age = 18
    st.session_state.height = "Medium"
    st.session_state.weight = 60
    st.session_state.occasion = "Casual"
    st.session_state.fashion_style = "Western"
    st.session_state.skin_tone = "Fair"

# Page navigation logic
if "page" not in st.session_state:
    st.session_state.page = "home"

# Function to display instructions
def display_instructions():
    st.title("Instruction Guide for Selecting Inputs")
    st.markdown("""
    ### Gender:
    - **Male (above 25 years):** Select this if you're a man aged 25 and above.
    - **Female (above 25 years):** Select this if you're a woman aged 25 and above.
    - **Boy (10 - 25 years):** Select this if you're a boy between the ages of 10 and 25.
    - **Girl (10 - 25 years):** Select this if you're a girl between the ages of 10 and 25.
    - **Baby Boy (1 - 10 years):** Select this for boys aged between 1 and 10.
    - **Baby Girl (1 - 10 years):** Select this for girls aged between 1 and 10.
    
    ### Body Shape:
    - **Hourglass:** Well-defined waist with similar bust and hip measurements.
    - **Pear:** Hips are wider than shoulders; narrow upper body with fuller hips and thighs.
    - **Apple:** Weight is carried around the midsection, with a wider torso, broad shoulders, and thinner legs.
    - **Rectangle:** Straight body shape with little difference between bust, waist, and hip measurements.
    - **Inverted Triangle:** Broad shoulders, narrow hips, and a more athletic build.
    - **Athletic:** Muscular build with toned limbs, often broad shoulders and narrower hips.
    - **Round:** Fuller figure with weight evenly distributed, rounder waist and hips.
    
    ### Height:
    - **Short:** Less than 5'4" (162 cm) for women, less than 5'8" (173 cm) for men.
    - **Medium:** Between 5'4" and 5'7" for women, 5'8" and 6'0" for men.
    - **Tall:** Taller than 5'7" for women, taller than 6'0" for men.
    
    ### Occasion:
    - **Casual, Formal, Party, Work, Sports, Wedding, Festive, Vacation** — Choose based on the event or setting.
    
    ### Cultural and Fashion Style:
    - **Western, Indian, Traditional, Streetwear, Bohemian, Minimalist, Sporty, Chic, Ethnic, Fusion** — Choose your cultural or fashion style preferences.
    
    ### Skin Tone:
    - **Fair, Light, Medium, Olive, Tan, Brown, Dark** — Choose the tone that best matches your complexion.
    """)

# Main Page Display
if page_options == "Home":
    st.title("Fashion Sense Recommender System")
    st.markdown("""
        Welcome to the *Fashion Sense Recommender System!* Please provide your details below to get personalized outfit recommendations.
    """)

    # Main input page logic
    input_method = st.sidebar.radio(
        "Choose Input Method:",
        ("Use Custom Text Input", "Use Selectboxes for Inputs"),
        key="input_method"
    )

    # Custom Text Input
    if input_method == "Use Custom Text Input":
        custom_query = st.text_input("Enter your custom question or query:", key="custom_query")
        if st.button("Get Recommendation"):
            if custom_query:
                try:
                    response = chain.invoke({"query": custom_query})
                    result = response.get("result", "Sorry! No recommendation could be generated.")
                    st.subheader("Your Fashion Recommendation:")
                    st.write(result)
                    st.session_state.history.append((custom_query, result))
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Please enter a question or query.")

    # Selectbox Inputs
    else:
        col1, col2 = st.columns(2)
        with col1:
            gender = st.selectbox("Select Gender:", ["Male (above 25 years)", "Female (above 25 years)", "Boy (10 - 25 years)", "Girl (10 - 25 years)", "Baby Boy (1 - 10 years)", "Baby Girl (1 - 10 years)"], key="gender")
        with col2:
            body_shape = st.selectbox("Select Body Shape:", ["Hourglass", "Pear", "Apple", "Rectangle", "Inverted Triangle", "Athletic", "Round"], key="body_shape")

        col3, col4 = st.columns(2)
        with col3:
            age = st.number_input("Enter Age:", min_value=0, max_value=100, step=1, key="age")
        with col4:
            height = st.selectbox("Select Height:", ["Small", "Medium", "Tall"], key="height")

        col5, col6 = st.columns(2)
        with col5:
            weight = st.number_input("Enter Weight (kg):", min_value=0, max_value=200, step=1, key="weight")
        with col6:
            occasion = st.selectbox("Select Occasion:", ["Casual", "Business", "Party", "Formal", "Office", "Wedding", "Travel", "Sports","Vacation","Festive"], key="occasion")

        col7, col8 = st.columns(2)
        with col7:
            fashion_style = st.selectbox("Select Cultural and Fashion Style Preferences:", ["Western", "Indian", "Traditional", "Bohemian", "Streetwear", "Vintage", "Minimalist", "Athleisure"], key="fashion_style")
        with col8:
            skin_tone = st.selectbox("Select Skin Tone:", ["Fair", "Light", "Medium", "Olive", "Dark", "Tan","Brown"], key="skin_tone")

        if st.button("Recommend Fashion"):
            query = f"Gender: {gender}\nAge: {age}\nBody Shape: {body_shape}\nHeight: {height}\nWeight: {weight} kg\nOccasion: {occasion}\nFashion Style: {fashion_style}\nSkin Tone: {skin_tone}"
            try:
                response = chain({"query": query})
                result = response.get("result", "Sorry! No recommendation could be generated.")
                st.subheader("Your Fashion Recommendation:")
                st.write(result)
                st.session_state.history.append((query, result))
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            display_instructions()

# Display user history if selected
elif page_options == "View History":
    st.subheader("Your History")
    if st.session_state.history:
        for idx, (query, response) in enumerate(st.session_state.history):
            st.write(f"{idx+1}. Query: {query}")
            st.write(f"Response: {response}")
            st.markdown("---")
    else:
        st.write("No history available.")

# Display instructions if selected
elif page_options == "Instructions":
    display_instructions()
