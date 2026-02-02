"""
Guild Commands Cog
Commands for guild/clan information and management
"""

import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import logging
from typing import Optional

from utils.api_client import FFAPIClient, DataFormatter

logger = logging.getLogger(__name__)


class GuildCommands(commands.Cog):
    """Commands for guild and clan information"""
    
    def __init__(self, bot):
        self.bot = bot
        self.api_client = FFAPIClient(bot.session)
        self.formatter = DataFormatter()
    
    @app_commands.command(name="guild", description="Get guild information from a player's UID")
    @app_commands.describe(
        uid="Player's UID to fetch guild from",
        region="Region (default: IND)"
    )
    @app_commands.choices(region=[
        app_commands.Choice(name="🇮🇳 India (IND)", value="IND"),
        app_commands.Choice(name="🇧🇷 Brazil (BR)", value="BR"),
        app_commands.Choice(name="🇺🇸 North America (NA)", value="NA"),
    ])
    async def guild_info(
        self,
        interaction: discord.Interaction,
        uid: str,
        region: str = "IND"
    ):
        """Get detailed guild information"""
        
        await interaction.response.defer()
        
        try:
            # Ensure region is a string
            region = str(region).upper()
            
            # Validate UID
            if not uid.isdigit() or len(uid) < 8 or len(uid) > 12:
                embed = discord.Embed(
                    title="❌ Invalid UID",
                    description="Please provide a valid Free Fire UID",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            # Fetch player data
            success, data, error = await self.api_client.get_player_info(uid, region)
            
            if not success:
                embed = discord.Embed(
                    title="❌ Error",
                    description=error or "Failed to fetch player information",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            clan_info = data.get('clanBasicInfo', {})
            basic_info = data.get('basicInfo', {})
            
            if not clan_info or not clan_info.get('clanName'):
                embed = discord.Embed(
                    title="❌ No Guild",
                    description=f"**{basic_info.get('nickname', 'Player')}** is not in any guild.",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Create guild embed
            embed = discord.Embed(
                title=f"🛡️ {clan_info.get('clanName', 'Unknown Guild')}",
                description=f"**Guild ID:** `{clan_info.get('clanId', 'N/A')}`",
                color=discord.Color.gold(),
                timestamp=datetime.utcnow()
            )
            
            # Guild Level
            embed.add_field(
                name="⬆️ Guild Level",
                value=f"**{clan_info.get('clanLevel', 0)}**",
                inline=True
            )
            
            # Members
            members = clan_info.get('clanMembers', 0)
            max_members = clan_info.get('clanMaxMembers', 50)
            embed.add_field(
                name="👥 Members",
                value=f"**{members}**/{max_members}",
                inline=True
            )
            
            # Captain
            captain = clan_info.get('captainName', 'Unknown')
            embed.add_field(
                name="👑 Captain",
                value=f"**{captain}**",
                inline=True
            )
            
            # Guild Stats
            if clan_info.get('clanKills'):
                stats_text = (
                    f"**Kills:** {self.formatter.format_number(clan_info.get('clanKills', 0))}\n"
                    f"**Wins:** {self.formatter.format_number(clan_info.get('clanWins', 0))}"
                )
                embed.add_field(
                    name="📊 Guild Stats",
                    value=stats_text,
                    inline=False
                )
            
            # Player's role in guild
            player_role = basic_info.get('clanRole', 'Member')
            embed.add_field(
                name="📌 Your Role",
                value=f"**{player_role}**",
                inline=True
            )
            
            embed.set_footer(
                text=f"Requested by {interaction.user.display_name}",
                icon_url=interaction.user.display_avatar.url
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in guild_info command: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="An error occurred while fetching guild information.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(GuildCommands(bot))
