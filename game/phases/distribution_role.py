from ..tools import *
import discord

import random
class Distribution(Tools):
    async def distribution(self, channel: discord.TextChannel, client):
        data = self.get_data(channel_id = channel.id)
        users = data["liste_participant"]
        roles = [role for role in data["liste_role"]]
        if "voleur" in roles:
            for _ in range(2):
                while True:
                    role = random.choice(roles)
                    if role != "voleur":
                        roles.remove(role)
                        data["data_role"]["voleur"].append(role)
                        break
        for user in users:
            _role = random.choice(roles)
            role = _role
            await self.mp(client.get_user(user), discord.Embed(title = "Role :", description = role))

            if role == "loup-blanc":
                data["data_role"]["loup-blanc"]["user_id"] = user
                role = "loup"

            if role == "loup":
                channel_loup: discord.TextChannel = client.get_channel(data["channels"]["loup"])
                await channel_loup.set_permissions(client.get_user(user), read_messages = True, send_messages = True, read_message_history=True)
                await channel_loup.send(f"{client.get_user(user).mention} voici ton salon de vote lors de la nuit")

            if role == "chien-loup":
                data["data_role"]["chien-loup"]["user_id"] = user
            
            if role == "enfant-sauvage":
                data["data_role"]["enfant-sauvage"]["user_id"] = user

            if role in data["role_user"]:
                data["role_user"][role].append(user)
            else:
                data["role_user"][role] = [user]
                
            data["user_role"][user] = role
            roles.remove(_role)
            
        self.push_data({str(channel.id) : data})
        await channel.send("distribution des roles faite")