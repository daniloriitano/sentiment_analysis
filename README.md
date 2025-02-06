# Sentiment Analysis with Selenium and VADER

This project performs sentiment analysis on newspaper articles using Selenium for web scraping and the VADER lexicon from NLTK for sentiment analysis. The script extracts text from specified URLs, removes unwanted content, and determines the overall sentiment tone of the text.

## 📌 Features
- Automatic extraction of text from newspaper articles using Selenium
- Cleaning of extracted text to remove irrelevant content
- Sentiment analysis using the VADER model
- Saving results to a CSV file

## 🚀 Installation

### Prerequisites
Ensure you have Python installed on your system. You can install the required packages with the following command:

```bash
pip install pandas nltk selenium webdriver-manager
```

Additionally, to use the Chrome WebDriver, ensure you have Google Chrome installed.

### Setting Up the Environment
We started by creating a **Conda** environment for better dependency management. You can create and activate the environment with the following commands:

```bash
conda create --name sentiment-analysis python=3.9
conda activate sentiment-analysis
```

After activating the environment, install the required packages:

```bash
pip install pandas nltk selenium webdriver-manager
```

### Clone the Repository
```bash
git clone https://github.com/daniloriitano/sentiment-analysis.git
cd sentiment-analysis
```

## 🔧 Usage

Run the script using:

```bash
python sentiment_analysis.py
```

The script will:
1. Load the URLs of the articles to be analyzed.
2. Use Selenium to extract the text.
3. Clean the text by removing irrelevant content.
4. Perform sentiment analysis using the VADER model.
5. Save the results to a `results_sentiment_ilgiornale.csv` file.

## 📄 Results
Results are saved in a CSV file with the following columns:
- **Party**: The political party associated with the article
- **URL**: Link to the analyzed article
- **Tone**: Sentiment classification (Positive, Neutral, Negative)
- **Score**: Normalized sentiment score
- **Text**: The first 1000 characters of the analyzed article

## 🛠️ Customization
To modify the articles analyzed, update the `articles` dictionary in the script with the desired URLs.

## 📌 Notes
- This script uses a headless browser mode, meaning it will run without displaying any windows.
- Some websites may block web scraping; if so, consider updating the user-agent in Selenium options.

## 🤝 Contributing
If you want to contribute to this project, feel free to submit a pull request or report issues in the Issues section of the repository.

## 📜 License
This project is distributed under the MIT license. Feel free to use and modify it as needed.
