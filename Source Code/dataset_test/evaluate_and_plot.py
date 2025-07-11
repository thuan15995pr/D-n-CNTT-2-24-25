import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Định nghĩa các mô hình và loại sentiment
MODELS = [
    'CNN-for-Time-Series-Prediction',
    'GRU-for-Time-Series-Prediction',
    'LSTM-for-Time-Series-Prediction',
    'RNN-for-Time-Series-Prediction',
    'Transformer-for-Time-Series-Prediction',
    'TimesNet-for-Time-Series-Prediction',
]
SENTIMENT_TYPES = ['sentiment', 'nonsentiment']
RESULT_FOLDERS = ['test_result_5', 'test_result_25', 'test_result_50']

# Hàm tính MAPE

def mean_absolute_percentage_error(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(np.abs((y_true - y_pred) / (y_true + 1e-8))) * 100

# Lưu kết quả tổng hợp
summary_rows = []

for model in MODELS:
    model_path = os.path.join(model)
    for result_folder in RESULT_FOLDERS:
        folder_path = os.path.join(model_path, result_folder)
        if not os.path.exists(folder_path):
            continue
        for stock_folder in os.listdir(folder_path):
            stock_path = os.path.join(folder_path, stock_folder)
            if not os.path.isdir(stock_path):
                continue
            # Xác định loại sentiment
            sentiment_type = 'sentiment' if 'sentiment' in stock_folder else 'nonsentiment'
            for file in os.listdir(stock_path):
                if not file.endswith('.csv'):
                    continue
                file_path = os.path.join(stock_path, file)
                try:
                    df = pd.read_csv(file_path)
                    # Ưu tiên lấy cột origin, nếu không có thì lấy cột thường
                    if 'True_Data_origin' in df.columns and 'Predicted_Data_origin' in df.columns:
                        y_true = df['True_Data_origin']
                        y_pred = df['Predicted_Data_origin']
                    elif 'True_Data' in df.columns and 'Predicted_Data' in df.columns:
                        y_true = df['True_Data']
                        y_pred = df['Predicted_Data']
                    else:
                        # Không đủ cột, bỏ qua file này
                        print(f"Bỏ qua {file_path}: không đủ cột dữ liệu thực tế/dự đoán")
                        continue
                    mae = mean_absolute_error(y_true, y_pred)
                    rmse = mean_squared_error(y_true, y_pred) ** 0.5
                    mape = mean_absolute_percentage_error(y_true, y_pred)
                    summary_rows.append({
                        'Model': model.replace('-for-Time-Series-Prediction',''),
                        'Result_Set': result_folder,
                        'Stock': stock_folder.split('_')[0],
                        'Sentiment': sentiment_type,
                        'MAE': mae,
                        'RMSE': rmse,
                        'MAPE': mape
                    })
                    # Vẽ biểu đồ thực tế vs dự đoán
                    plt.figure(figsize=(10,5))
                    plt.plot(y_true, label='Thực tế')
                    plt.plot(y_pred, label='Dự đoán')
                    plt.title(f'{model.replace("-for-Time-Series-Prediction","")} - {stock_folder} - {file}')
                    plt.xlabel('Thời gian')
                    plt.ylabel('Giá trị')
                    plt.legend()
                    plot_dir = os.path.join('plots', model, result_folder)
                    os.makedirs(plot_dir, exist_ok=True)
                    plt.savefig(os.path.join(plot_dir, f'{stock_folder}_{file.replace(".csv","")}.png'))
                    plt.close()
                except Exception as e:
                    print(f'Error processing {file_path}: {e}')

# Lưu bảng tổng hợp
summary_df = pd.DataFrame(summary_rows)
summary_csv = 'summary_metrics.csv'
summary_df.to_csv(summary_csv, index=False)
print(f'Đã lưu bảng tổng hợp: {summary_csv}')

# Vẽ biểu đồ cột so sánh các chỉ số giữa các mô hình cho từng stock
if not summary_df.empty and 'Stock' in summary_df.columns:
    for result_folder in RESULT_FOLDERS:
        for sentiment_type in SENTIMENT_TYPES:
            for stock in summary_df['Stock'].unique():
                df_plot = summary_df[(summary_df['Result_Set']==result_folder) & (summary_df['Sentiment']==sentiment_type) & (summary_df['Stock']==stock)]
                if df_plot.empty:
                    continue
                plt.figure(figsize=(10,5))
                x = np.arange(len(df_plot['Model']))
                width = 0.25
                plt.bar(x-width, df_plot['MAE'], width, label='MAE')
                plt.bar(x, df_plot['RMSE'], width, label='RMSE')
                plt.bar(x+width, df_plot['MAPE'], width, label='MAPE')
                plt.xticks(x, df_plot['Model'])
                plt.ylabel('Giá trị')
                plt.title(f'So sánh chỉ số - {stock} - {sentiment_type} - {result_folder}')
                plt.legend()
                plot_dir = os.path.join('plots', 'bar', result_folder)
                os.makedirs(plot_dir, exist_ok=True)
                plt.savefig(os.path.join(plot_dir, f'{stock}_{sentiment_type}.png'))
                plt.close()
    print('Đã vẽ xong các biểu đồ.')
else:
    print('Không có dữ liệu hợp lệ để vẽ biểu đồ.')