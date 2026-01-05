namespace sensors;

entity Data {
  key time: Timestamp @cds.on.insert : $now;
  temperature: Decimal(5,2);
  humidity: Decimal(5,2);
}