import yaml
import pandas as pd

def load_config(config_path='config.yaml'):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def get_stocks(config):
    stocks = []
    for sector in config['sectors']:
        stocks.extend(config['sectors'][sector]['tickers'])
    return stocks

def get_research_topic_data(config, topic):
    if topic not in config['research_topics']:
        raise ValueError(f"Research topic '{topic}' not found in config.")
    
    topic_data = config['research_topics'][topic]
    return topic_data['treatments'], topic_data['common_causes'], topic_data['outcome']

def preprocess_data(data_path, config, research_topic, outcome='next_return'):
    stocks = get_stocks(config)
    treatments, common_causes, outcome = get_research_topic_data(config, research_topic)

    df = pd.read_csv(data_path)
    df = df[df['ticker'].isin(stocks)]

    # Ensure all required columns are present
    required_columns = ['ticker', 'date'] + treatments + common_causes + [outcome]
    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing columns in the dataset: {missing_columns}")

    return df, treatments, common_causes, outcome
