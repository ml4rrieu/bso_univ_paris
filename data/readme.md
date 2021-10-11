### Dans ce dossier ajouter :

* les données bibliographiques de votre institution : WOS, Scopus, LENS etc.

* le jeu de données du Baromètre Français de la science ouverte 

https://data.enseignementsup-recherche.gouv.fr/explore/dataset/open-access-monitor-france/

* les ISSNs des journaux suspects

https://github.com/ml4rrieu/open_science_tools/blob/main/questionnable_journals/suspiciousIssns.json


* Un dossier `APC_tracking` contenant 


	* `openapc_dois.csv`, les DOIs de OpenAPC à récupérer en ligne

	https://github.com/OpenAPC/openapc-de/blob/master/data/apc_de.csv


	* `doaj_apc_journals.csv`, les APC signalés dans le DOAJ

	https://doaj.org/docs/public-data-dump/


	* `openapc_journals.csv`, les APC des journaux présents dans OpenAPC

	https://github.com/ml4rrieu/open_science_tools/blob/main/apc_journal_tables/openapc_journals.csv



<br /><br />

### Mémo Requêtes utilisées

Périmètre : les publications affiliées directement à Université de Paris et les publications affiliées à une unité de recherche dont Université de Paris est (co)tutelle. 


<br />

**Scopus**

Pour les unités de recherche de l'ancien contrat quinquénnal une tolérance de `année_cloture + 2` a été effectuée, pour répondre à l'inertie du processus de publication

limite du service : 2k depuis l'interface, 20k par email

`
AF-ID("Université de Paris" 60123796) OR AF-ID("Institut de Physique du Globe de Paris" 60001970) OR AF-ID("Pathologie Imagerie et Biothérapies Orofaciales" 60123803) OR AF-ID("Pharmacologie et Évaluation des Thérapeutiques chez L'enfant et la Femme Enceinte" 60210102) OR AF-ID("Physiopathologie &amp; Pharmacotoxicologie Placentaire Humaine / Microbiote Pré &amp; Postnatal" 60210103) OR AF-ID("Bioingénierie et Biomécanique Ostéo-Articulaire" 60106699) OR AF-ID("Biologie Anthropologie, Biométrie, Epigénétique, et Lignées" 60210187) OR AF-ID("Biologie de l'os et du Cartilage : Régulations et Ciblage Thérapeutique" 60210145) OR AF-ID("Cibles Thérapeutiques et Conception de Médicaments" 60210142) OR AF-ID("Centre de Recherche des Cordeliers" 60026040) OR AF-ID("Centre de Recherche Epidémiologiques et Bio Statistiques de Sorbonne Paris Cité CRESS" 60112042) OR AF-ID("Centre de Recherche sur l’Inflammation CRI" 60123678) OR AF-ID("Epidémiologie Clinique et Evaluation Economique Appliquées aux Populations Vulnérables" 60123713) OR AF-ID("Génomes Biologie Cellulaire et Thérapeutique" 60210107) OR AF-ID("Infection Anti-Microbien, Modélisation, Évolution" 60123665) OR AF-ID("Institut Cochin" 60031594) OR AF-ID("l'Institut des Maladies Génétiques Imagine" 60123804) OR AF-ID("Institut Necker-Enfants Malades INEM" 60123784) OR AF-ID("Institut de Psychiatrie et Neurosciences de Paris IPNP" 60123816) OR AF-ID("Innovations Thérapeutiques en Hémostase" 60210101) OR AF-ID("Laboratory for Vascular Translational Science" 60123697) OR AF-ID("Biomarqueurs CArdioNeuroVASCulaires" 60123677) OR AF-ID("Mère et Enfant en Milieu Tropical : Pathogènes Système de Santé et Transition Epidémiologique" 60210185) OR AF-ID("Optimisation Thérapeutique en Neuropsychopharmacologie" 60210109) OR AF-ID("PARCC - Paris-Centre de Recherche Cardiovasculaire" 60136279) OR AF-ID("Physiopathologie et Epidémiologie des Maladies Respiratoires" 60210100) OR AF-ID("Prévention et Traitement de la Perte Protéique Musculaire en Situation de Résistance à l’Anabolisme" 60210108) OR AF-ID("Unité de Recherches Biomatériaux Innovants et Interfaces - URB2i" 60210169) OR AF-ID("Unité de Technologies Chimiques et Biologiques pour la Santé" 60105728) OR AF-ID("Vigilance Fatigue Sommeil et Santé Publique" 60210154) OR AF-ID("Astrophysique Instrumentation et Modélisation de Paris-Saclay" 60106184) OR AF-ID("APC - AstroParticule et Cosmologie" 60105477) OR AF-ID("Unité de Biologie Fonctionnelle et Adaptative BFA" 60123679) OR AF-ID("Biologie Intégrée du Globule Rouge" 60123680) OR AF-ID("Centre de Nanosciences et de Nanotechnologies" 60109179) OR AF-ID("Centre Borelli" 60180341) OR AF-ID("Éco-anthropologie" 60123773) OR AF-ID("Epigénétique et Destin Cellulaire" 60210112) OR AF-ID("Expression Génétique Microbienne" 60210114) OR AF-ID("Epidémiologie et Physiopathologie des Virus Oncogènes" 60123709) OR AF-ID("Génétique Humaine et Fonctions Cognitives" 60123712) OR AF-ID("Génétique Moléculaire des Virus à ARN" 60123710) OR AF-ID("Institut d'Ecologie et des Sciences de l'Environnement de Paris IEES Paris" 60112048) OR AF-ID("Imagerie et Modélisation en Neurobiologie et Cancérologie" 60106119) OR AF-ID("Institut Jacques Monod" 60005370) OR AF-ID("Institut Langevin" 60105746) OR AF-ID("Institut de Mathématiques de Jussieu-Paris Rive Gauche" 60004833) OR AF-ID("Integrative Neuroscience and Cognition Center" 60210214) OR AF-ID("Institut des Sciences des Plantes de Paris-Saclay" 60106138) OR AF-ID("Institut de Recherche en Informatique Fondamentale IRIF" 60123660) OR AF-ID("Interfaces Traitements Organisation et DYnamique des Systèmes – ITODYS" 60123640) OR AF-ID("Laboratoire de Biologie Physico-Chimique des Protéines Membranaires" 60210110) OR AF-ID("Laboratoire de Biochimie Théorique" 60210113) OR AF-ID("Laboratoire de Chimie et de Biochimie Pharmacologiques et Toxicologiques LCBPT" 60123672) OR AF-ID("LDAR - Laboratoire de Didactique André Revuz" 60123663) OR AF-ID("Laboratoire d'Electrochimie MoléculaireLEM" 60123666) OR AF-ID("LESIA - Laboratoire d'Etudes Spatiales et d'Instrumentation en Astrophysique" 60028894) OR AF-ID("Laboratoire Interdisciplinaire des Energies de Demain - LIED" 60123652) OR AF-ID("Laboratoire Interuniversitaire des Systèmes Atmosphériques LISA - UMR 7583" 60122451) OR AF-ID("Laboratoire Jacques-Louis Lions" 60072945) OR AF-ID("Laboratoire de Physique de l’Ecole Normale Supérieure" 60210266) OR AF-ID("Laboratoire de Physique Nucléaire et de Hautes Energies" 60157983) OR AF-ID("Laboratoire de Probabilités Statistique et Modélisation" 60111003) OR AF-ID("LUTH - Laboratoire de l'Univers et de ses Theories" 60003174) OR AF-ID("Mathématiques Appliquées à Paris 5" 60210111) OR AF-ID("Laboratoire Matériaux et Phénomènes Quantiques" 60123671) OR AF-ID("Laboratoire Matière et Systèmes Complexes" 60123695) OR AF-ID("Pathogenèse des Bactéries Anaérobies" 60123705) OR AF-ID("Laboratoire de Physique et Mécanique des Milieux Hétérogènes" 60072969) OR AF-ID("Stabilité Génétique Cellules Souches et Radiation" 60106185) OR AF-ID("Institut des Neurosciences Paris Saint-Pères" 60210186) OR AF-ID("Environmental Toxicity Therapeutic Targets, Cellular Signaling And Biomarkers" 60210184) OR AF-ID("Anthropologie et Histoire des Mondes Antiques" 60120303) OR AF-ID("CCJ Chine Corée Japon" 60123643) OR AF-ID("Centre de Droit des Affaires et de Gestion" 60210180) OR AF-ID("Centre Population et Développement" 60123161) OR AF-ID("Centre d’Études et de Recherches Interdisciplinaires de l’UFR Lettres Arts, Cinéma" 60136261) OR AF-ID("CERLIS - Centre de Recherche sur les Liens Sociaux - UMR 8070" 60117541) OR AF-ID("Centre de Recherche Médecine, Sciences, Santé, Santé Mentale, Société" 60106086) OR AF-ID("CESSMA - Centre d'Etudes en Sciences Sociales sur les Mondes Africains Américains et Asiatiques" 60119214) OR AF-ID("Centre de Recherche sur les Civilisations de l’Asie Orientale CRCAO" 60123637) OR AF-ID("CRPMS Centre de Recherches Psychanalyse Médecine et Société" 60123696) OR AF-ID("Laboratoire EDA" 60210118) OR AF-ID("Géographie-Cités Lab" 60123629) OR AF-ID("Laboratoire d'Histoire des Théories Linguistiques" 60123670) OR AF-ID("Institut des Sciences du Sport Santé de Paris I3SP" 60126107) OR AF-ID("Identités Cultures Territoires" 60123675) OR AF-ID("Institut Droit et Santé" 60210117) OR AF-ID("Institut Français de Recherche sur l’Asie de l’Est" 60210182) OR AF-ID("Laboratoire Dynamiques Sociales et Recomposition des Espaces LADYSS" 60123642) OR AF-ID("Laboratoire de Psychologie et d’Ergonomie Appliquées" 60210166) OR AF-ID("Laboratoire de Psychologie du Développement et de l'Éducation de l'Enfant" 60210148) OR AF-ID("Laboratoire de Recherche sur les Cultures Anglophones" 60210170) OR AF-ID("Laboratoire du Changement Social et Politique" 60123662) OR AF-ID("Laboratoire Interdisciplinaire de Recherche Appliquée en Economie de la Santé LIRAES" 60210181) OR AF-ID("Laboratoire de Linguistique Formelle" 60123653) OR AF-ID("Laboratoire de Psychopathologie et Processus de Santé" 60210168) OR AF-ID("Laboratoire de Psychologie Sociale LPS" 60210171) OR AF-ID("Laboratoire de Psychologie Clinique Psychopathologie, Psychanalyse PCPP" 60210144) OR AF-ID("Pôle de Recherche Pour l'Organisation et la Diffusion de l'Information Géographique" 60110966) OR AF-ID("Sciences Philosophie, Histoire – UMR 7219, Laboratoire SPHERE" 60198731) OR AF-ID("Unité de Recherches Migrations et Société" 60110705) OR AF-ID("Laboratoire Vision Action Cognition" 60210157) OR AF-ID("Santé Mentale et Santé Publique" 60106307) OR AF-ID("GEPI - Galaxies Etoiles, Physique, Instrumentation" 60031186) OR AF-ID("Chimie Biologique des Membranes et Ciblage Thérapeutique" 60105763) OR AF-ID("CART Carcinose Angiogenèse et Recherche Translationnelle" 60123701) OR AF-ID("Variabilité Génétique et Maladies Humaines" 60210188) OR AF-ID("Génomique Fonctionnelle des Tumeurs Solides" 60210106) OR AF-ID("Service de Recherches en Hémato-Immunologie" 60106259) OR AF-ID("Génétique et Physiopathologie des Maladies Cérébro-Vasculaires" 60210167) OR AF-ID("Recherche Clinique Ville-Hôpital Méthodologies et Sociétés REMES" 60123711) OR AF-ID("Epidémiologie Environnementale : Impact Sanitaire des Pollutions" 60123632) AND PUBYEAR > 2015 AND PUBYEAR < 2021 
`

<br />

**WOS**

limite du service : 5k depuis l'interface 

_attention à la maj de 2021 où l'option 5k n'est plus disponible_ [tweet 2021-07-13](https://twitter.com/ml4rrieu/status/1414933875030122503)


`
OG = (universite de paris)  NOT (OG = (universite de paris) AND AD = (CHU OR HOSP* OR APHP OR HOP*) NOT AD=(UNIV* OR DESCARTES OR DIDEROT OR U*1138 OR U*1153 OR U*1149 OR U*1160 OR U*7212 OR U*976 OR U*1137 OR U*8104 OR U*1016 OR U*1163 OR U*8253 OR U*1151 OR U*1266 OR U*1148 OR U*942 OR U*1141 OR U*1144 OR U*970 OR U*1152 OR U*1178 OR U*965))
`


<br />

**HAL**

limites : 10k par pages

Utiliser la  pagination [voir doc](https://api.archives-ouvertes.fr/docs/search/?#paging) pour extraire davantage

`https://api.archives-ouvertes.fr/search?&q=collCode_s:UNIV-PARIS&fq=publicationDateY_i:[2016 TO 2020]&fq=( (docType_s:(ART OR COMM) AND popularLevel_s:0 AND peerReviewing_s:1) OR (docType_s:(OUV OR COUV OR DOUV) AND popularLevel_s:0) OR (docType_s:UNDEFINED))&fl=doiId_s,title_s,halId_s&sort=doiId_s asc&rows=10000`

ART et COMM : exclure la vulgarisation et uniquement si peer review

OUV, COUV, DOUV : si ce n'est pas de la vulgarisation

UNDEFINIED (inclusion des preprints !)

<br />

**Pubmed**

`(("paris diderot"[Affiliation]) OR ("paris descartes"[Affiliation])) AND (("2016/01/01"[Date - Publication] : "2020/12/31"[Date - Publication]))
`

<br />

**LENS**

`
Year Published = ( 2016 - 2020 ) Publication Type = ( excl dissertation , excl report , excl unknown ) Institution Name = ( Paris Descartes University , Paris Diderot University ) 
	 retrait de "university of paris" car cela double le résultat : fonctionnement incertain
`