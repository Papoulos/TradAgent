# Outil de Traduction par Agent

Cet outil de traduction littéraire multi-agents utilise des modèles de langage (LLM) pour traduire de longs textes en respectant le style de l'auteur. Il fonctionne en plusieurs étapes, chacune pouvant être exécutée indépendamment.

## Fonctionnalités

-   **Profilage de l'Auteur** : Analyse un échantillon de texte pour créer un profil détaillé du style de l'auteur (ton, vocabulaire, structure des phrases).
-   **Création de Glossaire** : Extrait les termes ambigus, culturels ou importants du texte source et génère un glossaire de traduction personnalisé.
-   **Traduction Intelligente** : Divise le texte en blocs, les traduit en utilisant le contexte du profil et du glossaire, et nettoie les répertoires temporaires après l'opération.
-   **Agent Réviseur (Optionnel)** : Un agent LLM supplémentaire peut être activé pour réviser et harmoniser les blocs traduits, assurant une cohérence stylistique sur l'ensemble du document.
-   **Gestion de Projet** : Crée un répertoire de projet dédié pour chaque fichier source, où sont stockés tous les artefacts (profil, glossaire, sortie finale).

## Workflow

L'outil suit un workflow en trois étapes principales :

1.  **`profile`** : Vous commencez par créer un profil stylistique de l'auteur. Cette étape génère un fichier `_profile.json`.
2.  **`preprocessing`** : Ensuite, vous générez un glossaire de traduction basé sur le texte source et le profil de l'auteur. Cette étape crée un fichier `_glossary.json`.
3.  **`translate`** : Enfin, vous lancez la traduction du document. Cette étape utilise le profil et le glossaire pour générer la traduction finale.

## Installation

1.  **Clonez le dépôt :**
    ```bash
    git clone <repository_url>
    cd <repository_name>
    ```

2.  **Installez les dépendances :**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configurez les clés API :**
    Créez un fichier `.env` à la racine du projet et ajoutez vos clés API.
    ```
    # .env
    GOOGLE_API_KEY="VOTRE_CLE_API_GOOGLE_ICI"
    ```

4.  **Configurez le fournisseur LLM :**
    Ouvrez `config.py` pour choisir et configurer votre fournisseur de modèle de langage.
    -   `LLM_TOOL` : `"gemini"` ou `"ollama"`.
    -   Configurez les noms de modèles spécifiques pour chaque fournisseur.

## Utilisation

L'outil s'exécute en ligne de commande. Voici les instructions pour chaque étape.

### 1. Créer le Profil de l'Auteur

Cette étape analyse le style de l'auteur à partir d'un échantillon de texte.

-   `--step profile` : Spécifie l'étape de profilage.
-   `--source` : Chemin vers le fichier texte source.
-   `--author` : Nom de l'auteur (obligatoire pour cette étape).

**Exemple :**
```bash
python main.py --step profile --source "sources/mon_livre.txt" --author "George Orwell"
```
Un fichier `mon_livre_profile.json` sera créé dans le dossier `sources/mon_livre/`.

### 2. Générer le Glossaire

Cette étape crée un glossaire de traduction basé sur le texte source et le profil de l'auteur.

-   `--step preprocessing` : Spécifie l'étape de prétraitement.
-   `--source` : Chemin vers le fichier texte source.

**Exemple :**
```bash
python main.py --step preprocessing --source "sources/mon_livre.txt"
```
Un fichier `mon_livre_glossary.json` sera créé dans le dossier `sources/mon_livre/`.

### 3. Traduire le Texte

C'est l'étape finale qui traduit l'intégralité du document.

-   `--step translate` : Spécifie l'étape de traduction.
-   `--source` : Chemin vers le fichier texte source.
-   `--max-blocks` (Optionnel) : Limite la traduction à un nombre spécifique de blocs pour des tests rapides.
-   `--reviewer` (Optionnel) : Active l'agent réviseur pour une harmonisation stylistique.

**Exemple de base :**
```bash
python main.py --step translate --source "sources/mon_livre.txt"
```

**Exemple avec l'agent réviseur :**
```bash
python main.py --step translate --source "sources/mon_livre.txt" --reviewer
```
La traduction finale sera enregistrée dans `sources/mon_livre/mon_livre_translated.txt`.
