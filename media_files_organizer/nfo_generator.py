from datetime import date
from fileinfo import FileInfo

class NFO:

    def __init__(self, data, type="tvshow", base_path="/data/anime", series_dir=None, season_dir=None):
        self.data = data
        if type != "tvshow" and type != "movie":
            raise ValueError("Type must be either 'tvshow' or 'movie'.")
        self.type = type
        self.base_path = base_path

        if series_dir is None:
            self.series_dir = self.data["series_name"]
        
        if season_dir is None:
            self.season_dir = f"Season {self.data['season_number']} - {self.data['season_name']}"
        
        self.full_path = f"{self.base_path}/{self.series_dir}/{self.season_dir}"


    def _validate_data_tvshow(self):
        """Validate the data."""
        if not self.data:
            raise ValueError("Data cannot be empty.")
    
    def _gen_file_info_part(self, filepath):
        """Generate the file info part of the NFO file."""
        fileinfo = FileInfo.get_media_info(filepath)
        print(fileinfo)

        nfo = f"""
  <fileinfo>
    <streamdetails>
      <video>
        <codec>{fileinfo["video"]["codec"]}</codec>
        <micodec>{fileinfo["video"]["micodec"]}</micodec>
        <bitrate>{fileinfo["video"]["bitrate"]}</bitrate>
        <width>{fileinfo["video"]["width"]}</width>
        <height>{fileinfo["video"]["height"]}</height>
        <aspect>{fileinfo["video"]["aspect"]}</aspect>
        <aspectratio>{fileinfo["video"]["aspect"]}</aspectratio>
        <framerate>{fileinfo["video"]["framerate"]}</framerate>
        <scantype>{fileinfo["video"]["scantype"]}</scantype>
        <default>{fileinfo["video"]["default"]}</default>
        <forced>{fileinfo["video"]["forced"]}</forced>
        <duration>{fileinfo["video"]["duration"]}</duration>
        <durationinseconds>{fileinfo["video"]["durationinseconds"]}</durationinseconds>
      </video>
      <audio>
        <codec>{fileinfo["audio"][0]["codec"]}</codec>
        <micodec>{fileinfo["audio"][0]["micodec"]}</micodec>
        <bitrate>{fileinfo["audio"][0]["bitrate"]}</bitrate>
        <language>{fileinfo["audio"][0]["language"]}</language>
        <scantype>{fileinfo["audio"][0]["scantype"]}</scantype>
        <channels>{fileinfo["audio"][0]["channels"]}</channels>
        <samplingrate>{fileinfo["audio"][0]["samplingrate"]}</samplingrate>
        <default>{fileinfo["audio"][0]["default"]}</default>
        <forced>{fileinfo["audio"][0]["forced"]}</forced>
      </audio>
    </streamdetails>
  </fileinfo>
"""
        return nfo



    def generate_tvshow_episode(self, episode_number, episode, filepath):
        """Generate a tvshow episode NFO file."""
        genres = self.data["genres"]
        #ep = self.data["episodes"][episode_number]
        ep = episode
        release_date_str = ep["air_date"]
        if release_date_str.isnumeric():
            year = date(int(release_date_str)).year
        else:
            year = ""
        
        s_num = str(self.data["season_number"])
        if s_num and len(s_num) < 2:
            s_num = f"0{s_num}"

        ep_num = str(ep["episode_number"])
        
        if ep_num and len(ep_num) < 2:
            ep_num = f"0{ep_num}"

        nfo = f"""<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<episodedetails>
  <plot>{ep["overview"]}</plot>
  <lockdata>false</lockdata>
  <dateadded>{ep["air_date"]}</dateadded>
  <title>{ep["episode_name"]}</title>
  <director></director>
  <rating>{ep["community_rating"]}</rating>
  <year>{year}</year>
  <showtitle>{self.data["series_name"]}</showtitle>
  <episode>{ep["episode_number"]}</episode>
  <season>{self.data["season_number"]}</season>
  <aired>{ep["air_date"]}</aired>
  <imdbid></imdbid>
  <tvdbid></tvdbid>
  <kitsuid></kitsuid>
  <runtime></runtime>
  <art>
    <poster>{self.full_path}/{self.data["series_name"]}/{self.data['season_name']}.S{s_num}E{ep_num}.{ep["episode_name"]}.thumb.jpg</poster>
  </art>
"""
        for genre in genres:
            nfo += f"  <genre>{genre}</genre>\n"
        
        for actor in ep["actors"]:
            name = actor["name"]
            initial = name[0].upper()
            nfo += f"""  <actor>
    <name>{name}</name>
    <role>{actor["role"]}</role>
    <type>Actor</type>
    <thumb>/config/data/metadata/People/{initial}/{name}/folder.jpg</thumb>
  </actor>
"""

        nfo += self._gen_file_info_part(filepath)
        nfo += "</episodedetails>"
        return nfo




    def generate_tvshow_season(self):
        """Generate a tvshow NFO file."""
        release_date_str = self.data["release_date"]
        if release_date_str.isnumeric():
            year = date(int(release_date_str)).year
        else:
            year = ""
        
        nfo = f"""<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<season>
  <plot>{self.data["overview"]}</plot>
  <outline>{self.data["overview"]}</outline>
  <lockdata>false</lockdata>
  <dateadded>{date.today()}</dateadded>
  <title>Season {self.data["season_number"]} - {self.data["season_name"]}</title>
  <seasonnumber>{self.data["season_number"]}</seasonnumber>
  <writer></writer>
  <credits></credits>
  <rating>{self.data["community_rating"]}</rating>
  <year>{year}/year>
  <premiered>{self.data["release_date"]}</premiered>
  <releasedate>{self.data["release_date"]}</releasedate>
"""
        for actor in self.data["actors"]:
            name = actor["name"]
            initial = name[0].upper()
            nfo += f"""  <actor>
    <name>{name}</name>
    <role>{actor["role"]}</role>
    <type>Actor</type>
    <thumb>/config/data/metadata/People/{initial}/{name}/folder.jpg</thumb>
  </actor>
"""
        nfo += "</season>"
        
        return nfo