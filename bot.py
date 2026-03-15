import discord
from discord.ext import commands
from discord.ui import Modal, TextInput, View, Button
from dotenv import load_dotenv
import os
import asyncio

# Загружаем .env
load_dotenv()

# Функция безопасного чтения числовых переменных среды
def get_env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        print(f"⚠️ Переменная среды {name} не число! Используем значение по умолчанию.")
        return default

# Переменные среды
TOKEN = os.getenv("TOKEN")
FORM_CHANNEL_ID = get_env_int("FORM_CHANNEL_ID", 1482025460304183460)
LOG_CHANNEL_ID = get_env_int("LOG_CHANNEL_ID", 1481012670210773084)

# Интенты
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="s!", intents=intents)

# ---------- МОДАЛЬНОЕ ОКНО ----------
class ContractModal(Modal):
    def __init__(self):
        super().__init__(title="Форма контракта")

        self.contract_name = TextInput(label="Название контракта")
        self.add_item(self.contract_name)

        self.contract_screen = TextInput(
            label="Скрин контракта (можно вставить ссылку или Discord attachment)",
            style=discord.TextStyle.paragraph,
            required=False
        )
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
        embed.add_field(name="Игрок", value=interaction.user.mention, inline=False)
        embed.add_field(name="Название", value=self.contract_name.value, inline=False)
        embed.add_field(name="Скрин контракта", value=self.contract_screen.value or "Не прикреплён", inline=False)
        embed.add_field(name="Исполнители", value=self.contract_tags.value, inline=False)

        # Отправляем embed
        message = await log_channel.send(embed=embed)

        # Удаляем сообщение через 60 секунд
        await asyncio.sleep(60)
        await message.delete()

        await interaction.response.send_message(
            "✅ Контракт отправлен!",
            ephemeral=True
        )

# ---------- ВИД С КНОПКОЙ ----------
class ContractView(View):
    def __init__(self):
        super().__init__(timeout=None)  # persistent view
        # Только одна кнопка, без декоратора
        self.add_item(
            Button(
                label="Создать контракт",
                style=discord.ButtonStyle.green,
                custom_id="create_contract_button"
            )
        )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Обрабатываем нажатие кнопки вручную
        if interaction.data.get("custom_id") == "create_contract_button":
            await interaction.response.send_modal(ContractModal())
        return True

# ---------- СОБЫТИЕ ON_READY ----------
@bot.event
async def on_ready():
    print(f"Бот запущен как {bot.user}")

    # Добавляем persistent view
    bot.add_view(ContractView())

    # Отправляем кнопку в канал, если её там ещё нет
    form_channel = bot.get_channel(FORM_CHANNEL_ID)
    if form_channel:
        existing = False
        async for msg in form_channel.history(limit=50):
            if msg.author == bot.user and msg.components:
                existing = True
                break
        if not existing:
            await form_channel.send("Нажмите кнопку ниже, чтобы создать контракт", view=ContractView())

# ---------- КОМАНДЫ ----------
@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")

# ---------- ЗАПУСК БОТА ----------
bot.run(TOKEN)
