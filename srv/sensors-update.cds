using { sensors as db } from '../db/schema';

@rest
@path: '/sensors/update'
service SensorsUpdateService {

  entity data as projection on db.Data;
}
