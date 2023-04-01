from ..tools import *
import asyncio

class But(Button, Tools):
    def __init__(self, client, channel, user = None):
        self.client = client
        self.channel = channel
        self.user = user
        if self.user is not None:
            super().__init__(style=discord.ButtonStyle.blurple, label=str(user))
        else:
            super().__init__(style=discord.ButtonStyle.blurple, label="supprimer")

    async def callback(self, interaction: discord.Interaction):
        await self.edit_cupidon(interaction)
    
    async def edit_cupidon(self, interaction: discord.Interaction):
        data = self.get_data(self.channel.id)
        if interaction.user.id not in data["role_user"]["cupidon"]:
            return
        if self.user is not None and self.user != "validation": #si il vote pour qlqun
            if self.user.id in data["data_role"]["cupidon"]: #si l'utilisateur est deja renseigné
                data["data_role"]["cupidon"].remove(self.user.id) #suppression de la personne
                description = " + ".join([str(self.client.get_user(user)) for user in data["data_role"]["cupidon"]])
            else:
                if len(data["data_role"]["cupidon"]) == 2: #si il a deja choisit 2 personnes
                    return
                else:
                    data["data_role"]["cupidon"].append(self.user.id) #ajout de la personne
                    description = " + ".join([str(self.client.get_user(user)) for user in data["data_role"]["cupidon"]])
        else: #si il valide
            if self.user is None:
                data["data_role"]["cupidon"] = [] #reset
                description = ""
            else:
                if len(data["data_role"]["cupidon"]) == 2:
                    description = "les nouveaux amoureux sont " + " et ".join([str(self.client.get_user(user)) for user in data["data_role"]["cupidon"]])
                    self.view.clear_items()
                    data["phase"] = "voyante"
                    for amoureux in data["data_role"]["cupidon"]:
                        amoureux = self.client.get_user(amoureux)
                        channel_amoureux: discord.TextChannel = self.client.get_channel(data["channels"]["amoureux"])
                        await channel_amoureux.set_permissions(amoureux, read_messages = True, send_messages = True, read_message_history=True)
                        await channel_amoureux.send(f"{amoureux.mention} voici ton salon de discussion entre amoureux")
                else:
                    return
        await interaction.response.edit_message(embed = discord.Embed(title = "Choix des Amoureux :", description = description).set_footer(text = self.client.get_user(data["role_user"]["cupidon"][0])), view = self.view)
        self.push_data({str(self.channel.id) : data})


class ViewBut(View, Tools):
    def __init__(self, client, channel, users, message):
        super().__init__(timeout = 30)
        self.channel = channel
        self.client = client
        self.message = message
        for user in users:
            self.add_item(But(client, channel, user))
        self.validation = But(client, channel, "validation")
        self.add_item(But(client, channel, None))
        self.add_item(self.validation)
    
    async def on_timeout(self) -> None:
        data = self.get_data(str(self.channel.id))
        data["phase"] = "voyante"
        if len([data["data_role"]["cupidon"]]) == 0:
            data["data_role"]["cupidon"] = __import__("random").choices(data["liste_participant_en_vie"], k=2)
            self.clear_items()
            await self.message.edit(embed = discord.Embed(title = "Choix des Amoureux :", description = "les nouveaux amoureux sont " + " et ".join([str(self.client.get_user(user)) for user in data["data_role"]["cupidon"]])).set_footer(text = self.client.get_user(data["role_user"]["cupidon"][0])), view = self)
            self.push_data({str(self.channel.id) : data})
            for amoureux in data["data_role"]["cupidon"]:
                amoureux = self.client.get_user(amoureux)
                channel_amoureux: discord.TextChannel = self.client.get_channel(data["channels"]["amoureux"])
                await channel_amoureux.set_permissions(amoureux, read_messages = True, send_messages = True, read_message_history=True)
                await channel_amoureux.send(f"{amoureux.mention} voici ton salon de discussion entre amoureux")


class Cupidon(Tools):
    async def cupidon(self, channel, client):
        data = self.get_data(channel.id)
        role = data["role_user"].get("cupidon", None)
        if role is not None:
            users = []
            for user in data["liste_participant_en_vie"]:
                users.append(client.get_user(user))
            message = self.mp(client.get_user(data["role_user"]["cupidon"][0]), embed = discord.Embed(title = "Choix des Amoureux :", description = ""))
            await message.edit(view = ViewBut(client, channel, users, message))
        else:
            data["phase"] = "voyante"
            self.push_data({str(channel.id) : data})