import json, pandas as pd

df = pd.read_csv("./data/out/step_c_apc.csv", dtype=str)
print("nb de publications", len(df))
####  /!\ pd.na is used



# ______1______ Add domain metadata

# add scientific field
scifield = pd.read_csv("./data/open-access-monitor-france.csv", usecols= ["doi", "scientific_field"],  sep=";" )
df = pd.merge(df, scifield, how= "left", on = "doi")
#df['scientific_field'].fillna('unknown', inplace = True) 
print(f"nb publi sans domaine apres alignement bso {len( df[ df['scientific_field'].isna()])}")

#___OPTION_MESRI____ Pour les publications sans domaine possibilité de contacter MESRI E. Jeangirard pour y remédier
# voir https://github.com/dataesr/scientific_tagger
# df_no_domain = df[ (df["scientific_field"] == "unknown") & (pd.notna(df["doi"]))]
# print("nb doi sans domaine", len(df_no_domain))
# df_no_domain.to_csv("./data/out/TEMPstep_d_temp_doi_no_domain_pour_eric.csv", index = False)
# exit()

#___OPTION_MESRI___ integrer les DOI sans domaines traités par le MESRI
dfmesri = pd.read_csv("./data/retour_mesri_doi_avec_classification_maxence.csv")
dfmesri["doi"] = dfmesri["doi"].str.lower()
df = pd.merge(df, dfmesri, how= "left", on = "doi")
# si domaine absent chez le bso alors récupérer celui transmi par le MESRI
df["scientific_field"] = df.apply(lambda x : x["scientific_field_x"] if pd.notna(x["scientific_field_x"]) else x["scientific_field_y"], axis = 1)
df.drop(columns = ["scientific_field_x", "scientific_field_y"], inplace = True)
print(f"nb publi sans domaine apres traitement MESRI {len(df[ df['scientific_field'].isna()] )}")

df['scientific_field'].fillna('unknown', inplace = True) 


# ______2______ Deduce open access information
# deduce is_oa
def deduce_oa(row) : 
	# si fichier dans HAL et pas d'empargo alors is_oa = true
	if (row["hal_location"] == "file" and row["hal_openAccess_bool"] == "True") or \
	row["hal_location"] == "arxiv" or \
	row["hal_location"] == "pubmedcentral" or \
	row["upw_coverage"] == "oa" : 
		return True
	else : 
		return False
df["is_oa"] = df.apply(lambda row : deduce_oa(row) , axis = 1)

# deduce oa_type
def deduce_oa_type(row) : 
	loc = []
	if pd.notna( row["upw_location"] ) : 
		loc.extend( row["upw_location"].split(";") )

	# si unpaywall n'a pas trouvé de "repository" mais que c'est dans HAL : s'assurer que c'est sans embargo puis ajouter repository
	if "repository" not in loc and\
	( (row["hal_location"] == "file" and row["hal_openAccess_bool"] == "True") or
	row["hal_location"] == "arxiv" or 
	row["hal_location"] == "pubmedcentral") : 
			loc.append("repository")

	if loc : 
		loc.sort()
		return ";".join(loc)
	else : 
		return "closed"

df["oa_type"] = df.apply(lambda row : deduce_oa_type(row) , axis = 1)


# ______3______ Alignements HAL & BSO doctype & domaine

# Aligner les types de documents
def align_doctype(row) : 
	if pd.notna(row["genre"]) : 
		return row["genre"]
	# si pas de genre chez unpaywall mais présence chez HAL
	if pd.isna(row["genre"]) and pd.notna(row["hal_docType"]) : 
		if row["hal_docType"] in match_ref["docType"] : 
			return match_ref["docType"][row["hal_docType"]] 
		else : print("cannot align doctype", row["halId"])

match_ref = json.load(open("./data/match_referentials.json"))		
df["genre"] = df.apply(lambda row : align_doctype(row) , axis = 1)

# Aligner les domaines scientifiques
def align_domain(row):
	if row["scientific_field"] == "unknown" and pd.notna(row["hal_domain"]) :
		if row["hal_domain"] in match_ref["domain"] : 
			return match_ref["domain"][row["hal_domain"]]
		else : 
			print("cannot align domain", row["halId"])
	else : 
		return row["scientific_field"]

df["scientific_field"] = df.apply(lambda row : align_domain(row), axis = 1)

# ______4______ Complétion des cellules vides pour la couverture des bases
df['hal_coverage'].fillna('missing', inplace = True) 
df['upw_coverage'].fillna('missing', inplace = True) 


# output data
df.to_csv(f"./data/out/step_d_complete.csv", index = False)