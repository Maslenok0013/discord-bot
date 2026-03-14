import discord
from discord.ext import commands
from discord.ui import Modal, TextInput, View, Button
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TOKEN")
FORM_CHANNEL_ID = int(os.getenv("FORM_CHANNEL_ID", 1482025460304183460))
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", 1481012670210773084))

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="s!", intents=intents)


class ContractModal(Modal):

    def __init__(self):
        super().__init__(title="Форма контракта")

        self.contract_name = TextInput(label="Название контракта")
        self.add_item(self.contract_name)

        self.contract_screen = TextInput(label="Скрин контракта (с исполнителями)")
        self.add_item(self.contract_screen)

        self.contract_tags = TextInput(label="Тэг исполнителей")
        self.add_item(self.contract_tags)

    async def on_submit(self, interaction: discord.Interaction):
        log_channel = bot.get_channel(LOG_CHANNEL_ID)

        if log_channel is None:
            await interaction.response.send_message(
                "❌ Канал для логов не найден.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="📄 Новый контракт",
            color=discord.Color.green()
        )

        embed.add_field(
            name="Игрок",
            value=interaction.user.mention,
            inline=False
        )

        embed.add_field(
            name="Название",
            value=self.contract_name.value,
            inline=False
        )

        embed.add_field(
            name="Скрин контракта",
            value=self.contract_screen.value,
            inline=False
        )

        embed.add_field(
            name="Исполнители",
            value=self.contract_tags.value,
            inline=False
        )

        await log_channel.send(embed=embed)

        await interaction.response.send_message(
            "✅ Контракт отправлен!",
            ephemeral=True
        )


class ContractView(View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Создать контракт", style=discord.ButtonStyle.green)
    async def create_contract(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(ContractModal())


@bot.event
async def on_ready():
    print(f"Бот запущен как {bot.user}")

    channel = bot.get_channel(FORM_CHANNEL_ID)
    if channel:
        await channel.send(
            "Нажмите кнопку ниже, чтобы создать контракт",
            view=ContractView()
        )


@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")


bot.run(TOKEN)