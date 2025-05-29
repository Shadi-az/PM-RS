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
        self.char_to_idx = None
        self.idx_to_char = None
        self.seq_length = 5  # How many characters to look at to predict the next one
        self.is_trained = False
        
    def download_dataset(self):
        """
        Download a dataset of common passwords for training.
        Returns a list of passwords between 6 and max_length characters.
        """
        try:
            # Read the 10k most common passwords dataset thanks to @danielmiessler
            url = "https://raw.githubusercontent.com/danielmiessler/SecLists/refs/heads/master/Passwords/Common-Credentials/10k-most-common.txt"
            response = requests.get(url, timeout=10)  # Add timeout to prevent hanging
            response.raise_for_status()  # Raise an exception for bad status codes
            passwords = response.text.splitlines()
            # Filter passwords to only include those with reasonable length
            return [p for p in passwords if 6 <= len(p) <= self.max_length]
        except Exception as e:
            # Fallback to a small diverse sample if download fails for any reason
            print(f"Using fallback dataset. Error: {e}")
            return [
                "password123", "qwerty123", "admin123", "welcome123",
                "monkey123", "football123", "baseball123", "dragon123",
                "abc123456", "123456789", "letmein123", "shadow123",
                "princess123", "chocolate123", "football123", "password123",
                "pass123@, house##123", "love123456", "bestclub123@",
                "superman123", "batman123", "hulk123", "spiderman123",
                "michael123", "jennifer123", "thomas123", "jessica123",
                "mustang123", "superman123", "starwars123", "matrix123,"
            ]
    
    def prepare_data(self, passwords):
        """
        Prepare the password data for training
        Creates sequences of characters and their next character predictions
        """
        # Create character mappings (including special characters)
        all_chars = set(''.join(passwords) + string.ascii_letters + string.digits + string.punctuation)
        self.char_to_idx = {c: i+1 for i, c in enumerate(all_chars)}
        self.char_to_idx['<pad>'] = 0
        self.idx_to_char = {i: c for c, i in self.char_to_idx.items()}
        
        # Create training sequences
        sequences = []
        next_chars = []
        
        for password in passwords:
            for i in range(len(password) - self.seq_length):
                sequences.append(password[i:i+self.seq_length])
                next_chars.append(password[i+self.seq_length])
        
        # Convert to numerical format for the model
        X = np.zeros((len(sequences), self.seq_length), dtype=np.int32)
        y = np.zeros((len(sequences), len(self.char_to_idx)), dtype=np.bool_)
        
        for i, sequence in enumerate(sequences):
            for t, char in enumerate(sequence):
                X[i, t] = self.char_to_idx[char]
            y[i, self.char_to_idx[next_chars[i]]] = 1
            
        return X, y
    
    def build_model(self, vocab_size):
        """
        Build the neural network model
        Uses LSTM layers to learn password patterns
        """
        model = Sequential([
            # Convert characters to dense vectors
            Embedding(vocab_size, 32, input_length=self.seq_length),  # Reduced embedding size for performance
            # First LSTM layer with dropout to prevent overfitting
            LSTM(64, return_sequences=True),  # Reduced LSTM units for performance
            Dropout(0.1),  # dropout to regularise
            # Second LSTM layer
            LSTM(64),
            Dropout(0.1),
            # Output layer to predict next character
            Dense(vocab_size, activation='softmax')
        ])
        
        model.compile(loss='categorical_crossentropy', 
                     optimizer='adam', 
                     metrics=['accuracy'])
        return model
    
    def train(self, epochs=5, batch_size=64):  # seems to be the decent number for now
        """
        Train the model on password data
        epochs: Number of training iterations
        batch_size: Number of samples processed before model update
        """
        if self.is_trained:
            print("Model is already trained!")
            return
            
        passwords = self.download_dataset()
        print(f"Training on {len(passwords)} passwords")
        
        X, y = self.prepare_data(passwords)
        vocab_size = len(self.char_to_idx)
        
        self.model = self.build_model(vocab_size)
        self.model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=1)
        self.is_trained = True
    
    def is_strong_password(self, password):
        """
        Check if a password meets strength requirements
        """
        # More reasonable requirements
        return (
            len(password) >= 8 and
            (any(c.isupper() for c in password) or any(c.islower() for c in password)) and  # At least one letter
            any(c.isdigit() for c in password)  # At least one number
        )
    
    def generate_password(self, seed=None, temperature=0.7):
        """
        Generate a single password using the trained model
        temperature: Controls randomness (note to self: lower = more predictable)
        """
        if not self.is_trained:
            raise Exception("Model not trained. Call train() first.") # debug purposes
        
        # Create random seed if none provided
        if seed is None:
            seed = ''.join(random.choice(string.ascii_letters + string.digits) 
                          for _ in range(self.seq_length))
        
        generated = seed
        
        # Generate characters until we reach max_length
        while len(generated) < self.max_length:
            # Convert seed to numerical form
            x = np.zeros((1, self.seq_length))
            for t, char in enumerate(seed):
                if char in self.char_to_idx:
                    x[0, t] = self.char_to_idx[char]
            
            # Predict next character
            preds = self.model.predict(x, verbose=0)[0]
            
            # Apply temperature for controlled randomness
            preds = np.log(preds + 1e-10) / temperature
            exp_preds = np.exp(preds)
            preds = exp_preds / np.sum(exp_preds)
            
            # Choose next character
            next_index = np.random.choice(len(preds), p=preds)
            next_char = self.idx_to_char[next_index]
            
            if next_char == '<pad>' or next_char == ' ':
                # Skip spaces and padding characters
                continue
                
            generated += next_char
            seed = seed[1:] + next_char
        
        return generated
    
    def generate_multiple(self, count=5): # testing purposes
        """
        Generate multiple strong passwords
        count: Number of passwords to generate
        """
        passwords = []
        attempts = 0
        max_attempts = count * 10  # set max attempts (note to self: increase or decrease when facing errors)
        
        print(f"Attempting to generate {count} passwords...")
        while len(passwords) < count and attempts < max_attempts:
            pwd = self.generate_password()
            print(f"Generated: {pwd}")  # Debug print
            if self.is_strong_password(pwd):
                passwords.append(pwd)
                print(f"Accepted password: {pwd}")  # Debug print (ignore, debug purposes)
            attempts += 1
                
        return passwords

#  Enabling usage for GUI integration in the app (This module I built separately to start with)
if __name__ == "__main__":
    # Create password generator
    generator = PasswordGenerator(max_length=15)
    
    # Train the model (only once)
    print("Training the model...")
    generator.train(epochs=10)
    
    # Example of generating passwords (this would be called from GUI)
    print("\nGenerating passwords...")
    passwords = generator.generate_multiple(5)  # Reduced number of passwords
    
    if passwords:
        print("\nFinal generated passwords:")
        for pwd in passwords:
            print(pwd)
    else:
        print("\nNo valid passwords were generated") # (error handling and debug purposes - adjust settings if error)
