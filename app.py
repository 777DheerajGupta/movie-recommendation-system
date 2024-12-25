import streamlit as st
import pickle
import pandas as pd
import requests

# Function to fetch movie poster from The Movie Database (TMDB)
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US"

    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIzNWQ5ZDVhMTA0YzQ4MjNkNmNkOWFiMjUwOTM3OGIzMSIsIm5iZiI6MTczNTAzMjg0Ny44NjYsInN1YiI6IjY3NmE4MDBmYjQzNDI1MTI2OGE5ZWExMSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.uyjmyKqVir5AQqBtZ065d4HriSKHrB1mnQqmy_kxD8M"  # Use a secret way to store the API key
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        poster_path = data.get('poster_path')

        if poster_path:
            # Construct the full image URL
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
            return poster_url
        else:
            return None
    else:
        return None

# Function to recommend movies based on similarity
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), key=lambda x: x[1], reverse=True)[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        movie_id = i[0]
        recommended_movies.append(movies.iloc[i[0]].title)
        poster = fetch_poster(movies.iloc[i[0]].movie_id)  # Assuming you have movie_id in the movies dataset
        recommended_movies_posters.append(poster)
    return recommended_movies, recommended_movies_posters

# Function to download similarity.pkl from GitHub Release
def download_similarity_file():
    url = "https://github.com/777DheerajGupta/movie-recommendation-system/releases/download/v1.0/similarity.pkl"
    response = requests.get(url)
    with open("similarity.pkl", "wb") as f:
        f.write(response.content)

# Ensure the similarity.pkl file is downloaded if not already present
try:
    similarity = pickle.load(open('similarity.pkl', 'rb'))
except FileNotFoundError:
    download_similarity_file()
    similarity = pickle.load(open('similarity.pkl', 'rb'))

# Load the movies data from the local file
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

# Streamlit app title and user input
st.title('Movie Recommender System')

selected_movie_name = st.selectbox('Select Movie', movies['title'].values)

# Display recommended movies upon button click
if st.button('Recommend Movie'):
    names, posters = recommend(selected_movie_name)

    # Create 5 columns for horizontal alignment
    col1, col2, col3, col4, col5 = st.columns(5)

    # Add movie details into columns
    for col, name, poster in zip([col1, col2, col3, col4, col5], names, posters):
        with col:
            # Display movie name
            st.markdown(f"<p style='text-align: center; font-weight: bold;'>{name}</p>", unsafe_allow_html=True)
            # Display movie poster (if available)
            if poster:
                try:
                    st.image(poster, use_container_width=True)
                except Exception as e:
                    st.write("Poster not available")
            else:
                st.write("Poster not available")
