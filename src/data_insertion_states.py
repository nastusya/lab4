from enum import Enum


class DataInsertionStates(Enum):
    ATTEMPT_TO_REFILL_STATUS = 'ATTEMPT_TO_REFILL'
    COMPLETED_STATUS = 'COMPLETED'
    STARTED_STATUS = 'STARTED'
