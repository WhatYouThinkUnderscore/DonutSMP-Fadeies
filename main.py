import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import requests
from api import DonutSMP
from typing import Literal
import webserver

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'{bot.user.name} has connected to Discord!')

def get_item(item):
    requests.get('api.donutsmp.net/')

class ahSortDropDown(discord.ui.Select):
    def __init__(self, item: str):
        self.item = item  # Save the item for later use
        options = [
            discord.SelectOption(label='Lowest Price', value='lowest_price'),
            discord.SelectOption(label='Highest Price', value='highest_price'),
            discord.SelectOption(label='Recently Listed', value='recently_listed'),
            discord.SelectOption(label='Last Listed', value='last_listed')
        ]
        super().__init__(
            placeholder='Sort by...',
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        sort_value = self.values[0]

        # Regenerate embed with new sort
        donut_smp = DonutSMP()
        donut_smp.get_item(item=self.item, sort=sort_value)

        updated_embed = discord.Embed(
            title=f"Auction Results For `{self.item}`",
            description=f"**{self.label_for(sort_value)}**",
            color=discord.Color.purple()
        )

        for i in range(0, 10):
            seller_name = donut_smp.get_seller(i)
            price = donut_smp.get_price(i)
            time_left = donut_smp.get_time_left(i)
            item_name = donut_smp.get_item_name(i)
            count = donut_smp.get_count(i)

            if seller_name == "Unknown" and item_name == "Unknown" and count ==  "Unknown":
                updated_embed.color = discord.Color.red()
                updated_embed.add_field(
                    name=f"No results for **{self.item}**",
                    value="",
                    inline=False
                )
                break
            else:
                updated_embed.add_field(
                    name=f"{i+1}. **{item_name.title()}** ({count}) by `{seller_name}`",
                    value=f"💵 **${price}** | ⌛ **{time_left}**",
                    inline=False
                )

        updated_embed.set_footer(text="WARNING: Amethyst Items don't work and could lead to wrong results!!")

        await interaction.response.edit_message(embed=updated_embed)

    def label_for(self, value):
        labels = {
            'lowest_price': 'Lowest Price Sort',
            'highest_price': 'Highest Price Sort',
            'recently_listed': 'Recently Listed Sort',
            'last_listed': 'Last Listed Sort'
        }
        return labels.get(value, "Unknown Sort")


class ahSortView(discord.ui.View):
    def __init__(self, item: str):
        super().__init__(timeout=None)
        self.add_item(ahSortDropDown(item=item))

@bot.tree.command(name='ah', description='Shows auction house listings')
async def ah(interaction: discord.Interaction, item: str, sort: Literal["lowest_price", "highest_price", "recently_listed", "last_listed"] = "lowest_price"):
    donut_smp = DonutSMP()
    donut_smp.get_item(item=item, sort=sort)

    labels = {
        'lowest_price': 'Lowest Price Sort',
        'highest_price': 'Highest Price Sort',
        'recently_listed': 'Recently Listed Sort',
        'last_listed': 'Last Listed Sort'
    }

    ah_embed = discord.Embed(
        title=f"Auction Results For `{item}`",
        description=f"**{labels[sort]}**",
        color=discord.Color.purple()
    )


    for i in range(0, 10):
        seller_name = donut_smp.get_seller(i)
        price = donut_smp.get_price(i)
        time_left = donut_smp.get_time_left(i)
        item_name = donut_smp.get_item_name(i)
        count = donut_smp.get_count(i)


        if seller_name == "Unknown" and item_name == "Unknown" and count ==  "Unknown":
            ah_embed.color = discord.Color.red()
            ah_embed.add_field(
                name=f"No results for **{item}**",
                value="",
                inline=False
            )
            break
        else:
            ah_embed.add_field(
                name=f"{i+1}. **{item_name.title()}** ({count}) by `{seller_name}`",
                value=f"💵 **${price}** | ⌛ **{time_left}**",
                inline=False
            )

    ah_embed.set_footer(text="WARNING: Amethyst Items don't work and could lead to wrong results!!")

    await interaction.response.send_message(embed=ah_embed, view=ahSortView(item=item))

@bot.tree.command(name="stats", description="Shows player's stats on DonutSMP")
async def stats(interaction: discord.Interaction, player_name: str):
    stats_embed = discord.Embed(
        title=f"Stats for {player_name}",
        color=discord.Color.purple()
    )

    donut_smp = DonutSMP()
    donut_smp.get_stats(player_name)

    stats_label = {
        "Money": ("money", True),
        "Shards": ("shards", False),
        "Kills": ("kills", False),
        "Deaths": ("deaths", False),
        "Playtime": ("playtime", False),
        "Placed Blocks": ("placed_blocks", False),
        "Broken Blocks": ("broken_blocks", False),
        "Mobs Killed": ("mobs_killed", False),
        "Money Spent on Shop": ("money_spent_on_shop", True),
        "Money Made From Sell": ("money_made_from_sell", True),
    }

    stats_text = ""

    for key, (value, is_currency) in stats_label.items():
        stat_value = donut_smp.get_stat(value)
        if is_currency:
            stat_value = f"${stat_value}"
        stats_text += f"**{key}:** `{stat_value}`\n"

    stats_embed.add_field(name="", value=stats_text, inline=False)

    await interaction.response.send_message(embed=stats_embed)

webserver.keep_alive()
bot.run(TOKEN, log_handler=handler, log_level=logging.DEBUG)
