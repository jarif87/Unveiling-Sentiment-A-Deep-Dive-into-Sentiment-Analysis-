import streamlit as st
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import one_hot
import pickle
import emoji
import os

# Streamlit app title
st.title('Unveiling Sentiment: A Deep Dive into Sentiment Analysis 🐨')

# Print the current working directory
st.write(f"Current working directory: {os.getcwd()}")

# Function to load model and predict sentiment
def predict_sentiment(custom_data):
    model_path = '/mount/src/unveiling-sentiment-a-deep-dive-into-sentiment-analysis/sentiment_analysis_model.h5'  # Use absolute path
    st.write(f"Model path: {model_path}")  # Debugging line to check the model path
    try:
        # Load the trained model
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"The model file was not found at {model_path}")
        
        model = load_model(model_path)
        st.write("Model loaded successfully.")  # Debugging line to confirm model loading

        # Load the one-hot encoding information
        with open('one_hot_info_1.pkl', 'rb') as handle:
            one_hot_info = pickle.load(handle)

        vocab_size = one_hot_info['vocab_size']
        max_len = one_hot_info['max_len']

        # Define labels with emojis
        labels_with_emojis = {
            'Positive': '😊',
            'Neutral': '😐',
            'Negative': '😔'
        }

        # One-hot encode each tweet
        one_hot_texts = [one_hot(text, vocab_size) for text in custom_data]

        # Pad the sequences
        padded_texts = pad_sequences(one_hot_texts, padding='pre', maxlen=max_len)

        # Predict the sentiments for all tweets
        predictions = model.predict(np.array(padded_texts))

        # Convert predictions to class labels and probabilities
        predicted_sentiments = []
        for prediction in predictions:
            sentiment = np.argmax(prediction)
            sentiment_label = list(labels_with_emojis.keys())[sentiment]
            sentiment_emoji = labels_with_emojis[sentiment_label]
            sentiment_probabilities = {label: round(prob, 4) for label, prob in zip(labels_with_emojis.keys(), prediction)}
            predicted_sentiments.append((sentiment_label, sentiment_emoji, sentiment_probabilities))

        return predicted_sentiments

    except Exception as e:
        st.error(f"Error during prediction: {e}")
        return None

# Streamlit UI
user_input = st.text_area("Please enter the tweet you'd like analyzed:")

if st.button('Analyze', key='analyze_button', help="Click to analyze the sentiment"):
    if user_input.strip():  # Check if input is not empty
        # Remove emojis and replace with their description
        user_input = emoji.demojize(user_input)
        
        # Split input by newlines to handle multiple tweets
        tweets = user_input.split('\n')
        
        # Predict sentiment for custom data
        predicted_sentiments = predict_sentiment(tweets)

        if predicted_sentiments is not None:
            # Display results for each tweet
            st.write("## Predicted Sentiments:")
            for i, (sentiment_label, sentiment_emoji, sentiment_probabilities) in enumerate(predicted_sentiments):
                st.write(f"Tweet {i+1}: {sentiment_label} {sentiment_emoji}")
                st.write("Probabilities:")
                for label, prob in sentiment_probabilities.items():
                    st.write(f"{label}: {prob:.4f}")
    else:
        st.write("Please enter tweet(s) to analyze.")
