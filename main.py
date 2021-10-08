import logging
from datetime import date, datetime
from typing import Dict

import hikari
import toml
from hikari import GuildTextChannel
from hikari.embeds import Embed

with open("config.toml", "r") as f:
    config = toml.loads(f.read())

bot = hikari.GatewayBot(token=config["token"])
prefix: str = config["prefix"]
injects: Dict = {}

# Officer name mappings to Discord IDs
officer: Dict[str, int] = {
    "brandon": 393909790625103883,
    "chase": 253044291935404032,
    "ramon": 121294930806177794,
}


@bot.listen()
async def update_injects(event: hikari.GuildMessageCreateEvent) -> None:
    if event.is_bot or not event.content:
        return

    if event.content.startswith(f"{prefix}inject"):
        member = await bot.rest.fetch_member(event.guild_id, event.author_id)
        if member is not None:
            if int(config["officer_role_id"]) not in member.role_ids:
                logging.warning(
                    f"{event.author.username}#{event.author.discriminator} tried to update injects."
                )
                return

        input: str | None = event.message.content
        if input is not None:
            global injects
            injects = {}
            input_injects = toml.loads(input.split(" ", 1)[1])
            for i in range(len(input_injects["problems"])):
                injects[input_injects["problems"][i]] = input_injects["solutions"][i]
            await event.message.respond("Updated injects!")
            logging.info(
                f"{event.author.username}#{event.author.discriminator} updated injects to {injects}."
            )
        else:
            await event.message.respond("Unable to update injects.")
            logging.info(
                f"{event.author.username}#{event.author.discriminator} tried to update injects unsuccessfully."
            )

        await event.message.delete()


@bot.listen()
async def submit(event: hikari.GuildMessageCreateEvent) -> None:
    if event.is_bot or not event.content:
        return

    if event.content.startswith(f"{prefix}submit"):
        input: str | None = event.message.content
        if input is not None:
            try:
                problem: str = input.split()[1]
                solution: str = input.split()[2]
                if problem in injects.keys() and solution == injects[problem]:
                    await event.message.respond(
                        f"{event.message.author.mention} has solved Challenge {problem}!"
                    )
                    logging.info(
                        f"{event.author.username}#{event.author.discriminator} successfully solved Challenge {problem}."
                    )
                else:
                    await event.message.respond(
                        f"{event.message.author.mention} Sorry, not quite."
                    )
                    logging.info(
                        f"{event.author.username}#{event.author.discriminator} failed to solve Challenge {problem}."
                    )
            except IndexError:
                await event.message.respond(
                    f"{event.message.author.mention}, invalid submission."
                )
                logging.info(
                    f"{event.author.username}#{event.author.discriminator} submitted an invalid input. Input was {event.message.content}."
                )
        else:
            await event.message.respond("Something went wrong!")
            logging.error(
                f"Something went wrong on challenge submission. Input was {event.message.content}."
            )

        await event.message.delete()


@bot.listen()
async def question(event: hikari.DMMessageCreateEvent) -> None:
    if event.is_bot or not event.content:
        return

    channel = await bot.rest.fetch_channel(config["question_id"])
    if isinstance(channel, GuildTextChannel):
        await channel.send(
            f"""<@&{config['officer_role_id']}>
            **Question**:
            {event.message.content}
            """
        )
        logging.info(f"Someone submitted a question: {event.message.content}.")
    else:
        logging.error("Unable to find question channel.")


@bot.listen()
async def announce(event: hikari.GuildMessageCreateEvent) -> None:
    if event.is_bot or not event.content:
        return

    if event.content.startswith(f"{prefix}announce"):
        member = await bot.rest.fetch_member(event.guild_id, event.author_id)
        if member is not None:
            if int(config["officer_role_id"]) not in member.role_ids:
                logging.warning(
                    f"{event.author.username}#{event.author.discriminator} tried to make an announcement."
                )
                return

        input: str | None = event.message.content
        if input is not None:
            # Prep work
            announcement = {}
            try:
                announcement = toml.loads(input.split(" ", 1)[1])
            except toml.TomlDecodeError:
                logging.error(f"Invalid announcement {event.message.content}.")
                return

            when = None
            if announcement["date"]:
                when = datetime.fromisoformat(announcement["date"])
            else:
                when = date.today()

            # Embed setup
            message = Embed()
            if announcement["type"] == "gbm":
                message.color = "000000"
                message.title = f"**General Body Meeting**"
            elif announcement["type"] == "competition":
                message.color = "a6192e"
                message.title = f"**Competition Team Meeting**"

            presenter = announcement["presenter"].lower()
            if presenter in officer.keys():
                presenter = await bot.rest.fetch_user(officer[presenter])
                presenter = presenter.mention
            else:
                presenter = announcement["presenter"]

            stream = ""
            if announcement["stream"]:
                stream = f"[[Stream]({announcement['stream']})]"

            recording = ""
            if announcement["recording"]:
                recording = f"[[Recording]({announcement['recording']})]"

            start = ""
            if announcement["start"]:
                start = f"• {announcement['start']}"

            room = "PG-242"
            if announcement["room"]:
                room = announcement["room"]

            message.description = f"""
            **{announcement["title"]}**
            {announcement["description"]}
            [[Slides]({announcement['slides']})] {stream}  {recording}

            Presented by {presenter}"""

            # Parse reminders
            if announcement["reminders"]:
                reminders = ""
                for reminder in announcement["reminders"]:
                    reminders += f"- {reminder}\n"
                message.add_field("Reminders", reminders)

            message.set_footer(
                f"{room} • {when.strftime('%-m/%-d/%y')} {start}",
                icon="https://sdsucyberdefense.org/images/cdt_logo.png",
            )
            await event.message.delete()
            await event.message.respond(message)
            logging.info(
                f"{event.author.username}#{event.author.discriminator} made an announcement!"
            )


bot.run()
