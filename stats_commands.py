"""
Stats Commands Cog
Advanced statistics and leaderboard features
"""

import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import logging
import json
import os
from typing import Dict, List

from utils.api_client import FFAPIClient, DataFormatter

logger = logging.getLogger(__name__)


class StatsCommands(commands.Cog):
    """Advanced statistics and leaderboard commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.api_client = FFAPIClient(bot.session)
        self.formatter = DataFormatter()
        self.tracked_players_file = "data/tracked_players.json"
        self.tracked_players = self.load_tracked_players()
    
    def load_tracked_players(self) -> Dict:
        """Load tracked players from file"""
        if os.path.exists(self.tracked_players_file):
            try:
                with open(self.tracked_players_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading tracked players: {e}")
        return {}
    
    def save_tracked_players(self):
        """Save tracked players to file"""
        try:
            os.makedirs(os.path.dirname(self.tracked_players_file), exist_ok=True)
            with open(self.tracked_players_file, 'w') as f:
                json.dump(self.tracked_players, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving tracked players: {e}")
    
    @app_commands.command(name="track", description="Track a player's statistics")
    @app_commands.describe(
        uid="Player's UID to track",
        region="Region (default: IND)"
    )
    async def track_player(
        self,
        interaction: discord.Interaction,
        uid: str,
        region: str = "IND"
    ):
        """Add a player to tracking list"""
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Ensure region is a string
            region = str(region).upper()
            
            # Validate UID
            if not uid.isdigit() or len(uid) < 8 or len(uid) > 12:
                await interaction.followup.send("❌ Invalid UID", ephemeral=True)
                return
            
            # Fetch player to verify
            success, data, error = await self.api_client.get_player_info(uid, region)
            
            if not success:
                await interaction.followup.send(f"❌ {error}", ephemeral=True)
                return
            
            basic_info = data.get('basicInfo', {})
            user_id = str(interaction.user.id)
            
            # Initialize user's tracking list
            if user_id not in self.tracked_players:
                self.tracked_players[user_id] = {}
            
            # Add player to tracking
            self.tracked_players[user_id][uid] = {
                "nickname": basic_info.get('nickname', 'Unknown'),
                "region": region,
                "added_at": datetime.utcnow().isoformat(),
                "initial_stats": {
                    "level": basic_info.get('level', 0),
                    "kills": basic_info.get('kills', 0),
                    "deaths": basic_info.get('deaths', 0)
                }
            }
            
            self.save_tracked_players()
            
            embed = discord.Embed(
                title="✅ Player Tracked",
                description=f"Now tracking **{basic_info.get('nickname', 'Unknown')}** (`{uid}`)",
                color=discord.Color.green()
            )
            embed.add_field(
                name="📊 Current Stats",
                value=(
                    f"Level: **{basic_info.get('level', 0)}**\n"
                    f"Kills: **{self.formatter.format_number(basic_info.get('kills', 0))}**\n"
                    f"K/D: **{self.formatter.calculate_kd_ratio(basic_info.get('kills', 0), basic_info.get('deaths', 0))}**"
                )
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in track_player: {e}")
            await interaction.followup.send("❌ An error occurred", ephemeral=True)
    
    @app_commands.command(name="untrack", description="Stop tracking a player")
    @app_commands.describe(uid="Player's UID to stop tracking")
    async def untrack_player(
        self,
        interaction: discord.Interaction,
        uid: str
    ):
        """Remove a player from tracking list"""
        
        user_id = str(interaction.user.id)
        
        if user_id not in self.tracked_players or uid not in self.tracked_players[user_id]:
            await interaction.response.send_message(
                "❌ You are not tracking this player.",
                ephemeral=True
            )
            return
        
        player_name = self.tracked_players[user_id][uid].get('nickname', 'Unknown')
        del self.tracked_players[user_id][uid]
        
        if not self.tracked_players[user_id]:
            del self.tracked_players[user_id]
        
        self.save_tracked_players()
        
        await interaction.response.send_message(
            f"✅ Stopped tracking **{player_name}** (`{uid}`)",
            ephemeral=True
        )
    
    @app_commands.command(name="tracked", description="View your tracked players")
    async def view_tracked(self, interaction: discord.Interaction):
        """View all tracked players"""
        
        await interaction.response.defer(ephemeral=True)
        
        user_id = str(interaction.user.id)
        
        if user_id not in self.tracked_players or not self.tracked_players[user_id]:
            embed = discord.Embed(
                title="📊 Tracked Players",
                description="You are not tracking any players.\nUse `/track <uid>` to start tracking.",
                color=discord.Color.blue()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title="📊 Your Tracked Players",
            description=f"Tracking {len(self.tracked_players[user_id])} player(s)",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        for uid, player_data in list(self.tracked_players[user_id].items())[:10]:
            nickname = player_data.get('nickname', 'Unknown')
            region = player_data.get('region', 'IND')
            added_at = player_data.get('added_at', 'Unknown')
            
            embed.add_field(
                name=f"🎮 {nickname}",
                value=f"UID: `{uid}`\nRegion: {region}\nAdded: {added_at[:10]}",
                inline=False
            )
        
        if len(self.tracked_players[user_id]) > 10:
            embed.set_footer(text=f"Showing 10 of {len(self.tracked_players[user_id])} tracked players")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @app_commands.command(name="progress", description="Check progress of a tracked player")
    @app_commands.describe(uid="Player's UID")
    async def check_progress(
        self,
        interaction: discord.Interaction,
        uid: str
    ):
        """Check a tracked player's progress"""
        
        await interaction.response.defer(ephemeral=True)
        
        user_id = str(interaction.user.id)
        
        if user_id not in self.tracked_players or uid not in self.tracked_players[user_id]:
            await interaction.followup.send(
                "❌ You are not tracking this player. Use `/track` first.",
                ephemeral=True
            )
            return
        
        player_data = self.tracked_players[user_id][uid]
        region = player_data.get('region', 'IND')
        
        # Fetch current stats
        success, data, error = await self.api_client.get_player_info(uid, region)
        
        if not success:
            await interaction.followup.send(f"❌ {error}", ephemeral=True)
            return
        
        basic_info = data.get('basicInfo', {})
        initial_stats = player_data.get('initial_stats', {})
        
        # Calculate differences
        current_level = basic_info.get('level', 0)
        current_kills = basic_info.get('kills', 0)
        current_deaths = basic_info.get('deaths', 0)
        
        initial_level = initial_stats.get('level', 0)
        initial_kills = initial_stats.get('kills', 0)
        initial_deaths = initial_stats.get('deaths', 0)
        
        level_diff = current_level - initial_level
        kills_diff = current_kills - initial_kills
        deaths_diff = current_deaths - initial_deaths
        
        # Create progress embed
        embed = discord.Embed(
            title=f"📈 Progress: {basic_info.get('nickname', 'Unknown')}",
            description=f"UID: `{uid}` | Tracked since: {player_data.get('added_at', 'Unknown')[:10]}",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        
        # Level progress
        embed.add_field(
            name="⬆️ Level",
            value=f"**{current_level}** ({'+' if level_diff >= 0 else ''}{level_diff})",
            inline=True
        )
        
        # Kills progress
        embed.add_field(
            name="💀 Kills",
            value=f"**{self.formatter.format_number(current_kills)}** ({'+' if kills_diff >= 0 else ''}{self.formatter.format_number(kills_diff)})",
            inline=True
        )
        
        # K/D progress
        current_kd = self.formatter.calculate_kd_ratio(current_kills, current_deaths)
        initial_kd = self.formatter.calculate_kd_ratio(initial_kills, initial_deaths)
        embed.add_field(
            name="📊 K/D Ratio",
            value=f"**{current_kd}** (was {initial_kd})",
            inline=True
        )
        
        embed.set_footer(text=f"Requested by {interaction.user.display_name}")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @app_commands.command(name="cache", description="View cache statistics")
    async def cache_stats(self, interaction: discord.Interaction):
        """View API cache statistics"""
        
        stats = self.api_client.get_cache_stats()
        
        embed = discord.Embed(
            title="💾 Cache Statistics",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="📊 Total Entries",
            value=f"**{stats['total_entries']}**",
            inline=True
        )
        
        embed.add_field(
            name="✅ Valid Entries",
            value=f"**{stats['valid_entries']}**",
            inline=True
        )
        
        embed.add_field(
            name="❌ Expired Entries",
            value=f"**{stats['expired_entries']}**",
            inline=True
        )
        
        embed.add_field(
            name="⏱️ Cache TTL",
            value=f"**{stats['cache_ttl']}** seconds",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(StatsCommands(bot))
