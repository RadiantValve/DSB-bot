import discord
from dataclasses import dataclass

# ─────────────────────────────
# State handling
# ─────────────────────────────

@dataclass
class MenuState:
    send_data: int | None = None
    hour: int | None = None
    minute: int | None = None


_MENU_STATE: dict[int, MenuState] = {}


def _state(user_id: int) -> MenuState:
    if user_id not in _MENU_STATE:
        _MENU_STATE[user_id] = MenuState()
    return _MENU_STATE[user_id]


# label->code mapping requested
CLASS_CODES: list[tuple[str, int]] = [
    ("5a", 51), ("5b", 52), ("5c", 53),
    ("6a", 61), ("6b", 62), ("6c", 63),
    ("7a", 71), ("7b", 72), ("7c", 73),
    ("8a", 81), ("8b", 82), ("8c", 83),
    ("9a", 91), ("9b", 92), ("9c", 93),
    ("10a", 101), ("10b", 102), ("10c", 103),
    ("EF", 11), ("Q1", 12), ("Q2", 13),
]

CODE_TO_LABEL = {code: label for label, code in CLASS_CODES}


def _summary(s: MenuState) -> str:
    if s.send_data is None:
        data_label = "Keine"
    else:
        data_label = CODE_TO_LABEL.get(s.send_data, str(s.send_data))

    h = f"{s.hour:02d}" if s.hour is not None else "--"
    m = f"{s.minute:02d}" if s.minute is not None else "--"
    return f"**DSB Einstellungen**\nKlasse/Kurs: `{data_label}` (`{s.send_data if s.send_data is not None else 'None'}`)\nZeit: `{h}:{m}`"


# ─────────────────────────────
# Persistence hook (ONLY json_handler functions)
# ─────────────────────────────

async def persist_settings(user_id: int, users, state: MenuState):
    enabled = (
        state.send_data is not None
        and state.hour is not None
        and state.minute is not None
    )

    users.change_info(user_id, enabled)
    users.change_data(user_id, state.send_data)
    users.change_time(user_id, state.hour, state.minute)


# ─────────────────────────────
# Page 1 – class / course
# ─────────────────────────────

class Page1(discord.ui.View):
    def __init__(self, user_id: int, users):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.users = users

        options = [discord.SelectOption(label="Keine", value="None", emoji="🚫")]

        for label, code in CLASS_CODES:
            options.append(
                discord.SelectOption(
                    label=label,
                    value=str(code),   # store numeric code as string (Select values must be str)
                    emoji="📔"
                )
            )

        self.select = discord.ui.Select(
            placeholder="Klasse / Kurs wählen",
            min_values=1,
            max_values=1,
            options=options
        )
        self.select.callback = self.on_select
        self.add_item(self.select)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    async def on_select(self, interaction: discord.Interaction):
        s = _state(self.user_id)
        val = self.select.values[0]
        s.send_data = None if val == "None" else int(val)
        await interaction.response.edit_message(content=_summary(s) + "\n\n**Seite 1 von 3**", view=self)

    @discord.ui.button(label="abbruch", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, _button: discord.ui.Button):
        _MENU_STATE.pop(self.user_id, None)
        await interaction.response.edit_message(content="Abgebrochen.", view=None)

    @discord.ui.button(label="1 von 3", style=discord.ButtonStyle.secondary, disabled=True)
    async def page_indicator(self, interaction: discord.Interaction, _button: discord.ui.Button):
        pass

    @discord.ui.button(label="weiter", style=discord.ButtonStyle.success)
    async def next(self, interaction: discord.Interaction, _button: discord.ui.Button):
        s = _state(self.user_id)
        await interaction.response.edit_message(content=_summary(s) + "\n\n**Seite 2 von 3**", view=Page2(self.user_id, self.users))


# ─────────────────────────────
# Page 2 – hour
# ─────────────────────────────

class Page2(discord.ui.View):
    def __init__(self, user_id: int, users):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.users = users

        options = [discord.SelectOption(label="Keine", value="None", emoji="🚫")]
        for h in range(24):
            options.append(discord.SelectOption(label=f"{h:02d}:00", value=str(h)))

        self.select = discord.ui.Select(
            placeholder="Stunde wählen",
            min_values=1,
            max_values=1,
            options=options
        )
        self.select.callback = self.on_select
        self.add_item(self.select)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    async def on_select(self, interaction: discord.Interaction):
        s = _state(self.user_id)
        val = self.select.values[0]
        s.hour = None if val == "None" else int(val)
        await interaction.response.edit_message(content=_summary(s) + "\n\n**Seite 2 von 3**", view=self)

    @discord.ui.button(label="zurück", style=discord.ButtonStyle.danger)
    async def back(self, interaction: discord.Interaction, _button: discord.ui.Button):
        s = _state(self.user_id)
        await interaction.response.edit_message(content=_summary(s) + "\n\n**Seite 1 von 3**", view=Page1(self.user_id, self.users))

    @discord.ui.button(label="2 von 3", style=discord.ButtonStyle.secondary, disabled=True)
    async def page_indicator(self, interaction: discord.Interaction, _button: discord.ui.Button):
        pass

    @discord.ui.button(label="weiter", style=discord.ButtonStyle.success)
    async def next(self, interaction: discord.Interaction, _button: discord.ui.Button):
        s = _state(self.user_id)
        await interaction.response.edit_message(content=_summary(s) + "\n\n**Seite 3 von 3**", view=Page3(self.user_id, self.users))


# ─────────────────────────────
# Page 3 – minute
# ─────────────────────────────

class Page3(discord.ui.View):
    def __init__(self, user_id: int, users):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.users = users

        options = [discord.SelectOption(label="Keine", value="None", emoji="🚫")]
        for m in [0, 15, 30, 45]:
            options.append(discord.SelectOption(label=f"00:{m:02d}", value=str(m)))

        self.select = discord.ui.Select(
            placeholder="Minute wählen",
            min_values=1,
            max_values=1,
            options=options
        )
        self.select.callback = self.on_select
        self.add_item(self.select)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    async def on_select(self, interaction: discord.Interaction):
        s = _state(self.user_id)
        val = self.select.values[0]
        s.minute = None if val == "None" else int(val)
        await interaction.response.edit_message(content=_summary(s) + "\n\n**Seite 3 von 3**", view=self)

    @discord.ui.button(label="zurück", style=discord.ButtonStyle.danger)
    async def back(self, interaction: discord.Interaction, _button: discord.ui.Button):
        s = _state(self.user_id)
        await interaction.response.edit_message(content=_summary(s) + "\n\n**Seite 2 von 3**", view=Page2(self.user_id, self.users))

    @discord.ui.button(label="3 von 3", style=discord.ButtonStyle.secondary, disabled=True)
    async def page_indicator(self, interaction: discord.Interaction, _button: discord.ui.Button):
        pass

    @discord.ui.button(label="Fertig", style=discord.ButtonStyle.success)
    async def finish(self, interaction: discord.Interaction, _button: discord.ui.Button):
        s = _state(self.user_id)
        await persist_settings(self.user_id, self.users, s)
        _MENU_STATE.pop(self.user_id, None)
        await interaction.response.edit_message(content=_summary(s) + "\n\n✅ Gespeichert", view=None)


# ─────────────────────────────
# Public entry point
# ─────────────────────────────

async def open_menu(message, users):
    s = _state(message.author.id)
    await message.channel.send(
        content=_summary(s) + "\n\n**Seite 1 von 3**",
        view=Page1(message.author.id, users)
    )
