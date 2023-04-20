import zipfile

import nltk
import pandas as pd
import re

nltk.download('stopwords')
from nltk.corpus import stopwords

stop_words = stopwords.words('english')
print(stop_words)

zip_path = "rows2.zip"
csv_file_name = "rows2.csv"

with zipfile.ZipFile(zip_path, "r") as zfile:
    # CSV dosyasını pandas DataFrame'e okuyun.
    with zfile.open(csv_file_name) as csv_file:
        veriler = pd.read_csv(csv_file, dtype=str)

print(veriler)

# print(veriler.shape)
# print(veriler.columns)
# print(veriler.dtypes)
# print(veriler.head())
# print(veriler.tail(7))
# print(veriler.info())
# print(veriler.isnull().sum().sort_values(ascending=False))
# print(veriler.describe())
# print(veriler["Product"].value_counts())


veriler = veriler.drop(
    ["Date received", "Sub-product", "Sub-issue", "Consumer complaint narrative", "Company public response", "Tags",
     "Consumer consent provided?", "Submitted via", "Date sent to company", "Company response to consumer",
     "Timely response?", "Consumer disputed?"], axis=1)
veriler.dropna(how="any", inplace=True)  # içinde null deger olan satırları siler

veriler['Product'] = veriler['Product'].apply(
    lambda x: ' '.join([word for word in x.split() if word not in (stop_words)]))

veriler['Issue'] = veriler['Issue'].apply(
    lambda x: ' '.join([word for word in x.split() if word not in (stop_words)]))

veriler['Company'] = veriler['Company'].apply(
    lambda x: ' '.join([word for word in x.split() if word not in (stop_words)]))

veriler['State'] = veriler['State'].apply(
    lambda x: ' '.join([word for word in x.split() if word not in (stop_words)]))

veriler['ZIP code'] = veriler['ZIP code'].apply(
    lambda x: ' '.join([word for word in x.split() if word not in (stop_words)]))

veriler['Complaint ID'] = veriler['Complaint ID'].apply(
    lambda x: ' '.join([word for word in x.split() if word not in (stop_words)]))

veriler['Product'] = [re.sub('[^\w\s]+', '', s) for s in veriler['Product'].tolist()]

veriler['Issue'] = [re.sub('[^\w\s]+', '', s) for s in veriler['Issue'].tolist()]

veriler['Company'] = [re.sub('[^\w\s]+', '', s) for s in veriler['Company'].tolist()]

veriler['State'] = [re.sub('[^\w\s]+', '', s) for s in veriler['State'].tolist()]

veriler['ZIP code'] = [re.sub('[^\w\s]+', '', s) for s in veriler['ZIP code'].tolist()]

veriler['Complaint ID'] = [re.sub('[^\w\s]+', '', s) for s in veriler['Complaint ID'].tolist()]

veriler.to_csv('rows2.csv', index=False)
