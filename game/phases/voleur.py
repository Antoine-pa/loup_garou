from datetime import time

from discord.types.components import Component
from ..tools import *
import asyncio
import discord

from discord.ui import *
Component

class But(Button, Tools):
    def __init__(self, channel, role):
        self.channel = channel
        self.role = role
        super().__init__(style=discord.ButtonStyle.blurple, label=role)
    
    async def callback(self, interaction: discord.Interaction):
        await self.edit_voleur(interaction, role = self.role)
    
    async def edit_voleur(self, interaction, role):
        data = self.get_data(self.channel.id)
        if interaction.user.id != data["role_user"]["voleur"][0]:
            return

        data["data_role"]["voleur"] = [] #supression de la partie voleur

        del data["role_user"]["voleur"] #supression du voleur
        if role in data["role_user"]: #si il y a deja un qlqun qui porte le ce role
            data["role_user"][role].append(interaction.user.id) #on l'ajoute a la liste
        else:
            data["role_user"][role] = [interaction.user.id] #on fait la llste

        del data["user_role"][str(interaction.user.id)] #supression du voleur
        data["user_role"][str(interaction.user.id)] = role #on remplace les data de la personne

        data["phase"] = "enfant-sauvage"

        self.push_data({str(self.channel.id) : data})

        await self.mp(interaction.user, embed = discord.Embed(title = "New Role : ", description = f"tu es désormais {role}"))
        self.view.clear_items()
        await interaction.message.delete()


class ViewBut(View, Tools):
    def __init__(self, channel, roles, message):
        super().__init__(timeout = 20)
        self.channel = channel
        self.message = message
        for role in roles:
            self.add_item(But(channel, role))
    
    async def on_timeout(self) -> None:
        data = self.get_data(self.channel.id)
        if len(data["data_role"]["voleur"]) == 2:
            role = data["data_role"]["voleur"][__import__("random").randint(0, 1)]
            if role in data["role_user"]: #si il y a deja un qlqun qui porte le ce role
                data["role_user"][role].append(data["role_user"]["voleur"][0]) #on l'ajoute a la liste
            else:
                data["role_user"][role] = [data["role_user"]["voleur"][0]] #on fait la llste
            del data["user_role"][str(data["role_user"]["voleur"][0])] #supression du voleur
            data["user_role"][str(data["role_user"]["voleur"][0])] = role
            self.mp(self.client.get_user(data["role_user"]["voleur"][0]), embed = discord.Embed(title = "New Role : ", description = f"tu es désormais {role} (choix automatique)"))
            del data["role_user"]["voleur"]
        self.clear_items()
        data["phase"] = "enfant-sauvage"
        self.push_data({str(self.channel.id) : data})
        await self.message.delete()



class Voleur(Tools):
    async def voleur(self, channel, client):
        data = self.get_data(channel.id)
        role = data["role_user"].get("voleur", None)
        if role is not None:
            await channel.send("voleur")
            user = client.get_user(data["role_user"]["voleur"][0])
            message = await self.mp(user, embed = discord.Embed(title = "Voleur :", description = f"quel role veux tu choisir?\n"))
            await message.edit(view = ViewBut(channel, data['data_role']['voleur']))
        else:
            self.get_data(str(channel.id))
            data["phase"] = "enfant-sauvage"
            self.push_data({str(channel.id) : data})