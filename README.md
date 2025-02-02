# media-files-organizer

## Instruções

1. Criar diretamente na base de dados a serie (`/database/pt_database.sqlite3`)
2. Correr o comando:
    
    ```
    python .\media_files_organizer\popdb.py season scrape "https://wikidobragens.fandom.com/pt/wiki/url_da_serie" <id_da_serie_na_bd> <numero_da_season>
    ```
3. Depois correr o comando:

    ```
    python .\media_files_organizer\cli.py <tmdb_id> "<path_to_series_dir>" --tvshow -s <numero_da_season> <nome_da_season>
    ```

    nome da season é opcional. Útil para as season de Pokémon que têm nomes

