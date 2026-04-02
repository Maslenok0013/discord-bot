import discord
from discord.ext import commands
from discord.ui import Modal, TextInput, View, Button
from dotenv import load_dotenv
import os

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

# ✅ ВСТАВЛЕН ТВОЙ ROLE_ID
ROLE_ID = 1467619367733690379

# ✅ Канал с реакциями
REACTION_CHANNEL_ID = 1482024804642193601

# Интенты
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix="s!", intents=intents)

# ---------- МОДАЛЬНОЕ ОКНО ----------
class ContractModal(Modal):
    def __init__(self):
        super().__init__(title="Форма контракта")

        self.contract_name = TextInput(label="Название контракта")
        self.add_item(self.contract_name)

        self.contract_tags = TextInput(label="Тэг исполнителей и награда")
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
        embed.add_field(name="Исполнители и награда", value=self.contract_tags.value, inline=False)

        await log_channel.send(embed=embed)

        await interaction.response.send_message(
            "✅ Контракт отправлен!",
            ephemeral=True
        )

# ---------- ВИД С КНОПКОЙ ----------
class ContractView(View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(
            Button(
                label="Создать контракт",
                style=discord.ButtonStyle.green,
                custom_id="create_contract_button"
            )
        )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.data.get("custom_id") == "create_contract_button":
            await interaction.response.send_modal(ContractModal())
        return True

# ---------- СОБЫТИЕ ON_READY ----------
@bot.event
async def on_ready():
    print(f"Бот запущен как {bot.user}")

    bot.add_view(ContractView())

    form_channel = bot.get_channel(FORM_CHANNEL_ID)
    if form_channel:
        existing = False
        async for msg in form_channel.history(limit=50):
            if msg.author == bot.user and msg.components:
                existing = True
                break

        if not existing:
            await form_channel.send(
                "Нажмите кнопку ниже, чтобы создать контракт",
                view=ContractView()
            )

# ---------- ✅ РЕАКЦИИ ----------
@bot.event
async def on_raw_reaction_add(payload):
    print("🔥 Реакция обнаружена:", payload.channel_id, str(payload.emoji))

    if payload.channel_id != REACTION_CHANNEL_ID:
        print("❌ Не тот канал")
        return

    if str(payload.emoji) != "✅":
        print("❌ Не та реакция")
        return

    guild = bot.get_guild(payload.guild_id)
    if not guild:
        print("❌ Сервер не найден")
        return

    member = guild.get_member(payload.user_id)
    if not member or member.bot:
        print("❌ Пользователь не найден или это бот")
        return

    role = guild.get_role(ROLE_ID)
    if not role:
        print("❌ Роль не найдена")
        return

    try:
        await member.add_roles(role)
        print(f"✅ Роль выдана: {member.name}")

        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(f"✅ {member.mention} получил роль {role.name}")
    except Exception as e:
        print("❌ Ошибка при выдаче роли:", e)

@bot.event
async def on_raw_reaction_remove(payload):
    print("🔥 Удаление реакции:", payload.channel_id, str(payload.emoji))

    if payload.channel_id != REACTION_CHANNEL_ID:
        return

    if str(payload.emoji) != "✅":
        return

    guild = bot.get_guild(payload.guild_id)
    if not guild:
        return

    member = guild.get_member(payload.user_id)
    if not member:
        return

    role = guild.get_role(ROLE_ID)
    if not role:
        return

    try:
        await member.remove_roles(role)
        print(f"❌ Роль снята: {member.name}")

        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(f"❌ {member.mention} потерял роль {role.name}")
    except Exception as e:
        print("❌ Ошибка при снятии роли:", e)

# ---------- КОМАНДЫ ----------
@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")

# ---------- ЗАПУСК ----------
bot.run(TOKEN)