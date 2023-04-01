from ..tools import *

class But(Button, Tools):
    def __init__(self, channel, client, name):
        self.channel = channel
        self.client = client
        self.name = name
        super().__init__(style = discord.ButtonStyle.blurple, label = str(self.name))
    
    async def callback(self, interaction: discord.Interaction):
        await self.edit_(interaction) #change name
    
    async def edit_(self, interaction: discord.Interaction): #change name
        data = self.get_data(self.channel.id)

        self.view.clear_items()
        await interaction.response.edit_message(view = self.view)
        
        data["phase"] = "" #add next phase
        self.push_data({str(self.channel.id) : data})


class ViewBut(View, Tools):
    def __init__(self, channel, client, message):
        self.channel = channel
        self.client = client
        self.message = message
        super().__init__(timeout = None) #change the timeout
        for name in []:  #add list
            self.add_item(But(self.channel, self.client, name))
    
    async def on_timeout(self):
        data = self.get_data(self.channel.id)
        if True: #change the condition

            self.clear_items()
            await self.message.edit(view = self)

            data["phase"] = "" #add next phase
            self.push_data({str(self.channel.id) : data})
    
class Personnage(Tools): #change name
    async def perso(self, channel, client): #change name
        data = self.get_data(channel.id)
        role = data["role_user"].get("role", None)
        if role is not None:
            message = await channel.send(embed = discord.Embed(title = "", description = "")) #change
            await message.edit(view = ViewBut(channel, client, message))
        else:
            data["phase"] = "" #add next phase
            self.push_data({str(channel.id) : data})
        