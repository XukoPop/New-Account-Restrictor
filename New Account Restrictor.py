@nightyScript(
    name="New Account Restrictor",
    author="jealousy",
    description="Restricts new accounts from sending files/links and limits them to basic messaging",
    usage="""`.restrict setup <server_id>` - Set up in a server
`.restrict on/off` - Enable/disable the system
`.restrict days <number>` - Set minimum account age
`.restrict role <name>` - Set role name
`.restrict status` - Check current settings
`.restrict reset` - Clear user cache
`.restrict kill` - Stop script"""
)
def new_account_restrictor():
    import json
    import asyncio
    import time
    from pathlib import Path
    from datetime import datetime, timedelta, timezone
    
    BASE_DIR = Path(getScriptsPath()) / "json"
    SERVERS_FILE = BASE_DIR / "restrict_servers.json"
    USERS_FILE = BASE_DIR / "restrict_processed.json"
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    
    CFG_ENABLED = "restrict_enabled"
    CFG_DAYS = "restrict_min_days"
    CFG_ROLE_NAME = "restrict_role_name"
    
    stats = {
        "start_time": time.time(),
        "detected": 0,
        "processed": 0
    }
    
    if not SERVERS_FILE.exists():
        with open(SERVERS_FILE, "w") as f:
            json.dump([], f, indent=4)
    
    if not USERS_FILE.exists():
        with open(USERS_FILE, "w") as f:
            json.dump({}, f, indent=4)
    
    if getConfigData().get(CFG_ENABLED) is None:
        updateConfigData(CFG_ENABLED, True)
    if getConfigData().get(CFG_DAYS) is None:
        updateConfigData(CFG_DAYS, 7)
    if getConfigData().get(CFG_ROLE_NAME) is None:
        updateConfigData(CFG_ROLE_NAME, "Restricted")
    
    def load_servers():
        try:
            with open(SERVERS_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    
    def save_servers(servers):
        with open(SERVERS_FILE, "w") as f:
            json.dump(servers, f, indent=4)
    
    def load_processed():
        try:
            with open(USERS_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    
    def save_processed(users):
        with open(USERS_FILE, "w") as f:
            json.dump(users, f, indent=4)
    
    def format_time(seconds):
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if days > 0:
            return f"{days}d {hours}h {mins}m"
        elif hours > 0:
            return f"{hours}h {mins}m {secs}s"
        else:
            return f"{mins}m {secs}s"
    
    @bot.command(name="restrict", description="New account restriction system")
    async def restrict_cmd(ctx, cmd: str="", *, args: str=""):
        await ctx.message.delete()
        
        if not cmd:
            help_text = """**New Account Restrictor Commands:**
`.restrict setup <server_id>` - Set up in a server
`.restrict on/off` - Enable/disable system
`.restrict days <number>` - Set minimum days
`.restrict role <name>` - Set role name
`.restrict status` - View settings
`.restrict reset` - Clear user cache
`.restrict kill` - Stop script"""
            msg = await ctx.send(help_text)
            await asyncio.sleep(10)
            await msg.delete()
            return
        
        cmd = cmd.lower()
        
        if cmd == "setup":
            if not args:
                msg = await ctx.send("❌ Missing server ID. Use: `.restrict setup <server_id>`")
                await asyncio.sleep(5)
                await msg.delete()
                return
            
            try:
                server_id = int(args)
                guild = bot.get_guild(server_id)
                
                if not guild:
                    msg = await ctx.send("❌ Server not found or not accessible")
                    await asyncio.sleep(5)
                    await msg.delete()
                    return
                
                status_msg = await ctx.send(f"Setting up in server: {guild.name}...")
                
                if not guild.me.guild_permissions.manage_roles:
                    await status_msg.edit(content="❌ Missing 'Manage Roles' permission in server")
                    await asyncio.sleep(7)
                    await status_msg.delete()
                    return
                    
                if not guild.me.guild_permissions.manage_channels:
                    await status_msg.edit(content="❌ Missing 'Manage Channels' permission in server")
                    await asyncio.sleep(7)
                    await status_msg.delete()
                    return
                
                role_name = getConfigData().get(CFG_ROLE_NAME, "Restricted")
                role = None
                
                for r in guild.roles:
                    if r.name == role_name:
                        role = r
                        break
                
                if not role:
                    try:
                        role = await guild.create_role(
                            name=role_name,
                            color=0xff5555,
                            reason="New Account Restrictor setup"
                        )
                        
                        await status_msg.edit(content=f"Created '{role_name}' role, setting up permissions...")
                        
                        success_count = 0
                        fail_count = 0
                        
                        for channel in guild.channels:
                            try:
                                if str(channel.type).lower() == "text":
                                    await channel.set_permissions(
                                        role,
                                        read_messages=True,
                                        send_messages=True,
                                        embed_links=False,
                                        attach_files=False,
                                        add_reactions=True,
                                        external_emojis=False,
                                        mention_everyone=False,
                                        manage_messages=False,
                                        read_message_history=True
                                    )
                                    success_count += 1
                                    
                                elif str(channel.type).lower() == "voice":
                                    await channel.set_permissions(
                                        role,
                                        view_channel=True,
                                        connect=True,
                                        speak=True,
                                        stream=False,
                                        use_voice_activation=True
                                    )
                                    success_count += 1
                                    
                                else:
                                    await channel.set_permissions(
                                        role,
                                        view_channel=True,
                                        send_messages=False
                                    )
                                    success_count += 1
                                    
                            except Exception as e:
                                fail_count += 1
                                print(f"Failed to set permissions for {channel.name}: {str(e)}", type_="WARNING")
                                await asyncio.sleep(0.2)
                                
                        await status_msg.edit(content=f"Set up permissions for {success_count} channels ({fail_count} failed).")
                    except Exception as e:
                        await status_msg.edit(content=f"❌ Failed to create role: {str(e)}")
                        await asyncio.sleep(7)
                        await status_msg.delete()
                        return
                else:
                    await status_msg.edit(content=f"Using existing '{role_name}' role in {guild.name}")
                    
                    confirm_msg = await ctx.send(f"Role exists. Update channel permissions? (yes/no)")
                    
                    def check(m):
                        return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id
                    
                    try:
                        response = await bot.wait_for('message', check=check, timeout=15.0)
                        if response.content.lower() == 'yes':
                            await response.delete()
                            await confirm_msg.delete()
                            
                            await status_msg.edit(content=f"Updating permissions for '{role_name}' role...")
                            
                            success_count = 0
                            fail_count = 0
                            
                            for channel in guild.channels:
                                try:
                                    if str(channel.type).lower() == "text":
                                        await channel.set_permissions(
                                            role,
                                            read_messages=True,
                                            send_messages=True,
                                            embed_links=False,
                                            attach_files=False,
                                            add_reactions=True,
                                            external_emojis=False,
                                            mention_everyone=False,
                                            manage_messages=False,
                                            read_message_history=True
                                        )
                                        success_count += 1
                                        
                                    elif str(channel.type).lower() == "voice":
                                        await channel.set_permissions(
                                            role,
                                            view_channel=True,
                                            connect=True,
                                            speak=True,
                                            stream=False,
                                            use_voice_activation=True
                                        )
                                        success_count += 1
                                        
                                    else:
                                        await channel.set_permissions(
                                            role,
                                            view_channel=True,
                                            send_messages=False
                                        )
                                        success_count += 1
                                        
                                except Exception as e:
                                    fail_count += 1
                                    print(f"Failed to set permissions for {channel.name}: {str(e)}", type_="WARNING")
                                    await asyncio.sleep(0.2)
                                    
                            await status_msg.edit(content=f"Updated permissions for {success_count} channels ({fail_count} failed).")
                        else:
                            await response.delete()
                            await confirm_msg.delete()
                            await status_msg.edit(content=f"Skipped permission updates, using existing role as-is.")
                    except asyncio.TimeoutError:
                        await confirm_msg.delete()
                        await status_msg.edit(content=f"Timed out waiting for response. Using existing role without changes.")
                
                servers = load_servers()
                if str(server_id) not in servers:
                    servers.append(str(server_id))
                    save_servers(servers)
                
                updateConfigData(CFG_ENABLED, True)
                await status_msg.edit(content=f"✅ Setup complete! New accounts in {guild.name} will be restricted to text and voice only.")
                await asyncio.sleep(8)
                await status_msg.delete()
                
            except ValueError:
                msg = await ctx.send("❌ Invalid server ID")
                await asyncio.sleep(5)
                await msg.delete()
            except Exception as e:
                msg = await ctx.send(f"❌ Error: {str(e)}")
                await asyncio.sleep(5)
                await msg.delete()
        
        elif cmd == "on":
            updateConfigData(CFG_ENABLED, True)
            msg = await ctx.send("✅ New account restriction enabled")
            await asyncio.sleep(5)
            await msg.delete()
        
        elif cmd == "off":
            updateConfigData(CFG_ENABLED, False)
            msg = await ctx.send("❌ New account restriction disabled")
            await asyncio.sleep(5)
            await msg.delete()
        
        elif cmd == "days":
            if not args:
                msg = await ctx.send("❌ Missing days value. Use: `.restrict days <number>`")
                await asyncio.sleep(5)
                await msg.delete()
                return
            
            try:
                days = int(args)
                if days < 1:
                    msg = await ctx.send("❌ Days must be at least 1")
                    await asyncio.sleep(5)
                    await msg.delete()
                    return
                
                updateConfigData(CFG_DAYS, days)
                msg = await ctx.send(f"✅ Minimum account age set to {days} days")
                await asyncio.sleep(5)
                await msg.delete()
            
            except ValueError:
                msg = await ctx.send("❌ Invalid number")
                await asyncio.sleep(5)
                await msg.delete()
        
        elif cmd == "role":
            if not args:
                msg = await ctx.send("❌ Missing role name. Use: `.restrict role <name>`")
                await asyncio.sleep(5)
                await msg.delete()
                return
            
            updateConfigData(CFG_ROLE_NAME, args)
            msg = await ctx.send(f"✅ Role name set to '{args}'")
            await asyncio.sleep(5)
            await msg.delete()
        
        elif cmd == "status":
            enabled = getConfigData().get(CFG_ENABLED, True)
            days = getConfigData().get(CFG_DAYS, 7)
            role_name = getConfigData().get(CFG_ROLE_NAME, "Restricted")
            servers = load_servers()
            
            runtime = time.time() - stats["start_time"]
            
            status = f"""**New Account Restrictor Status:**
Status: {'✅ Enabled' if enabled else '❌ Disabled'}
Minimum Age: {days} days
Role Name: '{role_name}'
Servers: {len(servers)}
Uptime: {format_time(runtime)}
Accounts Checked: {stats['processed']}
Accounts Restricted: {stats['detected']}"""
            
            msg = await ctx.send(status)
            await asyncio.sleep(10)
            await msg.delete()
        
        elif cmd == "reset":
            save_processed({})
            msg = await ctx.send("🔄 Processed users cache cleared")
            await asyncio.sleep(5)
            await msg.delete()
        
        elif cmd == "kill":
            msg = await ctx.send("⚠️ Stopping New Account Restrictor...")
            
            try:
                bot.remove_command("restrict")
                bot.remove_listener(on_member_join_check, 'on_member_join')
                
                await msg.edit(content="💀 New Account Restrictor stopped")
                await asyncio.sleep(5)
                await msg.delete()
            except:
                await msg.edit(content="❌ Failed to properly stop the script")
                await asyncio.sleep(5)
                await msg.delete()
        
        else:
            msg = await ctx.send(f"❌ Unknown command: '{cmd}'")
            await asyncio.sleep(5)
            await msg.delete()
    
    @bot.listen('on_member_join')
    async def on_member_join_check(member):
        if not getConfigData().get(CFG_ENABLED, True):
            return
        
        servers = load_servers()
        if str(member.guild.id) not in servers:
            return
        
        processed = load_processed()
        server_id = str(member.guild.id)
        
        if server_id not in processed:
            processed[server_id] = []
        
        if str(member.id) in processed[server_id]:
            return
        
        min_days = getConfigData().get(CFG_DAYS, 7)
        role_name = getConfigData().get(CFG_ROLE_NAME, "Restricted")
        
        account_created = member.created_at
        if account_created.tzinfo is None:
            account_created = account_created.replace(tzinfo=timezone.utc)
        
        now = datetime.now(timezone.utc)
        account_age = now - account_created
        age_days = account_age.days
        
        processed[server_id].append(str(member.id))
        save_processed(processed)
        stats["processed"] += 1
        
        if age_days < min_days:
            try:
                role = None
                for r in member.guild.roles:
                    if r.name == role_name:
                        role = r
                        break
                
                if not role:
                    try:
                        role = await member.guild.create_role(
                            name=role_name,
                            color=0xff5555,
                            reason="New Account Restrictor - auto created"
                        )
                    except:
                        print(f"Failed to create role in {member.guild.name}", type_="ERROR")
                        return
                
                await member.add_roles(role, reason=f"Account age: {age_days} days (minimum: {min_days})")
                stats["detected"] += 1
                
                system_channel = member.guild.system_channel
                if system_channel:
                    if age_days > 0:
                        age_str = f"{age_days} days"
                    else:
                        hours = int(account_age.total_seconds() // 3600)
                        age_str = f"{hours} hours"
                    
                    notification = f"⚠️ {member.mention} has been restricted (text & voice only) because their account is only {age_str} old (minimum: {min_days} days)"
                    
                    try:
                        notification_msg = await system_channel.send(notification)
                        await asyncio.sleep(20)
                        await notification_msg.delete()
                    except:
                        pass
            
            except Exception as e:
                print(f"Error restricting member: {str(e)}", type_="ERROR")
    
    print("New Account Restrictor started. Use `.restrict` for help.", type_="INFO")

new_account_restrictor()