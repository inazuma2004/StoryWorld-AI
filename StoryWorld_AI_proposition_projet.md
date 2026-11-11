# StoryWorld AI

## Plateforme intelligente de création de bandes dessinées et d'histoires illustrées par IA générative

**Proposition de projet --- Module : IA générative textuelle et
visuelle**\
**Spécialité : Ingénieur IA & Data Science**\
**Étudiant : Lamzouri Ishak --- EMSI Casablanca**

------------------------------------------------------------------------

## 1. Résumé du projet

StoryWorld AI est une application web qui transforme une idée, un thème
ou une courte description en une histoire illustrée sous forme de bande
dessinée. L'utilisateur définit les personnages, le genre narratif, le
style artistique, la langue et la longueur souhaitée. La plateforme
génère ensuite un scénario structuré, des dialogues, des scènes
illustrées et une BD exportable.

Le projet associe génération de texte par LLM, génération d'images par
modèle de diffusion, outils de composition graphique et, dans une partie
expérimentale contrôlée, des modèles VAE et GAN étudiés en cours.

**Promesse de démonstration :** saisir « un jeune inventeur découvre un
robot dans les ruelles de Casablanca », choisir un style, puis obtenir
une courte BD avec scénario, dialogues, illustrations et export PDF.

## 2. Problématique

La création d'une bande dessinée exige habituellement des compétences en
écriture, scénarisation, illustration et mise en page. Comment permettre
à un utilisateur sans expertise artistique de transformer une idée en
récit visuel cohérent, personnalisable et exportable, en combinant des
modèles génératifs textuels et visuels ?

## 3. Objectifs

-   Concevoir une application web multimodale de création narrative.
-   Générer un scénario structuré en scènes et cases, avec dialogues et
    descriptions visuelles.
-   Générer des illustrations correspondant aux scènes.
-   Permettre la personnalisation et la régénération ciblée des
    éléments.
-   Assembler automatiquement les résultats dans une bande dessinée.
-   Étudier et évaluer plusieurs approches génératives, sans entraîner
    un grand modèle depuis zéro.
-   Présenter une architecture modulaire, testable et évolutive.

## 4. Fonctionnalités

### 4.1 Fonctionnalités essentielles --- MVP

1.  **Assistant de création**
    -   Saisie d'une idée ou d'un thème.
    -   Choix du genre : aventure, fantastique, science-fiction,
        comédie, éducatif.
    -   Choix de la langue : français ou anglais au MVP; arabe en
        extension.
    -   Choix du nombre de scènes/cases et du style visuel.
    -   Choix du public cible : enfant, adolescent, adulte.
2.  **Génération du scénario**
    -   Titre, résumé, personnages, début, développement et conclusion.
    -   Découpage en scènes et cases.
    -   Dialogue court par case.
    -   Description visuelle séparée du texte affiché dans la case.
    -   Sortie structurée en JSON validé par schéma.
3.  **Génération d'illustrations**
    -   Génération d'une image par case ou par scène.
    -   Styles prédéfinis : manga, cartoon, aquarelle, comics.
    -   Prompts construits à partir de la scène et de la fiche du
        personnage.
    -   Indicateur de progression et gestion des erreurs.
4.  **Éditeur de BD**
    -   Aperçu des cases et dialogues.
    -   Modification du texte.
    -   Régénération d'une seule case sans refaire toute l'histoire.
    -   Réorganisation simple des cases.
    -   Mise en page en pages de BD.
5.  **Export**
    -   Export PDF.
    -   Export des images individuelles.
    -   Page de couverture avec titre et auteur.

### 4.2 Fonctionnalités différenciantes --- version enrichie

6.  **Fiche de personnage et bible visuelle**
    -   Nom, âge fictif, rôle, personnalité, vêtements, couleurs et
        attributs distinctifs.
    -   Portrait de référence généré une fois.
    -   Réutilisation de la description dans les prompts de chaque
        scène.
    -   Galerie des personnages et rappel de leurs caractéristiques.
7.  **Cohérence visuelle des personnages**
    -   Utiliser les portraits de référence avec une méthode
        image-to-image ou référence d'image lorsque le modèle le permet.
    -   Réutiliser une description visuelle normalisée et des paramètres
        de génération.
    -   Comparer visuellement les personnages entre les cases.
    -   Présenter cette fonction comme une amélioration progressive : la
        cohérence parfaite n'est pas garantie.
8.  **Modes de création**
    -   **Mode express :** idée → BD courte.
    -   **Mode guidé :** l'utilisateur valide les personnages, le plan
        et les scènes avant les illustrations.
    -   **Mode éducatif :** histoire expliquant un concept (réseaux,
        climat, sécurité numérique, etc.).
    -   **Mode adaptation :** transformer un texte fourni par
        l'utilisateur en storyboard, sans reproduire automatiquement des
        œuvres protégées.
9.  **Contrôle créatif**
    -   Régénérer le scénario, une scène, un dialogue ou une image
        séparément.
    -   Modifier l'ambiance : joyeuse, mystérieuse, épique, dramatique.
    -   Modifier le style artistique sans réécrire l'histoire.
    -   Favoris et historique des versions.
10. **Assistant de révision**
    -   Vérifier la longueur des dialogues, la présence d'un début et
        d'une conclusion, et les incohérences détectables dans les
        descriptions.
    -   Proposer des améliorations que l'utilisateur accepte ou refuse.
    -   Ne pas prétendre garantir la cohérence narrative
        automatiquement.
11. **Bibliothèque de projets**
    -   Sauvegarder les histoires, personnages, prompts et images.
    -   Reprendre une création ultérieurement.
    -   Dupliquer un projet pour créer une variante.
12. **Présentation professionnelle**
    -   Interface avec étapes visibles : idée → scénario → personnages →
        illustrations → édition → export.
    -   Progression par tâche, messages d'erreur utiles et possibilité
        de relancer une étape.
    -   Démonstration avec un projet préchargé en cas de réseau ou de
        quota indisponible.

### 4.3 Extensions facultatives --- uniquement si le MVP est stable

-   Narration audio des dialogues avec synthèse vocale.
-   Effets sonores ou musique d'ambiance libres de droits.
-   Génération de couverture alternative.
-   Traduction et adaptation des dialogues.
-   Partage par lien ou galerie publique avec consentement.
-   Collaboration multi-utilisateur.
-   Personnalisation par LoRA sur un petit jeu de données autorisé.
-   Application mobile ou déploiement cloud.

**Règle de périmètre :** les extensions ne doivent pas retarder la
génération d'une BD courte, l'édition ciblée et l'export PDF.

## 5. Dimension IA générative : modèles et rôle

### 5.1 LLM --- génération textuelle

Le LLM produit : - le synopsis et le titre ; - les fiches de personnages
; - le découpage en scènes et cases ; - les dialogues et descriptions
visuelles ; - les variantes et révisions demandées.

**Contrôle important :** demander une sortie JSON selon un schéma
précis, valider les champs, limiter la longueur des dialogues et prévoir
une correction ou une nouvelle tentative en cas de sortie invalide.

### 5.2 Modèle de diffusion --- illustrations finales

Un modèle de diffusion préentraîné est utilisé pour : - générer les
portraits des personnages ; - produire les illustrations des scènes ; -
effectuer des variations contrôlées ou des transformations
image-to-image si disponibles.

Le modèle préentraîné permet d'obtenir un résultat visuel convaincant
sans entraîner un grand modèle depuis zéro. L'application doit isoler le
fournisseur/modèle derrière une interface pour pouvoir changer de
solution.

### 5.3 VAE --- expérimentation pédagogique

Entraîner un petit VAE sur un dataset d'images adapté et légalement
utilisable (par exemple Fashion-MNIST ou un petit jeu de
visages/illustrations autorisé) afin de : - encoder des images dans un
espace latent ; - reconstruire des images ; - interpoler entre deux
vecteurs latents ; - visualiser l'effet des dimensions latentes.

Le VAE peut servir de **module expérimental séparé** ou de démonstrateur
dans la section « Laboratoire IA ». Il ne doit pas être présenté comme
le moteur principal de génération de BD si les images obtenues sont trop
simples.

### 5.4 GAN --- expérimentation pédagogique

Entraîner un DCGAN léger sur un dataset adapté et autorisé afin de : -
comprendre le rôle du générateur et du discriminateur ; - observer
l'évolution de la génération au fil des epochs ; - comparer les
échantillons et les limites (mode collapse, stabilité).

Comme pour le VAE, le GAN est un laboratoire comparatif. Il n'est pas
nécessaire de l'utiliser pour produire les illustrations finales de la
BD.

### 5.5 Tableau de répartition

  -----------------------------------------------------------------------
  Modèle                  Rôle dans le projet     Priorité
  ----------------------- ----------------------- -----------------------
  LLM                     Scénario, personnages,  Essentiel
                          dialogues, prompts      

  Diffusion préentraînée  Illustrations de        Essentiel
                          qualité                 

  VAE entraîné sur petit  Latent, reconstruction, Expérimental
  dataset                 interpolation           

  DCGAN entraîné sur      Génération adversariale Expérimental
  petit dataset           et comparaison          

  TTS                     Lecture audio           Bonus
  -----------------------------------------------------------------------

## 6. Architecture fonctionnelle

``` text
Utilisateur
   |
   v
Interface Web (Streamlit / React)
   |
   v
API Backend (FastAPI / Django)
   |
   +--> Gestion des projets et personnages
   |
   +--> Orchestrateur de génération
           |
           +--> LLM : synopsis, scènes, dialogues, prompts
           |
           +--> Validateur JSON / règles narratives
           |
           +--> Générateur d'images : diffusion
           |
           +--> Éditeur / composition des cases
           |
           +--> Export PDF / images
   |
   +--> Base de données + stockage des médias
```

### Stack recommandée

  -----------------------------------------------------------------------
  Couche                  Choix simple            Alternative
  ----------------------- ----------------------- -----------------------
  Interface               Streamlit               React

  Backend                 FastAPI                 Django

  LLM                     API ou modèle local     autre fournisseur
                          selon ressources        compatible

  Diffusion               API hébergée ou         autre modèle
                          Diffusers local         préentraîné

  Traitement image        Pillow                  OpenCV

  PDF                     ReportLab               outil de composition
                                                  équivalent

  Données                 SQLite pour MVP         PostgreSQL

  Validation              Pydantic                JSON Schema

  Versionnement           Git + GitHub/GitLab     ---
  -----------------------------------------------------------------------

**Recommandation de faisabilité :** commencer avec Streamlit + FastAPI
ou Streamlit seul pour réduire la complexité. Ajouter React et une
architecture plus lourde seulement si le temps le permet.

## 7. Parcours utilisateur de démonstration

1.  L'utilisateur saisit une idée : « Une étudiante découvre un robot
    qui protège les jardins de Casablanca ».
2.  Il choisit le genre aventure, le style manga et 4 cases.
3.  Le LLM génère titre, synopsis, personnages et storyboard.
4.  L'utilisateur valide ou modifie le scénario.
5.  Le système génère les portraits de référence.
6.  Les illustrations des cases sont générées avec les descriptions et
    références disponibles.
7.  L'utilisateur modifie un dialogue et régénère uniquement la case 3.
8.  L'application assemble la BD et exporte un PDF.
9.  Une page laboratoire montre une comparaison VAE/GAN et des exemples
    générés.

## 8. Évaluation scientifique

L'évaluation doit porter sur des critères observables, avec un petit jeu
de tests défini à l'avance.

### Texte

-   Respect du thème et des contraintes.
-   Cohérence entre les scènes.
-   Lisibilité et longueur des dialogues.
-   Taux de sorties JSON valides.
-   Évaluation humaine sur une grille simple.

### Images

-   Correspondance entre illustration et description de scène.
-   Lisibilité visuelle et qualité esthétique évaluées par utilisateurs.
-   Cohérence du personnage entre plusieurs cases (grille d'évaluation
    humaine).
-   Temps moyen et taux d'échec de génération.

### Application

-   Temps nécessaire pour produire une BD.
-   Taux de réussite du parcours complet.
-   Nombre d'étapes pouvant être relancées sans perdre le travail.
-   Tests de validation des entrées et de l'export.

### Comparaison expérimentale

-   VAE : qualité de reconstruction, évolution de la loss, interpolation
    latente.
-   GAN : qualité qualitative des échantillons, stabilité et exemples de
    mode collapse.
-   Diffusion : comparaison de prompts/styles ou paramètres sur un petit
    ensemble de scènes.

Éviter de promettre une métrique unique parfaite pour la qualité
créative. Utiliser une combinaison de mesures techniques et d'évaluation
humaine.

## 9. Risques et stratégies anti-blocage

  -----------------------------------------------------------------------
  Risque                              Prévention / solution
  ----------------------------------- -----------------------------------
  Quotas ou coût des API              Limiter le nombre d'images, mettre
                                      en cache, prévoir un mode démo
                                      pré-généré

  GPU insuffisant                     Utiliser une API ou un modèle plus
                                      léger; ne pas entraîner la
                                      diffusion depuis zéro

  Personnages incohérents             Portrait de référence, descriptions
                                      stables, régénération ciblée;
                                      annoncer la limite

  Texte illisible dans les images     Générer les illustrations sans
                                      texte puis composer dialogues et
                                      bulles avec Pillow

  LLM produit un JSON invalide        Schéma Pydantic, validation et une
                                      tentative de réparation

  Génération lente                    Progression par étapes, génération
                                      asynchrone, aperçu dès qu'une case
                                      est prête

  Scope trop large                    Prioriser MVP; bonus uniquement
                                      après tests et export fiables

  Données/licences                    Utiliser des datasets et modèles
                                      dont les licences autorisent
                                      l'usage prévu; documenter les
                                      sources
  -----------------------------------------------------------------------

## 10. Planning indicatif sur 8 semaines

  -----------------------------------------------------------------------
  Semaine                             Livrable
  ----------------------------------- -----------------------------------
  1                                   Cahier des charges, choix des
                                      modèles, maquettes et architecture

  2                                   Interface, gestion de projet et
                                      stockage

  3                                   Génération LLM : scénario,
                                      personnages, storyboard JSON

  4                                   Génération d'images et prompts par
                                      scène

  5                                   Éditeur, composition des cases et
                                      export PDF

  6                                   Références de personnages,
                                      régénération ciblée, gestion
                                      d'erreurs

  7                                   Laboratoire VAE/GAN, tests et
                                      évaluation

  8                                   Démo, documentation, rapport et
                                      préparation de soutenance
  -----------------------------------------------------------------------

Le planning est indicatif : si le délai est plus court, réduire d'abord
les fonctionnalités bonus et conserver le MVP.

## 11. Livrables

-   Application web fonctionnelle.
-   Code source versionné et instructions d'installation.
-   Jeu de démonstration avec histoire préchargée.
-   Rapport présentant architecture, modèles, expérimentations et
    limites.
-   Grille d'évaluation et résultats.
-   Démonstration vidéo ou soutenance avec génération et export d'une
    BD.
-   Fiche de provenance/licence des modèles et datasets utilisés.

## 12. Critères de réussite

Le projet est considéré comme réussi si : - une idée peut être
transformée en BD courte sans intervention technique ; - le scénario est
structuré et modifiable ; - les illustrations sont générées et associées
aux bonnes scènes ; - une case peut être régénérée sans perdre le reste
du projet ; - l'export PDF est lisible ; - les expérimentations VAE et
GAN sont reproductibles et expliquées ; - les limites, coûts et choix de
modèles sont documentés.

## 13. Formulation courte à présenter au professeur

> **StoryWorld AI : conception d'une plateforme multimodale de création
> de bandes dessinées par IA générative.**\
> Le système transforme une idée utilisateur en scénario structuré,
> personnages, dialogues et illustrations, puis assemble les éléments
> dans une BD exportable. Le projet combine un LLM pour la génération
> textuelle, un modèle de diffusion préentraîné pour les images, et une
> étude expérimentale de VAE et GAN sur des jeux de données adaptés.
> L'objectif est de proposer une application créative fonctionnelle tout
> en évaluant la qualité, la cohérence et les limites des modèles
> génératifs.

------------------------------------------------------------------------

**Périmètre conseillé :** réaliser d'abord une BD de 3 à 4 cases avec
génération textuelle, illustrations, édition ciblée et export PDF. Les
fonctions avancées et le laboratoire VAE/GAN viennent ensuite, selon le
temps disponible.
