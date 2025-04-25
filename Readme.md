# Discord New Account Restrictor

A security tool for Discord servers that automatically assigns a restricted role to new accounts.

## Features

- Automatically detects and restricts accounts newer than a set threshold
- Prevents new accounts from sending links, files, or embeds
- Allows basic text chat and voice communication
- Customizable minimum account age requirement
- Works across multiple servers simultaneously
- Easy setup with automatic role creation and permission configuration

## Commands

`.restrict setup <server_id>` - Set up the restrictor in a server
`.restrict on/off` - Enable or disable the system
`.restrict days <number>` - Set minimum account age (in days)
`.restrict role <name>` - Customize the role name
`.restrict status` - View current settings and statistics
`.restrict reset` - Clear the processed users cache
`.restrict kill` - Stop the script

## How It Works

1. When a new user joins a server, the script checks their account age
2. If the account is newer than the set threshold, it automatically assigns the restricted role
3. The restricted role has custom permissions that:
   - Allows reading and sending basic text messages
   - Allows connecting to voice channels and speaking
   - Prevents sending links, files, GIFs, and embeds
   - Prevents mentioning @everyone or @here
   - Prevents using external emojis

4. A notification is sent to the server's system channel (if available)
5. The role remains until manually removed by server moderators

## Installation

1. Add the script to your selfbot scripts folder
2. Reload your scripts or restart your selfbot
3. Use `.restrict setup <server_id>` to configure the script for your server

## Requirements

- The bot account must have "Manage Roles" and "Manage Channels" permissions
- The bot's role must be higher in the hierarchy than the restricted role it creates

## Credits

Created by jealousy, inspired by Boredom

## Disclaimer

Using selfbots is against Discord's Terms of Service. This tool is provided for educational purposes only. Use at your own risk.