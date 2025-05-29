import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Embedding, Dropout
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import random
import string
import requests
from io import StringIO

class PasswordGenerator:
    def __init__(self, max_length=12):
        """
        Initialize the password generator
        max_length: Maximum length of generated passwords
        """
        self.max_length = max_length
        self.model = None
        self.tokenizer = Tokenizer()
        self.is_trained = False
        
        # Fallback common words if download fails
        self.fallback_words = [
            "sun", "moon", "star", "rain", "snow", "wind", "fire", "water",
            "love", "hope", "dream", "life", "time", "home", "work", "play",
            "book", "game", "food", "tree", "bird", "fish", "cat", "dog",
            "blue", "red", "green", "black", "white", "gold", "silver",
            "mountain", "river", "ocean", "beach", "forest", "garden",
            "spring", "summer", "autumn", "winter", "day", "night", "sky"
        ]
        
        # Will be populated from downloaded passwords
        self.common_words = []
        
        self.common_numbers = ["123", "456", "789", "111", "222", "333", "444", "555"]
        self.common_special_chars = ["@", "#", "$", "!", "&", "*"]
        
    def download_dataset(self):
        """
        Download a dataset of common passwords for training.
        Returns a list of passwords between 6 and max_length characters.
        """
        try:
            # read from a more common dataset for faster and memorable training
            url = "https://raw.githubusercontent.com/danielmiessler/SecLists/refs/heads/master/Passwords/Common-Credentials/10k-most-common.txt"
            response = requests.get(url, timeout=10)  # Add timeout to prevent hanging
            response.raise_for_status()  # Raise an exception for bad status codes
            passwords = response.text.splitlines()
            # Filter passwords to only include those with reasonable length
            return [p for p in passwords if 6 <= len(p) <= self.max_length]
        except Exception as e:
            # Fallback to a small but diverse sample if download fails
            print(f"Using fallback dataset. Error: {e}")
            return [
                "password123", "qwerty123", "admin123", "welcome123",
                "monkey123", "football123", "baseball123", "dragon123",
                "abc123456", "123456789", "letmein123", "shadow123",
                "princess123", "chocolate123", "football123", "password123",
                "pass123@", "house123", "love123456", "bestclub123@",
                "superman123", "batman123", "hulk123", "spiderman123",
                "michael123", "jennifer123", "thomas123", "jessica123",
                "mustang123", "superman123", "starwars123", "matrix123"
            ]
    
    def prepare_data(self, passwords):
        """
        Prepare the password data for training
        Creates sequences of words and their next word predictions
        """
        # Create word-based sequences to help make memorable pw
        sequences = []
        next_words = []
        
        for password in passwords:
            # Split password into words (if possible) or characters
            words = self.split_into_words(password)
            for i in range(len(words) - 2):
                sequences.append(words[i:i+2])
                next_words.append(words[i+2])
        
        # Convert to numerical format for the model
        self.tokenizer.fit_on_texts(sequences + next_words)
        X = self.tokenizer.texts_to_matrix(sequences)
        y = self.tokenizer.texts_to_matrix(next_words)
            
        return X, y
    
    def split_into_words(self, password):
        """
        Split password into words or meaningful chunks
        Returns only alphabetic words (no numbers or special characters)
        """
        words = []
        current_word = ""
        
        for char in password:
            if char.isalpha():
                current_word += char.lower()  # Convert to lowercase for consistency
            else:
                if current_word and len(current_word) >= 3:  # Only keep words with 3+ characters
                    words.append(current_word)
                    current_word = ""
                # Don't add non-alphabetic characters to words list
        
        if current_word and len(current_word) >= 3:  # Check the last word too
            words.append(current_word)
            
        return words
    
    def build_model(self, vocab_size):
        """
        Build the neural network model
        Uses LSTM layers to learn password patterns
        """
        model = Sequential([
            Embedding(vocab_size, 32, input_length=2),
            LSTM(64, return_sequences=True),
            Dropout(0.1),
            LSTM(64),
            Dropout(0.1),
            Dense(vocab_size, activation='softmax')
        ])
        
        model.compile(loss='categorical_crossentropy', 
                     optimizer='adam', 
                     metrics=['accuracy'])
        return model
    
    def extract_common_words(self, passwords):
        """
        Extract common words from downloaded passwords
        """
        all_words = []
        for password in passwords:
            words = self.split_into_words(password)
            all_words.extend(words)
        
        # Count word frequencies
        word_counts = {}
        for word in all_words:
            if word in word_counts:
                word_counts[word] += 1
            else:
                word_counts[word] = 1
        
        # Sort by frequency and take the top 50 words
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        common_words = [word for word, count in sorted_words[:50] if len(word) >= 3]
        
        # If we found at least 10 common words, use them; otherwise, use fallback
        if len(common_words) >= 10:
            self.common_words = common_words
            print(f"Extracted {len(common_words)} common words from passwords")
        else:
            self.common_words = self.fallback_words
            print("Using fallback word list")
    
    def train(self, epochs=10, batch_size=64):
        """
        Train the model on password data
        """
        if self.is_trained:
            print("Model is already trained!")
            return
            
        passwords = self.download_dataset()
        print(f"Training on {len(passwords)} passwords")
        
        # Extract common words from passwords
        self.extract_common_words(passwords)
        
        X, y = self.prepare_data(passwords)
        vocab_size = len(self.tokenizer.word_index) + 1
        
        self.model = self.build_model(vocab_size)
        self.model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=1)
        self.is_trained = True
    
    def is_strong_password(self, password):
        """
        Check if a password meets strength requirements
        """
        return (
            len(password) >= 8 and
            any(c.isalpha() for c in password) and  # At least one letter
            any(c.isdigit() for c in password)  # At least one number
        )
    
    def generate_memorable_password(self):
        """
        Generate a memorable password using common patterns
        """
        # Choose a random pattern
        patterns = [
            # Word + Number + Special
            lambda: f"{random.choice(self.common_words).capitalize()}{random.choice(self.common_numbers)}{random.choice(self.common_special_chars)}",
            # Word + Word + Number
            lambda: f"{random.choice(self.common_words).capitalize()}{random.choice(self.common_words)}{random.choice(self.common_numbers)}",
            # Number + Word + Special
            lambda: f"{random.choice(self.common_numbers)}{random.choice(self.common_words).capitalize()}{random.choice(self.common_special_chars)}",
            # Word + Special + Number
            lambda: f"{random.choice(self.common_words).capitalize()}{random.choice(self.common_special_chars)}{random.choice(self.common_numbers)}"
        ]
        
        return random.choice(patterns)()
    
    def generate_multiple(self, count=5):
        """
        Generate multiple memorable passwords
        """
        # If common_words is empty, try to populate it from dataset passwords
        if not self.common_words:
            try:
                passwords = self.download_dataset()
                self.extract_common_words(passwords)
            except Exception as e:
                print(f"Error downloading passwords: {e}")
                self.common_words = self.fallback_words
        
        # If still empty, use fallback
        if not self.common_words:
            self.common_words = self.fallback_words
            print("Using fallback word list for password generation")
        
        passwords = []
        attempts = 0
        max_attempts = count * 5
        
        print(f"Generating {count} memorable passwords...")
        while len(passwords) < count and attempts < max_attempts:
            pwd = self.generate_memorable_password()
            # Ensure no spaces in the password
            pwd = pwd.replace(" ", "")
            if self.is_strong_password(pwd):
                passwords.append(pwd)
                print(f"Generated: {pwd}")
            attempts += 1
                
        return passwords

# Enable usage for GUI integration
if __name__ == "__main__":
    # Create password generator
    generator = PasswordGenerator(max_length=15)
    
    # read passwords and extract common words
    print("Downloading passwords and extracting common words...")
    try:
        passwords = generator.download_dataset()
        generator.extract_common_words(passwords)
        print(f"Using {len(generator.common_words)} common words from downloaded passwords")
    except Exception as e:
        print(f"Error: {e}\nUsing fallback word list")
    
    # Generate passwords 
    print("\nGenerating memorable passwords...")
    passwords = generator.generate_multiple(5)
    
    if passwords:
        print("\nFinal generated passwords:")
        for pwd in passwords:
            print(pwd)
    else:
        print("\nNo valid passwords were generated.")
