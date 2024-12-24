from enum import Enum


class SlackChannel(Enum):
    HKTVMALL_HYBRIS_REVAMP_CHECKOUT_QA = (
    "C0817D27M53", "hktvmall-hybris-revamp-checkout-qa", '18qF2qRLfyNfCozqSEOx4NrlW1tK7Di7_91syJ1UuL-o')
    HKTVMALL_HYBRIS_REVAMP_DEV = (
    "C05892F5T6H", "hktvmall-hybris-revamp-dev", '18qF2qRLfyNfCozqSEOx4NrlW1tK7Di7_91syJ1UuL-o')
    HKTVMALL_HYBRIS_REVAMP_CHECKOUT_DEV = (
        "C07NP241ZAT", "hktvmall-hybris-revamp-checkout-dev", '18qF2qRLfyNfCozqSEOx4NrlW1tK7Di7_91syJ1UuL-o')
    HKTVMALL_HYBRIS_REVAMP_QA = ("C05JT4VMXSN", "hktvmall-hybris-revamp-qa", '18qF2qRLfyNfCozqSEOx4NrlW1tK7Di7_91syJ1UuL-o')

    def __init__(self, id, channel_name, sheet_id):
        self.id = id
        self.channel_name = channel_name
        self.sheet_id = sheet_id

class SlackWebhooks(Enum):
    gitlab_build_team1 = ("T1PH69YNN/B086C7DBMR7/mH2DqToQnKbkQeVM7iByLw88")