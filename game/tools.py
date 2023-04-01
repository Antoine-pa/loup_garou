import json
import discord
from discord.ui import *

class Tools:

    def get_data(self, channel_id = None):
        with open("./data.json", "r") as file:
            data = json.load(file)
        if channel_id is not None:
            return data.get(str(channel_id), None)
        return data

    def push_data(self, data, overwrite = False):
        if not overwrite:
            all_data = self.get_data()
            for channel in data.items():
                all_data[channel[0]] = channel[1]
        else:
            all_data = data
        with open('./data.json', "w") as file:
            file.write(json.dumps(all_data, indent=4))

    async def make_description(self, client, channel, message = None, view = None):
        data = self.get_data(str(channel.id))
        table = self.maketable(client, data["positions"])
        embed = discord.Embed(title = "Partie :", description = f"table de jeu :\n\n{table}")
        embed.add_field(name = "Owner :", value = client.get_user(data["createur"]).name)
        embed.add_field(name = "Participants :", value = "\n".join([client.get_user(user_id).name for user_id in data["liste_participant"]]))
        if data["liste_role"] != []:
            embed.add_field(name = "Roles :", value = "\n".join([role for role in data["liste_role"]]))
        if message is None and view is not None:
            message = await channel.send(embed = embed, view = view)
            return message
        if view is None:
            await message.edit(embed = embed)
        else:
            await message.edit(embed = embed, view = view)
        return message

    async def mp(self, user, embed, view = None):
        dm = await user.create_dm()
        try:
            if view is None:
                message = await dm.send(embed = embed)
                return message
            message = await dm.send(embed = embed, view = view)
        except discord.Forbidden:
            pass
        return message

    
    async def check_win(self, data):
        if len(data["liste_participant_en_vie"]) == 1 and data["data_role"]["loup-blanc"]["user_id"] is not None:
            return "loup-blanc"
        elif data["liste_role"].count("loup") == len(data["liste_role"]):
            return "loup"
        elif len(data["data_role"]["cupidon"]) != 0:
            if len(data["data_role"]["cupidon"]) == len(data["liste_role"]):
                return "amoureux"
        elif data["liste_role"].count("loup") == 0:
            return "village"
        else:
            return False
    
    def kill(self, channel: discord.TextChannel, client, user: discord.User):
        data = self.get_data(channel.id)
        if user.id in data["liste_participant_en_vie"]:
            data["liste_participant_en_vie"].remove(user.id)
            data["role_user"][data["user_role"][str(user.id)]].remove(user.id)
            data["liste_role"].remove(data["user_role"][str(user.id)])
            del data["user_role"][str(user.id)]
            if str(user.id) in data["data_role"]["voyante"]:
                del data["data_role"]["voyante"][str(user.id)]
            if user.id == data["data_role"]["enfant-sauvage"]["user_id"]:
                data["data_role"]["enfant-sauvage"]["user_id"] = None
                data["data_role"]["enfant-sauvage"]["model"] = None
            elif user.id == data["data_role"]["chien-loup"]["user_id"]:
                data["data_role"]["chien-loup"]["user_id"] = None
                data["data_role"]["chien-loup"]["role"] = None
        
            data = self.del_position(data, user)
            self.push_data({str(channel.id) : data})
    
    def change_role(self, data, user_id, new_role, save = False):
        old_role = data["user_role"][str(user_id)]
        
        data["liste_role"].remove(old_role)
        data["liste_role"].append(new_role)

        data["user_role"][str(user_id)] = new_role

        if new_role in data["role_user"]:
            data["role_user"][new_role].append(user_id)
        else:
            data["role_user"][new_role] = [user_id]
        
        if str(user_id) in data["data_role"]["voyante"]:
            data["data_role"]["voyante"][str(user_id)] = new_role
        
        return data
    
    def maketable(self, client, positions: list):
        table = "```\n"
        droite = []
        gauche = []
        longueur = 25
        decalage = 0

        for pos in positions:
            positions[positions.index(pos)][0] = self.all_ascii(str(client.get_user(positions[positions.index(pos)][0])))
            if len(positions) % 2 != 0:
                if positions.index(pos) != 1:
                    if positions.index(pos) >= round(len(positions)/2):
                        if round(len(str(pos[0]))/2) > decalage:
                            decalage = round(len(str(pos[0]))/2)    
            else:
                if positions.index(pos) >= round(len(positions)/2):
                    if round(len(str(pos[0]))/2) > decalage:
                        decalage = round(len(str(pos[0]))/2)
        
        if len(positions) % 2 != 0:
            user = positions[0][0]
            longueur_line = longueur - len(str(user)) - 2
            start_line = "-" * round(longueur_line/2)
            end_line = "-" * (longueur_line - len(start_line))
            table += "\n" + " " * decalage + "+" + start_line + " " + str(user) + " " + end_line + "+"
            positions.remove(positions[0])
        else:
            table += "\n" + " " * decalage + "+" + "-" * longueur + "+"
        table += "\n" + " " * decalage + "|" + " " * (longueur) + "|"

        for pos in positions:
            if positions.index(pos) < round(len(positions)/2):
                droite.append(pos[0])
            else:
                gauche.append(pos[0])

        for i in range(round(len(positions)/2)):
            user1 = str(gauche[-(i+1)])
            user2 = str(droite[i])
            add_place_center = " " * (round((len(user1)-1)/2))
            center = " " * (longueur - len(user1) - len(user2) + 2 + int(len(user2)/2)) + add_place_center
            if len(user1) % 2 == 0:
                center = center + " "
            table += "\n" + " " * (decalage - (len(user1) - len(add_place_center)) + 1) + user1 + center + user2
            table += "\n" + " " * decalage + "|" + " " * (longueur) + "|"
        table += "\n" + " " * decalage + "+" + "-" * longueur + "+"
        table += "\n```"
        return table
    
    def add_position(self, data, user):
        data["positions"][0][1]["droite"] = user.id
        data["positions"][-1][1]["gauche"] = user.id
        data["positions"].append([user.id, {"droite" : data["positions"][-1][0], "gauche" : data["positions"][0][0]}])
        return data
    
    def del_position(self, data, user):
        for pos in data["positions"]:
            if pos[0] == user.id:
                index_pos = data["positions"].index(pos)
                data["positions"].remove(pos)
        index_pos_droite = index_pos - 1
        index_pos_gauche = index_pos
        if len(data["positions"]) == index_pos: #if out value
            index_pos_gauche = 0
        data["positions"][index_pos_droite][1]["gauche"] = data["positions"][index_pos_gauche][0]
        data["positions"][index_pos_gauche][1]["droite"] = data["positions"][index_pos_droite][0]
        return data
    
    def all_ascii(self, text: str):
        for char in text:
            value = ord(char)
            if value >= 128:
                text = text.replace(char, "")
        return text
        