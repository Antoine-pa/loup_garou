from discord.enums import ButtonStyle
from ..tools import *
from collections import Counter

class ButChoiceKill(Button, Tools):
    def __init__(self, channel, client, user):
        self.client = client
        self.channel = channel
        self.user = user
        if self.user is not None:
            super().__init__(style = ButtonStyle.blurple, label = str(self.user))
        else:
            super().__init__(style = ButtonStyle.blurple, label = "retour")
    
    async def callback(self, interaction: discord.Interaction):
        await self.edit_sorciere(interaction)
    
    async def edit_sorciere(self, interaction):
        view: ButView = self.view
        data = self.get_data(self.channel.id)
        if interaction.user.id != data["role_user"]["sorciere"][0]:
            return
        if self.user is not None: #si un utilisateur est renseigné
            data["data_role"]["sorciere"]["kill"] = self.user.id
            data["data_role"]["sorciere"]["tuer"] = 0
            self.push_data({str(self.channel.id) : data})
        view.clear_items()
        liste_but = ["ne rien faire"]
        if data["data_role"]["sorciere"]["tuer"] == 1:
            liste_but.append("tuer")
        if data["data_role"]["loup"]["kill"] is not None and data["data_role"]["sorciere"]["sauver"] == 1:
            liste_but.append("sauver")
        if len(liste_but) != 1:
            for name in liste_but:
                view.add_item(ButChoice(self.channel, self.client, name))
        await interaction.response.edit_message(view = view)


class ButChoice(Button, Tools):
    def __init__(self, channel, client, name):
        self.client = client
        self.channel = channel
        self.name = name
        super().__init__(style = ButtonStyle.blurple, label = self.name)

    
    async def callback(self, interaction: discord.Interaction):
        await self.edit_sorciere(interaction)
    
    async def edit_sorciere(self, interaction):
        data = self.get_data(self.channel.id)
        view: ButView = self.view
        if interaction.user.id != data["role_user"]["sorciere"][0]:
            return
        if self.name == "sauver":
            data["data_role"]["sorciere"]["sauver"] = 0
            await self.channel.send(f"tu as sauvé {self.client.get_user(data['data_role']['loup']['kill'])}")
            data["data_role"]["loup"]["kill"] = None
            self.push_data({str(self.channel.id) : data})
            view.remove_item(self)
        
        elif self.name == "tuer":
            view.clear_items()
            for user in data["liste_participant_en_vie"]:
                if user != data["role_user"]["sorciere"][0]:
                    view.add_item(ButChoiceKill(self.channel, self.client, self.client.get_user(user)))
            view.add_item(ButChoiceKill(self.channel, self.client, None))
        
        elif self.name == "ne rien faire":
            view.clear_items()
            await interaction.response.edit_message(view = view)
            data["phase"] = "vote"
            self.push_data({str(self.channel.id) : data})

        await interaction.response.edit_message(view = view)

        

class ButView(View, Tools):
    def __init__(self, client, channel, message):
        self.client = client
        self.channel = channel
        self.message = message
        super().__init__(timeout = 30)
        data = self.get_data(self.channel.id)
        liste_but = ["ne rien faire"]
        if data["data_role"]["sorciere"]["tuer"] == 1:
            liste_but.append("tuer")
        if data["data_role"]["loup"]["kill"] is not None and data["data_role"]["sorciere"]["sauver"] == 1:
            liste_but.append("sauver")
        for name in liste_but:
            self.add_item(ButChoice(self.channel, self.client, name))

    async def on_timeout(self) -> None:
        data = self.get_data(str(self.channel.id))
        data["phase"] = "vote"
        self.push_data({str(self.channel.id) : data})
        self.clear_items()
        await self.message.edit(view = self)

class Sorciere(Tools):
    async def sorciere(self, channel, client):
        data = self.get_data(channel.id)
        role = data["role_user"].get("sorciere", None)
        if role is not None and (data["data_role"]["sorciere"]["sauver"] == 1 or data["data_role"]["sorciere"]["tuer"] == 1):
            user_kill = data["data_role"]["loup"]["kill"]
            await channel.send("sorciere")
            if user_kill is not None:
                user_kill = client.get_user(user_kill).name
            else:
                user_kill = "personne"
            message = await self.mp(client.get_user(data["role_user"]["sorciere"][0]), embed = discord.Embed(description = f"{user_kill} a été tué"))
            await message.edit(view = ButView(client, channel, message))
        else:
            data["phase"] = "vote"
            self.push_data({str(channel.id) : data})