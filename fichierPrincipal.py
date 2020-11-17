import lireOracle

if __name__ == '__main__':
    df = lireOracle.lireConstraintes()
    print(df.head())

    print(lireOracle.lireFichierAir().head())
