import asyncio
from ..tools import *
from collections import Counter

class But(Button, Tools):
    def __init__(self, channel, client, user):
        self.channel = channel
        self.client = client
        self.user = user
        if user is not None:
            super().__init__(style = discord.ButtonStyle.blurple, label = str(self.user))
        else:
            super().__init__(style = discord.ButtonStyle.blurple, label = "personne")
    
    async def callback(self, interaction: discord.Interaction):
        await self.edit_vote(interaction)
    
    async def edit_vote(self, interaction: discord.Interaction):
        data = self.get_data(self.channel.id)
        view: ViewBut = self.view

        if interaction.user.id not in data["liste_participant_en_vie"]:
            return True
        if self.user is not None: #si il vote pour uen personne
            if str(interaction.user.id) not in data["data_role"]["vote"]: #si il vote pour la premiere fois
                data["data_role"]["vote"][str(interaction.user.id)] = self.user.id
                description = interaction.message.embeds[0].description + f"\n{self.client.get_user(interaction.user.id)} à voté pour {self.user.name}"
            else:
                if data["data_role"]["vote"][str(interaction.user.id)] == self.user.id: #si il revote pour la meme personne
                    del data["data_role"]["vote"][str(self.user.id)]
                    description = interaction.message.embeds[0].description + f"\n{self.client.get_user(interaction.user.id)} à enlevé son vote de {self.user.name}"
                else:
                    data["data_role"]["vote"][str(interaction.user.id)] = self.user.id
                    description = interaction.message.embeds[0].description + f"\n{self.client.get_user(interaction.user.id)} à voté pour {self.user.name}"
        else:
            if str(interaction.user.id) in data["data_role"]["vote"]: #si il avait deja voté 
                del data["data_role"]["vote"][str(self.user.id)]
                description = interaction.message.embeds[0].description + f"\n{self.client.get_user(interaction.user.id)} à enlevé son vote de {self.client.get_user(data['data_role']['loup']['vote'][str(interaction.user.id)])}"
            else:
                return True
        self.push_data({str(self.channel.id) : data})
        description = description.split("\n")
        if len(description) > 30:
            description = description[1:]
        description = "\n".join(description)
        embed = discord.Embed(title = "Vote :", description = description)
        value = []
        for user in data["liste_participant_en_vie"]:
            user = self.client.get_user(user)
            vote = data['data_role']['vote'].get(str(user.id), "personne")
            if vote != "personne":
                vote = self.client.get_user(vote)
            value.append(f"{user} => {vote}")
        embed.add_field(name = "votes", value = "\n".join(value))
        await interaction.response.edit_message(embed = embed, view = view)
        return True


class ViewBut(View, Tools):
    def __init__(self, client, channel, message):
        self.channel = channel
        self.client = client
        self.message = message
        super().__init__(timeout = 60)
        data = self.get_data(str(self.channel.id))
        for user in data["liste_participant_en_vie"]:
            self.add_item(But(self.channel, self.client, self.client.get_user(user)))
        self.add_item(But(self.channel, self.client, None))

    async def on_timeout(self) -> None:
        data = self.get_data(self.channel.id)
        liste_vote = []
        for vote in data["data_role"]["vote"].items():
            liste_vote.append(vote[1])
        res = Counter(liste_vote).most_common(2)
        if len(res) > 1 or len(res) == 0:
            await self.channel.send(f"fin du vote (personne n'a été tué)")
        else:
            user_kill = self.client.get_user(res[0][0])
            role = data['user_role'][str(user_kill.id)]
            if data["data_role"]["chien-loup"]["user_id"] ==  user_kill.id:
                role = "chien-loup (loup ou villageois ???)"
            elif data["data_role"]["enfant-sauvage"]["user_id"] == user_kill.id:
                role = role = "enfant-sauvage (loup ou villageois ???)"
            elif data["data_role"]["loup-blanc"]["user_id"] == user_kill.id:
                role = "loup blanc"
            if data["data_role"]["enfant-sauvage"]["model"] == user_kill.id:
                data = self.change_role(data, data["data_role"]["enfant-sauvage"]["user_id"], "loup")
                await self.mp(self.client.get_user(data["data_role"]["enfant-sauvage"]["user_id"]), embed = discord.Embed(title = "Votre model est mort", description = "Votre model vient de mourir vous venez donc loup garou"))

            await self.channel.send(f"fin du vote ({user_kill} a été tué({role}))")
            self.kill(self.channel, self.client, user_kill)

        data = self.get_data(self.channel.id)
        data["data_role"]["vote"] = {}
        data["phase"] = "voyante"
        self.push_data({str(self.channel.id) : data})
        self.clear_items()
        await self.message.edit(view = self)

        res = await self.check_win(data)
        if res:
            await self.channel.send(f"{res} win")
            return
        await self.channel.send("le village se rendort")


class Vote(Tools):
    async def vote(self, channel, client):
        data = self.get_data(str(channel.id))
        people_kill = []
        if data["data_role"]["loup"]["kill"] is not None:
            people_kill.append(client.get_user(data["data_role"]["loup"]["kill"]))
        if data["data_role"]["sorciere"]["kill"] is not None:
            people_kill.append(client.get_user(data["data_role"]["sorciere"]["kill"]))
        if data["data_role"]["loup-blanc"]["kill"] is not None:
            people_kill.append(client.get_user(data["data_role"]["loup-blanc"]["kill"]))


        if len(people_kill) == 0:
            embed = discord.Embed(title = "Le village se réveille", description = "personne n'est mort cette nuit")
        else:
            sentence = "personne est morte cette nuit :"
            if len(people_kill) > 1:
                sentence = "personnes sont mortes cette nuit :"
            people = []
            for user in people_kill:
                role = data["user_role"][str(user.id)] 
                if data["data_role"]["chien-loup"]["user_id"] ==  user.id:
                    role = "chien-loup (loup ou villageois ???)"
                elif data["data_role"]["enfant-sauvage"]["user_id"] == user.id:
                    role = "enfant-sauvage (loup ou villageois ???)"
                elif data["data_role"]["loup-blanc"]["user_id"] == user.id:
                    role = "loup blanc"
                if data["data_role"]["enfant-sauvage"]["model"] == user.id:
                    data = self.change_role(data, data["data_role"]["enfant-sauvage"]["user_id"], "loup")
                    await self.mp(self.client.get_user(data["data_role"]["enfant-sauvage"]["user_id"]), embed = discord.Embed(title = "Votre model est mort", description = "Votre model vient de mourir vous venez donc loup garou"))
                
                if user.id in data["data_role"]["cupidon"]:
                    people.append(f'{user} ({role}, amoureux)')
                    data["data_role"]["cupidon"].remove(user.id)
                    people_kill.append(client.get_user(data["data_role"]["cupidon"][0]))
                else:
                    people.append(f'{user} ({role})')
                self.push_data({str(channel.id) : data})

                self.kill(channel, client, user)
                
            data = self.get_data(channel.id)
            data["data_role"]["loup"]["kill"] = None
            data["data_role"]["sorciere"]["kill"] = None
            self.push_data({str(channel.id) : data})
            people = '\n'.join(people)
            embed = discord.Embed(title = "Le village se réveille", description = f"{len(people_kill)} {sentence}\n{people}")
        await channel.send(embed = embed)


        res = await self.check_win(data)
        if res:
            await channel.send(f"{res} win")
            return


        message = await channel.send("quel personne voulez vous tuer?", embed = discord.Embed(title = "Votes", description = "---------------").set_footer(text = f"15s de vote"))
        await message.edit(view = ViewBut(client, channel, message))