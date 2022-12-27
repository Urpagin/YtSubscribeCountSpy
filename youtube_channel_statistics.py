import requests


class YTChannelStatistics:
    """ Fetch the statistics of a given YouTube channel by its channelID """

    @staticmethod
    def number_prettifier(num: int | float | complex) -> str | None:
        # 1000000 -> 1 000 000, 1000000.555555 -> 1 000 000.555555, 1000j -> 1 000j
        if not isinstance(num, (int, float, complex)):
            return None
        return '{:,}'.format(num).replace(',', ' ')

    def __init__(self, channel_id: str, youtube_api_token: str):
        self._channel_id = channel_id
        self._youtube_api_token = youtube_api_token
        self.errors = []
        self.subscriber_count = None
        self.video_count = None
        self.view_count = None
        self.is_subscriber_count_hidden = None
        self.name = None
        self.description = None
        self.keywords = None
        self.country = None
        self.banner_url = None

        if not self._is_valid():
            raise TypeError

        self._parse_data_statistics()
        self._parse_data_branding()

    def _get_statistics_url(self) -> str:
        """Return the YoutubeApi url."""
        url = (
            f"https://www.googleapis.com/youtube/v3/channels?id="
            f"{self._channel_id}&key={self._youtube_api_token}&part=statistics"
        )
        return url

    def _get_branding_url(self) -> str:
        """Return the YoutubeApi url."""
        url = (
            f"https://www.googleapis.com/youtube/v3/channels?id="
            f"{self._channel_id}&key={self._youtube_api_token}&part=brandingSettings"
        )
        return url

    def _is_valid(self) -> bool:
        """ Verify that 'channel_id' & 'api_token' are str && the length they should be. If not return False."""

        if type(self._channel_id) != str or len(self._channel_id) != 24:
            print("The channel id is not correct.")
            return False
        if type(self._youtube_api_token) != str or len(self._youtube_api_token) != 39:
            print("The youtube api token is not correct")
            return False

        return True

    def _fetch_data(self, url: str) -> dict | None:
        """ Gets dict from the url with httpx.get() and json.load() methods."""
        try:
            site = requests.get(url)
        except Exception as e:
            print(f"Exception encountered: {str(e)}")
            self.errors.append(e)
            return None
        else:
            return site.json()

    def _parse_data_statistics(self):
        """ Get subscribers, views, video_count, is_sub_count_hidden. If error returns None"""
        data = self._fetch_data(self._get_statistics_url())

        if data is None:
            return

        try:
            self.subscriber_count = int(data['items'][0]['statistics']['subscriberCount'])
        except Exception as e:
            print(f"Exception encountered: {str(e)}")
            self.errors.append(e)
        try:
            self.view_count = int(data['items'][0]['statistics']['viewCount'])
        except Exception as e:
            print(f"Exception encountered: {str(e)}")
            self.errors.append(e)
        try:
            self.video_count = int(data['items'][0]['statistics']['videoCount'])
        except Exception as e:
            print(f"Exception encountered: {str(e)}")
            self.errors.append(e)
        try:
            self.is_subscriber_count_hidden = data['items'][0]['statistics']['hiddenSubscriberCount']
        except Exception as e:
            print(f"Exception encountered: {str(e)}")
            self.errors.append(e)

    def _parse_data_branding(self):
        """ Get name, description, keywords, country, banner_url If error returns None"""

        data = self._fetch_data(self._get_branding_url())

        if data is None:
            return

        try:
            self.name = data['items'][0]['brandingSettings']['channel']['title']
        except Exception as e:
            print(f"Exception encountered: {str(e)}")
            self.errors.append(e)
        try:
            self.description = data['items'][0]['brandingSettings']['channel']['description'].strip('\n')
        except Exception as e:
            print(f"Exception encountered: {str(e)}")
            self.errors.append(e)
        try:
            self.keywords = data['items'][0]['brandingSettings']['channel']['keywords']
        except Exception as e:
            print(f"Exception encountered: {str(e)}")
            self.errors.append(e)
        try:
            self.country = data['items'][0]['brandingSettings']['channel']['country']
        except Exception as e:
            print(f"Exception encountered: {str(e)}")
            self.errors.append(e)
        try:
            self.banner_url = data['items'][0]['brandingSettings']['image']['bannerExternalUrl']
        except Exception as e:
            print(f"Exception encountered: {str(e)}")
            self.errors.append(e)

    def __str__(self):
        return (
            f"_channel_id: {self._channel_id}\n"
            f"_api_token: {self._youtube_api_token}\n"
            f"errors: {self.errors}\n"
            f"subscriber_count: {self.subscriber_count}\n"
            f"video_count: {self.video_count}\n"
            f"view_count: {self.view_count}\n"
            f"is_subscriber_count_hidden: {self.is_subscriber_count_hidden}\n"
            f"name: {self.name}\n"
            f"description: {self.description}\n"
            f"keywords: {self.keywords}\n"
            f"country: {self.country}\n"
            f"banner_url: {self.banner_url}\n"
        )
