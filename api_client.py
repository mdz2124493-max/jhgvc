"""
API Utility Module for Free Fire Bot
Handles all external API interactions with caching and error handling
"""

import aiohttp
import asyncio
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import logging
import hashlib
import json

logger = logging.getLogger(__name__)

class FFAPIClient:
    """Advanced Free Fire API Client with caching and rate limiting"""
    
    # API Endpoints
    INFO_API_URL = "https://danger-info-alpha.vercel.app/accinfo?uid={uid}&key=DANGERxINFO"
    OUTFIT_API_URL = "https://ffoutfitapis.vercel.app/outfit-image?uid={uid}&region={region}&key=99day"
    ITEM_ICON_URL = "https://dl.cdn.freefireofficial.com/icons/{item_id}.png"
    
    # Regions
    REGIONS = {
        "IND": "India",
        "BR": "Brazil", 
        "NA": "North America",
        "SA": "South America",
        "EU": "Europe",
        "ME": "Middle East",
        "PK": "Pakistan",
        "BD": "Bangladesh",
        "SG": "Singapore",
        "TH": "Thailand",
        "VN": "Vietnam",
        "ID": "Indonesia"
    }
    
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes default
        self.rate_limits = {}
        
    def _get_cache_key(self, *args) -> str:
        """Generate cache key from arguments"""
        key_string = "_".join(str(arg) for arg in args)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.cache:
            return False
        
        cached_data = self.cache[cache_key]
        if datetime.utcnow() - cached_data['timestamp'] > timedelta(seconds=self.cache_ttl):
            del self.cache[cache_key]
            return False
        
        return True
    
    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Get data from cache if valid"""
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        return None
    
    def _add_to_cache(self, cache_key: str, data: Any, ttl: Optional[int] = None):
        """Add data to cache"""
        self.cache[cache_key] = {
            'data': data,
            'timestamp': datetime.utcnow(),
            'ttl': ttl or self.cache_ttl
        }
    
    async def get_player_info(self, uid: str, region: str = "IND") -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Fetch player information from API
        
        Returns:
            Tuple[success: bool, data: Optional[Dict], error: Optional[str]]
        """
        cache_key = self._get_cache_key("player_info", uid, region)
        
        # Check cache first
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            logger.info(f"Cache hit for player {uid}")
            return True, cached_data, None
        
        # Fetch from API
        try:
            url = self.INFO_API_URL.format(uid=uid)
            logger.info(f"Fetching player info for UID: {uid}")
            
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Validate response
                    if not data or 'basicInfo' not in data:
                        return False, None, "Invalid API response"
                    
                    # Cache successful response
                    self._add_to_cache(cache_key, data, ttl=300)
                    return True, data, None
                    
                elif response.status == 404:
                    return False, None, "Player not found"
                elif response.status == 429:
                    return False, None, "Rate limit exceeded. Please try again later"
                else:
                    error_text = await response.text()
                    logger.error(f"API error {response.status}: {error_text}")
                    return False, None, f"API error: {response.status}"
                    
        except asyncio.TimeoutError:
            logger.error(f"Timeout fetching player {uid}")
            return False, None, "Request timeout. Please try again"
        except aiohttp.ClientError as e:
            logger.error(f"Network error fetching player {uid}: {e}")
            return False, None, "Network error. Please try again"
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON response for player {uid}")
            return False, None, "Invalid API response format"
        except Exception as e:
            logger.error(f"Unexpected error fetching player {uid}: {e}")
            return False, None, "Unexpected error occurred"
    
    async def get_outfit_image(self, uid: str, region: str = "IND") -> Tuple[bool, Optional[bytes], Optional[str]]:
        """
        Fetch player outfit image
        
        Returns:
            Tuple[success: bool, image_data: Optional[bytes], error: Optional[str]]
        """
        cache_key = self._get_cache_key("outfit_image", uid, region)
        
        # Check cache
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            logger.info(f"Cache hit for outfit image {uid}")
            return True, cached_data, None
        
        try:
            url = self.OUTFIT_API_URL.format(uid=uid, region=region)
            logger.info(f"Fetching outfit image for UID: {uid}")
            
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=20)) as response:
                if response.status == 200:
                    image_data = await response.read()
                    
                    # Validate it's actually an image
                    if len(image_data) < 100:
                        return False, None, "Invalid image data"
                    
                    # Cache the image
                    self._add_to_cache(cache_key, image_data, ttl=600)  # 10 minutes
                    return True, image_data, None
                else:
                    return False, None, f"Failed to fetch outfit image: {response.status}"
                    
        except asyncio.TimeoutError:
            return False, None, "Outfit image request timeout"
        except Exception as e:
            logger.error(f"Error fetching outfit image: {e}")
            return False, None, "Failed to fetch outfit image"
    
    async def get_item_icon(self, item_id: str) -> Tuple[bool, Optional[bytes], Optional[str]]:
        """
        Fetch item icon
        
        Returns:
            Tuple[success: bool, image_data: Optional[bytes], error: Optional[str]]
        """
        cache_key = self._get_cache_key("item_icon", item_id)
        
        # Check cache
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return True, cached_data, None
        
        try:
            url = self.ITEM_ICON_URL.format(item_id=item_id)
            
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    image_data = await response.read()
                    
                    # Cache for longer (items don't change)
                    self._add_to_cache(cache_key, image_data, ttl=3600)  # 1 hour
                    return True, image_data, None
                else:
                    return False, None, f"Item icon not found: {item_id}"
                    
        except Exception as e:
            logger.error(f"Error fetching item icon {item_id}: {e}")
            return False, None, "Failed to fetch item icon"
    
    def clear_cache(self, pattern: Optional[str] = None):
        """Clear cache entries matching pattern"""
        if pattern is None:
            self.cache.clear()
            logger.info("Cache cleared completely")
        else:
            keys_to_delete = [k for k in self.cache.keys() if pattern in k]
            for key in keys_to_delete:
                del self.cache[key]
            logger.info(f"Cleared {len(keys_to_delete)} cache entries matching '{pattern}'")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_entries = len(self.cache)
        valid_entries = sum(1 for key in self.cache.keys() if self._is_cache_valid(key))
        
        return {
            "total_entries": total_entries,
            "valid_entries": valid_entries,
            "expired_entries": total_entries - valid_entries,
            "cache_ttl": self.cache_ttl
        }


class DataFormatter:
    """Format API data for Discord embeds"""
    
    @staticmethod
    def format_number(number: int) -> str:
        """Format large numbers with commas"""
        return f"{number:,}"
    
    @staticmethod
    def format_timestamp(timestamp: int) -> str:
        """Format Unix timestamp to readable date"""
        if timestamp <= 0:
            return "N/A"
        try:
            dt = datetime.utcfromtimestamp(timestamp)
            return dt.strftime('%Y-%m-%d %H:%M:%S UTC')
        except:
            return "Invalid Date"
    
    @staticmethod
    def get_rank_emoji(rank) -> str:
        """Get emoji for rank"""
        # Convert to string and uppercase to handle any type
        try:
            rank_upper = str(rank).upper()
        except:
            return "🎮"
            
        emojis = {
            "BRONZE": "🥉",
            "SILVER": "🥈",
            "GOLD": "🥇",
            "PLATINUM": "💎",
            "DIAMOND": "💠",
            "HEROIC": "👑",
            "GRANDMASTER": "⭐"
        }
        
        for rank_name, emoji in emojis.items():
            if rank_name in rank_upper:
                return emoji
        
        return "🎮"
    
    @staticmethod
    def calculate_kd_ratio(kills: int, deaths: int) -> str:
        """Calculate K/D ratio"""
        if deaths == 0:
            return f"{kills:.2f}" if kills > 0 else "0.00"
        return f"{kills / deaths:.2f}"
    
    @staticmethod
    def get_region_flag(region) -> str:
        """Get flag emoji for region"""
        # Convert to string and uppercase to handle any type
        try:
            region_str = str(region).upper()
        except:
            return "🌍"
            
        flags = {
            "IND": "🇮🇳",
            "BR": "🇧🇷",
            "NA": "🇺🇸",
            "SA": "🇦🇷",
            "EU": "🇪🇺",
            "ME": "🇸🇦",
            "PK": "🇵🇰",
            "BD": "🇧🇩",
            "SG": "🇸🇬",
            "TH": "🇹🇭",
            "VN": "🇻🇳",
            "ID": "🇮🇩"
        }
        return flags.get(region_str, "🌍")
