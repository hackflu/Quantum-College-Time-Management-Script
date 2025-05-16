import os
import discord
from dotenv import load_dotenv
import requests

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

class Search:
    def wikipedia_search(self,query):
        response = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}")
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def youtube_search(self,query):
        search_url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "key": os.getenv('YOUTUBE'),
            "maxResults": 10
        }
        response = requests.get(search_url, params=params)
        search_results = response.json()
        return search_results['items']

    def google_search(self,query):
        search_url = "https://serpapi.com/search.json"
        params = {
            "q": query,
            "api_key": os.getenv('SERAPE')
        }
        response = requests.get(search_url, params=params)
        search_results = response.json()
        result = search_results['organic_results'][:5]  # Get top 5 results
        return result


class Myclass(Search,discord.Client):
    async def on_ready(self):
        print(f"Logged in as {self.user}")

    async def on_message(self,message):
        if message.author == self.user:
            return

        if message.content.startswith("!wiki"):
            query = message.content[len('!wiki '):].replace(" ", "_")
            result = self.wikipedia_search(query)
            if result:
                title = result['title']
                summary = result['extract']
                page_url = result['content_urls']['desktop']['page']
                await message.channel.send(f"**{title}**\n{summary}\n{page_url}")
            else:
                await message.channel.send("No Wikipedia Found!")
        # Condition to search YouTube Url
        elif message.content.startswith("!you"):
            query = message.content[len('!you '):].replace(" ", "_")
            results = self.youtube_search(query)
            if results:
                youtube_url = ""
                for result in results:
                    video_title = result['snippet']['title']
                    youtube_url = f"https://www.youtube.com/watch?v={result['id']['videoId']}"
                    await message.channel.send(youtube_url)
            else:
                await message.channel.send("No Video Found!")
        # Condition to check the Google Search
        elif message.content.startswith("!search"):
            searchResult = ""
            results = self.google_search(message.content[len("!search"):])
            if results:
                for result in results:
                    searchResult = f"** {result['title']} **\n{result['link']}"
                await message.channel.send(searchResult)
            else:
                await message.channel.send("No Search result Found!")

    async def on_message_join(self,member):
        provide_role = discord.utils.get(member.guild.role , name="Member")

        # Added these functionalities to give a role to Welcome Member …
        if provide_role:
            await member.add_roles(provide_role)

        # Added these functionalities to Welcome the member
        welcome_channel = discord.utils.get(member.guild.text_channels,name="Orion")
        if welcome_channel:
            await welcome_channel.send(f"Welcome to the Server, {member.mention}")
        else:
            print("No member Found to Welcome")
        try:
            await member.send(f"Welcome to {member.guild.name}, {member.name}! We're glad to have you here.")
        except discord.Forbidden:
            print(f"Could not send a private message to {member.name}.")


client = Myclass(intents=intents)
client.run(os.getenv('TOKEN'))