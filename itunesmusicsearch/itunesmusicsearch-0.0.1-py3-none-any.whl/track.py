from itunesmusicsearch import result_item

class Track(result_item.ResultItem):

    def __init__(self, json):
        """
        Initializes the ResultItem class from the JSON provided
        :param json: String. Raw JSON data to fetch information from
        """
        result_item.ResultItem.__init__(self, json)

    def get_track_time_minutes(self, round_number=2):
        """
        Retrieves the track's length and converts it to minutes
        :param round_number: Int. Number of decimals to round the minutes
        :return: Int. Track length in minutes
        """
        return round(self.track_time / 60000, round_number)

    def get_track_time_hours(self, round_number=2):
        """
        Retrieves the track's length and converts it to hours
        :param round_number: Int. Number of decimals to round the hours
        :return: Int. Track length in hours
        """
        return round(self.track_time / 6000000, round_number)
