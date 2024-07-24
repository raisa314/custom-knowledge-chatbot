import pandas as pd
import re
def check_https(url):
    match = re.search(r'https://\S+', url)
    if match:
        clean_url = match.group(0)
        if clean_url.startswith('https://'):
            return clean_url
    return "NO"

def clean(file):
    df= pd.read_csv(file, usecols=['CODE','DESCRIPTION', 'Installation Instructions', 'Maintenance Instructions'], encoding='unicode_escape')
    df['NAME'] = df['DESCRIPTION']
    df.drop(columns=['DESCRIPTION'], inplace=True)
    df = df[df['NAME'].notna()]
    df['Maintenance Instructions'] = df['Maintenance Instructions'].apply(check_https)
    df['Installation Instructions'] = df['Installation Instructions'].apply(check_https)
    df = df[df['CODE'].notna()]
    df = df[['NAME','CODE','Installation Instructions','Maintenance Instructions']]
    df = df.astype(str)
    df.to_csv('Nikles_Instruction_Manual_cleaned.csv',index=False,encoding='utf-8-sig')


if __name__ == "__main__":
    clean('./data/maintenance_manual/Product_List_Catalogue_23[56](Foglio1).csv')
