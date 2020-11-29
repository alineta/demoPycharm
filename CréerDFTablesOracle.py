from LireBDOracle import BdDlisteRelations
from LireBDOracle import BdDlisteTables
from LireBDOracle import BdDlisteColonnesTables
import pandas as pd

""" _____ création des listes / Tables de la base Oracle
    - LiRelationsTables = la liste des relations 
    de la base de données avec les clés primaires pour
    chaque table de la relation
    - LiTables = liste des tables de la BdD
    - LiColTables = la liste des attributs pour chaque table
"""
def DfRelationsTables():
    LiRelTables = (BdDlisteRelations())
    return (LiRelTables)

liRel = DfRelationsTables()
#print(liRel)

def DfListeTables():
    LiTables = (BdDlisteTables())
    return (LiTables)

#liTab=DfListeTables()
#print(type (liTab))

attributTables = BdDlisteColonnesTables()

#________________aide Cyto
def getAttributTable(table):
    return attributTables[attributTables.nom_table == table].drop(columns='nom_table')

#LiColTables = (BdDlisteColonnesTables())
#print(LiColTables)

def CytoNoeudHTML (DfListe,LNoeuds):
    for i in DfListe.NomTable.unique() :
        #print(DfListe)
        LNoeuds.append({'data': {'id': i, 'label': i}})
 #       LTables.append({'label': i, 'value': i})
    #print(LNoeuds)
    return (LNoeuds)

def CytoHTML (DfListe,LNoeudsRelHTML):
    #print(DfListe)
    for index, ligne in DfListe.iterrows():
        LNoeudsRelHTML.append(
            {'data': {'source': ligne['NomTableMère'],
                      'target': ligne['NomTableFille'],
                      'relation': {'colTableMère': ligne["colTableMère"],
                                   'colTableFille': ligne["colTableFille"]}
                      },
             })
    #print(LNoeudsRelHTML)
    return (LNoeudsRelHTML)

def ListeDeroulanteTables (DfListe):
    listeTab=[]
    for i in DfListe.NomTable.unique():
        listeTab.append({'label': i, 'value': i})
    return (listeTab)

def ListeTables(DfListe):
    listeTab = []
    for i in DfListe.NomTable.unique():
        listeTab.append(i)
    return (listeTab)
    #print(LNoeuds)

def initAffichage(DfListe,nomTable):
    DfListeRel = []
    #print(DfListe)
    #print(nomTable)
    for index, ligne in DfListe[
        (DfListe['NomTableMère'] == nomTable) | (DfListe['NomTableFille'] == nomTable)].iterrows():
        DfListeRel.append({'data': {'id': ligne['NomTableMère'],
                                           'label': ligne['NomTableMère']}})
        DfListeRel.append({'data': {'id': ligne['NomTableFille'],
                                           'label': ligne['NomTableFille']}})
        DfListeRel.append({'data': {'source': ligne['NomTableMère'],
                                           'target': ligne['NomTableFille'],
                                    'relation': {'colTableMère': ligne["colTableMère"],
                                                 'colTableFille': ligne["colTableFille"]}
                                    },
                           })
    #print(DfListeRel)
    return DfListeRel



