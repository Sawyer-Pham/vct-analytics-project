# VCT Match Prediction & Analytics

A data analytics and machine learning project for analyzing professional VALORANT matches and predicting match outcomes using historical team and player performance.

## Overview

This project collects professional VALORANT match data, stores it in a relational SQL database, engineers performance-based features, and trains machine learning models to predict match winners.

I built the project to gain hands-on experience with data collection, relational database design, feature engineering, machine learning, and model evaluation using real-world esports data.

## Tech Stack

- Python
- SQL
- SQLite
- pandas
- scikit-learn
- Git / GitHub
- VLR data/API

## Database Design

Match data is organized into several related tables:

- **Teams** — team information and identifiers
- **Players** — player information and team associations
- **Matches** — match-level information
- **Map Results** — individual map results and winners
- **Player Map Stats** — player performance statistics by map
- **Map Vetoes** — map pick/ban information

The relational structure allows match, team, map, and player information to be combined when generating features for machine learning.

## Machine Learning Pipeline

The project follows a basic end-to-end ML workflow:

1. Collect professional VCT match data
2. Store and organize the data in SQL
3. Query historical team and player statistics
4. Generate features for each matchup
5. Split matches chronologically into training and testing data
6. Train a classification model
7. Evaluate predictions on unseen matches

## Features

The model currently incorporates features such as:

- Overall team win rate
- Recent team win rate
- Matches played
- Head-to-head win rate
- Win-rate differential
- Recent win-rate differential
- Average ACS differential
- Recent ACS differential

These features are generated using information available before each match to represent the relative strength and recent performance of the two teams.

## Model

The current implementation uses **Logistic Regression** through scikit-learn.

Rather than randomly splitting matches, the dataset is divided chronologically so earlier matches are used for training and later matches are used for testing. This more closely represents how the model would be used to predict future matches.

Model performance is evaluated using metrics including:

- Accuracy
- Precision
- Recall
- F1-score

## Project Goals

This project is an ongoing exploration of applying data engineering and machine learning to esports.

Future improvements include:

- Map-specific team win rates
- Player and agent performance features
- Elo-based team ratings
- Additional historical VCT data
- Improved feature scaling and preprocessing
- Comparison of multiple machine learning models
- Further evaluation and tuning of model performance

## What I Learned

Through this project, I have gained experience with:

- Designing relational database schemas
- Writing SQL queries across related datasets
- Building Python data-processing pipelines
- Cleaning and transforming real-world data
- Engineering features from historical information
- Training and evaluating machine learning models
- Preventing future information from leaking into training features
- Using Git and GitHub for version control

## Disclaimer

This project is an independent educational project and is not affiliated with Riot Games or VALORANT Champions Tour.
