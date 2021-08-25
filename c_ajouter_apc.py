import json, pandas as pd


def track_apc(doi, row) :
	"""Heuristique sur les APC""" 
	
	#__a Vérifier si le DOI est dans openapc
	if doi and openapc_dois["doi"].str.contains(doi, regex = False).any() :
		try : 
			apc_amount = openapc_dois.loc[ openapc_dois["doi"] == doi, "apc_amount_euros"].item()
		except : 
			apc_amount = "unknow"
		return{
		"apc_tracking" : "doi_in_openapc",
		"apc_amount" :  apc_amount,
		"apc_currency" : "EUR"
		}

	# Si le document n'a pas d'ISSN ne rien remplir
	if not row.journal_issns : 
		return {}
	
	#récupérer les différents issn
	issns = row.journal_issns.split(",")
	if row.journal_issn_l :
		issns.append(row.journal_issn_l)

	#__b si un ISSN est dans openapc et que des APC ont été payés la même année
	cols = ["issn", "issn_print", "issn_electronic", "issn_l"]
	openapc_mean = False
	if row.published_year and int(row.published_year) > 2014 and int(row.published_year) < 2021 : 
		for item in issns : 
			for col in cols : 
				if openapc_journals[col].str.contains(item).any() :
					openapc_mean = openapc_journals.loc[ openapc_journals[col] == item, str(int(row.published_year))].item()
					break

	if openapc_mean :
		return{
		"apc_tracking" : "journal_in_openapc",
		"apc_amount" :  openapc_mean,
		"apc_currency" : "EUR"
		}


	#__c si le type d'accès ouvert du document dans unpaywall est hybride
	if row.oa_status == "hybrid": 
		return { "apc_tracking" : "journal_is_hybrid"}

	
	#__d si le journal est dans le DOAJ extraire les données d' APC du DOAJ
	cols = ["Journal ISSN (print version)",	"Journal EISSN (online version)"] 
	for item in issns : 
		for col in cols : 
			if doaj_apc_journals[col].str.contains(item).any() : 
				return {
				"apc_tracking" : "apc_journals_in_doaj",
				"apc_amount" :  doaj_apc_journals.loc[ doaj_apc_journals[col] == item, "APC amount" ].item(),
				"apc_currency" : doaj_apc_journals.loc[ doaj_apc_journals[col] == item, "APC currency" ].item()
				}
	#__si aucun cas ne s'est présenté ne rien remplir
	return {}


def check_suspicious_j(row) :
	"""Vérifier si le journal est dans la liste de ceux suspects"""
	if not row.journal_issns :
		return {}

	is_suspicious = False
	issns = row.journal_issns.split(";")
	for item in issns : 
		if item in suspiciousIssns["print"] or item in suspiciousIssns["electronic"] : 
			is_suspicious = True
	
	return {"suspicious_journal" : is_suspicious }



# ______0______ load data

## Pour l'heuristique des APC
openapc_dois = pd.read_csv("./data/apc_tracking/openapc_dois.csv", na_filter= False)
openapc_journals = pd.read_csv("./data/apc_tracking/openapc_journals.csv", na_filter= False)
doaj_apc_journals = pd.read_csv("./data/apc_tracking/doaj_apc_journals.csv", na_filter= False)
fhjson = open('./data/suspiciousIssns.json') 
suspiciousIssns = json.load(fhjson)


df = pd.read_csv("./data/out/step_b_biblio_md.csv", converters={'doi' : str}, na_filter= False )

# ______1______ clean published_year data to int
def clean_pub_year(x) : 
	if x : 
		return int(float(x))
df["published_year"] = df["published_year"].apply(lambda x : clean_pub_year(x))
df["published_year"].fillna("", inplace = True)


# ______2______ add APC and suspicious data
for row in df.itertuples() : 

	# __a deduce APC
	md = track_apc(row.doi, row)

	# __b deduce suspect journal
	md.update(check_suspicious_j(row))

	#__e add metadata to df
	for field in md : 
		df.loc[row.Index, field] = md[field]

df.to_csv("./data/out/step_c_apc.csv", index = False)






