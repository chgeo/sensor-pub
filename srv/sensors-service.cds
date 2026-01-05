using { sensors as db } from '../db/schema';

@rest
@path: '/sensors/data'
service SensorsService {

  @readonly entity ![all] as projection on db.Data;

  @readonly entity current as projection on db.Data
    order by time desc
    limit 1;

}
