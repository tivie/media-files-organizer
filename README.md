# media-files-organizer

## Instruções


### Instalação

1. Instalar o python 3.

    O Python 3 costuma vir pré-instalado no linux e no MacOs.
    
    No windows o instalador está disponível [aqui](https://www.python.org/downloads/) ou pode ser usado um package manager (scoop ou chocolatey ou wget)

2. Instalar o pacote do Python chamado Poetry (https://python-poetry.org/docs/) 

3. Obter uma API KEY do TMDB. Ver instruções [aqui](https://developer.themoviedb.org/docs/getting-started)

4. Instalar o https://mediaarea.net/en/MediaInfo 

    Este programa lê as meta informações dos ficheiros como codecs, resolução, bitrate, etc... Importante para gerar os ficheiros NFOs

5. Criar um ficheiro `.env` na raiz do repositório (ao lado deste ficheiro readme). Deve ter o seguinte conteúdo:

    ```env
    TMDB_API_KEY=<API KEY DO TMDB>
    DB_PATH="database/pt_db.sqlite3"
    ```

6. (Opcional) Instalar um GUI para editar/explorar a base de dados. Recomendo o https://sqlitebrowser.org/

### Utilização

1. Criar a serie diretamente na base de dados:
    
    1. Primeiro procurar o ID da serie no TMDB. Está no url. Exemplo: Pókemon --> url: https://www.themoviedb.org/tv/60572/ --> TMDB ID: 60572
    2. Abrir a base de dados com o programa SQLITE Browser
    3. Na tabela tv_show criar uma entrada nova. Preencher as colunas tmdb_id, title e original title. O resto é opcional. A coluna id **não deve ser preenchida**
    4. Guardar as alterações
    5. Apontar qual é o id da serie recem criada (o id da serie na nossa base de dados, não do TMDB). Vai ser preciso depois

2. Correr o comando no terminal (Windows: Powershell; Linux: Bash):
    
    ```
    python .\media_files_organizer\popdb.py season scrape "https://wikidobragens.fandom.com/pt/wiki/url_da_serie" <id_da_serie_na_bd> <numero_da_season>
    ```

    Este comando vai ao site wikidobragens, faz scrape das vozes em português e guarda-as na base de dados.

3. Depois correr o comando:

    ```
    python .\media_files_organizer\cli.py <tmdb_id> "<path_to_series_dir>" --tvshow -s <numero_da_season> <nome_da_season:OPCIONAL>
    ```

    Este comando altera o nome dos ficheiros, normalizando-os. Usa também as informações dos ficheiros, do TMDB e da base de dados para criar os ficheiros NFO com meta informação para
    o KODI / Jellyfin / Plex.
    
    o nome da season é opcional. Útil para as season de Pokémon que têm nomes específicos.

