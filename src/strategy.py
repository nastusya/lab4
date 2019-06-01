import abc
import pandas as pd
import redis
import config_reader
from data_insertion_states import DataInsertionStates as States
from sodapy import Socrata


NUMBER_OF_MESSAGES = int(config_reader.cfg.get('LAB', 'number_of_messages'))
ENCODING = config_reader.cfg.get('LAB', 'encoding')
MESSAGES_PER_FETCH = int(config_reader.cfg.get('LAB', 'messages_per_fetch'))


class StrategySelector(object):
    def __init__(self, url, filename):
        self.dataset_filename = filename.strip()
        self.dataset_url = url.strip()

        self.strategies = {
            'terminal': DataWriterToTerminal(url=self.dataset_url, filename=self.dataset_filename)
        }

    def execute(self):
        strategy_name = config_reader.cfg.get('LAB', 'strategy_name')
        self.strategies[strategy_name].execute()


class BaseDataWriter(metaclass=abc.ABCMeta):
    def __init__(self, url=None, filename=None):
        self.dataset_url = url
        self.dataset_filename = filename

        self.redis_client = redis.Redis(
            host=config_reader.cfg.get('LAB', 'redis_host'),
            port=int(config_reader.cfg.get('LAB', 'redis_port')),
            db=0
        )

    @abc.abstractmethod
    def execute(self):
        pass


class DataWriterToTerminal(BaseDataWriter):
    def __init__(self, url, filename):
        super(DataWriterToTerminal, self).__init__(url, filename)

    def execute(self):
        dataset_id = '{}_{}'.format(self.dataset_url, self.dataset_filename)
        latest_status = self.redis_client.get(dataset_id)

        if latest_status == str(States.COMPLETED_STATUS) or latest_status == str(States.ATTEMPT_TO_REFILL_STATUS):
            self.redis_client.set(dataset_id, States.ATTEMPT_TO_REFILL_STATUS)

        client = Socrata(self.dataset_url, None)

        self.redis_client.set(dataset_id, str(States.STARTED_STATUS))

        for i in range(int(NUMBER_OF_MESSAGES / MESSAGES_PER_FETCH)):
            results = client.get(self.dataset_filename, limit=MESSAGES_PER_FETCH, offset=MESSAGES_PER_FETCH * i)

            results_df = pd.DataFrame.from_records(results)

            current_progress = '{} - {}'.format(str(i * MESSAGES_PER_FETCH + 1), str((i + 1) * MESSAGES_PER_FETCH))
            self.redis_client.set(dataset_id, current_progress)

            print('Progress {}'.format(current_progress))
            print(results_df)
            print()

        self.redis_client.set(self.dataset_url + "_" + self.dataset_filename, str(States.COMPLETED_STATUS))
