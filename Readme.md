# Outil de Traduction par Agent

Cet outil utilise des agents LangChain et la bibliothèque LangExtract de Google pour traduire de longs textes en plusieurs étapes.

## Configuration

1.  **Clonez le dépôt :**
    ```bash
    git clone <repository_url>
    cd <repository_name>
    ```

2.  **Installez les dépendances :**
    Assurez-vous d'avoir Python 3 installé. Ensuite, installez les bibliothèques requises.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configurez les clés API :**
    Renommez le fichier `.env.example` en `.env` et ajoutez vos clés API. Pour l'instant, seule une clé API Google est nécessaire si vous utilisez Gemini.
    ```
    # .env
    GOOGLE_API_KEY="VOTRE_CLE_API_GOOGLE_ICI"
    ```

4.  **Configurez le fournisseur LLM :**
    Ouvrez le fichier `config.py` pour configurer le fournisseur de modèle de langage et les modèles spécifiques à utiliser.

    -   `LLM_TOOL` : Choisissez votre fournisseur LLM. Les options sont `"gemini"` ou `"ollama"`.
    -   Configurez les noms de modèles pour la création du glossaire et l'évaluation en fonction du fournisseur que vous avez choisi.

## Utilisation

L'outil est exécuté depuis la ligne de commande et nécessite deux arguments principaux pour fonctionner.

### Arguments

-   `--step` : (Requis) Spécifie l'étape du processus de traduction à exécuter.
    -   `preprocessing` : Exécute l'étape de prétraitement, qui génère un glossaire à partir du fichier source et le fait évaluer par un LLM.
-   `--source` : (Requis pour l'étape `preprocessing`) Spécifie le chemin d'accès au fichier texte source que vous souhaitez traduire.

### Exemple de Commande

Pour exécuter l'étape de prétraitement sur un fichier nommé `mon_texte.txt` :
```bash
python main.py --step preprocessing --source mon_texte.txt
```
