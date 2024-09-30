import pandas as pd


def clean_column_names(data):
    data.columns = data.columns.str.strip().str.lower()
    return data


def load_and_label_data(filepath, website_name):
    data = pd.read_csv(filepath)
    data = clean_column_names(data)
    data['websitename'] = website_name
    print(f"Colonnes dans {filepath}: {data.columns}")
    return data


def merge_and_remove_duplicates(bayut_data, dubizle_data):
    combined_data = pd.concat([bayut_data, dubizle_data], ignore_index=True)
    print(f"Colonnes combinées: {combined_data.columns}")  # Pour vérification
    unique_data = combined_data.drop_duplicates(subset=['address', 'url'])
    return unique_data


bayut_data = load_and_label_data('continue.csv', 'Bayut')
dubizle_data = load_and_label_data('continue2.csv', 'Dubizle')

final_data = merge_and_remove_duplicates(bayut_data, dubizle_data)

final_data.to_csv('combined_properties.csv', index=False)

print("Les données combinées ont été sauvegardées dans 'combined_properties.csv'.")
