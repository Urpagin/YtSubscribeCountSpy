#!/usr/bin/python
# -*- coding: utf-8 -*-
# -*- version: 3.11 -*-
import time

from discord_webhook import DiscordWebhook
import pickle
from youtube_channel_statistics import YTChannelStatistics
import tomllib
from dotenv import load_dotenv
import os
from dataclasses import dataclass, field


def make_config_file(config_filename: str) -> None:
    """Creates the toml config file if it doesn't exist."""

    if os.path.isfile(config_filename):
        print(f"Found config file: {config_filename!r}")
    else:
        with open(config_filename, 'w') as file:
            base_file_data = (f"# Don't forget the double quotes in field 'channel_id' because it's a string.\n"
                              f"[channel_info]\n\tchannel_id = <FILL_HERE>\n\tbase_subs_count = <FILL_HERE>\n\n"
                              f"[runtime]\n\tstep_value = <FILL_HERE>\n\tcheck_interval = <FILL_HERE> # in seconds")
            file.write(base_file_data)
        quit(f"Please open {config_filename!r} and fill in the fields.")


@dataclass
class LoadConfig:
    """A class that loads variables from a toml config file."""
    config_filename: str

    channel_id: str = None, field(init=False)
    base_subs_count: int = None, field(init=False)
    subs_diff_step_value: int = None, field(init=False)
    check_interval: float = None, field(init=False)

    def load_config(self) -> dict:
        with open(self.config_filename, 'rb') as file:
            config_data: dict = tomllib.load(file)

        return config_data

    def __post_init__(self):
        config_data = self.load_config()

        self.channel_id = config_data['channel_info']['channel_id']
        self.base_subs_count = config_data['channel_info']['base_subs_count']
        self.subs_diff_step_value = config_data['runtime']['step_value']
        self.check_interval = config_data['runtime']['check_interval']


@dataclass
class LoadEnv:
    """A class that loads variables from a .env file."""
    youtube_api_key: str = field(init=False)
    discord_webhook_url: str = field(init=False)

    def __post_init__(self):
        load_dotenv()
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        self.discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL")


def has_changed(current_sub_count: int, step: int, filename: str) -> tuple[bool, int] | bool:
    """Returns True if subcount in pickle is equal to currentsubvcount AND picklesubcount is greater than step"""

    then_sub_count = read_diff(filename)

    if not current_sub_count != then_sub_count:
        return False
    if then_sub_count > step:
        return True


def number_prettifier(n: int) -> str:
    return f'{n:,}'.replace(',', ' ')


def send_webhook(webhook_url: str, message: str) -> None:
    """Sends a Discord webhook."""
    webhook = DiscordWebhook(url=webhook_url, content=message)

    try:
        status_code = webhook.execute().status_code
        print(f"Successfully sent webhook. Status code: {status_code}")
    except Exception as e:
        print(f"Failed to send webhook. Error: {e}")


def webhook_message(channel: YTChannelStatistics, sub_diff: int):
    return (f":clock1: <t:{get_current_timestamp()}:F> :clock1:\n"
            f"-**{channel.name}** has roughly **{number_prettifier(channel.subscriber_count)}** subscribers.\n"
            f"-That means **{channel.name}** lost roughly **{number_prettifier(sub_diff)}** subscribers!")


def get_current_timestamp() -> int:
    return int(time.time())


def write_subs(current_subs: int, filename: str) -> None:
    """writes the current subscribers in .pickle file."""

    with open(filename, 'wb') as file:
        pickle.dump(current_subs, file)


def read_diff(filename: str) -> int:
    """Reads the .pickle file that contains the difference of subscribers and returns it."""

    with open(filename, 'rb') as f:
        return pickle.load(f)


def main() -> None:
    make_config_file(CONFIG_FILENAME)
    env = LoadEnv()
    config = LoadConfig(CONFIG_FILENAME)

    channel = YTChannelStatistics(channel_id=config.channel_id, youtube_api_token=env.youtube_api_key)
    write_subs(current_subs=channel.subscriber_count, filename=DIFFERENCE_PICKLE_FILENAME)

    while True:
        channel = YTChannelStatistics(channel_id=config.channel_id, youtube_api_token=env.youtube_api_key)
        if has_changed(current_sub_count=channel.subscriber_count,
                       step=config.subs_diff_step_value, filename=DIFFERENCE_PICKLE_FILENAME):
            message = webhook_message(channel=channel, youtube_token=env.youtube_api_key,
                                      sub_diff=config.subs_diff_step_value)
            send_webhook(webhook_url=env.discord_webhook_url, message=message)
        write_subs(current_subs=channel.subscriber_count, filename=DIFFERENCE_PICKLE_FILENAME)

        time.sleep(config.check_interval)


if __name__ == '__main__':
    CONFIG_FILENAME = 'config.toml'
    DIFFERENCE_PICKLE_FILENAME = 'diff.pickle'
    main()
