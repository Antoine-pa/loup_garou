from ..tools import *
from collections import Counter
import asyncio

class But(Button, Tools):
    def __init__(self, client, channel, user = None):
        self.client = client
        self.channel = channel
        self.channel_loup = self.client.get_channel(self.get_data(self.channel.id)["channels"]["loup"])
        self.user = user
        if self.user is not None:
            super().__init__(style=discord.ButtonStyle.blurple, label=str(user))
        else:
            super().__init__(style=discord.ButtonStyle.blurple, label="personne")

    async def callback(self, interaction: discord.Interaction):
        await self.edit_loup(interaction)


    async def edit_loup(self, interaction):
        data = self.get_data(self.channel.id)
        if interaction.user.id not in data["role_user"]["loup"]:
            return
        if self.user is not None: #si il vote pour qlqun
            if str(interaction.user.id) in data["data_role"]["loup"]["vote"]: #si il avait deja fait un vote
                if data["data_role"]["loup"]["vote"][str(interaction.user.id)] != self.user.id: #si il vote pour une autre personne
                    data["data_role"]["loup"]["vote"][str(interaction.user.id)] = self.user.id
                    description = interaction.message.embeds[0].description + f"\n{self.client.get_user(interaction.user.id)} à voté pour {self.user.name}"
                else:
                    del data["data_role"]["loup"]["vote"][str(interaction.user.id)]
                    description = interaction.message.embeds[0].description + f"\n{self.client.get_user(interaction.user.id)} à enlevé son vote de {self.user.name}"
            else:
                data["data_role"]["loup"]["vote"][str(interaction.user.id)] = self.user.id
                description = interaction.message.embeds[0].description + f"\n{self.client.get_user(interaction.user.id)} à voté pour {self.user.name}"
        else:
            if str(interaction.user.id) in data["data_role"]["loup"]["vote"]: #si il avait deja fait un vote
                description = interaction.message.embeds[0].description + f"\n{self.client.get_user(interaction.user.id)} à enlevé son vote de {self.client.get_user(data['data_role']['loup']['vote'][str(interaction.user.id)])}"
                del data["data_role"]["loup"]["vote"][str(interaction.user.id)]
            else:
                return
                
        description = description.split("\n")
        if len(description) > 30:
            description = description[1:]
        description = "\n".join(description)
        value = []
        for user in data["role_user"]["loup"]:
            user = self.client.get_user(user)
            vote = data["data_role"]["loup"]["vote"].get(str(user.id), "personne")
            if vote != "personne":
                vote = self.client.get_user(vote)
            value.append(f"{user} => {vote}")
        embed = discord.Embed(title = "quel personne voulez vous tuer?", description=description)
        embed.add_field(name = "votes", value = "\n".join(value))
        await interaction.message.edit(embed = embed)
        self.push_data({str(self.channel.id) : data})

class ViewBut(View, Tools):
    def __init__(self, client, channel, users, message):
        super().__init__(timeout = 45)
        self.channel = channel
        self.client = client
        self.channel_loup = self.client.get_channel(self.get_data(self.channel.id)["channels"]["loup"])
        self.message = message
        users.append(None)
        for user in users:
            self.add_item(But(client, channel, user))
    
    async def on_timeout(self) -> None:
        data = self.get_data(self.channel.id)
        votes = data["data_role"]["loup"]["vote"]
        liste_vote = []
        for vote in votes.items():
            liste_vote.append(vote[1])
        res = Counter(liste_vote).most_common(2)
        if len(res) > 1 or len(res) == 0:
            await self.channel_loup.send(f"fin du vote des loups (personne n'a été tué)")
        else:
            user_kill = self.client.get_user(res[0][0])
            data["data_role"]["loup"]["kill"] = user_kill.id
            await self.channel_loup.send(f"fin du vote des loups ({user_kill.name} a été tué)")
        data["data_role"]["loup"]["vote"] = {}
        data["phase"] = "loup-blanc"
        self.clear_items()
        await self.message.edit(view = self)
        self.push_data({str(self.channel.id) : data})

class Loups(Tools):
    async def loups(self, channel, client):
        data = self.get_data(channel.id)
        role = data["role_user"].get("loup", None)
        if role is not None:
            channel_loup = client.get_channel(self.get_data(channel.id)["channels"]["loup"])
            users = []
            for user in data["liste_participant_en_vie"]:
                if user not in data["role_user"]["loup"]:
                    users.append(client.get_user(user))

            pings = "".join(client.get_user(user).mention for user in data["role_user"]["loup"])
            message = await channel_loup.send(f"{pings}\nquel personne voulez vous tuer?", embed = discord.Embed(title = "Votes", description = "---------------").set_footer(text = f"45s de vote"))
            await message.edit(view = ViewBut(client, channel, users, message))
        else:
            data["phase"] = "loup-blanc"
            self.push_data({str(channel.id) : data})
