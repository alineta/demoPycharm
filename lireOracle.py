
import pandas as pd

def lireFichierAir():
    return pd.read_csv('c:/Solutions/donnees/AirQualityUCI01.csv')


if __name__ == '__main__':
    print(lireFichierAir().head())
