"""
Player Commands Cog
Advanced player information and statistics
"""

import discord
from discord import app_commands
from discord.ext import commands
import io
from datetime import datetime
import logging
from typing import Optional
import asyncio

from utils.api_client import FFAPIClient, DataFormatter

logger = logging.getLogger(__name__)


class PlayerCommands(commands.Cog):
    """Commands for player information and statistics"""
    
    def __init__(self, bot):
        self.bot = bot
        self.api_client = FFAPIClient(bot.session)
        self.formatter = DataFormatter()
        self.cooldowns = {}
        
    @app_commands.command(name="player", description="Get detailed information about a Free Fire player")
    @app_commands.describe(
        uid="Player's UID (User ID)",
        region="Player's region (default: IND)"
    )
    @app_commands.choices(region=[
        app_commands.Choice(name="🇮🇳 India (IND)", value="IND"),
        app_commands.Choice(name="🇧🇷 Brazil (BR)", value="BR"),
        app_commands.Choice(name="🇺🇸 North America (NA)", value="NA"),
        app_commands.Choice(name="🇦🇷 South America (SA)", value="SA"),
        app_commands.Choice(name="🇪🇺 Europe (EU)", value="EU"),
        app_commands.Choice(name="🇸🇦 Middle East (ME)", value="ME"),
        app_commands.Choice(name="🇵🇰 Pakistan (PK)", value="PK"),
        app_commands.Choice(name="🇧🇩 Bangladesh (BD)", value="BD"),
        app_commands.Choice(name="🇸🇬 Singapore (SG)", value="SG"),
        app_commands.Choice(name="🇹🇭 Thailand (TH)", value="TH"),
        app_commands.Choice(name="🇻🇳 Vietnam (VN)", value="VN"),
        app_commands.Choice(name="🇮🇩 Indonesia (ID)", value="ID"),
    ])
    async def player_info(
        self, 
        interaction: discord.Interaction, 
        uid: str,
        region: str = "IND"
    ):
        """Get comprehensive player information"""
        
        # Defer response as this might take a moment
        await interaction.response.defer()
        
        try:
            # Ensure region is a string
            region = str(region).upper()
            
            # Validate UID
            if not uid.isdigit() or len(uid) < 8 or len(uid) > 12:
                embed = discord.Embed(
                    title="❌ Invalid UID",
                    description="Please provide a valid Free Fire UID (8-12 digits)",
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
            
            # Extract data
            basic_info = data.get('basicInfo', {})
            social_info = data.get('socialInfo', {})
            clan_info = data.get('clanBasicInfo', {})
            
            # Create main embed
            embed = discord.Embed(
                title=f"🎮 {basic_info.get('nickname', 'Unknown Player')}",
                description=f"**UID:** `{uid}` | **Region:** {self.formatter.get_region_flag(region)} {region}",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )
            
            # Account Status
            account_status = "✅ Active" if not basic_info.get('accountStatus') else "⛔ Banned"
            embed.add_field(
                name="📊 Account Status",
                value=account_status,
                inline=True
            )
            
            # Level and XP
            level = basic_info.get('level', 0)
            exp = basic_info.get('exp', 0)
            embed.add_field(
                name="⬆️ Level",
                value=f"**{level}** ({self.formatter.format_number(exp)} XP)",
                inline=True
            )
            
            # Rank
            rank = basic_info.get('rank', 'Unranked')
            rank_emoji = self.formatter.get_rank_emoji(rank)
            embed.add_field(
                name="🏆 Rank",
                value=f"{rank_emoji} {rank}",
                inline=True
            )
            
            # Statistics
            kills = basic_info.get('kills', 0)
            deaths = basic_info.get('deaths', 0) 
            kd_ratio = self.formatter.calculate_kd_ratio(kills, deaths)
            
            stats_text = (
                f"**Kills:** {self.formatter.format_number(kills)}\n"
                f"**Deaths:** {self.formatter.format_number(deaths)}\n"
                f"**K/D Ratio:** {kd_ratio}\n"
                f"**Headshots:** {self.formatter.format_number(basic_info.get('headshots', 0))}"
            )
            embed.add_field(
                name="📈 Combat Stats",
                value=stats_text,
                inline=True
            )
            
            # Guild/Clan Information
            if clan_info and clan_info.get('clanName'):
                clan_text = (
                    f"**Name:** {clan_info.get('clanName', 'N/A')}\n"
                    f"**Level:** {clan_info.get('clanLevel', 0)}\n"
                    f"**Members:** {clan_info.get('clanMembers', 0)}"
                )
                embed.add_field(
                    name="🛡️ Guild",
                    value=clan_text,
                    inline=True
                )
            else:
                embed.add_field(
                    name="🛡️ Guild",
                    value="No Guild",
                    inline=True
                )
            
            # Social Stats
            likes = social_info.get('likes', 0)
            visitors = basic_info.get('profileVisits', 0)
            social_text = (
                f"**Likes:** {self.formatter.format_number(likes)}\n"
                f"**Visitors:** {self.formatter.format_number(visitors)}"
            )
            embed.add_field(
                name="💫 Social",
                value=social_text,
                inline=True
            )
            
            # Credit Score
            credit_score = basic_info.get('creditScore', 0)
            if credit_score >= 80:
                credit_emoji = "💚"
            elif credit_score >= 60:
                credit_emoji = "💛"
            else:
                credit_emoji = "❤️"
            
            embed.add_field(
                name="📊 Credit Score",
                value=f"{credit_emoji} **{credit_score}**/100",
                inline=True
            )
            
            # Account Creation
            create_time = basic_info.get('accountCreatedAt', 0)
            if create_time > 0:
                create_date = self.formatter.format_timestamp(create_time)
                embed.add_field(
                    name="📅 Account Created",
                    value=create_date,
                    inline=False
                )
            
            # Last Login
            last_login = basic_info.get('lastLogin', 0)
            if last_login > 0:
                last_login_date = self.formatter.format_timestamp(last_login)
                embed.add_field(
                    name="🕐 Last Login",
                    value=last_login_date,
                    inline=False
                )
            
            embed.set_footer(
                text=f"Requested by {interaction.user.display_name}",
                icon_url=interaction.user.display_avatar.url
            )
            
            # Try to fetch outfit image
            outfit_file = None
            try:
                success_img, image_data, error_img = await self.api_client.get_outfit_image(uid, region)
                if success_img and image_data:
                    outfit_file = discord.File(io.BytesIO(image_data), filename=f"outfit_{uid}.png")
                    embed.set_image(url=f"attachment://outfit_{uid}.png")
            except Exception as e:
                logger.warning(f"Failed to fetch outfit image: {e}")
            
            # Send response
            if outfit_file:
                await interaction.followup.send(embed=embed, file=outfit_file)
            else:
                await interaction.followup.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Error in player_info command: {e}")
            embed = discord.Embed(
                title="❌ Unexpected Error",
                description="An unexpected error occurred. Please try again later.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="compare", description="Compare two Free Fire players")
    @app_commands.describe(
        uid1="First player's UID",
        uid2="Second player's UID",
        region="Region (default: IND)"
    )
    @app_commands.choices(region=[
        app_commands.Choice(name="🇮🇳 India (IND)", value="IND"),
        app_commands.Choice(name="🇧🇷 Brazil (BR)", value="BR"),
        app_commands.Choice(name="🇺🇸 North America (NA)", value="NA"),
    ])
    async def compare_players(
        self,
        interaction: discord.Interaction,
        uid1: str,
        uid2: str,
        region: str = "IND"
    ):
        """Compare statistics between two players"""
        
        await interaction.response.defer()
        
        try:
            # Ensure region is a string
            region = str(region).upper()
            
            # Validate UIDs
            for uid in [uid1, uid2]:
                if not uid.isdigit() or len(uid) < 8 or len(uid) > 12:
                    embed = discord.Embed(
                        title="❌ Invalid UID",
                        description=f"UID `{uid}` is invalid. Please provide valid UIDs (8-12 digits)",
                        color=discord.Color.red()
                    )
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return
            
            # Fetch both players concurrently
            results = await asyncio.gather(
                self.api_client.get_player_info(uid1, region),
                self.api_client.get_player_info(uid2, region),
                return_exceptions=True
            )
            
            success1, data1, error1 = results[0]
            success2, data2, error2 = results[1]
            
            if not success1 or not success2:
                embed = discord.Embed(
                    title="❌ Error Fetching Players",
                    description=f"Player 1: {error1 or 'OK'}\nPlayer 2: {error2 or 'OK'}",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Extract basic info
            p1_basic = data1.get('basicInfo', {})
            p2_basic = data2.get('basicInfo', {})
            
            # Create comparison embed
            embed = discord.Embed(
                title="⚔️ Player Comparison",
                description=f"Comparing **{p1_basic.get('nickname', 'Player 1')}** vs **{p2_basic.get('nickname', 'Player 2')}**",
                color=discord.Color.purple(),
                timestamp=datetime.utcnow()
            )
            
            # Compare levels
            level1 = p1_basic.get('level', 0)
            level2 = p2_basic.get('level', 0)
            level_winner = "🟢" if level1 > level2 else ("🔴" if level1 < level2 else "🟡")
            embed.add_field(
                name="⬆️ Level",
                value=f"{level_winner} **{level1}** vs **{level2}**",
                inline=True
            )
            
            # Compare kills
            kills1 = p1_basic.get('kills', 0)
            kills2 = p2_basic.get('kills', 0)
            kills_winner = "🟢" if kills1 > kills2 else ("🔴" if kills1 < kills2 else "🟡")
            embed.add_field(
                name="💀 Kills",
                value=f"{kills_winner} **{self.formatter.format_number(kills1)}** vs **{self.formatter.format_number(kills2)}**",
                inline=True
            )
            
            # Compare K/D
            kd1 = self.formatter.calculate_kd_ratio(kills1, p1_basic.get('deaths', 0))
            kd2 = self.formatter.calculate_kd_ratio(kills2, p2_basic.get('deaths', 0))
            kd_winner = "🟢" if float(kd1) > float(kd2) else ("🔴" if float(kd1) < float(kd2) else "🟡")
            embed.add_field(
                name="📊 K/D Ratio",
                value=f"{kd_winner} **{kd1}** vs **{kd2}**",
                inline=True
            )
            
            # Compare headshots
            hs1 = p1_basic.get('headshots', 0)
            hs2 = p2_basic.get('headshots', 0)
            hs_winner = "🟢" if hs1 > hs2 else ("🔴" if hs1 < hs2 else "🟡")
            embed.add_field(
                name="🎯 Headshots",
                value=f"{hs_winner} **{self.formatter.format_number(hs1)}** vs **{self.formatter.format_number(hs2)}**",
                inline=True
            )
            
            # Compare credit score
            cs1 = p1_basic.get('creditScore', 0)
            cs2 = p2_basic.get('creditScore', 0)
            cs_winner = "🟢" if cs1 > cs2 else ("🔴" if cs1 < cs2 else "🟡")
            embed.add_field(
                name="📊 Credit Score",
                value=f"{cs_winner} **{cs1}** vs **{cs2}**",
                inline=True
            )
            
            embed.set_footer(
                text=f"Requested by {interaction.user.display_name} | 🟢 = Player 1 Wins | 🔴 = Player 2 Wins | 🟡 = Tie",
                icon_url=interaction.user.display_avatar.url
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in compare command: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to compare players. Please try again.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="quickinfo", description="Get quick player stats")
    @app_commands.describe(uid="Player's UID")
    async def quick_info(self, interaction: discord.Interaction, uid: str):
        """Get quick player information"""
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            if not uid.isdigit() or len(uid) < 8 or len(uid) > 12:
                await interaction.followup.send("❌ Invalid UID", ephemeral=True)
                return
            
            success, data, error = await self.api_client.get_player_info(uid, "IND")
            
            if not success:
                await interaction.followup.send(f"❌ {error}", ephemeral=True)
                return
            
            basic_info = data.get('basicInfo', {})
            
            response = (
                f"**🎮 {basic_info.get('nickname', 'Unknown')}**\n"
                f"UID: `{uid}`\n"
                f"Level: **{basic_info.get('level', 0)}**\n"
                f"Kills: **{self.formatter.format_number(basic_info.get('kills', 0))}**\n"
                f"K/D: **{self.formatter.calculate_kd_ratio(basic_info.get('kills', 0), basic_info.get('deaths', 0))}**"
            )
            
            await interaction.followup.send(response, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in quick_info: {e}")
            await interaction.followup.send("❌ An error occurred", ephemeral=True)


async def setup(bot):
    await bot.add_cog(PlayerCommands(bot))
