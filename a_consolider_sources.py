import pandas as pd, unidecode, re

'''

'''

def normalize_txt(title) : 
	"""retirer les espaces, les accents, tout en minuscules, retirer les carac spéciaux"""
	cut = re.split("\W+", str(title))
	join_cut = "".join(cut).lower()
	return unidecode.unidecode(join_cut)


def conforme_df(df, col_name):
	"""garde les colonnes de col_name, les renommes et passe en miniscule doi et titre """
	#memo : on ne suppr pas colonne titre, car elle est utilisée pour le dédoublonnage
	df = df[ list(col_name.keys()) ].copy()  
	df.rename(columns = col_name, inplace = True) 

	df["doi"] = df["doi"].str.lower() # doi en minuscule
	df["title_norm"] = df["title"].apply(lambda row:  normalize_txt(row))
	return df

def extract_stats_from_base(src_name, df) : 
	"""de la base extraire les données total publi, doi only, no doi"""
	no_doi = df["doi"].isna().sum()
	w_doi = df["doi"].str.match("10.").sum()
	if no_doi + w_doi == len(df.index) : 
		print(f"\n\n{src_name} imported ok\n\tdois {w_doi}\n\tno dois {no_doi}")
		stats_buffer.append([src_name, len(df.index), w_doi, no_doi] )
	else :
		print(f"{src_name} not imported")
	


#___0___Charger les fichiers CSV_______
stats_buffer, df_buffer = [], []

# HAL 
hal = pd.read_csv("./data/hal_doi_halid_20210705.csv")
hal = conforme_df( hal, {"doiId_s": "doi", 'halId_s': 'halId', 'title_s': 'title'})
extract_stats_from_base("hal", hal)

# WOS
files = ["wos_2016a.txt" , "wos_2016b.txt", "wos_2016c.txt", "wos_2017a.txt", "wos_2017b.txt", "wos_2017c.txt", "wos_2018a.txt", "wos_2018b.txt", "wos_2018c.txt", "wos_2019a.txt", "wos_2019b.txt", "wos_2019c.txt", "wos_2020a.txt", "wos_2020b.txt", "wos_2020c.txt"]
for f in files : 
	df = pd.read_csv("./data/"+f, sep="\t", index_col=False) 
	df_buffer.append(df)
wos = pd.concat(df_buffer)
df_buffer.clear()
wos = conforme_df( wos, {"DI":"doi", "TI": "title"})
extract_stats_from_base('wos', wos)


# SCOPUS
for filename in ["scopus_2016", "scopus_2017", "scopus_2018", "scopus_2019", "scopus_2020"] : 
	df_buffer.append( pd.read_csv(f"./data/{filename}.csv", encoding = 'utf8' ))

scopus = pd.concat(df_buffer)
df_buffer.clear()
scopus = conforme_df(scopus, {"DOI" : "doi", "Title" : "title"})
extract_stats_from_base("scopus", scopus)


# PUBMED
for filename in ["pubmed_2016", "pubmed_2017" , "pubmed_2018" , "pubmed_2019-20" ] : 
	df_buffer.append( pd.read_csv(f"./data/{filename}.csv"))

pubmed = pd.concat(df_buffer)
df_buffer.clear()
pubmed = conforme_df( pubmed, {"DOI" : "doi" , "Title" : "title" })
extract_stats_from_base('pubmed', pubmed)


# LENS
lens = pd.read_csv("./data/lens_2016-20.csv")
lens = conforme_df(lens, {"DOI" : "doi", "Title" : "title"})

## retirer les listes de doi assemblé par "; "
def removeJoinDois(x): 
	doi = str(x).strip()
	if "; " in doi :
		cut = doi.split("; ")
		return cut[0]
	else : 
		return x

lens["doi"] = lens["doi"].apply(lambda x : removeJoinDois(x))

extract_stats_from_base("lens", lens)


#___1___Dedoublonner les documents_______
rawdf = pd.concat([wos, scopus, hal, pubmed, lens]) 
# trie des documents par DOI puis par halId 
rawdf.sort_values(by=['doi', 'halId'], inplace = True)
print("\n\nAvant dédoublonnage nb items", len(rawdf[ rawdf['doi'].notna()]) )

# __a Dedoublonnage sur les DOI
# retirer les docs dont le DOI est en double (et conserver les docs sans DOI)
# (dans le mask il faut que la valeur boolean soit False pour qu'elle soit retirée, d'où le ~ )
clean_doi = rawdf[ (~rawdf['doi'].duplicated()) | (rawdf['doi'].isna()) ].copy()
print('Apres dédoublonnage sur DOI, nb publi', len(clean_doi.index))


## parenthèse pour estimer l'efficacité du dédoublonnage sur titre uniquement
"""clean_doi["titre_double"] = clean_doi["title_norm"].duplicated()
clean_doi.to_csv("publication_doi_titre__verif_dedoublonnage.csv", index= False)
"""


# __b pour les sans DOI, dedoublonnage sur les titres normés
#sélectionner les documents  avec DOI, et ceux sans DOI dont les titres ne sont pas des doublons
mask = (clean_doi['doi'].notna()) | ( (clean_doi['doi'].isna()) & (~clean_doi['title_norm'].duplicated()) )
clean_doi_title = clean_doi[mask].copy()
print("Apres dédoublonnage DOI et (pour les sans DOI) sur titre , nb publi", len(clean_doi_title.index))

# __c conserver uniquement les publis  avec DOI ou idHAL
#commentaire : on pourrait retirer avant les docs sans DOI
final = clean_doi_title[ (clean_doi_title['doi'].notna()) | (clean_doi_title['halId'].notna()) ].copy()


#___2___imprimer et exporter stats 
toprint = {
"\n\ndoc total apres dedoublonnage" : len(clean_doi_title),
'docs exclus (no doi no halId) ' : len( clean_doi_title[  (clean_doi_title['doi'].isna()) & (clean_doi_title['halId'].isna()) ] ),
'doc inclus (doi ou halId)\t': len(final),

'pertinence (doi ou halId)%\t' : round(
	len(final.index)/len(clean_doi_title.index)*100, 1),

'pertinence (doi only)%\t\t' : round(
	len(final[ final['doi'].notna() ])/len(clean_doi_title)*100, 1),

'\n\ndoc à traiter avec doi': len(final[ final['doi'].notna() ]),
'doc à traiter sans doi' : len(final[ final['doi'].isna() ]),
}

[print(k, '\t\t', v) for k, v in toprint.items()]


# Extraire des statistiques pour comparer les sources
#ajout des données retenues dans les stats
stats_buffer.append([
	"retenu", 
	len(final), 
	len(final[ final['doi'].notna()]), 
	len(final[ final['doi'].isna()]) ])

stat_table = pd.DataFrame(stats_buffer, columns=['name', 'all', 'doi', 'no_doi'])
stat_table.to_csv("./data/out/step_a__statistiques_sur_les_bases.csv", index = False)

#extraire le jeu de données final
final.drop(columns=["title", "title_norm"], inplace = True)
final.to_csv("./data/out/step_a_consolidate_doi_halid.csv", index = False, encoding = 'utf8')


#______________OPTIONNEL :  extraire des tables pour enrichir et nettoyer HAL

# __a Identifier les documents HAL sans DOI et dont le titre correspond à un document avec DOI 
doionly = rawdf[(
	 rawdf['doi'].notna() & rawdf['halId'].isna() )].copy()
doionly['doi'] = doionly['doi'].str.lower()
doionly.drop_duplicates('doi', inplace = True)
del doionly['halId']

halonly = rawdf[(
	rawdf['doi'].isna() & rawdf['halId'].notna()) ].copy()
del halonly['doi']

hal_verify_doi = pd.merge(doionly, halonly, on='title_norm')
hal_verify_doi.sort_values("title_norm", inplace = True)
hal_verify_doi.drop( columns=["title_y", "title_norm"], inplace = True)
hal_verify_doi.to_csv("./data/out/step_a__hal_verif_doi_manquants.csv", index= False, encoding = 'utf8')


# __b identifier les doublons de titre sur les notices HAL sans DOI
halonly = rawdf[(
	rawdf['doi'].isna() & rawdf['halId'].notna() )].copy()
# identification des doublons de titre
halonly['duplicated'] = halonly.duplicated('title_norm', keep = False)
halonly_doubl = halonly[ halonly['duplicated']].copy()
halonly_doubl.sort_values("title", inplace = True)
halonly_doubl.drop(["doi", "title_norm", "duplicated"], axis = 1, inplace = True)

halonly_doubl.to_csv("./data/out/step_a__hal_verif_doublons_titres.csv", index= False, encoding = 'utf8')

