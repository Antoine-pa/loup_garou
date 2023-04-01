from ..tools import *
import asyncio

class But(Button, Tools):
    def __init__(self, client, channel, user = None):
        self.client = client
        self.channel = channel
        self.user = user
        super().__init__(style=discord.ButtonStyle.blurple, label=str(user))

    async def callback(self, interaction: discord.Interaction):
        await self.edit_voyante(interaction)
    
    async def edit_voyante(self, interaction):
        data = self.get_data(self.channel.id)
        if interaction.user.id not in data["role_user"]["voyante"]:
            return
        view: ViewBut = self.view
        view.clear_items()
        data["data_role"]["voyante"][str(self.user.id)] = data["user_role"][str(self.user.id)] #ajout de la personne
        await interaction.response.edit_message(view = view)
        await interaction.message.channel.send(embed = discord.Embed(title = str(self.user), description = f"le role de {self.user} est {data['user_role'][str(self.user.id)]}"))
        data["phase"] = "loup"
        self.push_data({str(self.channel.id) : data})


class ViewBut(View, Tools):
    def __init__(self, client, channel, users, message):
        super().__init__(timeout = 20)
        self.channel = channel
        self.client = client
        self.message = message
        for user in users:
            self.add_item(But(client, channel, user))
    
    async def on_timeout(self) -> None:
        data = self.get_data(str(self.channel.id))
        data["phase"] = "loup"
        self.clear_items()
        await self.message.edit(view = self)
        self.push_data({str(self.channel.id) : data})


class Voyante(Tools):
    async def voyante(self, channel, client):
        data = self.get_data(channel.id)
        role = data["role_user"].get("voyante", None)
        if role is not None:
            users = []
            for user in data["liste_participant_en_vie"]:
                if user not in data["data_role"]["voyante"] and user not in data["role_user"]["voyante"]:
                    users.append(client.get_user(user))
            message = await self.mp(client.get_user(data["role_user"]["voyante"][0]), embed = discord.Embed(title = "Quel joueur voulez vous voir?", description = "Vous connaissez déjà :" + "\n" + "\n".join([f"{client.get_user(int(user))} ({role})" for (user, role) in data["data_role"]["voyante"].items()])))
            await message.edit(view = ViewBut(client, channel, users, message))
        else:
            data["phase"] = "loup"
            self.push_data({str(channel.id) : data})