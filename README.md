# Stock Price Prediction with Deep Learning and Sentiment Analysis

## 1. Project Overview

This project predicts stock prices using deep learning models (CNN, RNN, LSTM, GRU, Transformer, TimesNet) and integrates sentiment analysis from news and social media. The workflow includes data scraping, preprocessing, sentiment scoring, model training, and evaluation.

---

## 2. Environment Setup

2. **Install dependencies** (Python 3.8+ recommended):
   ```
   pip install -r requirements.txt
   ```

---

## 3. Data Collection

- **Raw data** (stock prices, news, social media) is collected using scripts in:
  - `Source Code/data_scraper/`
    - `headline scraper/` for news headlines
    - `news_content_scraper/` for news content
    - `stock_price_scraper/` for stock prices

- **To run a scraper** (example for headlines):
   ```
   cd "Source Code/data_scraper/headline scraper"
   python find_headlines.py
   ```

---

## 4. Data Preprocessing & Sentiment Integration

- **Preprocess and clean data:**
   ```
   cd "Source Code/data_processor"
   python preprocess.py
   ```

- **Score news with GPT sentiment:**
   ```
   python score_by_gpt.py
   ```

- **Summarize news (optional):**
   ```
   python summarize.py
   ```

- **Integrate price and sentiment data:**
   ```
   python price_news_integrate.py
   ```

---

## 5. Model Training & Testing

Each model has its own folder in `Source Code/dataset_test/`. To train and test a model:

- **Example: Train/test CNN**
   ```
   cd "Source Code/dataset_test/CNN-for-Time-Series-Prediction"
   python run.py
   ```

- **Other models:**  
  - `GRU-for-Time-Series-Prediction`
  - `LSTM-for-Time-Series-Prediction`
  - `RNN-for-Time-Series-Prediction`
  - `Transformer-for-Time-Series-Prediction`
  - `TimesNet-for-Time-Series-Prediction`

  Replace the folder name above to run each model.

---

## 6. Results Integration & Evaluation

- **Integrate results from all models:**
   ```
   cd "Source Code/dataset_test"
   python integrate_result.py
   ```

- **Evaluate and compare models:**
   ```
   python eval_output.py
   ```

- **Results** will be saved in:
  - `integrated_eval_data_{n}/` (metrics: MAE, MSE, R2)
  - `integrated_predicted_data_{n}/` (predictions)
  - `merged_eval_data_{n}.csv` (comparison table)

---

## 7. Output Files

- **Trained models:**  
  Saved in each model's `saved_models/` folder.
- **Test results:**  
  In `test_result_5/`, `test_result_25/`, `test_result_50/` (for different test set sizes).
- **Evaluation summaries:**  
  In `merged_eval_data_5.csv`, `merged_eval_data_25.csv`, `merged_eval_data_50.csv`.

---

## 8. Notes

- For detailed usage and troubleshooting, see the `.md` files in each subfolder.
- Update API keys (e.g., for OpenAI) as needed in the relevant scripts.
- Ensure all data paths are correct if you move folders.

---

**Contact:**  
Võ Lâm Duy Thuận, Võ Hùng Anh  
[duythuan.vl2511@gmail.com/vohunganh2811@gmail.com] 