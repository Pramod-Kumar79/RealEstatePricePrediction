# House Price Prediction for Bangalore

This project demonstrates an end-to-end machine learning pipeline for predicting house prices in Bangalore. The process starts from scraping real estate data from MagicBricks.com, followed by data cleaning, extensive feature engineering, and finally, training and evaluating predictive models.

## Project Workflow

The project is structured into a clear, sequential workflow:

1.  **Web Scraping**: Data is collected from MagicBricks using Python scripts.
2.  **Data Cleaning**: Raw data is processed and cleaned to prepare it for feature engineering.
3.  **Feature Engineering & Encoding**: New features are created, and categorical data is encoded for modeling.
4.  **Modeling**: Machine learning models are trained and evaluated to predict house prices.

## File Structure

```
├── data/
│   ├── bronze-houseprices.csv    # Raw scraped data
│   ├── silver_dataset.csv        # Cleaned data
│   └── gold-houseprices.csv      # Data ready for modeling
├── models/
│   └── random_forest_model.pkl   # Saved model file
├── scripts/
│   ├── 01_Data_Cleaning.ipynb
│   ├── 02_Encoding_FeatureEng.ipynb
│   └── 03_model.ipynb
├── web-scraping/
│   ├── 01_screping_html.py
│   └── scrapping_selenium.py
├── requirements.txt
└── README.md
```

## How to Run the Project

1.  **Clone the repository**

    ```bash
    git clone <repository-url>
    cd <repository-folder>
    ```

2.  **Set up a virtual environment**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables**
    Create a `.env` file in the `scripts/` directory and add your Google Maps API key:

    ```
    GMAPS_API_KEY="YOUR_API_KEY"
    ```

5.  **Run the notebooks**
    Execute the Jupyter Notebooks in the `scripts/` directory in the following order:

    1.  `01_Data_Cleaning.ipynb`
    2.  `02_Encoding_FeatureEng.ipynb`
    3.  `03_model.ipynb`

    _Note: The web scraping scripts in `web-scraping/` can be run to gather fresh data, which will be saved in the `data/` directory._

## Dependencies

All required Python packages are listed in the `requirements.txt` file.
