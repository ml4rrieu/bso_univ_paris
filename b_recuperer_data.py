import requests, json, pandas as pd

def req_to_json(url):
	"""S'assuer que la réponse de l'API est en JSON"""
	found = False
	while not found :
		req = requests.get(url)
		try : 
			res = req.json()
			found = True
		except : 
			pass
	return res

def get_hal_data(doi, halId):
	""" Récupérer les métadonnées de HAL.
	Si le DOI est dans unpaywall les métadonnées de HAL communes seront écrasées """
	
	if halId : 
		query = f"halId_s:{str(halId)}"
	if not halId and doi : 
		query = "doiId_s:" + str(doi)
	if not doi and not halId : 
		print("!! problem : no doi & no halId")
		return {}
		
	res = req_to_json("https://api.archives-ouvertes.fr/search/?q="+ query+\
		"&fl=halId_s,title_s,authFullName_s,publicationDate_s,publicationDateY_i,docType_s,journalTitle_s,journalIssn_s,"\
		"journalEissn_s,journalPublisher_s,domain_s,submittedDate_s,submitType_s,linkExtId_s,openAccess_bool,licence_s,selfArchiving_bool"
		)

	# Si l'API renvoie une erreur ou bien si aucun document n'est trouvé
	if res.get("error") or res['response']['numFound'] == 0 : 
		return {
		'hal_coverage':'missing'
		}

	res = res['response']['docs'][0]
	#print(json.dumps(res, indent = 2))

	#déduire hal_location
	if res['submitType_s'] == 'file' : 
		hal_location = 'file' # primauté sur les fichiers de HAL comparé a Arxiv ou pubmed
	elif res['submitType_s'] == 'notice' and (res.get('linkExtId_s') == 'arxiv' or res.get('linkExtId_s') == 'pubmedcentral') : 
		hal_location = res['linkExtId_s']
	else : 
		hal_location = 'notice'

	#déduire les ISSNs
	issn = [ res.get("journalIssn_s"), res.get("journalEissn_s")]
	issn = [item for item in issn if item]
	issn = ",".join(issn) if issn else False

	# Vérifier la présence de domaine disciplinaire (qq notices peuvent ne pas avoir de domaine)
	domain = False
	if res.get('domain_s') : 
		domain = res["domain_s"][0]

	authCount = False
	if res.get("authFullName_s") : 
		authCount = len(res['authFullName_s'])
	
	return{
	#métadonnées partagées avec unpaywall
	'title': res['title_s'][0],
	'author_count': authCount,
	'published_date': res.get('publicationDate_s'),
	'published_year': res.get('publicationDateY_i'),
	'journal_name': res.get('journalTitle_s'),
	'journal_issns': issn,
	'publisher': res.get('journalPublisher_s'),
	#métadonnées propres à HAL
	'halId': res.get('halId_s'),
	'hal_coverage' : 'in',
	'hal_submittedDate' : res.get('submittedDate_s'),
	'hal_location' : hal_location, 
	'hal_openAccess_bool' : res.get("openAccess_bool"),
	'hal_licence': res.get('licence_s'),
	'hal_selfArchiving' : res.get("selfArchiving_bool"),
	'hal_docType': res.get('docType_s'),
	'hal_domain': domain,
	}
	


def get_upw_data(doi):
	"""Récupérer les métadonnées de Unpaywall """
	## 2021-07-16 inclure/encoder # dans caractère
	# exemple "10.1002/(sici)1521-3951(199911)216:1<135::aid-pssb135>3.0.co;2-#"
	"""
	doi.replace("#", "%23")
	doi.replace(";", "%3B")
	doi.replace(",", "%2C")
	"""

	res = req_to_json(f"https://api.unpaywall.org/v2/{doi}?email=m@larri.eu")
	
	# déduire upw_coverage
	if res.get("message") and "isn't in Unpaywall" in res.get("message") : 
		upw_coverage = "missing"
	elif res.get("is_oa") :
		upw_coverage = "oa"
	else : 
		upw_coverage = "closed"

	# facultif : déduire nombre auteurs 
	author_count = len(res['z_authors']) if res.get('z_authors') else False

	# déduire upw_location
	location = licence = version = None
	if res.get('oa_locations') : 

		oa_loc = res.get('oa_locations')
		location = list(set(
			[loc["host_type"] for loc in oa_loc]))
		location = ";".join(location) 
		
		licence = list(set(
			[loc["license"] for loc in oa_loc if loc["license"] ]))
		licence = ";".join(licence) if licence else None
		
		version = list(set(
			[loc["version"] for loc in oa_loc if loc["version"] ]))
		version = ";".join(version) if version else None

	return {
	# métadonnées partagées avec HAL
	"title": res.get("title"), 
	"author_count": author_count,
	"published_date": res.get("published_date"),
	"published_year": res.get("year"),
	"journal_name": res.get("journal_name"),
	"journal_issns": res.get("journal_issns"),
	"publisher": res.get("publisher"),
	# métadonnées propres à unpaywall
	"genre": res.get("genre"),
	"journal_is_in_doaj": res.get("journal_is_in_doaj"),
	"upw_coverage": upw_coverage,
	"is_paratext": res.get("is_paratext"),
	"journal_issn_l": res.get("journal_issn_l"),
	"journal_is_oa": res.get("journal_is_oa"),
	"oa_status" : res.get("oa_status"),
	"upw_location": location, 
	"licence": licence, 
	"version": version
	}



def enrich_df(df, buffer_file, count):
	"""pour chaque publications lancer les requêtes et ajouter les métadonnées"""

	#trouver le dernier index ayant été traité
	lastIdx = df.apply(pd.Series.last_valid_index)
	lastIdxVal = lastIdx.get("hal_coverage")
	print("last index w value", lastIdxVal, '\n\n')

	nb = 0 
	for row in df.itertuples():

		if lastIdxVal and row.Index <= lastIdxVal : 
			continue
		
		print(row.Index)

		# __a define steps for progressions
		# for each step output data and print progression 
		if row.Index > 0 and row.Index % int(len(df)/1000) == 0 :  # le denominateur impact l'intervalle des étapes : 100 une étape tout les 1% etc.
			# output a snapshot
			df.to_csv("./data/out/"+buffer_file, index = False)
			print( round(row.Index / len(df) * 100, 1), "%")
		
		# __b get HAL medatadata
		md = get_hal_data(row.doi, row.halId)
	
		# __c if DOI then get data from Unpaywall
		# (Les métadonnées de HAL communes avec unpaywall seront écrasées)
		if row.doi  : 
			add = get_upw_data(row.doi)
			# ajout des métadonnées qui ne sont pas False
			md.update( (k, v) for k, v in add.items() if v ) 

		#__d add metadata (md) to df
		for field in md : 
			df.loc[row.Index, field] = md[field]
		
		nb+=1
		if nb  > count : break
	return df



# ______0______ Charger les données

## charger DOI & halId des publications
df_first = pd.read_csv("./data/out/step_a_consolidate_doi_halid.csv", converters={'doi' : str}, na_filter= False, encoding='utf8')

print("nb of publis to treat", len(df_first))

## charger ce qui a déjà été traité
buffer = "step_b__buffer.csv"

try : 
	df_treated = pd.read_csv("./data/out/"+buffer, converters={'doi' : str, "author_count" : str}, na_filter= False, encoding='utf8')
	# author_count type to remove a pandas error from read_csv
except : 
	df_treated = pd.DataFrame()

#fusionner les deux df
if not df_treated.empty :
	# reduire la df à ce qui a été traité en excluant les publis sans DOI  (= hal_coverage & doi )
	df_treated_val_only = df_treated[ (df_treated["hal_coverage"] != "") & (df_treated["doi"] != "") ].copy()
	print("nb publis already treated", len(df_treated_val_only) )
	df = pd.merge(df_first, df_treated_val_only, how = "left", on="doi")
	#reconstruct halId column
	df.rename(columns={"halId_x" : "halId"}, inplace = True)
	df["halId"] = df.apply(lambda row: row['halId_y'] if pd.notna(row['halId_y']) else row['halId'], axis=1) # récupérer le halId du buffer s'il n'est pas vide
	df["halId"].fillna("", inplace = True) # /!\ logique de String vide dans ce code : on remplace les na
	df.drop(columns=["halId_y"], inplace = True)
	df.sort_values(by = ["hal_coverage"], ascending=True, inplace = True)
	df.reset_index(drop=True, inplace=True)
	print("taille de la df apres fusion", len(df))
	
else : 
	df = df_first


# ______1______ Ajouter métadonnées bibliographiques : HAL & Unpaywall

df = enrich_df(df, buffer, 100000)  #df principal, buffer_file_name, nb of line to treat

df.to_csv(f"./data/out/{buffer}", index = False)

df_reorder = df[["doi", "halId", "hal_coverage", "upw_coverage", "title", "hal_docType", "hal_location", "hal_openAccess_bool", "hal_submittedDate", "hal_licence", "hal_selfArchiving", "hal_domain", "published_date", "published_year", "journal_name", "journal_issns", "publisher", "genre", "journal_issn_l", "oa_status", "upw_location", "version", "suspicious_journal", "licence", "journal_is_in_doaj", "journal_is_oa", "author_count", "is_paratext" ]]
df_reorder.to_csv(f"./data/out/step_b_biblio_md.csv", index = False)


