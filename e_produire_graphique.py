import pandas as pd, matplotlib, matplotlib.pyplot  as plt
import numpy as np, math


"""
  circulaire : bilan open access sur une année
  oa_evol : evolution taux open access par an et type oa
  oa_discipline : type d'accès ouvert par discipline
  oa_editeur : type d'accès ouvert par éditeurs
  publication_discipline : n
  doctype_discipline : doctype par discipline
  doctype_evol : doctype évolution par années

  evol types d'accès ouvert green to diamond 
"""


df_raw = pd.read_csv("./data/out/step_d_complete.csv", dtype={"published_year":"string"}, na_filter=False, low_memory=False)

# filtre : retrait des documents de paratexte
df = df_raw[df_raw["is_paratext"] == ""]
# rmq:  des publications ne sont pas dans la fourchette souhaitée [2016-2020]

# les noms des graphiques possibles : 
# circulaire // oa_evol // oa_discipline // oa_editeur // 
# comparaison_bases // apc_evol // apc_discipline // bibliodiversity
# publication_discipline // doctype_evol
# hal_evol // hal_discipline
graph = "hal_discipline" 


#====================hal_discipline=======================================
def deduce_hal_presence(row) :
    """deduction du type de présence dans HAL : autoarchive, fichier non déposé par l'auteur, notice etc. """
    if row["hal_location"] == "file" and row["hal_selfArchiving"] == "True" : 
        return "hal_file_auto"

    if row["hal_location"] == "file" and row["hal_selfArchiving"] == "False" : 
        return "hal_file_no_auto"

    if (row["hal_coverage"] == "in" and row["hal_location"] != "file") and row["is_oa"] : 
        return "hal_notice_oa"

    if (row["hal_coverage"] == "in" and row["hal_location"] != "file") and not row["is_oa"] :
        return "hal_notice_not_oa"

    if row["hal_coverage"] == "missing" : 
        return "not_in_hal"


if graph == "hal_discipline" :
    print("graphique hal disicpline\n\n")
    oneyear_pub = df.loc[df['published_year'] == "2020.0",:]

    print("2020 nb of publi", len(oneyear_pub))
    
    # genere une SettingWithCopyWarning why  ? 
    oneyear_pub["hal_presence"] = oneyear_pub.apply(lambda row : deduce_hal_presence(row), axis = 1)

    print(oneyear_pub["hal_presence"].value_counts())

    df_hal_field = pd.crosstab([oneyear_pub['scientific_field']] , oneyear_pub['hal_presence'])
    # rearengement des colonnes
    df_hal_field = df_hal_field[["hal_file_auto", "hal_file_no_auto", "hal_notice_oa", "hal_notice_not_oa", "not_in_hal"]]
    df_hal_field = (df_hal_field.T / df_hal_field.T.sum()).mul(100).round(1)
    df_hal_field = df_hal_field.T

    df_hal_field.sort_index( ascending = False, inplace = True)

    #import matplotlib.ticker as mtick
    ax = df_hal_field.plot(kind="barh", stacked=True, figsize=(14, 10),
        color=['#7e96c4','#8ba6e9','#bed0f4','#e5eaf3', '#f4f6fa']) 

    ## _______ configurer l'afichage
    # remove axis
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    # remove xticks
    plt.tick_params(
        axis = 'x',          # changes apply to the x-axis
        which = 'both',      # both major and minor ticks are affected
        bottom = False,      # ticks along the bottom edge are off
        labelbottom = False) # labels along the bottom edge are off

    labels = []
    for j in df_hal_field.columns:
        for i in df_hal_field.index:
            label = df_hal_field.loc[i][j]
            if type(label) != str : 
                #pour un meilleur affichage : si ce n'est pas la discipline on arrondi 
                label = str(round(label))
                label += " %"     #:label.find(".")
                #if j != "not_in_hal" : # on ne met pas de label pour les "not_int_hal"
                labels.append(label)

    patches = ax.patches
    for label, rect in zip(labels, patches):
        width = rect.get_width()
        if width > 0 :
            x = rect.get_x()
            y = rect.get_y()
            height = rect.get_height()
            ax.text(x + width/2., y + height/2., label, ha='center', va='center', fontsize=9)

    plt.tick_params(axis = 'both', labelsize = 13)
    plt.ylabel(None, fontsize = 15)
    
    """
    plt.legend(
    ["Dans HAL avec fichier déposé par l'auteur", "Dans HAL avec fichier non déposé par l'auteur", "Dans HAL avec accès ouvert à l'extérieur", 'Dans HAL sans accès ouvert'],
                loc = 'upper right', ncol = 1,
                markerscale = 1, title = None, fontsize = 11,
                borderpad = 0.3, labelspacing = 0.3, framealpha= True, bbox_to_anchor=(1, 0.95))
    """
    plt.legend(
    ["Dans HAL avec texte intégral (déposé par l'auteur)", "Dans HAL avec texte intégral (non déposé par l'auteur)", "Dans HAL avec texte intégral en hyperlien",
     'Dans HAL sans texte intégral', 'Non présent dans HAL'],
                loc = 'upper center', ncol = 2, frameon=False,
                markerscale = 1, title = None, fontsize = 11,
                borderpad = 0.3, labelspacing = 0.3, framealpha= True , bbox_to_anchor=(0.4, 1.09))
    
    #plt.title("Types de présence dans HAL des publications de 2020 par discipline", fontsize = 22, x = 0.49, y = 1.03,  alpha = 0.6)
    plt.title("Types de présence dans HAL des publications de 2020 par discipline", fontsize = 22, x = 0.4, y = 1.08,  alpha = 0.6)
    plt.savefig('./img/hal_discipline.png', dpi=100, bbox_inches='tight', pad_inches=0.1)



#====================hal_evol=======================================
# hal fichier avec auto archiv 
# hal fichier not auto archive
# hal notice avec oa
# hal notice sans oa
 
# evolution de la présence dans HAL
if graph == "hal_evol" : 
    print("graphique hal_evol\n\n")
    dfyears = df.loc[ df["published_year"].isin(["2016.0", "2017.0", "2018.0", "2019.0", "2020.0"]), :].copy()
    
    #deduire type dans hal
    dfyears["hal_file_auto"] = np.where( (dfyears["hal_location"] == "file") & (dfyears["hal_selfArchiving"] == "True"), True, False)
    dfyears["hal_file_no_auto"] = np.where( (dfyears["hal_location"] == "file") & (dfyears["hal_selfArchiving"] == "False"), True, False)
    dfyears["hal_notice_oa"] = np.where( (dfyears["hal_coverage"] == "in") & (dfyears["hal_location"] != "file") & (dfyears["is_oa"] == True), True, False)
    dfyears["hal_notice_not_oa"] = np.where( (dfyears["hal_coverage"] == "in") & (dfyears["hal_location"] != "file") & (dfyears["is_oa"] == False), True, False)
    

    #definition du taux AO par années
    dfhal = pd.DataFrame(dfyears.groupby(["published_year"])
    [["hal_file_auto", "hal_file_no_auto", "hal_notice_oa", "hal_notice_not_oa"]].agg(
      ["count", np.mean])).reset_index()

    dfhal.columns = ["published_year", "nb_publi", "hal_file_auto_mean", "nb_publi", "hal_file_no_auto_mean", "nb_publi", "hal_notice_oa_mean", "nb_publi", "hal_notice_not_oa_mean"]

    # retrait du . dans le string des années
    dfhal["published_year"] = dfhal.apply(
        lambda x: x.published_year[ : x.published_year.index(".")], axis = 1)

    # ____1____ passer les données dans le modele de representation
    fig, (ax) = plt.subplots(figsize=(15, 10), dpi=100, facecolor='w', edgecolor='k')

    ax.bar(dfhal.published_year, dfhal.hal_file_auto_mean.tolist() , align='center', alpha = 1.0, color='#7e96c4',
          ecolor='black', label="Dans HAL avec texte intégral (déposé par l'auteur)")

    ax.bar(dfhal.published_year, dfhal.hal_file_no_auto_mean.tolist(), align='center', alpha = 1.0, color='#8ba6e9',
          bottom = dfhal.hal_file_auto_mean.tolist(),
          ecolor='black', label="Dans HAL avec texte intégral (non déposé par l'auteur)")

    ax.bar(dfhal.published_year, dfhal.hal_notice_oa_mean.tolist() , align='center',alpha = 1.0, color='#bed0f4',
         bottom = [sum(x) for x in zip(dfhal.hal_file_auto_mean.tolist(), dfhal.hal_file_no_auto_mean.tolist())], 
         ecolor='black', label="Dans HAL avec texte intégral en hyperlien")

    ax.bar(dfhal.published_year, dfhal.hal_notice_not_oa_mean.tolist() , align='center',alpha = 1.0, color='#e5eaf3',
         bottom = [sum(x) for x in zip(dfhal.hal_file_auto_mean.tolist(), dfhal.hal_file_no_auto_mean.tolist(), dfhal.hal_notice_oa_mean.tolist())], 
         ecolor='black', label="Dans HAL sans texte intégral")


    # ____2____ configurer l'affichage
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    # retirer l'origine sur Y
    yticks = ax.yaxis.get_major_ticks()
    yticks[0].label1.set_visible(False)

    # tracer les grilles 
    ax.yaxis.grid(ls='--', alpha=0.4)

    ax.set_xticks(np.arange(len(dfhal["published_year"]))) # just to remove an mess error UserWarning: FixedFormatter should only be used together with FixedLocator
    ax.set_xticklabels(dfhal["published_year"].tolist(), fontsize = 15)
    ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1])
    ax.set_yticklabels(['{:,.0%}'.format(x) for x in ax.get_yticks()], fontsize = 10)
    # reordonner la legende pour avoir en haut l'éditeur
    handles, labels = ax.get_legend_handles_labels()
    order = [3, 2, 1, 0]
    ax.legend([handles[idx] for idx in order],[labels[idx] for idx in order], fontsize = 15, loc="upper center", borderaxespad =1.7)

    
    hal_total = [sum(x) for x in zip(dfhal.hal_file_auto_mean.tolist(), dfhal.hal_file_no_auto_mean.tolist(), dfhal.hal_notice_oa_mean.tolist(), dfhal.hal_notice_not_oa_mean.tolist())]

    #ajout taux de présence global
    for year_ix in range(len(dfhal.published_year)): 
        ax.annotate(f"{ round(hal_total[year_ix] * 100)} %", 
                          xy=(year_ix , hal_total[year_ix]),
                          xytext=(0, 10),  
                          size=9,
                          textcoords="offset points",
                          ha='center', va='bottom', color = "#555555")
    '''
    ## Ajouter les taux par type, difficulté : il faut prendre en compte les taux précédents
    colname = ["oa_repository_mean", "oa_publisher_repository_mean", "oa_publisher_mean"]
    for col in  colname : 
    for year_ix in range(len(dfoa.year_label)) : 

      ypos_bottom = 0 
      for col_before_ix in range(colname.index(col)) :
        col_before = colname[col_before_ix]
        ypos_bottom += dfoa[col_before][year_ix]

      ax.annotate( f"{int(round( dfoa[col][year_ix] * 100 ))} %",
        xy = (year_ix, ypos_bottom + dfoa[col][year_ix] * 0.40), 
        xytext= (0,0), 
        size = 8, 
        textcoords="offset points",
        ha='center', va='bottom', color = "black")
        '''

    plt.title("Évolution et types de présence dans HAL", fontsize = 25, x = 0.5, y = 1.05, alpha = 0.6)
    plt.savefig('./img/hal_evol.png', dpi=100, bbox_inches='tight', pad_inches=0.1)


#====================doctype_discipline=======================================
# evolution des types de publications
if graph == "doctype_discipline" : 
  print("graphique doctype_discipline")
  dfyears = df.loc[ df["published_year"] == "2020.0"].copy()

  # netoyer les doctypes
  dfyears["genre"].replace(
    {"monograph" : "book",
     "peer-review" : "other",
      "journal-issue": "other", 
      "reference-entry" : "book-chapter",
      "component" : "other", # cest des données de la rech souvent
      "reference-book" : "book", 
      "journal" : "other",
      "report" : "other",
      "proceedings" : "other"
      }, inplace = True)


  fields = pd.crosstab(df["scientific_field"], dfyears["genre"])
  # passer en pourcentage 
  fields = fields.T
  fields = fields / fields.sum() * 100
  fields = fields.T
  fields.sort_index(ascending = False, inplace = True)
  
  print(fields.columns)
  ax = fields.plot(kind = "barh", stacked=True, figsize=(14, 10), color = ["#9dd866", "#6f4e7c", "#0b84a5", "grey", "#ffa056", "#f6c85f"])
  
  ## _______ configurer l'afichage
  # remove axis
  ax.spines['top'].set_visible(False)
  ax.spines['right'].set_visible(False)
  ax.spines['bottom'].set_visible(False)
  # remove xticks
  plt.tick_params(
      axis='x',          # changes apply to the x-axis
      which='both',      # both major and minor ticks are affected
      bottom=False,      # ticks along the bottom edge are off
      labelbottom=False) # labels along the bottom edge are off

  labels = []
  for j in fields.columns:
      for i in fields.index:
          label = fields.loc[i][j]
          if type(label) != str : 
            #pour un meilleur affichage : si ce n'est pas la discipline on arrondi 
            label = str(round(label))
            label += " %"     #:label.find(".")
            labels.append(label)          

  patches = ax.patches
  for label, rect in zip(labels, patches):
      width = rect.get_width()
      if width > 3:
          x = rect.get_x()
          y = rect.get_y()
          height = rect.get_height()
          ax.text(x + width/2., y + height/2., label, ha='center', va='center', fontsize=8)

  plt.ylabel(None, fontsize = 15)
  plt.legend(["Ouvrage", "Chapitre d'ouvrage", "Article de revue", "Autre", "Preprint", "Article de conférence"], 
    frameon = True, markerscale = 1, loc = "center", ncol = 3, bbox_to_anchor=(0.5, 1.02), framealpha= False  )
  plt.title("Types de publications de 2020 par discipline", fontsize = 25, x = 0.49, y = 1.07,  alpha = 0.6)
  plt.savefig("img/doctype_par_discipline.png", dpi=100, bbox_inches='tight')


#====================doctype_evol=======================================
# evolution des types de publications
if graph == "doctype_evol" : 
  print("graphique doctype_evol")
  dfyears = df.loc[ df["published_year"].isin(["2016.0", "2017.0", "2018.0", "2019.0", "2020.0"]), :].copy()

  # view all doctypes 

  # and clean as much as you want
  dfyears["genre"].replace(
    {"monograph" : "book",
     "peer-review" : "other",
      "journal-issue": "other", 
      "reference-entry" : "book-chapter",
      "component" : "other", # cest des données de la rech souvent
      "reference-book" : "book", 
      "journal" : "other",
      "report" : "other",
      "proceedings" : "other"
      }, inplace = True)

  print(dfyears["genre"].value_counts())
  dfdoctype = pd.crosstab(dfyears["published_year"], dfyears["genre"]) 
  
  # ____1____ passer les données dans le modele de representation
  fig, (ax) = plt.subplots(figsize=(12, 8), dpi=100, facecolor='w', edgecolor='k')

  ax.bar(dfdoctype.index, dfdoctype["journal-article"] , align='center', alpha = 1.0,
   color='#0b84a5', label="Article de revue")
  
  ax.bar(dfdoctype.index, dfdoctype["proceedings-article"] , bottom = dfdoctype["journal-article"],
    align='center', alpha = 1.0, color='#f6c85f', label="Article de conférence")
  
  ax.bar(dfdoctype.index, dfdoctype["book-chapter"] , 
    bottom = [sum(x) for x in zip(dfdoctype["journal-article"] , dfdoctype["proceedings-article"])],
    align='center', alpha = 1.0, color='#6f4e7c', label="Chapitre d'ouvrage")

  ax.bar(dfdoctype.index, dfdoctype["book"] , 
    bottom = [sum(x) for x in zip(dfdoctype["journal-article"] , dfdoctype["proceedings-article"], 
      dfdoctype["book-chapter"])],
    align='center', alpha = 1.0, color="#9dd866", label="Ouvrage")

  ax.bar(dfdoctype.index, dfdoctype["posted-content"] , 
    bottom = [sum(x) for x in zip(dfdoctype["journal-article"] , dfdoctype["proceedings-article"], 
      dfdoctype["book-chapter"], dfdoctype["book"])],
    align='center', alpha = 1.0, color='#ffa056', label="Preprint")

  ax.bar(dfdoctype.index, dfdoctype["other"] , 
    bottom = [sum(x) for x in zip(dfdoctype["journal-article"] , dfdoctype["proceedings-article"], 
    dfdoctype["book-chapter"], dfdoctype["posted-content"], dfdoctype["book"] )],
    align='center', alpha = 1.0, color='grey', label="Autre")


  # ____2____ configurer l'affichage
  ax.spines['top'].set_visible(False)
  ax.spines['right'].set_visible(False)
  ax.spines['left'].set_visible(False)
  # retirer l'origine sur Y
  yticks = ax.yaxis.get_major_ticks()
  yticks[0].label1.set_visible(False)

  # tracer les grilles 
  ax.yaxis.grid(ls='--', alpha=0.4)

  # légende : reordonner les éléments
  handles, labels = ax.get_legend_handles_labels()
  print(labels)
  order = [5, 4, 3, 2, 1, 0]
  ax.legend([handles[idx] for idx in order], [labels[idx] for idx in order], 
    fontsize = 14, loc="center", framealpha =0.95, frameon = True, borderaxespad =-1)

  ax.set_xticks(np.arange(len(dfdoctype.index))) # just to remove an mess error UserWarning: FixedFormatter should only be used together with FixedLocator
  ax.set_xticklabels([year[: year.index(".")] for year in dfdoctype.index.tolist()], fontsize = 15)

  plt.title("Évolution des types de publication", fontsize = 25, x = 0.5, y = 1.05, alpha = 0.6)
  plt.savefig('./img/doctype_evolution.png', dpi=100, bbox_inches='tight', pad_inches=0.1)
  plt.show()

  exit()


#====================disciplines=======================================
# nb publications par discipline
if graph == "publication_discipline" : 
  print("graphique nb publication par disciplines")
  oneyear = df[ df["published_year"] == "2020.0"]

  df_field_oa =pd.crosstab(oneyear["scientific_field"], oneyear["is_oa"])
  df_field_oa.columns = ["not_oa", "is_oa"]
  df_field_oa["total"] = df_field_oa["not_oa"] + df_field_oa["is_oa"]

  print("\n\n\n")
  
  ### calculer taux_concentration par discipline
  ## __ nettoyer les données de publisher
  oneyear_clean_publisher = oneyear[ oneyear["publisher"] != ""].copy()
  oneyear_clean_publisher["publisher"].replace({"Elsevier BV": "Elsevier"}, inplace = True)
  oneyear_clean_publisher["publisher"].replace({"Springer Science and Business Media LLC": "Springer"}, inplace = True)
  oneyear_clean_publisher["publisher"].replace({"Springer International Publishing": "Springer"}, inplace = True)


  def calc_concentration(row) :
    field_publications = pd.DataFrame()
    field_publications = oneyear_clean_publisher[ oneyear_clean_publisher["scientific_field"] == row.name ]
    
    nb_publisher = len(field_publications["publisher"].value_counts() )
    
    #first_publisher_nb = nb publisher 1er centile
    first_publisher_nb = math.ceil(nb_publisher/100) #1er centile : besoin d'arrondir en haut
            
    #first_pubsliher_nb_publication = nombre de publication pour le 1er centile des publisher
    first_pubsliher_nb_publication = field_publications["publisher"].value_counts()[:first_publisher_nb].sum()
    taux = round(first_pubsliher_nb_publication / row.total *100)

    return [nb_publisher, first_publisher_nb, first_pubsliher_nb_publication, taux ]
   
  df_concentration = df_field_oa.apply(calc_concentration, axis = 1, result_type='expand')
  df_concentration.columns = ["nb_publisher", "first_publisher_nb", "first_nb_publication", "taux_concentration"]
  df_concentration.to_csv("vieww_df.csv")
  #fusionner les deux df pour avoir les données d'accès ouvert, de quantité de publi et de concentration
  df_field = df_field_oa.merge(df_concentration, how = "left", on = "scientific_field")
    
  # ____1____ passer les données dans le modele de representation
  fig, (ax) = plt.subplots(figsize=(12, 7), dpi=100, facecolor='w', edgecolor='k')

  ax.bar(df_field.index, df_field["is_oa"].tolist(),  color='#7E96C4', align='center',label="Accès ouvert")

  ax.bar(df_field.index, df_field["not_oa"].tolist(), bottom = df_field["is_oa"].tolist(), align='center', color='#BED0F4', label="Accès fermé")

  # ____2____ configurer l'affichage
  ax.spines['top'].set_visible(False)
  ax.spines['right'].set_visible(False)
  #ax.spines['left'].set_visible(False)
  # retirer l'origine sur Y
  yticks = ax.yaxis.get_major_ticks()
  yticks[0].label1.set_visible(False)
  ax.yaxis.grid(ls='--', alpha=0.4)

  ## ajout des taux de concentrations

  for x, y in zip(df_field.index, df_field.total) : 
    plt.annotate(
      f"{df_field.loc[x, 'taux_concentration']} %" , 
      (x,y),
      textcoords="offset points", # how to position the text
      xytext=(0,2), # distance from text to points (x,y)
      ha='center', # horizontal alignment can be left, right or center
      va = 'bottom', 
      fontsize = 8,
      color = "grey"
      )
  
  ax.set_xticklabels(df_field.index, ha = "right", rotation = 60, fontsize = 12)

  #plt.tight_layout()
  plt.legend( loc = "upper left",  bbox_to_anchor=(0.14, 0.85),  fontsize = 14,  frameon = False)
  plt.text(0.95, 5000 , "n % : taux de concentration\n         des éditeurs", fontsize = 12, color = "grey")

  plt.title("Quantité de publication en 2020 par discipline\n et concentration éditoriale", fontsize = 20, x = 0.5, y = 1, alpha = 0.6)
  plt.savefig("img/publication_par_discipline.png", dpi=100, bbox_inches='tight')
  
  



#====================CIRCULAIRE=======================================
#circulaire bilan open access sur une année
if graph == "circulaire" : 
  dfpie = df[ df["published_year"] == "2020.0"]
  oa_bool = dfpie["is_oa"].value_counts().sort_index()
  oa_bool = oa_bool.rename( {True : "Accès ouvert", False : "Accès fermé"})
  print(oa_bool)

  oa_type = dfpie["oa_type"].value_counts().sort_index()
  oa_type = oa_type.rename({"closed" : "Accès fermé", "publisher" : "Éditeur", 
    "repository" : "Archive ouverte", "publisher;repository" : "Éditeur et Archive ouverte"})
  #print(oa_type)

  fig, ax = plt.subplots(dpi=100)
  ax.set_aspect('equal')
  ax.pie(oa_bool, labels=oa_bool.index, radius=3, labeldistance = None, 
    colors=['tomato', 'springgreen'], autopct=lambda x: str(round(x, 1)) + '%', pctdistance = 0.9, shadow = True);
  ax.pie(oa_type, labels=oa_type.index, radius=2.3, labeldistance = None, 
    colors=['firebrick','gold','greenyellow','seagreen'], autopct=lambda x: str(round(x, 1)) + '%', pctdistance = 0.9);
      
  ax.pie([1], radius=1.3, colors='white');

  # légende : reordonner les éléments
  handles, labels = ax.get_legend_handles_labels()
  print(labels)
  order = [0, 1, 3, 4, 5]
  ax.legend([handles[idx] for idx in order], [labels[idx] for idx in order], 
    fontsize = 14, loc="center", framealpha =1, frameon = True, borderaxespad =-1)

  #ax.legend(loc="", fontsize = 12)
  plt.title('Proportion des publications 2020 en accès ouvert (mesuré en 2021)', fontsize = 23, x = 0.55, y = 1.8, alpha = 0.6)
  #plt.show()
  plt.savefig('./img/circulaire_2020.png', dpi=150, bbox_inches='tight', pad_inches=0.9)



#=========================OA_EVOL==================================
##Evolution taux open access par années et par type
if graph == "oa_evol" : 
  
  # ____0____ recupérer les données
  dfyears = df.loc[ df["published_year"].isin(["2016.0", "2017.0", "2018.0", "2019.0", "2020.0"]), :]
  print("nb publis a traiter", len(dfyears))
  pd.set_option('mode.chained_assignment', None)
  dfyears.is_oa = dfyears.is_oa.astype(bool)

  # retour consol uniquement : comparer les valeurs avec ou sans DOI
  halnodoi = dfyears[ dfyears["doi"] == ""]
  print(f"nb publis hal uniquement {len(halnodoi.index)}")
  print(f"soit en % de plus {round(len(halnodoi.index)/len(dfyears) * 100, 1)}")
  haloa = dfyears.loc[ (dfyears["doi"]== "") & (dfyears["is_oa"] == True) , :]
  print("nombre de publi oa dans hal", len(haloa))

  ## /!\ Si on veut réduire aux publications avec DOI seulement
  dfyears = dfyears[ dfyears["doi"] != ""].copy()

  #retrouver les types d'AO
  dfyears["oa_publisher_repository"] = dfyears.oa_type == "publisher;repository"
  dfyears["oa_repository"] = dfyears.oa_type == "repository"
  dfyears["oa_publisher"] = dfyears.oa_type == "publisher"
  dfyears["oa_unk"] = dfyears.oa_type == "unknow"

  #definition du taux AO par années
  dfoa = pd.DataFrame(dfyears.groupby(["published_year"])
    [["is_oa", "oa_repository", "oa_publisher", "oa_unk", "oa_publisher_repository"]].agg(
      ["count", np.mean])).reset_index()

  dfoa.columns = ["published_year", "nb_doi", "oa_mean", "nbdoi1", "oa_repository_mean", "nb_doi2",
  "oa_publisher_mean", "nb_doi3", "oa_unk_mean", "nb_doi4", "oa_publisher_repository_mean"]

  dfoa["year_label"] = dfoa.apply(
    lambda x: "{}\n{} publications".format(x.published_year[:x.published_year.index(".")]
    , int(x.nb_doi)), axis = 1)
  dfoa = dfoa.sort_values(by = "published_year", ascending = True)


  # ____1____ passer les données dans le modele de representation
  fig, (ax) = plt.subplots(figsize=(15, 10), dpi=100, facecolor='w', edgecolor='k')

  ax.bar(dfoa.year_label, dfoa.oa_repository_mean.tolist() , align='center', alpha = 1.0, color='seagreen',
          ecolor='black', label="Archive ouverte")

  ax.bar(dfoa.year_label, dfoa.oa_publisher_repository_mean.tolist(), align='center', alpha = 1.0, color='greenyellow',
          bottom = dfoa.oa_repository_mean.tolist(),
          ecolor='black', label="Éditeur et Archive ouverte")

  ax.bar(dfoa.year_label, dfoa.oa_publisher_mean.tolist() , align='center',alpha = 1.0, color='gold',
         bottom = [sum(x) for x in zip(dfoa.oa_repository_mean.tolist(), dfoa.oa_publisher_repository_mean.tolist())], ecolor='black', label="Éditeur")

  # ____2____ configurer l'affichage
  ax.spines['top'].set_visible(False)
  ax.spines['right'].set_visible(False)
  ax.spines['left'].set_visible(False)
  # retirer l'origine sur Y
  yticks = ax.yaxis.get_major_ticks()
  yticks[0].label1.set_visible(False)

  # tracer les grilles 
  ax.yaxis.grid(ls='--', alpha=0.4)

  ax.set_xticks(np.arange(len(dfoa["year_label"]))) # just to remove an mess error UserWarning: FixedFormatter should only be used together with FixedLocator
  ax.set_xticklabels(dfoa["year_label"].tolist(), fontsize = 15)
  ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1])
  ax.set_yticklabels(['{:,.0%}'.format(x) for x in ax.get_yticks()], fontsize = 10)
  # reordonner la legende pour avoir en haut l'éditeur
  handles, labels = ax.get_legend_handles_labels()
  order = [2,1,0]
  ax.legend([handles[idx] for idx in order],[labels[idx] for idx in order], fontsize = 15, loc="upper center", borderaxespad =1.7)

  oa_total_mean = [sum(x) for x in zip(dfoa.oa_repository_mean.tolist(), dfoa.oa_publisher_repository_mean.tolist(), dfoa.oa_publisher_mean.tolist())]

  #ajout le taux d'accès ouvert global
  for year_ix in range(len(dfoa.year_label)):
      ax.annotate("{:,.1%}".format(oa_total_mean[year_ix]),
                          xy=(year_ix , oa_total_mean[year_ix]),
                          xytext=(0, 20),  
                          size=16,
                          textcoords="offset points",
                          ha='center', va='bottom')

  ## Ajouter les taux par type, difficulté : il faut prendre en compte les taux précédents
  colname = ["oa_repository_mean", "oa_publisher_repository_mean", "oa_publisher_mean"]
  for col in  colname : 
    for year_ix in range(len(dfoa.year_label)) : 

      ypos_bottom = 0 
      for col_before_ix in range(colname.index(col)) :
        col_before = colname[col_before_ix]
        ypos_bottom += dfoa[col_before][year_ix]

      ax.annotate( f"{int(round( dfoa[col][year_ix] * 100 ))} %",
        xy = (year_ix, ypos_bottom + dfoa[col][year_ix] * 0.40), 
        xytext= (0,0), 
        size = 8, 
        textcoords="offset points",
        ha='center', va='bottom', color = "black")


  plt.title("Évolution du taux d'accès ouvert aux publications", fontsize = 25, x = 0.5, y = 1.05, alpha = 0.6)
  plt.savefig('./img/oa_evolution.png', dpi=100, bbox_inches='tight', pad_inches=0.1)


#========================OA_DISCIPLINE===================================
if graph == "oa_discipline" : 
  oneyear_pub = df.loc[df['published_year'] == "2020.0",:]
  oneyear_pub = oneyear_pub[ oneyear_pub["scientific_field"] != "" ] # retrait des publications où le domaine serait resté vide
  print("2020 nb of publi", len(oneyear_pub))
  publications_par_domaine = oneyear_pub['scientific_field'].value_counts().sort_index()
  print(publications_par_domaine)


  """
  df_oa_discipline_global = pd.crosstab([oneyear_pub['scientific_field']],oneyear_pub['oa_type'])
  # Ajout d'une colonne avec le total par discipline
  df_oa_discipline_global["Total"] = publications_par_domaine
  # Ajout d'une colonne qui concatène le nom de la discipline et le total
  df_oa_discipline_global["y_label"] = df_oa_discipline_global.index + "\n" + df_oa_discipline_global["Total"].apply(str) + " publications"

  # Réindexation de l'index pour que les bonnes informations s'affichent dans le graphique final
  df_oa_discipline_global.index = df_oa_discipline_global["y_label"]
  """

  df_oa_discipline = pd.crosstab([oneyear_pub['scientific_field']] , oneyear_pub['oa_type'])
  df_oa_discipline = (df_oa_discipline.T / df_oa_discipline.T.sum()).mul(100).round(1)
  df_oa_discipline = df_oa_discipline.T
  df_oa_discipline["Total"] = publications_par_domaine
  df_oa_discipline["y_label"] = df_oa_discipline.index + "\n" + df_oa_discipline["Total"].apply(str) + " publications"
  df_oa_discipline.index = df_oa_discipline["y_label"]

  df_oa_discipline.sort_index( ascending = False, inplace = True)

  import matplotlib.ticker as mtick
  ax = df_oa_discipline.drop(["Total", "y_label"], axis=1).plot(kind="barh", stacked=True, figsize=(14, 10), 
      color=['tomato','gold','greenyellow','seagreen'])
  #ax.xaxis.set_major_formatter(mtick.PercentFormatter())

  ## _______ configurer l'afichage
  # remove axis
  ax.spines['top'].set_visible(False)
  ax.spines['right'].set_visible(False)
  ax.spines['bottom'].set_visible(False)
  # remove xticks
  plt.tick_params(
      axis='x',          # changes apply to the x-axis
      which='both',      # both major and minor ticks are affected
      bottom=False,      # ticks along the bottom edge are off
      labelbottom=False) # labels along the bottom edge are off


  labels = []
  for j in df_oa_discipline.columns:
      for i in df_oa_discipline.index:
          label = df_oa_discipline.loc[i][j]
          if type(label) != str : 
            #pour un meilleur affichage : si ce n'est pas la discipline on arrondi 
            label = str(round(label))
            label += " %"     #:label.find(".")
            labels.append(label)
          

  patches = ax.patches
  for label, rect in zip(labels, patches):
      width = rect.get_width()
      if width > 0:
          x = rect.get_x()
          y = rect.get_y()
          height = rect.get_height()
          ax.text(x + width/2., y + height/2., label, ha='center', va='center', fontsize=9)

  # Trier les disciplines par ordre alphabétique
  #plt.gca().invert_yaxis()
  plt.tick_params(axis = 'both', labelsize = 13)

  plt.ylabel(None, fontsize = 15)

  plt.legend(['Accès fermé', 'Éditeur', 'Éditeur et Archive ouverte', 'Archive ouverte'],
                loc = 'best', ncol = 4,
                frameon = True, markerscale = 1, title = None, fontsize = 15,
                borderpad = 0.2, labelspacing = 0.3, bbox_to_anchor=(0.02, 0.985), framealpha= False)

  plt.title("Taux d'accès ouvert des publications 2020 par discipline", fontsize = 25, x = 0.49, y = 1.07,  alpha = 0.6)

  #plt.show()
  plt.savefig('./img/oa_discipline.png', dpi=100, bbox_inches='tight', pad_inches=0.1)



#=========================oa_editeur==================================
#type d'accès ouvert par éditeurs

if graph == "oa_editeur" : 
  oneyear_pub = df.loc[ df['published_year'] == "2020.0", : ].copy()

  #print(oneyear_pub['publisher'].value_counts().iloc[0:30])
  
  # fusionner les éditeurs similaires  
  oneyear_pub["publisher"].replace({"Elsevier BV": "Elsevier"}, inplace = True)
  oneyear_pub["publisher"].replace({"Springer Science and Business Media LLC": "Springer"}, inplace = True)
  oneyear_pub["publisher"].replace({"Springer International Publishing": "Springer"}, inplace = True)

  publications_par_editeur = oneyear_pub['publisher'].value_counts().iloc[0:30]
  print("\n\napres fusion\n\n",publications_par_editeur)
  
  sel_editors = ["Elsevier", "Springer", "Wiley", "Oxford University Press (OUP)", "MDPI AG", "EDP Sciences", "Ovid Technologies (Wolters Kluwer Health)", 
  "American Physical Society (APS)", "Frontiers Media SA", "Informa UK Limited", "BMJ", "American Chemical Society (ACS)", "American Astronomical Society", 
  "IOP Publishing", "Cold Spring Harbor Laboratory"]
  
  oneyear_editors = oneyear_pub[oneyear_pub['publisher'].isin(sel_editors)]

  # #Quelle est la proportion d'accès ouvert, par type d'accès, des publications par éditeur dans l'année ?
  # df_oa_editeur_global = pd.crosstab([oneyear_editors['publisher']],oneyear_editors['oa_type'])
  # df_oa_editeur_global["Total"] = publications_par_editeur
  # df_oa_editeur_global["y_label"] = df_oa_editeur_global.index + " - " + df_oa_editeur_global["Total"].apply(str) + " publications"
                                       
  # df_oa_editeur_global.index = df_oa_editeur_global["y_label"]

  # récupérer les données d'accès ouvert
  df_oa_editeur = pd.crosstab([oneyear_pub['publisher']],oneyear_editors['oa_type'])
  #Convertir le résultat en pourcentages
  df_oa_editeur = (df_oa_editeur.T / df_oa_editeur.T.sum()).mul(100).round(1)
  df_oa_editeur = df_oa_editeur.T
  df_oa_editeur["Total"] = publications_par_editeur
  df_oa_editeur["y_label"] = df_oa_editeur.index + "\n"+df_oa_editeur["Total"].apply(str)+" publications"
  df_oa_editeur.index = df_oa_editeur["y_label"]
  df_oa_editeur.sort_values(by=['closed'], ascending=True, inplace = True)
  
  ## __2__ Générer le graphique
  import matplotlib.ticker as mtick
  ax = df_oa_editeur.drop(["Total", "y_label"], axis=1).plot(kind="barh", stacked=True, figsize=(15, 13), 
    color=['tomato','gold','greenyellow','seagreen'])


  ## ___3____ Configurer l'afichage
  # remove axis
  ax.spines['top'].set_visible(False)
  ax.spines['right'].set_visible(False)
  ax.spines['bottom'].set_visible(False)
  # remove xticks
  plt.tick_params(
      axis='x',          # changes apply to the x-axis
      which='both',      # both major and minor ticks are affected
      bottom=False,      # ticks along the bottom edge are off
      labelbottom=False) # labels along the bottom edge are off

  # Ajotuer le pourcentage pour chaque types
  labels = []
  for j in df_oa_editeur.columns:
      for i in df_oa_editeur.index:
        label = df_oa_editeur.loc[i][j]
        #label = str(df_oa_editeur.loc[i][j]) + "%"
        if type(label) != str : 
          label = round(label)
          label = str(label) + "%"
          labels.append(label)
  

  patches = ax.patches
  for label, rect in zip(labels, patches):
      width = rect.get_width()
      if width > 1: ## mettre > 0 pour avoir les faibles pourcentages, >1 pour ne pas surcharger
          x = rect.get_x()
          y = rect.get_y()
          height = rect.get_height()
          ax.text(x +.3 + width/2., y + height/2., label, ha='center', va='center', fontsize=11)
          
  plt.gca().invert_yaxis()
  plt.tick_params(axis = 'both', labelsize = 18)
  plt.ylabel(None)

  # generer une premiere fois sans renomer les colonnes pour s'assurer que le renommage est correcte
  plt.legend(   ['Accès fermé', 'Éditeur', 'Éditeur et Archive ouverte', 'Archive ouverte'],
                loc = 'best', ncol = 4, markerscale = 1, title = None, fontsize = 16,
                borderpad = 0.2, labelspacing = 0.3, bbox_to_anchor=(0.01, 0.985), framealpha= False)

  plt.title("Taux d'accès ouvert aux publications 2020 par éditeurs", fontsize = 34, x = 0.49, y = 1.1,  alpha = 0.6)
  plt.suptitle("Visualisation des 15 premiers éditeurs par quantité de publications", fontsize = 20, x = 0.49, y = 0.95,  alpha = 0.6)
  plt.savefig('./img/oa_editeur.png', dpi=100, bbox_inches='tight', pad_inches=0.9)



#=========================extra : comparaison_bases=================================
# comparaison du nb de publications dans les bases scopus wos hal et cie.
if graph == "comparaison_bases" : 

  # ____0____ recupérer les données
  df = pd.read_csv("./data/out/step_a__statistiques_sur_les_bases.csv")
  data = df.to_dict("list")
  x = np.arange(len(data["name"]))  # the label locations
  width = 0.2

  # ____1____ passer les données dans le modele de representation graphique
  fig, ax = plt.subplots(figsize=(7,4))
  ax.bar(x - width, data["all"], width, label='toutes publications', color = "orchid")
  ax.bar(x , data["doi"], width, label='publications avec DOI',color = "gold")
  ax.bar(x + width, data["no_doi"], width, label='publications sans DOI', color = "skyblue")

  # ____2____ configurer l'affichage
  ax.yaxis.grid(ls='--', alpha=0.4)

  ax.spines['top'].set_visible(False)
  ax.spines['right'].set_visible(False)
  ax.spines['left'].set_visible(False)
  # retirer l'origine sur Y
  yticks = ax.yaxis.get_major_ticks()
  yticks[0].label1.set_visible(False)

  plt.yticks([i for i in range(0, 100_000, 20_000)], fontsize = 10)
  ax.set_ylabel('Nombre de publications', fontsize = 8)
  ax.set_xticks(x)
  ax.set_xticklabels([n.capitalize() for n in data["name"] ], fontsize = 11)
  plt.legend(loc="upper center", fontsize = 8)

  ax.set_title("Quantité de publications dans les bases", fontsize=16, alpha = 0.6, y = 1.05)
  plt.suptitle("Années 2016-2020", fontsize=10, alpha = 0.6, y = 0.92)
  plt.savefig('./img/comparaisons_entre_les_bases.png', dpi=150, bbox_inches='tight', pad_inches=0.05)
  exit()


#=========================APC Evolution=================================
# estimation du pourcentage de publication en accès ouvert chez l'éditeur avec APC
if graph == "apc_evol" : 
  # ____0____ recupérer les données
  dfyears = df.loc[ df["published_year"].isin(["2016.0", "2017.0", "2018.0", "2019.0", "2020.0"]), :]
  print("nb publis a traiter", len(dfyears), '\n\n')
  pd.set_option('mode.chained_assignment', None)
  df_gold = dfyears.loc[ dfyears["oa_type"].str.contains("publisher", regex = False), : ]
  #print(df_gold["oa_type"].value_counts())

  df_gold["has_apc"] =  df_gold["apc_tracking"] != ""
  df_gold = df_gold.astype({'has_apc': 'bool'})
  print("nb public avec  APC", len(df_gold[ df_gold["has_apc"]]))
  
  # ____1____produire le tableau
  df_apc = pd.DataFrame( df_gold.groupby(["published_year"])[["has_apc"]].agg( ["count", np.mean])).reset_index()
  df_apc.columns = ["published_year", "nb", "has_apc_mean"]

  df_apc["label"] = df_apc.apply(
    lambda x: "{}\n{} publications".format( x.published_year[:x.published_year.index(".")] , int(x.nb)), axis= 1)
    
  df_apc.sort_values(by = "published_year", ascending = True, inplace = True)
  print(df_apc)

  # ____2____ passer les données dans le modele de representation
  fig, (ax) = plt.subplots(figsize=(15, 10), dpi=100, facecolor='w', edgecolor='k')

  ax.bar(df_apc.label, df_apc.has_apc_mean.tolist() , align='center', alpha = 1.0, color='lightpink',
          ecolor='black', label="Accès ouvert chez l'éditeur avec APC")

  no_apc = 1- df_apc["has_apc_mean"]
  ax.bar(df_apc.label, no_apc,  align='center', alpha = 1.0, color='gainsboro',
          bottom = df_apc.has_apc_mean.tolist(),
          ecolor='black', label="Accès ouvert chez l'éditeur sans APC")
  

  # ____2____ configurer l'affichage
  ax.spines['top'].set_visible(False)
  ax.spines['right'].set_visible(False)
  ax.spines['left'].set_visible(False)
  # retirer l'origine sur Y
  yticks = ax.yaxis.get_major_ticks()
  yticks[0].label1.set_visible(False)

  # tracer les grilles 
  ax.yaxis.grid(ls='--', alpha=0.4)
  ax.set_xticks(np.arange(len(df_apc["label"]))) # just to remove an mess error UserWarning: FixedFormatter should only be used together with FixedLocator
  ax.set_xticklabels(df_apc["label"].tolist(), fontsize = 15)
  ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1])
  ax.set_yticklabels(['{:,.0%}'.format(x) for x in ax.get_yticks()], fontsize = 10)

  apc_percent = df_apc["has_apc_mean"].tolist()
  print(apc_percent)
  print(range(len(df_apc.label)))

  #ajout du label sur les hist
  for year_ix in range(len(df_apc.label)):
    ax.annotate("{:,.1%}".format(apc_percent[year_ix]),
                          xy=(year_ix , apc_percent[year_ix]),
                          xytext=(0, 10),  
                          size=16,
                          textcoords="offset points",
                          ha='center', va='bottom')


  plt.legend(loc='upper center', bbox_to_anchor=(0.5, 0.8) ,fontsize = 12)


  plt.title("Estimation du pourcentage de publications en accès ouvert \nchez l'éditeur avec frais de publications (APC)",
    fontsize = 25, x = 0.5, y = 1, alpha = 0.6)
  plt.savefig('./img/apc_evolution.png', dpi=100, bbox_inches='tight', pad_inches=0.1)


#========================apc_discipline===================================
if graph == "apc_discipline" : 
  oneyear_pub = df.loc[df['published_year'] == "2020.0",:]
  gold = oneyear_pub.loc[ oneyear_pub["oa_type"].str.contains("publisher", regex = False), : ]
  gold = gold[ gold["scientific_field"] != "" ].copy() # retrait des publications où le domaine serait resté vide
  print("2020 nb of publi", len(oneyear_pub))
    
  gold["has_apc"] = gold['apc_tracking'] != ""

  df_apc_discipline = pd.crosstab([gold['scientific_field']] , gold['has_apc'])
  print(df_apc_discipline.columns)
  df_apc_discipline.columns = ["no_apc", "has_apc"]
  df_apc_discipline["total"] = df_apc_discipline["has_apc"] + df_apc_discipline["no_apc"]
  df_apc_discipline["has_apc_percent"] = df_apc_discipline["has_apc"] / df_apc_discipline["total"] * 100
  df_apc_discipline["no_apc_percent"] = df_apc_discipline["no_apc"] / df_apc_discipline["total"] * 100

  df_apc_discipline["y_label"] = df_apc_discipline.index + "\n" + df_apc_discipline["total"].apply(str) + " publications"
  df_apc_discipline.index = df_apc_discipline["y_label"]
  df_apc_discipline.sort_index( ascending = False, inplace = True)
  df_apc_discipline.drop(["has_apc", "no_apc", "total", "y_label"], axis=1, inplace = True)

  #configurer l'affichage
  import matplotlib.ticker as mtick

  ax = df_apc_discipline.plot(kind="barh", stacked=True, figsize=(14, 10), color= ['lightpink', 'gainsboro'])
  
  ## _______ configurer l'afichage
  # remove axis
  ax.spines['top'].set_visible(False)
  ax.spines['right'].set_visible(False)
  ax.spines['bottom'].set_visible(False)
  
  # remove xticks
  plt.tick_params(
      axis='x',          # changes apply to the x-axis
      which='both',      # both major and minor ticks are affected
      bottom=False,      # ticks along the bottom edge are off
      labelbottom=False) # labels along the bottom edge are off

  #ajout des pourcentages
  labels = []
  for j in df_apc_discipline.columns:
      for i in df_apc_discipline.index:
          label = df_apc_discipline.loc[i][j]
          if type(label) != str : 
            #pour un meilleur affichage : si ce n'est pas la discipline on arrondi 
            label = str(round(label))
            label += " %"     #:label.find(".")
            labels.append(label)

  patches = ax.patches
  for label, rect in zip(labels, patches):
      width = rect.get_width()
      if width > 0:
          x = rect.get_x()
          y = rect.get_y()
          height = rect.get_height()
          ax.text(x + width/2., y + height/2., label, ha='center', va='center', fontsize=9)
  
  # plt.tick_params(axis = 'both', labelsize = 13)
  plt.ylabel(None, fontsize = 15)

  plt.title("Estimation du pourcentage des publications de 2020 \nen accès ouvert chez l'éditeur avec APC", fontsize = 25, x = 0.49, y = 1.05,  alpha = 0.6) 
  plt.legend(['Accès ouvert chez l\'éditeur avec APC', 'Accès ouvert chez l\'éditeur sans APC'],
                loc = 'upper center', ncol = 2,
                frameon = True, markerscale = 1, title = None, fontsize = 12,
                borderpad = 0.2, labelspacing = 0.3, bbox_to_anchor=(0.45, 1.025), framealpha= False)

  plt.savefig('./img/apc_discipline.png', dpi=100, bbox_inches='tight', pad_inches=0.1)



#====================bibliodiversity=======================================
# pour éclairer la bibiodiversité
if graph == "bibliodiversity" : 
  print("graphique bibliodiversity")
  oneyear = df[ (df["published_year"] == "2020.0") & (df["publisher"]!= "") ].copy()
  #fusionner les éditeurs au mm nom
  oneyear["publisher"].replace({"Elsevier BV": "Elsevier"}, inplace = True)
  oneyear["publisher"].replace({"Springer Science and Business Media LLC": "Springer"}, inplace = True)
  oneyear["publisher"].replace({"Springer International Publishing": "Springer"}, inplace = True)
  #print(oneyear["publisher"].value_counts())

  
  bibdiversity = pd.crosstab(oneyear["publisher"], oneyear["is_oa"])
  bibdiversity["total"] = bibdiversity[False] + bibdiversity[True]
  # renomer les colonnes
  bibdiversity.columns = ["not_oa", "is_oa", "total"]
  bibdiversity.sort_values(by = "total", ascending = False, inplace = True)

  ### données pour la phrase "n publisher publient 50 % des publications d'UP"
  nb_publisher = len(bibdiversity)
  nb_publications = bibdiversity["total"].sum()
  one_percent = round(nb_publisher/100)
  print("1 % des éditeurs = ", one_percent, "publishers")
  one_percent_total = bibdiversity["total"].iloc[0:7].sum()
  one_percent_total_percent = round(one_percent_total/ nb_publications * 100) 
  string4graph = f"1 % des éditeurs publient\n{one_percent_total_percent} % des publications d'Université de Paris\n≠ bibliodiversité"
  print(string4graph)

  ## __x__generer graphique
  df4graph = bibdiversity[:30]

  fig, (ax) = plt.subplots(figsize=(15, 10), dpi=100, facecolor='w', edgecolor='k')
  ax.bar(df4graph.index, df4graph.is_oa, color = "#7E96C4", label = "Accès ouvert")
  ax.bar(df4graph.index, df4graph.not_oa, bottom = df4graph.is_oa , color = "#BED0F4", label = "Accès fermé")

  # ajout des noms des publishers en haut des histogrammes
  for x, y in zip(df4graph.index, df4graph.total) : 
    plt.annotate(
      x, 
      (x,y),
      textcoords="offset points", # how to position the text
      xytext=(0,2), # distance from text to points (x,y)
      ha='left', # horizontal alignment can be left, right or center
      va = 'bottom', 
      rotation= 30, 
      fontsize = 9
      )
    
  # ____2____ configurer l'affichage
  ax.spines['top'].set_visible(False)
  ax.spines['right'].set_visible(False)
  ax.set_ylabel("Nombre de publications", labelpad = 10)
  ax.set_xlabel("Éditeurs", labelpad = 10)

  # remove xticks
  plt.tick_params(
    axis='x',          # changes apply to the x-axis
    which='both',      # both major and minor ticks are affected
    bottom=False,      # ticks along the bottom edge are off
    top=False,         # ticks along the top edge are off
    labelbottom=False) # labels along the bottom edge are off
  
  # punchline
  plt.text(19, 2000 , string4graph, fontsize = 19)
  #

  plt.legend( loc = "upper center",fontsize = 14, bbox_to_anchor=(0.5, 0.95),   borderaxespad =1.7)
  plt.title("Quantité de publication en 2020 \npour les 30 premiers éditeurs", fontsize = 25, x = 0.5, y = 1.03, alpha = 0.6)
  plt.suptitle(f"éditeurs = {nb_publisher}    publications = {nb_publications}", fontsize = 13, x = 0.5, y = 0.89,  alpha = 0.6)
  plt.savefig('./img/bibliodiversite.png', dpi=100, bbox_inches='tight', pad_inches=0.1)

  


exit()
#===========================================================
##___________________bonus : evol types d'accès ouvert green to diamond
#===========================================================
df = pd.read_csv("./data/out/uvsq_publications_2015_19.csv", dtype={"published_year":"string"}, na_filter = False, low_memory=False)
df = df.loc[ df["published_year"].isin(["2015.0", "2016.0", "2017.0", "2018.0", "2019.0"]), :]
print("doc a tratier", len(df))
print("doc en oa", len(df[ df["is_oa"]]))


# ____0____ récupérer les données
# repo only = repo and not suspicious
def deduce_green(row) : 
  if row["oa_type"] == "repository" and row["suspicious_journal"] != "True" :
    return True
  else : False

df["green"] = df.apply(lambda row : deduce_green(row), axis = 1)
df["suspicious"] = df.suspicious_journal == "True"

### deduce bronze (at publisher but without licence and not suspicious)
def deduce_bronze(row) : 
  if row["oa_status"] == "bronze" and row["suspicious_journal"] != "True" : 
    return True
  else : False
df["bronze"] = df.apply(lambda row : deduce_bronze(row), axis = 1)

### deduce hybrid
def deduce_hybrid(row) : 
  if row["oa_status"] == "hybrid" and row["suspicious_journal"] != "True" : 
    return True
  else : False
df["hybrid"] = df.apply(lambda row : deduce_hybrid(row), axis = 1)

### deduce gold
def deduce_gold(row) : 
  if row["oa_status"] == "gold" and row["suspicious_journal"] != "True" and row["apc_tracking"] != "" : 
    return True
  else : False
df["gold"] = df.apply(lambda row : deduce_gold(row), axis = 1)

### deduce diamond
def deduce_diamond(row) : 
  if row["oa_status"] == "gold" and row["suspicious_journal"] != "True" and row["apc_tracking"] == "" : 
    return True
  else : False
df["diamond"] = df.apply(lambda row : deduce_diamond(row), axis = 1)

# set dtype bools for new columns
df = df.astype({'green': 'bool', 'bronze': 'bool', 'hybrid':'bool', 'gold' : 'bool', 'diamond':'bool'})

dfoatype = pd.DataFrame(df.groupby(["published_year"])
  [["green", "suspicious", "bronze", "hybrid", "gold", "diamond"]].agg(
    ["count", np.mean])).reset_index()

dfoatype.columns= ["published_year", "nb1", "green", "nb2", "suspicious", "nb3", "bronze", "nb4", "hybrid", "nb5", "gold", "nb6", "diamond"]


#ajout du nb de publications pour l'abscisse
dfoatype["year_label"] = dfoatype.apply(
  lambda x: "{}\n({} publications)".format(x.published_year[:x.published_year.index(".")]
  , int(x.nb1)), axis = 1)
dfoatype = dfoatype.sort_values(by = "published_year", ascending = True)


# ____1____ passer les données dans le modele de representation graphique

fig, (ax) = plt.subplots(figsize=(12, 7), dpi=100, facecolor='w', edgecolor='k')

ax.bar(dfoatype.year_label, dfoatype.green, label = "Archive uniquement", color ="#665191" )

ax.bar(dfoatype.year_label, dfoatype.suspicious, bottom = dfoatype.green.tolist(), label = "Éditeur avec journal suspect" , color ="#7E7A7A" )

ax.bar(dfoatype.year_label, dfoatype.bronze, bottom = [sum(x) for x in zip(dfoatype.green.tolist(),dfoatype.suspicious.tolist())], 
  label = "Éditeur sans licence ouverte (bronze)", color = "#a05195" )

ax.bar(dfoatype.year_label, dfoatype.hybrid, bottom = [sum(x) for x in zip(dfoatype.green.tolist(),dfoatype.suspicious.tolist(), dfoatype.bronze.tolist())], 
  label = "Éditeur avec journal sur abonnement (hybrid)", color = "#d45287" )

ax.bar(dfoatype.year_label, dfoatype.gold, bottom = 
  [sum(x) for x in zip(dfoatype.green.tolist(),dfoatype.suspicious.tolist(), dfoatype.bronze.tolist(), dfoatype.hybrid.tolist() )], 
  label = "Éditeur avec frais de publications (gold)", color = "#ffa701" )

ax.bar(dfoatype.year_label, dfoatype.diamond, bottom = 
  [sum(x) for x in zip(dfoatype.green.tolist(),dfoatype.suspicious.tolist(), dfoatype.bronze.tolist(), dfoatype.hybrid.tolist(),dfoatype.gold.tolist() )], 
  label = "Éditeur sans frais de publications (diamond)", color = "#FFDE50" )


# ____2____ configurer l'affichage
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
# tracer les grilles 
ax.yaxis.grid(ls='--', alpha=0.2)
# preciser legend pour Y
ax.set_ylim([0,.8])
ax.set_yticklabels( [f"{int(round(x*100))} %" for x in ax.get_yticks()], fontsize = 10)
# retirer l'origine sur Y
yticks = ax.yaxis.get_major_ticks()
yticks[0].label1.set_visible(False)
# légende : reordonner les éléments
handles, labels = ax.get_legend_handles_labels()
order = [5, 4, 3, 2, 1, 0]
ax.legend([handles[idx] for idx in order], [labels[idx] for idx in order], 
  fontsize = 11, loc="upper center", framealpha =1, frameon = False, borderaxespad =-1)

## boucle pour ajouter les taux, difficulté : il faut prendre en compte les taux précédents
colname = ["green", "bronze", "hybrid", "gold", "diamond"]
for col in  colname : 
  for year_ix in range(len(dfoatype.year_label)) : 

    ypos_bottom = 0 #if col =="green" else dfoatype["green"][year_ix]
    
    for col_before_ix in range(colname.index(col)) :
      col_before = colname[col_before_ix]
      ypos_bottom += dfoatype[col_before][year_ix]

    ax.annotate( f"{int(round( dfoatype[col][year_ix] * 100 ))}%",
      xy = (year_ix, ypos_bottom + dfoatype[col][year_ix] * 0.40), 
      xytext= (0,0), 
      size = 8, 
      textcoords="offset points",
      ha='center', va='bottom', color = "black")

plt.title("Évolution des types d'accès ouvert", fontsize = 18, x = 0.5, y = 1.05, alpha = 0.8)
plt.savefig('./img/evolution_type_ao.png', dpi=100, bbox_inches='tight') #, pad_inches=0.1)
exit()














