import streamlit as st
from langchain_helper import get_qa_chain, create_vector_db
import torch
from PIL import Image
import random
from streamlit_lottie import st_lottie
import requests
import json

# Initialize the language model chain
chain = get_qa_chain()

# Set page config for a better layout
st.set_page_config(
    page_title="FashionSense AI",
    page_icon="𓁇",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS to enhance the visual appeal
st.markdown("""
<style>
    .reportview-container {
        background: linear-gradient(to right, #f6e5e5, #f5e1e6);
    }
    .sidebar .sidebar-content {
        background: linear-gradient(to bottom, #f9d1d1, #f7c8d0);
    }
    .Widget>label {
        color: #4a4a4a;
        font-family: 'Helvetica', sans-serif;
    }
    .stTextInput>div>div>input {
        color: #4a4a4a;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar setup
st.sidebar.title("FeshionSense AI ♡")

# Load Lottie animation
# lottie_fashion = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_asuimgrk.json")

# Add instructions to the sidebar
page_options = st.sidebar.radio("Navigation", ["Home", "View History", "Style Guide"])

# Initialize or load the user history
if "history" not in st.session_state:
    st.session_state.history = []

# Reset session state for input fields
def reset_inputs():
    st.session_state.custom_query = ""
    st.session_state.gender = "Male (above 25 years)"
    st.session_state.body_shape = "Hourglass"
    st.session_state.age = 25
    st.session_state.height = "Medium"
    st.session_state.weight = 60
    st.session_state.occasion = "Casual"
    st.session_state.fashion_style = "Western"
    st.session_state.skin_tone = "Fair"

# Function to display the style guide
def display_style_guide():
    st.title("FashionSense AI Style Guide")
    st.markdown("""
    ### Welcome to Your Personal Style Journey!
    
    Discover the perfect look for every occasion with our comprehensive style guide. 
    Let's break down the key elements that make up your unique fashion profile:
    
    #### 🧍 Gender:
    - **Male (above 25 years):** Select this if you're a man aged 25 and above.
    - **Female (above 25 years):** Select this if you're a woman aged 25 and above.
    - **Boy (10 - 25 years):** Select this if you're a boy between the ages of 10 and 25.
    - **Girl (10 - 25 years):** Select this if you're a girl between the ages of 10 and 25.
    - **Baby Boy (1 - 10 years):** Select this for boys aged between 1 and 10.
    - **Baby Girl (1 - 10 years):** Select this for girls aged between 1 and 10.
    
    #### 🧍 Body Shapes
    - **Hourglass:** Well-defined waist with similar bust and hip measurements.
    - **Pear:** Hips are wider than shoulders; narrow upper body with fuller hips and thighs.
    - **Apple:** Weight is carried around the midsection, with a wider torso, broad shoulders, and thinner legs.
    - **Rectangle:** Straight body shape with little difference between bust, waist, and hip measurements.
    - **Inverted Triangle:** Broad shoulders, narrow hips, and a more athletic build.
    - **Athletic:** Muscular build with toned limbs, often broad shoulders and narrower hips.
    - **Round:** Fuller figure with weight evenly distributed, rounder waist and hips.
    
    #### 🧍 Height:
    - **Short:** Less than 5'4" (162 cm) for women, less than 5'8" (173 cm) for men.
    - **Medium:** Between 5'4" and 5'7" for women, 5'8" and 6'0" for men.
    - **Tall:** Taller than 5'7" for women, taller than 6'0" for men.
    
    #### 👔 Occasion Wear
    - **Casual**: Relaxed, everyday comfort
    - **Business**: Professional, polished looks
    - **Party**: Fun, eye-catching ensembles
    - **Formal**: Elegant, sophisticated attire
    
    #### 🎨 Fashion Styles
    - **Western**: Modern, trendy looks
    - **Traditional**: Classic, cultural outfits
    - **Bohemian**: Free-spirited, artistic flair
    - **Minimalist**: Clean lines, simple elegance
    
    #### 🌈 Complementing Your Skin Tone
    - **Fair**: Soft, cool colors
    - **Medium**: Rich, warm hues
    - **Dark**: Bold, vibrant shades
    
    Remember, fashion is about expressing yourself. Use these guidelines as a starting point, 
    but don't be afraid to experiment and find what makes you feel confident and comfortable!
    """)

# Main Page Display
if page_options == "Home":
    st.title("Welcome to Fashion Recommendation AI")
    
    st.markdown("""
        Discover your perfect style with our AI-powered fashion recommender. 
        Whether you're dressing for a casual day out or a formal event, we've got you covered!
    """)
    
    # Main input page logic
    input_method = st.sidebar.radio(
        "Choose Your Style Adventure:",
        ("Quick Fashion Query", "Detailed Style Profiling"),
        key="input_method"
    )

    # Quick Fashion Query
    if input_method == "Quick Fashion Query":
        custom_query = st.text_area("Ask me anything about fashion:", key="custom_query", height=100)
        if st.button("Get Fashionable Insight", key="quick_query_button"):
            if custom_query:
                try:
                    with st.spinner("Crafting your personalized style advice..."):
                        response = chain.invoke({"query": custom_query})
                        result = response.get("result", "Oops! It seems our fashion sense is taking a coffee break. Please try again!")
                    st.success("Your Personalized Fashion Advice is Ready!")
                    st.write(result)
                    st.session_state.history.append((custom_query, result))
                except Exception as e:
                    st.error(f"Fashion faux pas alert! An error occurred: {e}")
            else:
                st.warning("Please share your fashion curiosity with us!")

    # Detailed Style Profiling
    else:
        st.subheader("Let's Create Your Fashion Profile")
        col1, col2 = st.columns(2)
        with col1:
            gender = st.selectbox("What's Your Style Category?", 
                                  ["Male (above 25 years)", "Female (above 25 years)", 
                                   "Boy (10 - 25 years)", "Girl (10 - 25 years)", 
                                   "Baby Boy (1 - 10 years)", "Baby Girl (1 - 10 years)"], 
                                  key="gender")
            occasion = st.selectbox("Dressing Up For...", 
                                    ["Casual", "Business", "Party", "Formal", "Office", "Wedding", "Travel", "Sports", "Vacation", "Festive"], 
                                    key="occasion")
            age = st.slider("Age is just a number, but it helps with style!", 
                            min_value=1, max_value=100, value=25, key="age")
            
            skin_tone = st.select_slider("Your Beautiful Skin Tone", 
                                         options=["Fair", "Light", "Medium", "Olive", "Tan", "Brown", "Dark"], 
                                         value="Medium", key="skin_tone")
        
        with col2:
            body_shape = st.selectbox("Your Fabulous Body Shape", 
                                      ["Hourglass", "Pear", "Apple", "Rectangle", "Inverted Triangle", "Athletic", "Round"], 
                                      key="body_shape")
            height = st.selectbox("Height Range", 
                                      options=["Small", "Medium", "Tall"], 
                                     key="height")
            weight = st.slider("Weight (kg) - Every body is beautiful!", 
                                     min_value=1, max_value=200, value=60, key="weight")
            fashion_style = st.multiselect("Your Fashion Vibes (Select up to 3)", 
                                           ["Western", "Indian", "Traditional", "Bohemian", "Streetwear", "Vintage", "Minimalist", "Athleisure"], 
                                           default=["Western"], key="fashion_style")

        if st.button("Reveal My Perfect Look", key="detailed_profile_button"):
            if len(fashion_style) > 3:
                st.warning("Please select up to 3 fashion styles.")
            else:
                query = f"""
                Gender: {gender}
                Age: {age}
                Body Shape: {body_shape}
                Height: {height}
                Weight: {weight} kg
                Occasion: {occasion}
                Fashion Style: {', '.join(fashion_style)}
                Skin Tone: {skin_tone}
                """
                try:
                    with st.spinner("Our AI stylist is curating your perfect look..."):
                        response = chain({"query": query})
                        result = response.get("result", "Our fashion crystal ball is a bit foggy. Please try again!")
                    st.success("Voila! Your Personalized Style Recommendation is Ready!")
                    st.write(result)
                    st.session_state.history.append((query, result))
                    
                    # Display a random fashion tip
                    fashion_tips = [
                        "Pro Tip: Accessorize to elevate any outfit!",
                        "Remember: Confidence is your best accessory.",
                        "Fashion Wisdom: Invest in timeless pieces for a versatile wardrobe.",
                        "Style Secret: Don't be afraid to mix patterns and textures!"
                    ]
                    st.info(random.choice(fashion_tips))
                    
                except Exception as e:
                    st.error(f"Oops! Our fashion AI tripped on its haute couture. Error: {e}")

# Display user history if selected
elif page_options == "View History":
    st.title("Your Style Journey")
    if st.session_state.history:
        for idx, (query, response) in enumerate(st.session_state.history):
            with st.expander(f"Look {idx+1}"):
                st.write(f"**Your Style Profile:**\n{query}")
                st.write(f"**AI Stylist Recommendation:**\n{response}")
    else:
        st.write("Your fashion adventure is just beginning! No past looks to show yet.")

# Display style guide if selected
elif page_options == "Style Guide":
    display_style_guide()

# Add a footer
st.markdown("""
    <div style='text-align: center; color: grey;'>
        Made with ♡ by COZA AI | Stay Stylish!
    </div>
""", unsafe_allow_html=True)