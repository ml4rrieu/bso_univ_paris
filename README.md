# Baromètre Science Ouverte Université de Paris

_2021-08-01 : en construction_

Le Baromètre de la science ouverte d'Université de Paris se base sur celui réalisé par l'université de la Lorraine en 2020 (voir code sur [Gitlab](https://gitlab.com/Cthulhus_Queen/barometre_scienceouverte_universitedelorraine/-/tree/master)). Deux éléments clés ont été ajoutés : la prise en compte des publications dans HAL sans DOI et une heuristique pour estimer la présence de frais de publications (Article Processing Charges : APC). 

<!-- ([Présentation du baromètre sur le portail science ouverte de l'université u-paris.fr/science-ouverte](https://u-paris.fr/science-ouverte/barometre/)
-->

* [Sur l'intégration des publications de HAL sans DOI](#Sur-lintégration-des-publications-sans-doi)

* [Sur la détection des frais de publications(APC)](#Sur-la-détection-des-APC)

* [Schéma de données](#schéma-de-données) -- [Télécharger les données](/data/out/step_d_complete.csv)  


<br />
<br />
<br />


## Sur l'intégration des publications sans DOI

La prise en compte des publications dans HAL sans DOI _baisse_ de quelques pourcentages (1-5 %) le taux d'accès ouvert. Voir le graphique "Comparaison des taux d'accès ouvert en incluant ou non les publications sans DOI" [à venir].


## Sur la détection des APC

L'heuristique sur les APC permet de savoir si une publication a recquis des frais de publications. Attention, une publication ayant nécessité des APC ne signifie pas qu'ils ont été payés par l'université de Paris : l'heuristique est indifférente à l'établissement payeur. Cette détection petmet d'obtenir deux graphiques : l'un sur [l'évolution de la quantité de publication avec APC](./apc_evol.png), l'autre sur [la quantité de publications avec APC par disciplines](./apc_disciplines.png). La méthode utilisée pour la détection des APC est décrite dans le [baromètre 2020 de l'UVSQ ](https://github.com/ml4rrieu/barometre_science_ouverte_uvsq#pister-les-apc)


## Notes de réalisation

```
2021-05/6  : définition du périmètre
2021-07-05 : récupérer données HAL, Scopus
2021-07-13 : récupérer données Wos, Pubmed, Lens
2021-07-15 : métadonnées biblio récupérées
2021-07-16 : métadonnées APC déduites (compter 2h)
2021-07-23 : envoi au MENESR des DOI sans domaines
2021-07-24 : doc dans HAL avec fichier sous embargo non marqué OA
2021-08-17 : génération des graphiques
2021-08-24 : intégration des données du MENESR pour les DOI sans publications
2021-08-25 : réalisation dépôt github


Statistiques - step_a 2021-07-24
-------------------------
Avant dédoublonnage 		 			187_499
Apres dédoublonnage sur DOI			 	94_102
Apres dédoublonnage DOI et (pour les sans DOI) sur titre 89_746
doc total apres dedoublonnage 		 	89_746
docs exclus (no doi no halId)  		 	69_87
doc inclus (doi ou halId)	 		 	82_759
pertinence (doi ou halId)%	 		 	92.2
pertinence (doi only)%		 		 	81.2


doc à traiter avec doi 		 72868
doc à traiter sans doi 		 9891


```



## Améliorations effectuées

- `b_recuperer_data.py` la récupération des métadonnées dans HAL et Unpaywall se fait à l'aide d'un chariot permettant d'arrêter le processus sans perdre les métadonnées (nécessaire en cas d'erreur chez une API)

- `d_aligner_data.py` ajout de l'option d'enrichissement des domaines via le MESRI

- `d_aligner_data.py` un fichier dans HAL mais sous embargo n'est plus considéré comme de l'accès ouvert (métadonnée HAL `openAccess_bool`)


## Schéma de données

| column             | description (if needed)                                                                       | source                   |
|--------------------|-----------------------------------------------------------------------------------------------|--------------------------|
| doi                |                                                                                               |                          |
| halId              | Publication deposit id in HAL                                                                 | hal                      |
| hal_coverage       | Hal coverage (in or missing )                                                                 | hal                      |
| upw_coverage       | Unpaywall coverage (oa, missing, closed)                                                      | unpaywall                |
| title              |                                                                                               | hal or unpaywall         |
| hal_docType        | Type of document                                                                              | hal                      |
| hal_location       | Where OA is founded (file, arxiv, pubmedcentral), notice if not OA                            | hal                      |
| hal_openAccess_bool| is the document in Open Access									                             | hal                      |
| hal_submittedDate  | When the publication has been submitted in HAL                                                | hal                      |
| hal_licence        | Licence in HAL deposit                                                                        | hal                      |
| hal_selfArchiving  | Curiosity : is the deposit made by the author                                                 | hal                      |
| hal_domain         | Domain, scientific field                                                                      | hal                      |
| published_date     |                                                                                               | hal or unpaywall         |
| published_year     |                                                                                               | hal or unpaywall         |
| journal_name       |                                                                                               | hal or unpaywall         |
| journal_issns      |                                                                                               | hal or unpaywall         |
| publisher          |                                                                                               | hal or unpaywall         |
| genre              | document type                                                                                 | hal or unpaywall         |
| oa_status          | Status/type of open access (green, gold, hybrid, bronze)                                      | unpaywall                |
| upw_location       | Where OA is founded (repository and/or publisher)                                             | unpaywall                |
| version            | Publication version available (submitted, accepted, published)                                | unpaywall                |
| suspicious_journal | Is the journal in "predatory" list                                                            | [Stop Predatory Journals](https://github.com/stop-predatory-journals/stop-predatory-journals.github.io)|
| licence            | licence finded in unpaywall                                                                   | unpaywall                |
| journal_is_in_doaj | Is this resource published in a DOAJ-indexed journal                                          | unpaywall                |
| journal_is_oa      | Is this resource published in a completely OA journal                                         | unpaywall                |
| author_count       | Curiosity : number of authors                                                                 | hal or unpaywall         |
| is_paratext        | Is the item an ancillary part of a journal (column disappear if everything is False )         | unpaywall                |
| apc_tracking       | APC information (doi_in_openapc, journal_in_openapc, journal_is_hybrid, apc_journals_in_doaj) | openapc, doaj, unpaywall |
| apc_amount         | Rough approximation of APC cost                                                               | openapc, doaj            |
| apc_currency       |                                                                                               | openapc, doaj            |
| scientific_field   | Scientific field from barometre-science-ouverte and hal                                       | barometre-so, hal        |
| is_oa              | Is there an OA copy of this ressource                                                         | hal, unpaywall           |
| oa_type            | Publisher and/or repository                                                                   | hal, unpaywall           |