import streamlit as st
import pickle
import pandas as pd
import requests

# --- DATA LOADING ---
# Load the movie dictionary from the pickle file
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
# Convert the dictionary back to a pandas DataFrame
movies = pd.DataFrame(movies_dict)

# Load the similarity matrix
similarity = pickle.load(open('similarity.pkl', 'rb'))

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Movie Buddy", layout="wide")

# --- API KEY ---
# Access your OMDb API key securely from Streamlit secrets
# Before deploying, create a file .streamlit/secrets.toml and add:
# OMDB_API_KEY = "YOUR_KEY_HERE"
OMDB_API_KEY = st.secrets.get("OMDB_API_KEY", "6f527921") # Fallback for local testing

# --- HELPER FUNCTIONS ---
def fetch_movie_info(movie_title):
    """
    Fetches movie poster, IMDb link, and other details from OMDb API.
    """
    url = f"http://www.omdbapi.com/?t={movie_title}&apikey={OMDB_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()

        # Set a placeholder if the poster is not available
        poster = data.get("Poster", "https://placehold.co/150x220/000000/FFFFFF?text=No+Poster")
        if poster == "N/A":
            poster = "https://placehold.co/150x220/000000/FFFFFF?text=No+Poster"

        # Construct IMDb URL
        imdb_id = data.get("imdbID", "")
        imdb_url = f"https://www.imdb.com/title/{imdb_id}" if imdb_id else "#"

        # Get other details with fallbacks
        year = data.get("Year", "N/A")
        rating = data.get("imdbRating", "N/A")
        genre = data.get("Genre", "N/A")

        return poster, imdb_url, year, rating, genre
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {e}")
        # Return default values on failure
        return "https://placehold.co/150x220/000000/FFFFFF?text=API+Error", "#", "N/A", "N/A", "N/A"


def recommend(movie):
    """
    Finds the top 10 most similar movies based on the similarity matrix.
    """
    try:
        index = movies[movies['title'] == movie].index[0]
        distances = similarity[index]
        # Get the top 10 similar movies, skipping the first one (which is the movie itself)
        movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:11]
        
        recommendations = []
        for i in movie_list:
            recommendations.append(movies.iloc[i[0]].title)
        return recommendations
    except IndexError:
        st.error("Movie not found in the dataset. Please select another one.")
        return []

# --- UI LAYOUT ---

# 🎞️ Hero Banner with Styled Border
hero_section = """
<style>
    .hero-container {
        position: relative;
        height: 330px;
        background-image: linear-gradient(to right, rgba(0, 0, 0, 0.7), rgba(0,0,0,0.1)), url('https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYWk1MzQ1Y2FqejRkYzJ2bDJ2eHR3cW13emc3dHc5dWpjZ2E5amh5ZCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/A8OSeenhtpey43CcMG/giphy.gif');
        background-size: cover;
        background-position: center;
        border-radius: 16px;
        margin-bottom: 40px;
        border: 4px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.5);
        overflow: hidden;
    }
    .hero-text {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        text-align: center;
        color: white;
    }
    .hero-text h1 {
        font-size: 3.5rem; /* 56px */
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        letter-spacing: 2px;
        font-weight: bold;
        margin: 0;
        text-shadow: 3px 3px 8px #000;
    }
    .hero-text p {
        font-size: 1.375rem; /* 22px */
        font-family: 'Segoe UI', sans-serif;
        margin-top: 14px;
        color: #f0f0f0;
        text-shadow: 1px 1px 6px #000;
    }
</style>
<div class="hero-container">
    <div class="hero-text">
        <h1>MOVIE RECOMMENDER</h1>
        <p>Find your next favorite movie with just one click</p>
    </div>
</div>
"""
st.markdown(hero_section, unsafe_allow_html=True)

# 🎥 Movie Selection UI
st.header("Choose a movie to get recommendations:")
selected_movie = st.selectbox(
    "Select from the dropdown below:",
    movies['title'].values,
    label_visibility="collapsed"
)

# Recommendation Button and Display
if st.button("Recommend Me", type="primary"):
    recommendations = recommend(selected_movie)
    if recommendations:
        st.subheader("Top 10 Recommendations:")

        # Display recommendations in a 2x5 grid
        for i in range(0, len(recommendations), 5):
            cols = st.columns(5)
            # Get the next 5 movies for the current row
            row_movies = recommendations[i:i+5]
            for j, movie_title in enumerate(row_movies):
                with cols[j]:
                    poster_url, imdb_url, year, rating, genre = fetch_movie_info(movie_title)
                    
                    # Modern card layout for each movie
                    card_html = f"""
                        <div style="background-color: #0d1117; border: 1px solid #30363d; border-radius: 12px; overflow: hidden; box-shadow: 0 6px 16px rgba(0,0,0,0.4); transition: transform 0.3s ease-in-out; height: 100%;"
                             onmouseover="this.style.transform='scale(1.05)'; this.style.boxShadow='0 10px 25px rgba(0,0,0,0.7)';"
                             onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='0 6px 16px rgba(0,0,0,0.4)';">
                            <a href="{imdb_url}" target="_blank" style="text-decoration: none;">
                                <img src="{poster_url}" style="width: 100%; height: auto; display: block;"
                                     onerror="this.onerror=null;this.src='https://placehold.co/150x220/000000/FFFFFF?text=Error';" />
                                <div style="padding: 12px; color: white; text-align: center;">
                                    <h4 style="margin: 0 0 8px 0; font-size: 1rem; font-weight: 600; min-height: 40px;">{movie_title}</h4>
                                    <p style="margin: 5px 0; font-size: 0.875rem;">📅 {year} | ⭐ {rating}</p>
                                    <p style="margin: 0; font-size: 0.8rem; color: #8b949e; min-height: 35px;">🎭 {genre}</p>
                                </div>
                            </a>
                        </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)
                    st.write("") # Adds vertical space between cards

# --- Footer ---
st.markdown("---")
st.markdown("<p style='text-align: center; color: #888;'>Made by AMY</p>", unsafe_allow_html=True)
