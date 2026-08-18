warning: in the working copy of 'app/service.py', LF will be replaced by CRLF the next time Git touches it
[1mdiff --git a/app/service.py b/app/service.py[m
[1mindex 2d943a8..03f44d3 100644[m
[1m--- a/app/service.py[m
[1m+++ b/app/service.py[m
[36m@@ -1,17 +1,142 @@[m
[31m-﻿from app.models import Anime, Season[m
[32m+[m[32m﻿import requests[m
[32m+[m
[32m+[m[32mfrom app.models import Anime, Season, Episode, Source[m
 from app.sources.anilist import AniListProvider[m
[31m-from app.sources.animesalt import AnimeSaltProvider[m
 [m
 [m
 class AnimeService:[m
 [m
[32m+[m[32m    ANIVEXA_URL = "https://anivexa.vercel.app"[m
[32m+[m
[32m+[m[32m    PROVIDER_PRIORITY = [[m
[32m+[m[32m        "reanime",[m
[32m+[m[32m        "anikoto",[m
[32m+[m[32m        "animegg",[m
[32m+[m[32m        "anineko",[m
[32m+[m[32m        "anidbapp",[m
[32m+[m[32m        "2dhive",[m
[32m+[m[32m        "anizone",[m
[32m+[m[32m        "anibd",[m
[32m+[m[32m        "kaa",[m
[32m+[m[32m        "animedunya",[m
[32m+[m[32m    ][m
[32m+[m
     def __init__(self):[m
         self.anilist = AniListProvider()[m
[31m-        self.animesalt = AnimeSaltProvider()[m
[32m+[m
[32m+[m[32m        self.session = requests.Session()[m
[32m+[m[32m        self.session.headers.update({[m
[32m+[m[32m            "User-Agent": "Anime-VLC/1.0",[m
[32m+[m[32m            "Accept": "application/json",[m
[32m+[m[32m        })[m
 [m
     def search(self, query):[m
         return self.anilist.search(query)[m
 [m
[32m+[m[32m    def _get_anivexa_episodes(self, anilist_id):[m
[32m+[m[32m        response = self.session.get([m
[32m+[m[32m            f"{self.ANIVEXA_URL}/episodes/{anilist_id}",[m
[32m+[m[32m            timeout=25,[m
[32m+[m[32m        )[m
[32m+[m[32m        response.raise_for_status()[m
[32m+[m
[32m+[m[32m        data = response.json()[m
[32m+[m
[32m+[m[32m        if isinstance(data, dict):[m
[32m+[m[32m            return data.get("results", data)[m
[32m+[m
[32m+[m[32m        return {}[m
[32m+[m
[32m+[m[32m    def _get_stream(self, provider, anilist_id, category, episode_id):[m
[32m+[m[32m        try:[m
[32m+[m[32m            response = self.session.get([m
[32m+[m[32m                f"{self.ANIVEXA_URL}/{episode_id.lstrip('/')}",[m
[32m+[m[32m                timeout=30,[m
[32m+[m[32m            )[m
[32m+[m
[32m+[m[32m            response.raise_for_status()[m
[32m+[m
[32m+[m[32m            data = response.json()[m
[32m+[m
[32m+[m[32m            if isinstance(data, dict):[m
[32m+[m[32m                data = data.get("results", data)[m
[32m+[m
[32m+[m[32m            streams = data.get("streams", []) if isinstance(data, dict) else [][m
[32m+[m
[32m+[m[32m            for stream in streams:[m
[32m+[m[32m                if not isinstance(stream, dict):[m
[32m+[m[32m                    continue[m
[32m+[m
[32m+[m[32m                url = stream.get("url")[m
[32m+[m
[32m+[m[32m                if not url:[m
[32m+[m[32m                    continue[m
[32m+[m
[32m+[m[32m                return Source([m
[32m+[m[32m                    language=category.upper(),[m
[32m+[m[32m                    url=url,[m
[32m+[m[32m                    server=provider,[m
[32m+[m[32m                    quality=stream.get("quality"),[m
[32m+[m[32m                )[m
[32m+[m
[32m+[m[32m        except (requests.RequestException, ValueError):[m
[32m+[m[32m            pass[m
[32m+[m
[32m+[m[32m        return None[m
[32m+[m
[32m+[m[32m    def _build_episode(self, episode_number, title, provider_data, anilist_id):[m
[32m+[m[32m        sources = [][m
[32m+[m
[32m+[m[32m        episodes = provider_data.get("episodes", {})[m
[32m+[m
[32m+[m[32m        for category in ("sub", "dub"):[m
[32m+[m[32m            entries = episodes.get(category, [])[m
[32m+[m
[32m+[m[32m            if not isinstance(entries, list):[m
[32m+[m[32m                continue[m
[32m+[m
[32m+[m[32m            matching = None[m
[32m+[m
[32m+[m[32m            for entry in entries:[m
[32m+[m[32m                if not isinstance(entry, dict):[m
[32m+[m[32m                    continue[m
[32m+[m
[32m+[m[32m                try:[m
[32m+[m[32m                    number = int(entry.get("number"))[m
[32m+[m[32m                except (TypeError, ValueError):[m
[32m+[m[32m                    continue[m
[32m+[m
[32m+[m[32m                if number == episode_number:[m
[32m+[m[32m                    matching = entry[m
[32m+[m[32m                    break[m
[32m+[m
[32m+[m[32m            if not matching:[m
[32m+[m[32m                continue[m
[32m+[m
[32m+[m[32m            episode_id = matching.get("id")[m
[32m+[m
[32m+[m[32m            if not episode_id:[m
[32m+[m[32m                continue[m
[32m+[m
[32m+[m[32m            source = self._get_stream([m
[32m+[m[32m                provider_data["_provider"],[m
[32m+[m[32m                anilist_id,[m
[32m+[m[32m                category,[m
[32m+[m[32m                episode_id,[m
[32m+[m[32m            )[m
[32m+[m
[32m+[m[32m            if source:[m
[32m+[m[32m                sources.append(source)[m
[32m+[m
[32m+[m[32m        if not sources:[m
[32m+[m[32m            return None[m
[32m+[m
[32m+[m[32m        return Episode([m
[32m+[m[32m            number=episode_number,[m
[32m+[m[32m            title=title,[m
[32m+[m[32m            sources=sources,[m
[32m+[m[32m        )[m
[32m+[m
     def get_anime(self, query):[m
         results = self.anilist.search(query)[m
 [m
[36m@@ -29,15 +154,17 @@[m [mclass AnimeService:[m
             or query[m
         )[m
 [m
[32m+[m[32m        anilist_id = result["id"][m
[32m+[m
         anime = Anime([m
[31m-            canonical_id=f"anilist:{result['id']}",[m
[32m+[m[32m            canonical_id=f"anilist:{anilist_id}",[m
             title=title,[m
             alternate_titles=[[m
                 value[m
                 for value in [[m
                     title_data.get("english"),[m
                     title_data.get("romaji"),[m
[31m-                    title_data.get("native")[m
[32m+[m[32m                    title_data.get("native"),[m
                 ][m
                 if value and value != title[m
             ],[m
[36m@@ -46,30 +173,43 @@[m [mclass AnimeService:[m
             popularity=result.get("popularity"),[m
         )[m
 [m
[31m-        episode_count = result.get("episodes") or 0[m
[31m-[m
[31m-        # Convert title to the source's normal slug format.[m
[31m-        slug = title.lower()[m
[32m+[m[32m        try:[m
[32m+[m[32m            anivexa = self._get_anivexa_episodes(anilist_id)[m
[32m+[m[32m        except requests.RequestException as exc:[m
[32m+[m[32m            print(f"Anivexa unavailable: {exc}")[m
[32m+[m[32m            return anime[m
 [m
[31m-        import re[m
[31m-        slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")[m
[32m+[m[32m        providers = anivexa.get("providers", {})[m
 [m
         season = Season(number=1)[m
 [m
[32m+[m[32m        episode_count = result.get("episodes") or 0[m
[32m+[m
         for episode_number in range(1, episode_count + 1):[m
[31m-            source_slug = f"{slug}-1x{episode_number}"[m
[32m+[m[32m            episode = None[m
[32m+[m
[32m+[m[32m            for provider_name in self.PROVIDER_PRIORITY:[m
[32m+[m[32m                provider_data = providers.get(provider_name)[m
 [m
[31m-            try:[m
[31m-                episode = self.animesalt.parse_episode(source_slug)[m
[32m+[m[32m                if not isinstance(provider_data, dict):[m
[32m+[m[32m                    continue[m
 [m
[31m-                if episode.number is not None:[m
[31m-                    season.episodes.append(episode)[m
[32m+[m[32m                provider_data = dict(provider_data)[m
[32m+[m[32m                provider_data["_provider"] = provider_name[m
 [m
[31m-            except Exception as exc:[m
[31m-                print([m
[31m-                    f"Skipping episode {episode_number}: {exc}"[m
[32m+[m[32m                episode = self._build_episode([m
[32m+[m[32m                    episode_number,[m
[32m+[m[32m                    None,[m
[32m+[m[32m                    provider_data,[m
[32m+[m[32m                    anilist_id,[m
                 )[m
 [m
[32m+[m[32m                if episode:[m
[32m+[m[32m                    break[m
[32m+[m
[32m+[m[32m            if episode:[m
[32m+[m[32m                season.episodes.append(episode)[m
[32m+[m
         anime.seasons.append(season)[m
 [m
[31m-        return anime[m
[32m+[m[32m        return anime[m
\ No newline at end of file[m
