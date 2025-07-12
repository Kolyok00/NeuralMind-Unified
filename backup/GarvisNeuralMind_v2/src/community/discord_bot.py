"""
Discord Bot Integration - Bridge between Discord and GarvisNeuralMind Community.
"""

import asyncio
import logging
from typing import Optional, Dict, Any

try:
    import discord
    from discord.ext import commands
    DISCORD_AVAILABLE = True
except ImportError:
    DISCORD_AVAILABLE = False
    discord = None
    commands = None

from src.core.config import get_settings

logger = logging.getLogger(__name__)


class DiscordBot:
    """Discord bot for community integration."""
    
    def __init__(self):
        self.settings = get_settings()
        self.bot: Optional[commands.Bot] = None
        self._running = False
        
        if not DISCORD_AVAILABLE:
            logger.warning("📱 Discord.py not available - Discord integration disabled")
            return
        
        if not self.settings.DISCORD_BOT_TOKEN:
            logger.info("📱 Discord bot token not provided - Discord integration disabled")
            return
        
        # Initialize Discord bot
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        
        self.bot = commands.Bot(
            command_prefix='!garvis ',
            intents=intents,
            description="GarvisNeuralMind Community Assistant"
        )
        
        self._setup_commands()
        self._setup_events()
    
    async def start(self):
        """Start the Discord bot."""
        if not self.bot or not self.settings.DISCORD_BOT_TOKEN:
            logger.info("📱 Discord bot not starting - missing bot or token")
            return
        
        try:
            self._running = True
            # Start bot in background task
            asyncio.create_task(self.bot.start(self.settings.DISCORD_BOT_TOKEN))
            logger.info("📱 Discord bot started successfully")
        except Exception as e:
            logger.error(f"📱 Failed to start Discord bot: {e}")
    
    async def stop(self):
        """Stop the Discord bot."""
        if self.bot and self._running:
            self._running = False
            await self.bot.close()
            logger.info("📱 Discord bot stopped")
    
    def _setup_commands(self):
        """Setup Discord bot commands."""
        if not self.bot:
            return
        
        @self.bot.command(name="help")
        async def help_command(ctx):
            """Show available commands."""
            embed = discord.Embed(
                title="🤖 GarvisNeuralMind Commands",
                description="Available community commands",
                color=0x00ff00
            )
            
            embed.add_field(
                name="!garvis community",
                value="Get community statistics",
                inline=False
            )
            embed.add_field(
                name="!garvis profile @user",
                value="Get user profile information",
                inline=False
            )
            embed.add_field(
                name="!garvis invite",
                value="Get invitation link to the web platform",
                inline=False
            )
            embed.add_field(
                name="!garvis ai <message>",
                value="Chat with AI companion",
                inline=False
            )
            
            await ctx.send(embed=embed)
        
        @self.bot.command(name="community")
        async def community_stats(ctx):
            """Get community statistics."""
            try:
                # This would integrate with the CommunityManager
                stats = {
                    "total_members": len(ctx.guild.members) if ctx.guild else 0,
                    "online_members": len([m for m in ctx.guild.members if m.status != discord.Status.offline]) if ctx.guild else 0,
                    "platform_users": "Connect to web platform for detailed stats"
                }
                
                embed = discord.Embed(
                    title="📊 Community Statistics",
                    color=0x0099ff
                )
                
                embed.add_field(
                    name="Discord Members",
                    value=f"{stats['total_members']} total\n{stats['online_members']} online",
                    inline=True
                )
                embed.add_field(
                    name="Platform Integration",
                    value=stats['platform_users'],
                    inline=True
                )
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Error in community command: {e}")
                await ctx.send("❌ Error retrieving community statistics")
        
        @self.bot.command(name="profile")
        async def user_profile(ctx, member: discord.Member = None):
            """Get user profile information."""
            if not member:
                member = ctx.author
            
            embed = discord.Embed(
                title=f"👤 Profile: {member.display_name}",
                color=member.color
            )
            
            embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
            embed.add_field(name="Username", value=member.name, inline=True)
            embed.add_field(name="Joined Discord", value=member.created_at.strftime("%Y-%m-%d"), inline=True)
            embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d") if member.joined_at else "Unknown", inline=True)
            embed.add_field(name="Status", value=str(member.status).title(), inline=True)
            embed.add_field(name="Roles", value=", ".join([role.name for role in member.roles[1:]]) or "None", inline=False)
            
            # Add platform integration note
            embed.add_field(
                name="Platform Profile",
                value="Link your Discord to access full community features on the web platform!",
                inline=False
            )
            
            await ctx.send(embed=embed)
        
        @self.bot.command(name="invite")
        async def invite_command(ctx):
            """Get invitation link to the web platform."""
            embed = discord.Embed(
                title="🌐 Join GarvisNeuralMind Platform",
                description="Experience the full community features on our web platform!",
                color=0xff9900
            )
            
            embed.add_field(
                name="Features",
                value="• AI Companions & VTuber interactions\n• Community posts & discussions\n• Real-time chat\n• User profiles & achievements\n• Plugin system",
                inline=False
            )
            
            embed.add_field(
                name="Access",
                value="Visit: http://localhost:8000\n*(Update this with your actual domain)*",
                inline=False
            )
            
            await ctx.send(embed=embed)
        
        @self.bot.command(name="ai")
        async def ai_chat(ctx, *, message: str):
            """Chat with AI companion."""
            try:
                # This would integrate with the AI system
                embed = discord.Embed(
                    title="🤖 AI Response",
                    description=f"Hello {ctx.author.mention}! This is a placeholder response. The full AI integration will provide personalized responses based on your community profile and preferences.",
                    color=0x9900ff
                )
                
                embed.add_field(
                    name="Your Message",
                    value=message[:500] + "..." if len(message) > 500 else message,
                    inline=False
                )
                
                embed.add_field(
                    name="Enhanced AI Features",
                    value="Visit the web platform for advanced AI interactions, voice chat, and personalized companions!",
                    inline=False
                )
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Error in AI chat: {e}")
                await ctx.send("❌ Error processing AI request")
    
    def _setup_events(self):
        """Setup Discord bot events."""
        if not self.bot:
            return
        
        @self.bot.event
        async def on_ready():
            """Bot ready event."""
            logger.info(f"📱 Discord bot {self.bot.user} is ready!")
            
            # Set bot activity
            activity = discord.Activity(
                type=discord.ActivityType.watching,
                name="GarvisNeuralMind Community"
            )
            await self.bot.change_presence(activity=activity)
        
        @self.bot.event
        async def on_member_join(member):
            """Welcome new members."""
            if not member.guild:
                return
            
            # Find welcome channel
            welcome_channel = discord.utils.get(member.guild.channels, name="welcome")
            if not welcome_channel:
                welcome_channel = discord.utils.get(member.guild.channels, name="general")
            
            if welcome_channel:
                embed = discord.Embed(
                    title="🎉 Welcome to GarvisNeuralMind Community!",
                    description=f"Hello {member.mention}! Welcome to our AI-powered community.",
                    color=0x00ff00
                )
                
                embed.add_field(
                    name="Getting Started",
                    value="• Use `!garvis help` to see available commands\n• Join our web platform for full features\n• Introduce yourself in the chat!",
                    inline=False
                )
                
                embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
                
                await welcome_channel.send(embed=embed)
        
        @self.bot.event
        async def on_message(message):
            """Handle messages."""
            if message.author == self.bot.user:
                return
            
            # Process commands
            await self.bot.process_commands(message)
            
            # Handle mentions or AI keywords
            if self.bot.user.mentioned_in(message) or any(keyword in message.content.lower() for keyword in ["ai", "assistant", "help"]):
                if not message.content.startswith("!garvis"):
                    embed = discord.Embed(
                        title="🤖 GarvisNeuralMind Assistant",
                        description="Hello! I'm here to help with community features. Use `!garvis help` to see available commands.",
                        color=0x0099ff
                    )
                    
                    await message.channel.send(embed=embed)
        
        @self.bot.event
        async def on_command_error(ctx, error):
            """Handle command errors."""
            if isinstance(error, commands.CommandNotFound):
                embed = discord.Embed(
                    title="❌ Command Not Found",
                    description=f"Command not found. Use `!garvis help` to see available commands.",
                    color=0xff0000
                )
                await ctx.send(embed=embed)
            else:
                logger.error(f"Discord command error: {error}")
                await ctx.send("❌ An error occurred while processing the command.")
    
    # Integration methods for community platform
    
    async def notify_new_user(self, username: str, user_id: int):
        """Notify Discord about new platform user."""
        if not self.bot or not self._running:
            return
        
        # Find notification channel
        guild_id = self.settings.DISCORD_GUILD_ID
        if guild_id:
            guild = self.bot.get_guild(int(guild_id))
            if guild:
                channel = discord.utils.get(guild.channels, name="community-updates")
                if channel:
                    embed = discord.Embed(
                        title="👋 New Community Member",
                        description=f"**{username}** just joined the platform!",
                        color=0x00ff00
                    )
                    await channel.send(embed=embed)
    
    async def notify_community_milestone(self, milestone_type: str, data: Dict[str, Any]):
        """Notify Discord about community milestones."""
        if not self.bot or not self._running:
            return
        
        guild_id = self.settings.DISCORD_GUILD_ID
        if guild_id:
            guild = self.bot.get_guild(int(guild_id))
            if guild:
                channel = discord.utils.get(guild.channels, name="community-updates")
                if channel:
                    embed = discord.Embed(
                        title="🎉 Community Milestone",
                        description=f"Our community reached a new milestone: {milestone_type}",
                        color=0xff9900
                    )
                    for key, value in data.items():
                        embed.add_field(name=key.title(), value=value, inline=True)
                    
                    await channel.send(embed=embed)
    
    async def sync_user_roles(self, discord_user_id: int, platform_roles: list):
        """Sync user roles between platform and Discord."""
        if not self.bot or not self._running:
            return
        
        # This would implement role synchronization
        # For now, just log the action
        logger.info(f"📱 Role sync requested for Discord user {discord_user_id}: {platform_roles}")


# Global instance
discord_bot = DiscordBot()