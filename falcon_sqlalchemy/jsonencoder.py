import datetime

from chainson import AbstractJSONEncoderWithChecker, DateTimeJSONEncoder, JSONEncoderChain

utc = datetime.timezone.utc


class UTCDateTimeJSONEncoder(DateTimeJSONEncoder):
    def enc(self, o: datetime.datetime):
        if o.tzinfo is None:
            # assume UTC
            o = o.replace(tzinfo=utc)
        return o.astimezone(utc).isoformat()


class SQLAlchemyEncoder(AbstractJSONEncoderWithChecker):
    def chk(self, o):
        return hasattr(o, "to_dict")

    def enc(self, o):
        return o.to_dict()


encoder = (
    JSONEncoderChain()
        .add_encoder(SQLAlchemyEncoder())
        .add_encoder(UTCDateTimeJSONEncoder())
)
