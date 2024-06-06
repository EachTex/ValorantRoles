#coding=utf-8
from discord.ui import Select, View, Button, Modal
from discord.ext import commands
import discord, requests, os, json

api_key = "YOUR_HENRIK_API_KEY_HERE"

en_ranks = {
    "ランク無し": "Unranked",
    "アイアン": "Iron",
    "ブロンズ": "Bronze",
    "シルバー": "Silver",
    "ゴールド": "Gold",
    "プラチナ": "Platinum",
    "ダイヤモンド": "Diamond",
    "アセンダント": "Ascendant",
    "イモータル": "Immortal",
    "レディアント": "Radiant"
}

class ValorantRolesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    valorantroles = discord.SlashCommandGroup(name = f"valorantroles", description = f"VALORANTロールに関するコマンドです。")

    @valorantroles.command(name = f"panel", description = f"ロール設定用のパネルを配置します。※管理者専用")
    async def valorantroles_panel(self, ctx):
        if ctx.author.guild_permissions.administrator is False:
            e = discord.Embed(title = "エラー", description = f"権限がありません！", color = 0xfa0909)
            await ctx.respond(embed = e, ephemeral = True)
            return

        else:
            e = discord.Embed(title = "パネル設定", description = f"配置するパネルをカスタマイズできます。\n設定が完了したら、「送信」ボタンを押してパネルを配置してください。", color = 0x3ab37b)
            preview = discord.Embed(title = "VALORANT認証", description = f"VALORANTのIDを入力して、ランクロールを設定しましょう！", color = 0xfd4556)
            v = View()
            title = Button(
                label = f"タイトルを編集する",
                style = discord.ButtonStyle.blurple,
                custom_id = f"valorantroles:edit_panel:title"
            )
            desc = Button(
                label = f"概要を編集する",
                style = discord.ButtonStyle.blurple,
                custom_id = f"valorantroles:edit_panel:desc"
            )
            send = Button(
                label = f"送信",
                style = discord.ButtonStyle.green,
                custom_id = f"valorantroles:edit_panel:send"
            )
            for item in [title, desc, send]:
                v.add_item(item)

            await ctx.respond(embeds = [e, preview], view = v, ephemeral = True)

    @valorantroles.command(name = F"role", description = f"付与するロールを設定します。※管理者専用")
    async def valorantroles_setrole(self, ctx):
        if ctx.author.guild_permissions.administrator is False:
            e = discord.Embed(title = "エラー", description = f"権限がありません！", color = 0xfa0909)
            await ctx.respond(embed = e, ephemeral = True)
            return

        e = discord.Embed(title = "付与するロールを設定する", description = f"各ランクに付与するロールを選択してください：", color = 0x3ab37)
        ranks = [
            "ランク無し",
            "アイアン",
            "ブロンズ",
            "シルバー",
            "ゴールド",
            "プラチナ",
            "ダイヤモンド",
            "アセンダント",
            "イモータル",
            "レディアント"
        ]
        if os.path.isfile(f"./valorantroles/{ctx.guild.id}.json") is False:
            v = View()
            for rank in ranks:
                e.add_field(name = f"{rank}", value = f"❔｜未設定")
                b = Button(
                    label = f"{rank}",
                    style = discord.ButtonStyle.blurple,
                    custom_id = f"valorantroles:set_rankrole:{rank}"
                )
                v.add_item(b)
            b = Button(
                label = f"設定完了",
                style = discord.ButtonStyle.green,
                custom_id = f"valorantroles:set_rankrole:complete",
                row = 3
            )
            v.add_item(b)

        else:
            with open(f"./valorantroles/{ctx.guild.id}.json", "r") as f:
                data = json.load(f)
                f.close()

            v = View()
            for rank in ranks:
                if en_ranks[rank] in data.keys():
                    _roleid = data[(en_ranks[rank])]
                    try:
                        _role = ctx.guild.get_role(int(_roleid)).mention
                        _style = discord.ButtonStyle.blurple
                    except:
                        _role = f"❔｜未設定"
                        _style = discord.ButtonStyle.red
                    e.add_field(name = f"{rank}", value = f"{_role}")
                    b = Button(
                        label = f"{rank}",
                        style = _style,
                        custom_id = f"valorantroles:set_rankrole:{rank}"
                    )
                    v.add_item(b)
                else:
                    e.add_field(name = f"{rank}", value = f"❔｜未設定")
                    b = Button(
                        label = f"{rank}",
                        style = discord.ButtonStyle.red,
                        custom_id = f"valorantroles:set_rankrole:{rank}"
                    )
                    v.add_item(b)
            b = Button(
                label = f"設定完了",
                style = discord.ButtonStyle.green,
                custom_id = f"valorantroles:set_rankrole:complete",
                row = 3
            )
            v.add_item(b)

        await ctx.respond(embed = e, view = v, ephemeral = True)

    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        if interaction.custom_id == None or not interaction.custom_id.startswith("valorantroles:"):
            return

        command = interaction.custom_id[len("valorantroles:"):].split(":")

        if command[0] == "edit_panel":
            prev = interaction.message.embeds[1]
            if command[1] == "title":
                _title = prev.title
                m = Modal(
                    title = "パネルのタイトルを編集する",
                    custom_id = f"valorantroles:edit_panel:set_title"
                )
                m.add_item(
                    discord.ui.InputText(
                        label = f"新しいタイトル",
                        placeholder = f"例: VALORANT認証",
                        value = _title,
                    )
                )
                await interaction.response.send_modal(m)

            elif command[1] == "set_title":
                _value = interaction.data['components'][0]['components'][0]['value']
                _prev = discord.Embed(title = _value, description = prev.description, color = prev.color)
                await interaction.response.edit_message(embeds = [interaction.message.embeds[0], _prev])

            elif command[1] == "desc":
                _desc = prev.description
                m = Modal(
                    title = "パネルの概要を編集する",
                    custom_id = f"valorantroles:edit_panel:set_desc"
                )
                m.add_item(
                    discord.ui.InputText(
                        label = f"新しい概要",
                        placeholder = f"例: VALORANTのIDを入力して、ランクロールを設定しましょう！",
                        value = _desc,
                    )
                )
                await interaction.response.send_modal(m)

            elif command[1] == "set_desc":
                _value = interaction.data['components'][0]['components'][0]['value']
                _prev = discord.Embed(title = prev.title, description = _value, color = prev.color)
                await interaction.response.edit_message(embeds = [interaction.message.embeds[0], _prev])

            elif command[1] == "send":
                _e = interaction.message.embeds[1]
                v = View()
                b = Button(
                    label = f"認証する",
                    style = discord.ButtonStyle.green,
                    custom_id = f"valorantroles:register"
                )
                v.add_item(b)
                msg = await interaction.message.channel.send(embed = _e, view = v)
                e = discord.Embed(title = "設定完了", description = f"パネルを配置しました。", color = 0x3ab37b)
                _v = View()
                _b = Button(
                    label = f"メッセージに飛ぶ",
                    style = discord.ButtonStyle.gray,
                    url = msg.jump_url
                )
                _v.add_item(_b)
                await interaction.response.edit_message(embed = e, view = _v)

        elif command[0] == "register":
            with open(f"./valorant_puuid.json", "r") as f:
                userdata = json.load(f)
                f.close()

            if str(interaction.user.id) in userdata.keys():
                e = discord.Embed(title = "ID確認", description = f"あなたのアカウントはすでに紐づけられています！\nこのまま登録を続行しますか？", color = 0x3ab37b)
                v = View()
                _b1 = Button(
                    label = f"続行",
                    style = discord.ButtonStyle.green,
                    custom_id = f"valorantroles:registered_id"
                )
                _b2 = Button(
                    label = f"キャンセル",
                    style = discord.ButtonStyle.red,
                    custom_id = f"valorantroles:regist_cancel"
                )
                v.add_item(_b1)
                v.add_item(_b2)
                await interaction.response.send_message(embed = e, view = v, ephemeral = True)

            else:
                m = Modal(
                    title = "VALORANT IDを登録する",
                    custom_id = f"valorantroles:register_id"
                )
                m.add_item(
                    discord.ui.InputText(
                        label = f"あなたのVALORANT ID",
                        placeholder = f"例: xMasa#1022",
                        required = True
                    )
                )
                await interaction.response.send_modal(m)

        elif command[0] == "registered_id":
            with open(f"./valorant_puuid.json", "r") as f:
                userdata = json.load(f)
                f.close()

            e = discord.Embed(title = "アカウント認証中…", description = f"数秒ほどお待ちください…\n(10秒以上認証できなかった場合、自動でキャンセルされます。)", color = 0x3ab37b)
            await interaction.response.edit_message(embed = e, view = None)

            _puuid = userdata[str(interaction.user.id)]
            req = requests.get(url = f"https://api.henrikdev.xyz/valorant/v1/by-puuid/account/{_puuid}?api_key={api_key}", timeout = 10)
            if req.json()['status'] != 200:
                e = discord.Embed(title = "エラー", description = f"認証サーバーに接続できませんでした。\n詳しくは管理者にお問い合わせください。", color = 0xfa0909)
                e.set_footer(text = f"Error: {req.json()['errors'][0]['message']}")
                await interaction.followup.edit_message(interaction.message.id, embed = e)
                return

            _puuid = req.json()['data']['puuid']
            _region = req.json()['data']['region']
            _name = f"{req.json()['data']['name']}#{req.json()['data']['tag']}"
            _req = requests.get(url = f"https://api.henrikdev.xyz/valorant/v2/by-puuid/mmr/{_region}/{_puuid}?api_key={api_key}", timeout = 10)
            if _req.json()['status'] != 200:
                e = discord.Embed(title = "エラー", description = f"認証サーバーに接続できませんでした。\n詳しくは管理者にお問い合わせください。", color = 0xfa0909)
                e.set_footer(text = f"Error: {req.json()['errors'][0]['message']}")
                await interaction.followup.edit_message(interaction.message.id, embed = e)
                return

            _current = _req.json()['data']['current_data']['currenttierpatched']
            _max = _req.json()['data']['highest_rank']['patched_tier']

            e = discord.Embed(title = "登録完了", description = f"ユーザー名: `{_name}`\n現在のランク: {_current}\n最高ランク: {_max}\nで登録しました。", color = 0xfd4556)
            await interaction.followup.edit_message(interaction.message.id, embed = e)

            if os.path.isfile(f"./valorantroles/{interaction.guild.id}.json") is True:
                with open(f"./valorantroles/{interaction.guild.id}.json", "r") as f:
                    data = json.load(f)
                    f.close()

                if _current == "Radiant":
                    pass
                else:
                    _current = _current[:-2]

                _roleid = int(data[_current])
                try:
                    _role = interaction.guild.get_role(_roleid)
                    await interaction.user.add_roles(_role)
                except:
                    pass

            else:
                return

        elif command[0] == "register_id":
            _value = interaction.data['components'][0]['components'][0]['value']
            if "#" not in _value:
                e = discord.Embed(title = "エラー", description = f"VALORANT IDが正しくありません！", color = 0xfa0909)
                await interaction.response.send_message(embed = e, ephemeral = True)
                return
            e = discord.Embed(title = "ID確認", description = f"あなたのIDは `{_value}` でよろしいですか？", color = 0x3ab37b)
            v = View()
            _conf = Button(
                label = f"登録する",
                style = discord.ButtonStyle.green,
                custom_id = f"valorantroles:registering"
            )
            _canc = Button(
                label = f"キャンセル",
                style = discord.ButtonStyle.red,
                custom_id = f"valorantroles:regist_cancel"
            )
            v.add_item(_conf)
            v.add_item(_canc)
            await interaction.response.send_message(embed = e, view = v, ephemeral = True)

        elif command[0] == "registering":
            e = discord.Embed(title = "アカウント認証中…", description = f"数秒ほどお待ちください…\n(10秒以上認証できなかった場合、自動でキャンセルされます。)", color = 0x3ab37b)
            await interaction.response.edit_message(embed = e, view = None)
            _e = interaction.message.embeds[0]
            _desc = _e.description
            _value = _desc.split("`")[1]
            _id = _value.split("#")
            req = requests.get(url = f"https://api.henrikdev.xyz/valorant/v1/account/{_id[0]}/{_id[1]}?api_key={api_key}", timeout = 10)
            if req.json()['status'] != 200:
                e = discord.Embed(title = "エラー", description = f"認証サーバーに接続できませんでした。\n詳しくは管理者にお問い合わせください。", color = 0xfa0909)
                await interaction.followup.edit_message(interaction.message.id, embed = e)
                return

            _puuid = req.json()['data']['puuid']
            _region = req.json()['data']['region']
            _req = requests.get(url = f"https://api.henrikdev.xyz/valorant/v2/by-puuid/mmr/{_region}/{_puuid}?api_key={api_key}", timeout = 10)
            if _req.json()['status'] != 200:
                e = discord.Embed(title = "エラー", description = f"認証サーバーに接続できませんでした。\n詳しくは管理者にお問い合わせください。", color = 0xfa0909)
                await interaction.followup.edit_message(interaction.message.id, embed = e)
                return

            _current = _req.json()['data']['current_data']['currenttierpatched']
            _max = _req.json()['data']['highest_rank']['patched_tier']

            e = discord.Embed(title = "登録完了", description = f"ユーザー名: `{_value}`\n現在のランク: {_current}\n最高ランク: {_max}\nで登録しました。", color = 0xfd4556)
            await interaction.followup.edit_message(interaction.message.id, embed = e)

            with open(f"./valorant_puuid.json", "r") as f:
                userdata = json.load(f)
                f.close()

            userdata[interaction.user.id] = _puuid

            with open(f"./valorant_puuid.json", "w") as f:
                json.dump(userdata, f, indent = 4, ensure_ascii = False)
                f.close()

            if os.path.isfile(f"./valorantroles/{interaction.guild.id}.json") is True:
                with open(f"./valorantroles/{interaction.guild.id}.json", "r") as f:
                    data = json.load(f)
                    f.close()

                if _current == "Radiant":
                    pass
                else:
                    _current = _current[:-2]

                _roleid = int(data[_current])
                try:
                    _role = interaction.guild.get_role(_roleid)
                    await interaction.user.add_roles(_role)
                except:
                    pass

            else:
                return

        elif command[0] == "regist_cancel":
            e = discord.Embed(title = f"登録 - キャンセル", description = f"登録はキャンセルされました。", color = 0xfa0909)
            await interaction.response.edit_message(embed = e, view = None)

        elif command[0] == "set_rankrole":
            if command[1] != "complete":
                e = discord.Embed(title = f"{command[1]} - ランクロール", description = f"付与するロールを選択してください：", color = 0x3ab37b)
                v = View()
                options = []
                for role in interaction.guild.roles:
                    if role == interaction.guild.default_role or role.managed == True:
                        pass
                    else:
                        options.append(
                            discord.SelectOption(
                                label = f"{role.id}",
                                description = f"{role.name}",
                            )
                        )
                if len(options) != 0:
                    s = Select(
                        placeholder = f"{command[1]} ...",
                        options = options,
                        custom_id = f"valorantroles:rankrole:{command[1]}"
                    )
                    v.add_item(s)
                    await interaction.response.edit_message(embed = e, view = v)
                else:
                    e = discord.Embed(title = "エラー", description = f"このサーバーには選択可能なロールがありません！", color = 0xfa0909)
                    await interaction.response.edit_message(embed = e, view = None)

            else:
                _re = interaction.message.embeds[0]
                for field in _re.fields:
                    if "❔｜未設定" in field.value:
                        e = discord.Embed(title = "エラー", description = f"未設定のロールがありますが続行しますか？", color = 0xfa0909)
                        v = View()
                        _cont = Button(
                            label = f"続行する",
                            style = discord.ButtonStyle.green,
                            custom_id = f"valorantroles:setrolecomplete"
                        )
                        v.add_item(_cont)
                        _can = Button(
                            label = f"修正する",
                            style = discord.ButtonStyle.red,
                            custom_id = f"valorantroles:setrolecancel"
                        )
                        v.add_item(_can)
                else:
                    e = discord.Embed(title = "設定完了", description = f"設定が完了しました。", color = 0x3ab37b)
                    v = None
                await interaction.response.edit_message(embed = e, view = v)

        elif command[0] == "setrolecomplete":
            e = discord.Embed(title = "設定完了", description = f"設定が完了しました。", color = 0x3ab37b)
            await interaction.response.edit_message(embed = e, view = None)

        elif command[0] == "setrolecancel":
            e = discord.Embed(title = "付与するロールを設定する", description = f"各ランクに付与するロールを選択してください：", color = 0x3ab37)
            ranks = [
                "ランク無し",
                "アイアン",
                "ブロンズ",
                "シルバー",
                "ゴールド",
                "プラチナ",
                "ダイヤモンド",
                "アセンダント",
                "イモータル",
                "レディアント"
            ]
            if os.path.isfile(f"./valorantroles/{interaction.guild.id}.json") is False:
                v = View()
                for rank in ranks:
                    e.add_field(name = f"{rank}", value = f"❔｜未設定")
                    b = Button(
                        label = f"{rank}",
                        style = discord.ButtonStyle.blurple,
                        custom_id = f"valorantroles:set_rankrole:{rank}"
                    )
                    v.add_item(b)
                b = Button(
                    label = f"設定完了",
                    style = discord.ButtonStyle.green,
                    custom_id = f"valorantroles:set_rankrole:complete",
                    row = 3
                )
                v.add_item(b)

            else:
                with open(f"./valorantroles/{interaction.guild.id}.json", "r") as f:
                    data = json.load(f)
                    f.close()

                v = View()
                for rank in ranks:
                    if en_ranks[rank] in data.keys():
                        _roleid = data[(en_ranks[rank])]
                        try:
                            _role = interaction.guild.get_role(int(_roleid)).mention
                            _style = discord.ButtonStyle.blurple
                        except:
                            _role = f"❔｜未設定"
                            _style = discord.ButtonStyle.red
                        e.add_field(name = f"{rank}", value = f"{_role}")
                        b = Button(
                            label = f"{rank}",
                            style = _style,
                            custom_id = f"valorantroles:set_rankrole:{rank}"
                        )
                        v.add_item(b)
                    else:
                        e.add_field(name = f"{rank}", value = f"❔｜未設定")
                        b = Button(
                            label = f"{rank}",
                            style = discord.ButtonStyle.red,
                            custom_id = f"valorantroles:set_rankrole:{rank}"
                        )
                        v.add_item(b)
                b = Button(
                    label = f"設定完了",
                    style = discord.ButtonStyle.green,
                    custom_id = f"valorantroles:set_rankrole:complete",
                    row = 3
                )
                v.add_item(b)

            await interaction.response.edit_message(embed = e, view = v)

        elif command[0] == "rankrole":
            if os.path.isfile(f"./valorantroles/{interaction.guild.id}.json") is False:
                data = {}
            else:
                with open(f"./valorantroles/{interaction.guild.id}.json", "r") as f:
                    data = json.load(f)
                    f.close()
            _value = command[1]
            _data = interaction.data['values'][0]
            _role = interaction.guild.get_role(int(_data))
            _rank = en_ranks[_value]
            data[_rank] = _data

            with open(f"./valorantroles/{interaction.guild.id}.json", "w") as f:
                json.dump(data, f, indent = 4, ensure_ascii = False)
                f.close()

            e = discord.Embed(title = f"{_value} - ランクロール", description = f"{_value} のランクロールを {_role.mention} に設定しました。", color = 0x3ab37b)
            v = View()
            b = Button(
                label = f"ランク選択に戻る",
                style = discord.ButtonStyle.green,
                custom_id = f"valorantroles:rankrolepanel"
            )
            v.add_item(b)
            await interaction.response.edit_message(embed = e, view = v)

        elif command[0] == "rankrolepanel":
            e = discord.Embed(title = "付与するロールを設定する", description = f"各ランクに付与するロールを選択してください：", color = 0x3ab37)
            ranks = [
                "ランク無し",
                "アイアン",
                "ブロンズ",
                "シルバー",
                "ゴールド",
                "プラチナ",
                "ダイヤモンド",
                "アセンダント",
                "イモータル",
                "レディアント"
            ]
            if os.path.isfile(f"./valorantroles/{interaction.guild.id}.json") is False:
                v = View()
                for rank in ranks:
                    e.add_field(name = f"{rank}", value = f"❔｜未設定")
                    b = Button(
                        label = f"{rank}",
                        style = discord.ButtonStyle.blurple,
                        custom_id = f"valorantroles:set_rankrole:{rank}"
                    )
                    v.add_item(b)
                b = Button(
                    label = f"設定完了",
                    style = discord.ButtonStyle.green,
                    custom_id = f"valorantroles:set_rankrole:complete",
                    row = 3
                )
                v.add_item(b)

            else:
                with open(f"./valorantroles/{interaction.guild.id}.json", "r") as f:
                    data = json.load(f)
                    f.close()

                v = View()
                for rank in ranks:
                    if en_ranks[rank] in data.keys():
                        _roleid = data[(en_ranks[rank])]
                        try:
                            _role = interaction.guild.get_role(int(_roleid)).mention
                            _style = discord.ButtonStyle.blurple
                        except:
                            _role = f"❔｜未設定"
                            _style = discord.ButtonStyle.red
                        e.add_field(name = f"{rank}", value = f"{_role}")
                        b = Button(
                            label = f"{rank}",
                            style = _style,
                            custom_id = f"valorantroles:set_rankrole:{rank}"
                        )
                        v.add_item(b)
                    else:
                        e.add_field(name = f"{rank}", value = f"❔｜未設定")
                        b = Button(
                            label = f"{rank}",
                            style = discord.ButtonStyle.red,
                            custom_id = f"valorantroles:set_rankrole:{rank}"
                        )
                        v.add_item(b)
                b = Button(
                    label = f"設定完了",
                    style = discord.ButtonStyle.green,
                    custom_id = f"valorantroles:set_rankrole:complete",
                    row = 3
                )
                v.add_item(b)

            await interaction.response.edit_message(embed = e, view = v)

def setup(bot):
    bot.add_cog(ValorantRolesCog(bot))